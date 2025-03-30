# --- START OF FULL FILE src/html_generator.py ---
# Delete all existing content in the file and paste this entire block.

"""
HTML Generator module for ProfileDash
Handles all HTML generation and processing
"""

import os
import re # Add re import here
import json
from datetime import datetime
import html # Standard library for HTML processing
import traceback # For detailed error logging

# --- Helper Function for Cleaning LLM Output ---
def clean_llm_output(content, section_num=None, section_title=None):
    """Removes ```html markers and duplicate titles if possible"""
    if not content:
        return ""

    # Remove ```html marker and ```
    content = content.replace('```html', '').replace('```', '')

    # Only attempt duplicate title removal if we have section info
    if section_num is not None and section_title is not None:
        # Pattern to find the expected H2 title (more robustly)
        h2_pattern_str = rf'<h2[^>]*>\s*{re.escape(str(section_num))}\.\s*{re.escape(section_title)}.*?</h2>'
        h2_match = re.search(h2_pattern_str, content, re.IGNORECASE | re.DOTALL)

        cleaned_content = content

        if h2_match:
            h2_end_pos = h2_match.end()
            escaped_title = re.escape(section_title)
            # Adjusted pattern to look for potential duplicates immediately following H2, possibly with whitespace/symbols
            duplicate_title_pattern_str = rf'^\s*(?:{re.escape(str(section_num))}\.\s*)?{escaped_title}\s*▼?\s*'
            following_content = content[h2_end_pos:]
            # Check if the following content *starts* with the duplicate title pattern
            duplicate_match = re.match(duplicate_title_pattern_str, following_content.lstrip(), re.IGNORECASE | re.MULTILINE)

            if duplicate_match:
                # If a duplicate is found right after H2, remove it
                # Calculate how much whitespace was stripped before the match
                leading_whitespace = len(following_content) - len(following_content.lstrip())
                # Remove the matched duplicate text plus any leading whitespace before it
                cleaned_content = content[:h2_end_pos + leading_whitespace] + following_content.lstrip()[duplicate_match.end():]
        # else: If H2 wasn't found, cleaned_content remains content (already stripped of ```html)

        return cleaned_content.strip()
    else:
        # If no section info, just remove the ```html markers
        return content.strip()
# --- END OF Helper FUNCTION ---


def create_profile_folder(company_name):
    """Create a unique folder for storing profile sections"""
    clean_name = ''.join(c for c in company_name if c.isalnum() or c in [' ', '_', '-']).replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"profile_{clean_name}_{timestamp}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name, timestamp

# save_section and load_section are not used by the Gradio app currently
# def save_section(profile_folder, section_number, content): ...
# def load_section(profile_folder, section_number): ...

def validate_html(html_content):
    """Simplified HTML validation."""
    if not html_content or not html_content.strip(): 
        print("Warning: Empty HTML content")
        return False
        
    # Basic structure check - look for any content between tags
    if not re.search(r'<[^>]+>.*?</[^>]+>', html_content, re.DOTALL):
        print("Warning: No valid HTML tags found")
        return False
        
    # Check for critical tags that must be balanced
    critical_tags = ['div', 'table', 'tr', 'td', 'th']
    for tag in critical_tags:
        try:
            opening = len(re.findall(f'<{tag}(?:\\s+[^>]*?)?>(?!</{tag}>)', html_content, re.IGNORECASE))
            closing = len(re.findall(f'</{tag}\\s*>', html_content, re.IGNORECASE))
            if opening != closing:
                print(f"Warning: Unbalanced <{tag}> tags. O:{opening}, C:{closing}")
                # Only fail validation for tables and their components
                if tag in ['table', 'tr', 'td', 'th']:
                    return False
        except Exception as e:
            print(f"Warning: Regex error validating <{tag}>: {e}")
            # Don't fail validation for regex errors
            
    return True

def repair_html(html_content, section_num=None, section_title=None):
    """Enhanced repair of common HTML issues."""
    import re
    MAX_ITERATIONS = 5
    current_iteration = 0

    # Default content if input is empty or None
    if not html_content or not html_content.strip():
        default_h2 = f'{section_num or "?"}. {section_title or "Untitled"}'
        return f'<div class="section" id="section-{section_num or "unknown"}"><h2>{default_h2}</h2><p class="error">No content available or generation failed.</p></div>'

    # --- Initial Cleaning ---
    html_content = re.sub(r'<br\s*>', '<br/>', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'^\s*[\*\-]\s+', '', html_content, flags=re.MULTILINE)
    html_content = html_content.replace('```html', '').replace('```', '')

    previous_content = ""
    while current_iteration < MAX_ITERATIONS and html_content != previous_content:
        previous_content = html_content
        current_iteration += 1
        cleaned_this_iter = False

        # 1. Ensure Section Wrapper and Header (if section info provided)
        if section_num is not None and section_title is not None:
            id_attr = f'id="section-{section_num}"'
            h2_text = f'{section_num}. {section_title}'
            div_start_pattern_outer = r'^\s*<div\s+class=["\']section["\']'
            div_start_pattern_inner = r'<div\s+class=["\']section["\']'
            h2_pattern_exact = rf'<h2[^>]*?>\s*{re.escape(h2_text)}\s*</h2\s*>'
            h2_pattern_generic = rf'<h2[^>]*?>\s*{re.escape(str(section_num))}\.\s*.*?</h2\s*>'

            if not re.match(div_start_pattern_outer, html_content, re.IGNORECASE | re.DOTALL):
                html_content = f'<div class="section" {id_attr}>\n{html_content}'
                cleaned_this_iter = True
            elif not re.search(rf'{div_start_pattern_inner}[^>]*?{id_attr}', html_content, re.IGNORECASE):
                 html_content = re.sub(div_start_pattern_inner, rf'\g<0> {id_attr}', html_content, count=1, flags=re.IGNORECASE)
                 cleaned_this_iter = True

            if not re.search(h2_pattern_exact, html_content, re.IGNORECASE | re.DOTALL):
                html_content = re.sub(h2_pattern_generic, '', html_content, flags=re.IGNORECASE | re.DOTALL)
                div_match = re.search(r'(<div\s+class=["\']section["\'][^>]*?>\n?)', html_content, flags=re.IGNORECASE)
                if div_match:
                    html_content = html_content[:div_match.end()] + f'<h2>{h2_text}</h2>\n' + html_content[div_match.end():]
                    cleaned_this_iter = True
                else:
                    html_content = f'<h2>{h2_text}</h2>\n' + html_content
                    cleaned_this_iter = True

        # 2. Ensure Closing Div (simple balancing)
        opening_divs = len(re.findall(r'<div(?!\s*/\s*>)', html_content, re.IGNORECASE))
        closing_divs = len(re.findall(r'</div\s*>', html_content, re.IGNORECASE))
        if opening_divs > closing_divs:
            html_content += '\n</div>' * (opening_divs - closing_divs)
            cleaned_this_iter = True
        elif closing_divs > opening_divs:
            extra = closing_divs - opening_divs
            temp_content = html_content.rstrip()
            removed_count = 0
            while removed_count < extra and temp_content.lower().endswith('</div>'):
                temp_content = temp_content[:-6].rstrip()
                removed_count += 1
            if removed_count > 0:
                html_content = temp_content + '\n'
                cleaned_this_iter = True

        # 3. Fix table structure (Basic thead/tbody addition)
        try:
            new_table_content = ""
            last_table_end = 0
            for table_match in re.finditer(r'(<table[^>]*>)(.*?)(</table\s*>)', html_content, re.DOTALL | re.IGNORECASE):
                new_table_content += html_content[last_table_end:table_match.start()]
                original_table = table_match.group(0)
                table_start_tag = table_match.group(1)
                table_inner_content = table_match.group(2).strip()
                table_end_tag = table_match.group(3)

                modified_inner_content = table_inner_content
                has_thead = bool(re.search(r'<thead[^>]*>', modified_inner_content, re.IGNORECASE))
                has_tbody = bool(re.search(r'<tbody[^>]*>', modified_inner_content, re.IGNORECASE))
                has_th = bool(re.search(r'<th[^>]*>', modified_inner_content, re.IGNORECASE))
                has_tr = bool(re.search(r'<tr[^>]*>', modified_inner_content, re.IGNORECASE))

                # Add <thead> if <th> is present but <thead> is missing
                if has_tr and has_th and not has_thead:
                    header_row_match = re.search(r'(<tr.*?(?:<th.*?>).*?</tr\s*>)', modified_inner_content, re.IGNORECASE | re.DOTALL)
                    if header_row_match:
                        header_row_html = header_row_match.group(1)
                        temp_inner_content = modified_inner_content.replace(header_row_html, '', 1).strip()
                        # Wrap remaining content in tbody if needed
                        if temp_inner_content and not has_tbody:
                             temp_inner_content = f"<tbody>\n{temp_inner_content}\n</tbody>"
                        modified_inner_content = f"<thead>\n{header_row_html}\n</thead>\n{temp_inner_content}"
                        has_thead = True
                        has_tbody = bool(re.search(r'<tbody[^>]*>', temp_inner_content, re.IGNORECASE))

                # Add <tbody> if <tr> exists but <tbody> is missing (and potentially after thead)
                if has_tr and not has_tbody:
                    tbody_content_to_wrap = modified_inner_content # Assume all content goes in tbody initially
                    if has_thead:
                        thead_match = re.search(r'(</thead\s*>)', modified_inner_content, re.IGNORECASE)
                        if thead_match:
                            thead_end_pos = thead_match.end()
                            tbody_content_to_wrap = modified_inner_content[thead_end_pos:].strip()
                            if tbody_content_to_wrap:
                                 modified_inner_content = modified_inner_content[:thead_end_pos] + f"\n<tbody>\n{tbody_content_to_wrap}\n</tbody>"
                        elif '<tr' in modified_inner_content: # thead opening exists but maybe no closing
                             first_tr_match = re.search(r'<tr.*', modified_inner_content, re.IGNORECASE | re.DOTALL)
                             if first_tr_match:
                                 thead_part = modified_inner_content[:first_tr_match.start()]
                                 body_part = first_tr_match.group(0)
                                 if body_part:
                                    modified_inner_content = thead_part + f"\n<tbody>\n{body_part}\n</tbody>"

                    elif tbody_content_to_wrap: # No thead, just wrap everything in tbody
                        modified_inner_content = f"<tbody>\n{tbody_content_to_wrap}\n</tbody>"

                new_table_html = table_start_tag + '\n' + modified_inner_content + '\n' + table_end_tag
                new_table_content += new_table_html
                last_table_end = table_match.end()
                if original_table != new_table_html:
                    cleaned_this_iter = True

            new_table_content += html_content[last_table_end:]
            html_content = new_table_content
        except Exception as e:
            print(f"Warning: Error during table repair for section {section_num}: {e}")


        # 4. Attempt to close common unclosed tags (simple append)
        tags_to_close = ['p', 'li', 'td', 'th', 'tr', 'ul', 'ol']
        for tag in tags_to_close:
            try:
                 opening = len(re.findall(f'<{tag}(?:\\s+[^>]*?)?>', html_content, re.IGNORECASE))
                 closing = len(re.findall(f'</{tag}\\s*>', html_content, re.IGNORECASE))
                 if opening > closing:
                     html_content += f'</{tag}>' * (opening - closing)
                     cleaned_this_iter = True
            except Exception as e:
                print(f"Warning: Error checking tag balance for <{tag}>: {e}")

        if not cleaned_this_iter and previous_content == html_content:
            break

    if current_iteration == MAX_ITERATIONS:
        print(f"Warning: HTML repair hit max iterations for section {section_num}.")

    if not validate_html(html_content):
        print(f"Warning: HTML repair failed validation for section {section_num}. Attempting text extraction fallback.")
        try:
            text_content = extract_text_from_html(html_content)
            if len(text_content) > 3000: text_content = text_content[:3000] + "..."
            escaped_text = html.escape(text_content) # Use html.escape for safety
            default_h2 = f'{section_num or "?"}. {section_title or "Untitled"}'
            html_content = f'''<div class="section" id="section-{section_num or "unknown"}"><h2>{default_h2}</h2><p class="error">Warning: Original HTML structure invalid, showing extracted text:</p><pre style="white-space: pre-wrap; word-wrap: break-word;">{escaped_text}</pre></div>'''
        except Exception as fallback_e:
            print(f"Error during fallback text extraction for section {section_num}: {fallback_e}")
            default_h2 = f'{section_num or "?"}. {section_title or "Untitled"}'
            html_content = f'<div class="section" id="section-{section_num or "unknown"}"><h2>{default_h2}</h2><p class="error">Error: Could not repair content or extract text.</p></div>'

    return html_content.strip()


# MODIFIED: Added app_version parameter
def generate_full_html_profile(company_name, sections, section_contents, app_version=""):
    """Generate a complete HTML document from section contents"""
    from datetime import datetime

    # --- CSS Modifications ---
    html_head = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Company Profile: {html.escape(company_name)}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"; margin: 20px; line-height: 1.6; background-color: #f4f7f6; color: #212529; }} /* <-- Changed body color */
        .container {{ max-width: 1000px; margin: 20px auto; background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 15px; font-weight: 600; }}
        h2 {{ color: #2c3e50; margin-top: 40px; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; font-weight: 600; font-size: 1.4em; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }}
        h2 .toggle-indicator {{ font-size: 0.8em; color: #7f8c8d; transition: transform 0.2s; }}
        h2.collapsed .toggle-indicator {{ transform: rotate(-90deg); }}
        h3 {{ margin-top: 25px; color: #34495e; font-weight: 600; font-size: 1.2em; }}
        table.data-table {{ border-collapse: collapse; width: 100%; margin: 20px 0; border: 1px solid #ddd; }}
        th, td {{ border: 1px solid #ddd; padding: 10px 12px; text-align: left; vertical-align: top; font-size: 0.95em; }}
        th {{ background-color: #f8f9fa; font-weight: 600; color: #495057; }}
        tbody tr:nth-child(even) {{ background-color: #fdfdfd; }}
        .section {{ margin-bottom: 25px; padding-top: 10px; }}
        .section-content {{ padding-left: 10px; border-left: 3px solid #f0f0f0; margin-top: 15px; overflow: hidden; transition: max-height 0.4s ease-out, padding-top 0.4s ease-out, padding-bottom 0.4s ease-out, margin-top 0.4s ease-out, opacity 0.3s ease-out; max-height: 50000px; /* High value for default */ padding-top: 15px; padding-bottom: 15px; opacity: 1; }}
        .section-content.collapsed {{ max-height: 0; padding-top: 0; padding-bottom: 0; margin-top: 0; border-left: 3px solid #f0f0f0; visibility: hidden; opacity: 0; transition: max-height 0.3s ease-in, visibility 0s 0.3s, opacity 0.2s ease-in, padding-top 0.3s ease-in, padding-bottom 0.3s ease-in, margin-top 0.3s ease-in; }}
        .footnotes {{ margin-top: 40px; border-top: 1px solid #eee; padding-top: 15px; font-size: 0.85em; color: #555; }}
        .footnotes ol {{ padding-left: 20px; }}
        ul, ol {{ margin-left: 20px; padding-left: 15px; }}
        li {{ margin-bottom: 5px; }}
        p {{ margin-top: 0; margin-bottom: 1em; color: #343a40; }} /* <-- Explicit paragraph color */
        .error {{ color: #c0392b; padding: 12px; background-color: #fdedec; border: 1px solid #f5c6cb; border-radius: 4px; margin-top: 15px; }}
        strong {{ font-weight: 600; color: #34495e; }}
        .header-wrapper {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
        .company-meta {{ color: #7f8c8d; font-size: 0.9em; margin-top: 5px; }} /* Added margin-top */
        .toc {{ background-color: #f8f9fa; padding: 20px; margin-bottom: 30px; border-radius: 5px; border: 1px solid #eee; }}
        .toc h3 {{ margin-top: 0; color: #34495e; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 15px; }}
        .toc ul {{ list-style-type: none; padding-left: 0; }}
        .toc li {{ margin-bottom: 8px; }}
        .toc a {{ text-decoration: none; color: #2980b9; transition: color 0.2s; }}
        .toc a:hover {{ text-decoration: none; color: #1f618d; }}
        .print-button {{ display: block; width: 120px; margin: 20px auto; padding: 8px 15px; background-color: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; text-align: center; font-size: 0.9em; }}
        .print-button:hover {{ background-color: #2980b9; }}
        pre {{ background-color: #eee; padding: 10px; border-radius: 3px; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; }}
        @media print {{
            body {{ font-size: 10pt; margin: 10mm; box-shadow: none; }}
            .container {{ box-shadow: none; border: none; padding: 0; margin: 0; max-width: 100%; }}
            h1, h2, h3 {{ color: #000; }}
            h2 {{ border-bottom: 1px solid #000; }}
            table.data-table, th, td {{ border: 1px solid #aaa !important; font-size: 9pt; }}
            th {{ background-color: #eee !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            tbody tr:nth-child(even) {{ background-color: #fff !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            a {{ text-decoration: none; color: #000; }}
            /* .toc {{ display: none; }} <-- REMOVED this line to show ToC when printing */
            .no-print, .print-button, .toggle-indicator {{ display: none; }}
            .section {{ page-break-inside: avoid; }}
            .section-content {{ max-height: none !important; visibility: visible !important; opacity: 1 !important; border-left: none !important; padding-left: 0 !important; padding-top: 15px !important; padding-bottom: 15px !important; margin-top: 15px !important; }}
            .section-content.collapsed {{ max-height: none !important; visibility: visible !important; opacity: 1 !important; }} /* Ensure collapsed sections also print */
            .footnotes {{ font-size: 8pt; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-wrapper">
            <h1>Company Profile: {html.escape(company_name.upper())}</h1>
            <div class="company-meta">
                Generated on: {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}
            </div>
            <div class="company-meta">
                By ProfileDash {html.escape(app_version)}
            </div>
        </div>

        <div class="toc">
            <h3>Table of Contents</h3>
            <ul>
"""

    # Add table of contents
    toc_content = ""
    for section in sections:
        section_num = section["number"]
        section_title = section["title"]
        # Escape section title in TOC
        toc_content += f'                <li><a href="#section-{section_num}">{section_num}. {html.escape(section_title)}</a></li>\n'

    toc_end = """            </ul>
        </div>

        <button onclick="window.print()" class="print-button no-print">Print Profile</button>

        <div class="content">
"""

    html_foot = """
        </div> <!-- content -->
    </div> <!-- container -->

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Add toggle indicator (down arrow) to section headers initially
             const sectionHeaders = document.querySelectorAll('.content > .section > h2');
             sectionHeaders.forEach(header => {
                // Avoid adding indicator if one already exists (e.g., from LLM output)
                 if (!header.querySelector('.toggle-indicator')) {
                    let indicator = document.createElement('span');
                    indicator.className = 'toggle-indicator no-print';
                    indicator.innerHTML = '▼'; // Default to expanded
                    header.appendChild(indicator);
                 }
             });


            // Wrap content following H2 in a div for collapsing, if not already done
             const sections = document.querySelectorAll('.content > .section');
             sections.forEach(section => {
                 const header = section.querySelector('h2');
                 if (!header) return;

                 let contentWrapper = section.querySelector('.section-content');
                 if (!contentWrapper) {
                     contentWrapper = document.createElement('div');
                     contentWrapper.className = 'section-content';
                     let currentElement = header.nextElementSibling;
                     while (currentElement) {
                        // Stop wrapping if we hit the next section's H2 or footnotes
                         if ((currentElement.tagName === 'H2' && currentElement.parentNode === section.parentNode) || currentElement.classList.contains('footnotes')) {
                            break;
                         }
                         const nextElement = currentElement.nextElementSibling;
                         contentWrapper.appendChild(currentElement);
                         currentElement = nextElement;
                     }

                     if (contentWrapper.hasChildNodes()) {
                         // Insert the wrapper right after the header
                         header.parentNode.insertBefore(contentWrapper, header.nextSibling);
                     } else {
                        // If no content was found to wrap, don't insert the div
                         contentWrapper = null;
                     }
                 }


                 // Add click listener ONLY if a content wrapper exists
                 if(contentWrapper){
                    let indicator = header.querySelector('.toggle-indicator');
                     // Ensure indicator exists before adding listener
                     if (!indicator) {
                         indicator = document.createElement('span');
                         indicator.className = 'toggle-indicator no-print';
                         indicator.innerHTML = '▼';
                         header.appendChild(indicator);
                     }

                     header.addEventListener('click', function() {
                         const isCollapsed = contentWrapper.classList.toggle('collapsed');
                         header.classList.toggle('collapsed', isCollapsed);
                         indicator.innerHTML = isCollapsed ? '▶' : '▼';
                     });
                 }
             });
        });
    </script>
</body>
</html>
"""

    full_profile = html_head + toc_content + toc_end

    # Add each section's HTML content
    for i, content in enumerate(section_contents):
        section_num_for_error = sections[i]['number'] if i < len(sections) else 'Unknown'
        section_title_for_error = sections[i]['title'] if i < len(sections) else 'Unknown Section'
        # Escape the section title when generating error placeholders or wrapping content
        escaped_section_title = html.escape(section_title_for_error)
        if content and isinstance(content, str):
             # Basic check if the content *looks* like a section div
             if not content.strip().lower().startswith('<div class="section"'):
                  print(f"Warning: Section {section_num_for_error} content missing outer div wrapper - attempting to wrap.")
                  full_profile += f'<div class="section error-wrapper" id="section-{section_num_for_error}"><h2 class="error-header">{section_num_for_error}. {escaped_section_title}<span class="toggle-indicator no-print">▼</span></h2><p class="error">Content wrapper missing, attempting recovery:</p><div class="section-content">{content}</div></div>\n'
             else:
                  # Make sure section content itself is added safely
                  full_profile += content + "\n"
        else:
             full_profile += f'<div class="section" id="section-{section_num_for_error}"><h2 class="error-header">{section_num_for_error}. {escaped_section_title}<span class="toggle-indicator no-print">▼</span></h2><p class="error">Error: Section content was missing or empty.</p></div>\n'


    full_profile += html_foot
    # Final cleanup just in case
    full_profile = full_profile.replace('```html', '').replace('```', '')
    return full_profile


# --- CORRECTED extract_text_from_html ---
def extract_text_from_html(html_content):
    """Extract plain text from HTML content"""
    import re
    # import html # Standard library for HTML processing - Already imported at top level
    # import traceback # For detailed error logging - Already imported at top level

    if not isinstance(html_content, str): # Handle non-string input
        return ""

    try:
        # Remove script and style elements first
        text = re.sub(r'<(script|style).*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        # Replace <br> tags with newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        # Replace block elements like p, div, li, h1-h6, tr, table elements with newlines for better paragraphing
        text = re.sub(r'</(p|div|li|h[1-6]|tr|table|thead|tbody|th|td|ul|ol)>\s*', '\n', text, flags=re.IGNORECASE)
        # Remove all other tags
        text = re.sub(r'<[^>]+>', ' ', text)

        # Decode HTML entities using the standard library
        try:
            # Primary method: use html.unescape
            text = html.unescape(text)
        except Exception as unescape_err:
            # Fallback method if html.unescape fails
            print(f"Warning: html.unescape failed: {unescape_err}. Using basic entity replacements.")
            # --- CORRECTED FALLBACK REPLACEMENTS ---
            text = text.replace('>', '>')
            text = text.replace('"', '"')
            text = text.replace("'", "'")  # Correctly replace single quote
            text = text.replace('&nbsp;', ' ')  # Handle non-breaking space entity
            text = text.replace('&', '&')  # Replace & last to avoid double-replacing
            # --- END OF CORRECTIONS ---
            # Attempt to remove other entities crudely as a last resort
            text = re.sub(r'&[a-zA-Z]+;', ' ', text) # Remove any remaining named entities
            text = re.sub(r'&#\d+;', ' ', text)     # Remove any remaining numeric entities

        # Replace non-breaking space Unicode character if not caught by entity decoding
        text = text.replace('\u00A0', ' ') # Explicitly target the unicode char U+00A0

        # Normalize whitespace: replace multiple spaces/newlines with single space/newline
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n\n', text) # Keep maximum double newlines

        return text.strip()

    except Exception as e:
        print(f"Error during HTML text extraction: {e}")
        traceback.print_exc() # Print full traceback for debugging
        return "[Error extracting text]"
# --- END OF extract_text_from_html FUNCTION ---


# --- ENSURE UNUSED SCHEMA FUNCTIONS ARE REMOVED ---
# The following functions related to schema generation were previously marked for removal.
# Ensure they are *not* present in your file after this point.
# If they still exist, delete them.

# def generate_html_from_schema(section_data, section_def): ...
# def generate_content_from_data(data, level=0, skip_keys=None): ...
# def generate_table_from_objects(items): ...
# def generate_footnotes_html(footnotes): ...
# def parse_ai_response_to_schema(ai_text, section_def): ...

# --- END OF FULL FILE src/html_generator.py ---