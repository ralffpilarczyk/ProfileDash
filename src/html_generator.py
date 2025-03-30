"""
HTML Generator module for ProfileDash
Handles all HTML generation and processing
"""

import os
import re # Add re import here
import json
from datetime import datetime

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
            duplicate_title_pattern_str = rf'^\s*{re.escape(str(section_num))}\.\s*{escaped_title}\s*▼?\s*'
            following_content = content[h2_end_pos:]
            duplicate_match = re.match(duplicate_title_pattern_str, following_content, re.IGNORECASE | re.MULTILINE)

            if duplicate_match:
                duplicate_text = duplicate_match.group(0)
                cleaned_content = content[:h2_end_pos] + following_content[len(duplicate_text):]
        # else: # If H2 wasn't found, cleaned_content remains content (already stripped of ```html)

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

def save_section(profile_folder, section_number, content):
    """Save a section's HTML content to a file."""
    if not isinstance(content, str): content = str(content)
    try:
        filepath = os.path.join(profile_folder, f"section_{section_number}.html")
        with open(filepath, "w", encoding="utf-8") as f: f.write(content)
    except Exception as e: print(f"Error saving section {section_number} to {profile_folder}: {e}")

def load_section(profile_folder, section_number):
    """Load a section's HTML content from a file if it exists."""
    filepath = os.path.join(profile_folder, f"section_{section_number}.html")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f: return f.read()
        except Exception as e: print(f"Error loading section {section_number} from {filepath}: {e}")
    return None

def validate_html(html_content):
    """Simplified HTML validation."""
    if not html_content or not html_content.strip(): return False
    if not re.search(r'<div\s+class=["\']section["\']', html_content, re.IGNORECASE): return False
    tags_to_check = ['div', 'table', 'thead', 'tbody', 'tr', 'td', 'th', 'ul', 'ol', 'li', 'p']
    balanced = True
    for tag in tags_to_check:
        try:
             opening = len(re.findall(f'<{tag}(?:\\s+[^>]*?)?>', html_content, re.IGNORECASE))
             closing = len(re.findall(f'</{tag}\\s*>', html_content, re.IGNORECASE))
             if opening != closing:
                 print(f"Warning: Unbalanced <{tag}> tags. O:{opening}, C:{closing}")
                 if tag == 'div': balanced = False # Stricter for divs
        except Exception as e: print(f"Warning: Regex error validating <{tag}>: {e}"); balanced = False
    return balanced

def repair_html(html_content, section_num=None, section_title=None):
    """Enhanced repair of common HTML issues."""
    import re
    MAX_ITERATIONS = 5; current_iteration = 0
    if not html_content or not html_content.strip():
        return f'<div class="section" id="section-{section_num or "unknown"}"><h2>{section_num or "?"}. {section_title or "Untitled"}</h2><p>No content available</p></div>'

    html_content = re.sub(r'<br\s*>', '<br/>', html_content, flags=re.IGNORECASE)
    previous_content = ""
    while current_iteration < MAX_ITERATIONS and html_content != previous_content:
        previous_content = html_content; current_iteration += 1; cleaned_this_iter = False

        # 1. Fix section wrapper
        if section_num is not None and section_title is not None:
            id_attr = f'id="section-{section_num}"'
            h2_text = f'{section_num}. {section_title}'
            h2_pattern = rf'<h2(?: [^>]*)?>\s*{re.escape(h2_text)}\s*</h2\s*>'
            div_start_pattern = r'<div\s+class=["\']section["\']'

            if not re.match(div_start_pattern, html_content.strip(), re.IGNORECASE):
                html_content = f'<div class="section" {id_attr}>\n{html_content}'; cleaned_this_iter = True
            elif not re.search(id_attr, html_content, re.IGNORECASE):
                 html_content = re.sub(div_start_pattern, rf'\g<0> {id_attr}', html_content, count=1, flags=re.IGNORECASE); cleaned_this_iter = True

            if not re.search(h2_pattern, html_content, re.IGNORECASE | re.DOTALL):
                 html_content = re.sub(rf'<h2[^>]*>\s*{re.escape(str(section_num))}\..*?</h2>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
                 div_match = re.search(r'(<div\s+class=["\']section["\'][^>]*?>\n?)', html_content, flags=re.IGNORECASE)
                 if div_match: html_content = html_content[:div_match.end()] + f'<h2>{h2_text}</h2>\n' + html_content[div_match.end():]; cleaned_this_iter = True

        # 2. Ensure closing div
        opening_divs = len(re.findall(r'<div', html_content)); closing_divs = len(re.findall(r'</div', html_content))
        if opening_divs > closing_divs: html_content += '\n</div>' * (opening_divs - closing_divs); cleaned_this_iter = True
        elif closing_divs > opening_divs:
             extra = closing_divs - opening_divs; temp_content = html_content.rstrip(); removed_count = 0
             while removed_count < extra and temp_content.endswith('</div>'): temp_content = temp_content[:-6].rstrip(); removed_count += 1
             if removed_count > 0: html_content = temp_content + '\n'; cleaned_this_iter = True

        # 3. Fix table structure
        try:
            new_table_content = ""; last_table_end = 0
            for table_match in re.finditer(r'(<table[^>]*>)(.*?)(</table>)', html_content, re.DOTALL | re.IGNORECASE):
                new_table_content += html_content[last_table_end:table_match.start()]
                original_table = table_match.group(0); table_start_tag = table_match.group(1)
                table_inner_content = table_match.group(2); table_end_tag = table_match.group(3)
                modified_inner_content = table_inner_content
                has_thead = '<thead' in modified_inner_content.lower(); has_tbody = '<tbody' in modified_inner_content.lower()
                has_th = '<th' in modified_inner_content.lower(); has_tr = '<tr' in modified_inner_content.lower()

                if has_tr and has_th and not has_thead:
                    header_row_match = re.search(r'(<tr.*?(?:<th.*?>).*?</tr>)', modified_inner_content, re.IGNORECASE | re.DOTALL | re.MULTILINE)
                    if header_row_match: modified_inner_content = modified_inner_content.replace(header_row_match.group(1), f"<thead>{header_row_match.group(1)}</thead>", 1); has_thead = True

                if has_tr and not has_tbody:
                    if has_thead:
                         thead_end_match = re.search(r'</thead>', modified_inner_content, re.IGNORECASE)
                         if thead_end_match:
                              thead_end_pos = thead_end_match.end(); body_part = modified_inner_content[thead_end_pos:]
                              if '<tr' in body_part.lower(): modified_inner_content = modified_inner_content[:thead_end_pos] + f"<tbody>{body_part}</tbody>"
                    elif '<tr' in modified_inner_content.lower(): modified_inner_content = f"<tbody>{modified_inner_content}</tbody>"

                new_table_html = table_start_tag + modified_inner_content + table_end_tag
                new_table_content += new_table_html; last_table_end = table_match.end()
                if original_table != new_table_html: cleaned_this_iter = True
            new_table_content += html_content[last_table_end:]; html_content = new_table_content
        except Exception as e: print(f"Warning: Error during table repair for section {section_num}: {e}")

        # 4. Attempt to close common unclosed tags
        tags_to_close = ['p', 'li', 'td', 'th', 'tr']
        for tag in tags_to_close:
            try:
                 opening = len(re.findall(f'<{tag}[^>]*>', html_content, re.IGNORECASE))
                 closing = len(re.findall(f'</{tag}\\s*>', html_content, re.IGNORECASE))
                 if opening > closing: html_content += f'</{tag}>' * (opening - closing); cleaned_this_iter = True
            except Exception as e: print(f"Warning: Error checking tag balance for <{tag}>: {e}")

        if not cleaned_this_iter and previous_content == html_content: break

    # --- End of Iterative Loop ---
    if current_iteration == MAX_ITERATIONS: print(f"Warning: HTML repair hit max iterations for section {section_num}.")

    # Final validation and fallback
    if not validate_html(html_content) and section_num is not None and section_title is not None:
        print(f"Warning: HTML repair failed validation for section {section_num}. Attempting text extraction fallback.")
        try:
            text_content = extract_text_from_html(html_content)
            if len(text_content) > 2000: text_content = text_content[:2000] + "..."
            html_content = f'''<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">Warning: Original HTML structure invalid, showing extracted text:</p><pre style="white-space: pre-wrap; word-wrap: break-word;">{text_content}</pre></div>'''
        except Exception as fallback_e:
            print(f"Error during fallback text extraction: {fallback_e}")
            html_content = f'<div class="section" id="section-{section_num or "unknown"}"><h2>{section_num or "?"}. {section_title or "Untitled"}</h2><p class="error">Error: Could not repair content or extract text.</p></div>'

    return html_content.strip()

def generate_full_html_profile(company_name, sections, section_contents):
    """Generate a complete HTML document from section contents"""
    from datetime import datetime

    html_head = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Company Profile: {company_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"; margin: 20px; line-height: 1.6; background-color: #f4f7f6; color: #333; }}
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
        p {{ margin-top: 0; margin-bottom: 1em; }}
        .error {{ color: #c0392b; padding: 12px; background-color: #fdedec; border: 1px solid #f5c6cb; border-radius: 4px; margin-top: 15px; }}
        strong {{ font-weight: 600; color: #34495e; }}
        .header-wrapper {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
        .company-meta {{ color: #7f8c8d; font-size: 0.9em; }}
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
            .no-print, .print-button, .toc, .toggle-indicator {{ display: none; }}
            .section {{ page-break-inside: avoid; }}
            .section-content {{ max-height: none !important; visibility: visible !important; opacity: 1 !important; border-left: none !important; padding-left: 0 !important; padding-top: 15px !important; padding-bottom: 15px !important; margin-top: 15px !important; }}
            .section-content.collapsed {{ max-height: none !important; visibility: visible !important; opacity: 1 !important; }}
            .footnotes {{ font-size: 8pt; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-wrapper">
            <h1>Company Profile: {company_name.upper()}</h1>
            <div class="company-meta">
                Generated on: {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}
            </div>
        </div>

        <div class="toc no-print">
            <h3>Table of Contents</h3>
            <ul>
"""

    # Add table of contents
    toc_content = ""
    for section in sections:
        section_num = section["number"]
        section_title = section["title"]
        toc_content += f'                <li><a href="#section-{section_num}">{section_num}. {section_title}</a></li>\n'

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
            const sections = document.querySelectorAll('.section');
            sections.forEach(section => {
                const header = section.querySelector('h2');
                if (!header) return;

                // Wrap content following H2 in a div for collapsing, if not already done
                let contentWrapper = section.querySelector('.section-content');
                if (!contentWrapper) {
                    contentWrapper = document.createElement('div');
                    contentWrapper.className = 'section-content';
                    let currentElement = header.nextElementSibling;
                    while (currentElement) {
                        if(currentElement.classList.contains('footnotes')) break; // Stop before footnotes
                        const nextElement = currentElement.nextElementSibling; // Get next before moving current
                        contentWrapper.appendChild(currentElement);
                        currentElement = nextElement;
                    }
                    if (contentWrapper.hasChildNodes()) { // Only insert if content was found
                        header.parentNode.insertBefore(contentWrapper, header.nextSibling);
                    } else {
                        contentWrapper = null; // No content to wrap
                    }
                }

                if (!contentWrapper) return; // Skip if no content wrapper exists or was created

                let indicator = header.querySelector('.toggle-indicator');
                if (!indicator) {
                    indicator = document.createElement('span');
                    indicator.className = 'toggle-indicator no-print';
                    indicator.innerHTML = '▼'; // Default to expanded
                    header.appendChild(indicator);
                }

                header.addEventListener('click', function() {
                    const isCollapsed = contentWrapper.classList.toggle('collapsed');
                    header.classList.toggle('collapsed', isCollapsed);
                    indicator.innerHTML = isCollapsed ? '▶' : '▼';
                });
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
        if content and isinstance(content, str):
             if not re.search(r'<div\s+class=["\']section["\']', content, re.IGNORECASE):
                  print(f"Warning: Section {section_num_for_error} content missing outer div wrapper - attempting to wrap.")
                  full_profile += f'<div class="section error-wrapper" id="section-{section_num_for_error}"><h2 class="error-header">{section_num_for_error}. {section_title_for_error}</h2><p class="error">Content wrapper missing, attempting recovery:</p>{content}</div>\n'
             else:
                  full_profile += content + "\n"
        else:
             full_profile += f'<div class="section" id="section-{section_num_for_error}"><h2 class="error-header">{section_num_for_error}. {section_title_for_error}</h2><p class="error">Error: Section content was missing or empty.</p></div>\n'

    full_profile += html_foot
    full_profile = full_profile.replace('```html', '').replace('```', '')
    return full_profile

# --- CORRECTED extract_text_from_html ---
def extract_text_from_html(html_content):
    """Extract plain text from HTML content"""
    import re
    if not isinstance(html_content, str): # Handle non-string input
        return ""
    # Remove script and style elements first
    text = re.sub(r'<(script|style).*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    # Replace <br> tags with newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
     # Replace block elements like p, div, li, h1-h6, tr with newlines for better paragraphing
    text = re.sub(r'</(p|div|li|h[1-6]|tr)>\s*', '\n', text, flags=re.IGNORECASE)
     # Remove all other tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    try:
        import html
        text = html.unescape(text)
    except ImportError:
        # Basic entity decoding if html module is not available
        # Order matters slightly - replace & last
        text = text.replace('<', '<')
        text = text.replace('>', '>')
        text = text.replace('"', '"')
        text = text.replace(''', "'")
        text = text.replace(''', "'") # Handle '
        text = text.replace(' ', ' ')
        text = text.replace('&', '&') # Replace & last

    # Replace non-breaking space Unicode character if not caught by entity decoding
    text = text.replace(' ', ' ') # This is the non-breaking space character U+00A0

    # Normalize whitespace: replace multiple spaces/newlines with single space/newline
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text) # Keep maximum double newlines
    return text.strip()
# --- END OF CORRECTED FUNCTION ---

# --- REMOVE UNUSED SCHEMA FUNCTIONS ---
# (Ensure these are actually deleted from your file if they exist)
# def generate_html_from_schema(section_data, section_def): ...
# def generate_content_from_data(data, level=0, skip_keys=None): ...
# def generate_table_from_objects(items): ...
# def generate_footnotes_html(footnotes): ...
# def parse_ai_response_to_schema(ai_text, section_def): ...
# --- END OF REMOVED FUNCTIONS ---