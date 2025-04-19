"""
HTML Generator module for ProfileDash
Handles all HTML generation, cleaning, repair, and processing.
Includes functions potentially unused by current app.py but kept from Old Version.
"""

import os
import re
import json
from datetime import datetime
import html # Standard library for HTML processing (e.g., escaping, unescaping)
import traceback # For detailed error logging

# --- Helper Function for Cleaning LLM Output ---
def clean_llm_output(content, section_num=None, section_title=None):
    """Removes ```html markers and duplicate titles if possible"""
    if not content or not isinstance(content, str):
        return ""

    # Remove common markdown code block fences
    content = content.replace('```html', '').replace('```', '').strip()

    # Only attempt duplicate title removal if section number and title are provided
    if section_num is not None and section_title is not None:
        # Pattern to find the expected H2 title (allows for attributes, whitespace, optional period)
        h2_pattern_str = rf'<h2[^>]*?>\s*{re.escape(str(section_num))}\.?\s*{re.escape(section_title)}.*?</h2>'
        h2_match = re.search(h2_pattern_str, content, re.IGNORECASE | re.DOTALL)

        cleaned_content = content

        if h2_match:
            h2_full_tag = h2_match.group(0)
            h2_end_pos = h2_match.end()
            escaped_title = re.escape(section_title)
            # Pattern to look for potential duplicates immediately following H2
            # Allows for whitespace, optional number/dot, optional down arrow symbol (▼)
            duplicate_title_pattern_str = rf'^\s*(?:{re.escape(str(section_num))}\.?\s*)?{escaped_title}\s*▼?\s*'
            following_content = content[h2_end_pos:]

            # Use re.match to check if the *beginning* of the following content matches the duplicate pattern
            duplicate_match = re.match(duplicate_title_pattern_str, following_content, re.IGNORECASE | re.MULTILINE)

            if duplicate_match:
                # If a duplicate title text is found right after the H2 tag, remove it
                duplicate_text_length = duplicate_match.end()
                # Reconstruct content: keep up to the end of H2 tag, then skip the duplicate text
                cleaned_content = content[:h2_end_pos] + following_content[duplicate_text_length:]
                print(f"HTML Cleaner: Removed suspected duplicate title for section {section_num}")

        return cleaned_content.strip()
    else:
        # If no section info, just return the content stripped of code fences
        return content

# --- Folder/File Operations (Kept from Old Version, potentially inactive) ---
def create_profile_folder(company_name):
    """Create a unique folder for storing profile sections (potentially inactive)."""
    print("HTML Generator: create_profile_folder called (inactive in current app).")
    clean_name = ''.join(c for c in company_name if c.isalnum() or c in [' ', '_', '-']).replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"profile_{clean_name}_{timestamp}"
    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        return folder_name, timestamp
    except Exception as e:
        print(f"HTML Generator Error creating folder {folder_name}: {e}")
        return ".", timestamp # Fallback to current directory if folder creation fails

def save_section(profile_folder, section_number, content):
    """Save a section's HTML content to a file (potentially inactive)."""
    print(f"HTML Generator: save_section {section_number} called (inactive in current app).")
    if not isinstance(content, str): content = str(content)
    try:
        filepath = os.path.join(profile_folder, f"section_{section_number}.html")
        with open(filepath, "w", encoding="utf-8") as f: f.write(content)
    except Exception as e: print(f"HTML Generator Error saving section {section_number} to {profile_folder}: {e}")

def load_section(profile_folder, section_number):
    """Load a section's HTML content from a file if it exists (potentially inactive)."""
    print(f"HTML Generator: load_section {section_number} called (inactive in current app).")
    filepath = os.path.join(profile_folder, f"section_{section_number}.html")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f: return f.read()
        except Exception as e: print(f"HTML Generator Error loading section {section_number} from {filepath}: {e}")
    return None
# --- End Folder/File Operations ---

def validate_html(html_content):
    """Performs simplified HTML validation, focusing on common structural issues."""
    if not html_content or not isinstance(html_content, str) or not html_content.strip():
        print("HTML Validator Warning: Empty HTML content")
        return False # Empty content is considered invalid

    # 1. Check for basic section structure (presence of <div class="section">)
    # This pattern handles potential attributes within the div tag.
    if not re.search(r'<div\s+[^>]*?class=["\']section["\']', html_content, re.IGNORECASE):
        print("HTML Validator Warning: Missing outer <div class=\"section\"> tag.")
        # Note: Currently treated as a warning, not a hard failure.
        # return False

    # 2. Check for likely unclosed tags at the very end (simple check)
    # Looks for tags like <p>, <li>, etc., followed only by optional whitespace at the end.
    if re.search(r'< (p|li|td|th) [^>]* > $', html_content.strip(), re.IGNORECASE | re.MULTILINE):
         print("HTML Validator Warning: Possible unclosed tag at the end.")
         # return False # Optional: Could be treated as a failure

    # 3. Check balance of critical container tags (div, table, tr, td, th)
    critical_tags = ['div', 'table', 'tr', 'td', 'th']
    balanced = True
    for tag in critical_tags:
        try:
            # Regex to find opening tags, ignoring self-closing ones like <br/>
            # Handles attributes within the tag.
            opening_pattern = f'<{tag}(?:\\s+[^>]*?)?>(?!</{tag}>)'
            closing_pattern = f'</{tag}\\s*>'

            opening_count = len(re.findall(opening_pattern, html_content, re.IGNORECASE))
            closing_count = len(re.findall(closing_pattern, html_content, re.IGNORECASE))

            if opening_count != closing_count:
                print(f"HTML Validator Warning: Unbalanced <{tag}> tags detected. Opening: {opening_count}, Closing: {closing_count}")
                # Consider DIV and TABLE mismatches critical failures.
                if tag in ['div', 'table']:
                    balanced = False
                    # Stop checking further if a critical tag is unbalanced
                    # break
        except Exception as e:
            # Handle potential regex compilation/matching errors, treat as validation failure.
            print(f"HTML Validator Error validating <{tag}>: {e}")
            balanced = False
            # break

    # The HTML is considered valid if critical tags are balanced (and other checks passed or were non-fatal).
    return balanced


def repair_html(html_content, section_num=None, section_title=None):
    """Attempts to repair common HTML issues, like missing wrappers, headers, and unbalanced tags."""
    if not html_content or not isinstance(html_content, str) or not html_content.strip():
        # Generate default error content if input is empty or invalid.
        default_h2 = f'{section_num or "?"}. {section_title or "Untitled Section"}'
        return f'<div class="section" id="section-{section_num or "unknown"}"><h2 class="error-header">{default_h2}</h2><p class="error">No content available or initial generation failed.</p></div>'

    # --- Initial Cleaning ---
    html_content = html_content.replace('```html', '').replace('```', '').strip()
    # Standardize self-closing br tags for consistency.
    html_content = re.sub(r'<br\s*>', '<br/>', html_content, flags=re.IGNORECASE)
    # Remove potential markdown list prefixes if they accidentally remain.
    html_content = re.sub(r'^\s*[\*\-]\s+', '', html_content, flags=re.MULTILINE)

    # --- Ensure Section Wrapper and Header ---
    # Only proceed if section number and title are available for context.
    if section_num is not None and section_title is not None:
        id_attr = f'id="section-{section_num}"'
        class_attr = 'class="section"'
        h2_text = f'{section_num}. {section_title}'
        # Robust patterns allowing attributes and varying whitespace.
        div_start_pattern = re.compile(r'^\s*<div\s+[^>]*?class=["\']section["\']', re.IGNORECASE | re.DOTALL)
        div_id_pattern = re.compile(rf'id=["\']section-{section_num}["\']', re.IGNORECASE)
        h2_pattern = re.compile(rf'<h2[^>]*?>\s*{re.escape(str(section_num))}\.?\s*{re.escape(section_title)}.*?</h2>', re.IGNORECASE | re.DOTALL)
        h2_generic_pattern = re.compile(rf'<h2[^>]*?>\s*{re.escape(str(section_num))}\.?\s*.*?</h2>', re.IGNORECASE | re.DOTALL)

        # 1. Check/Add Outer Div Wrapper (<div class="section" id="...">)
        if not div_start_pattern.search(html_content):
            print(f"HTML Repair (Sec {section_num}): Adding missing outer div.")
            html_content = f'<div {class_attr} {id_attr}>\n{html_content}\n</div>'
        else:
            # If the outer div exists, ensure it has the correct ID attribute.
            first_div_match = re.search(r'<div[^>]*>', html_content, re.IGNORECASE)
            if first_div_match:
                first_div_tag = first_div_match.group(0)
                if not div_id_pattern.search(first_div_tag):
                    print(f"HTML Repair (Sec {section_num}): Adding missing ID to existing div.")
                    # Insert the id attribute into the existing tag.
                    html_content = html_content.replace(first_div_tag, f'{first_div_tag[:-1]} {id_attr}>', 1)

        # 2. Check/Add H2 Header (within the div)
        if not h2_pattern.search(html_content):
            print(f"HTML Repair (Sec {section_num}): Adding/Fixing H2 header.")
            # Remove any existing H2 for this section number first to avoid duplicates.
            html_content = h2_generic_pattern.sub('', html_content)
            # Insert the correct H2 right after the opening div tag.
            html_content = re.sub(r'(<div[^>]*?>\n?)', rf'\1<h2>{h2_text}</h2>\n', html_content, count=1, flags=re.IGNORECASE)

    # --- Tag Balancing (Simple iterative approach) ---
    # Focus on common block elements prone to causing layout issues if unclosed.
    tags_to_balance = ['p', 'li', 'ul', 'ol', 'td', 'th', 'tr', 'thead', 'tbody', 'table', 'div']
    MAX_ITERATIONS = 3 # Limit iterations to prevent potential infinite loops in edge cases.
    for _ in range(MAX_ITERATIONS):
        made_change = False
        for tag in tags_to_balance:
            try:
                # Find all opening tags (ignoring self-closing syntax within the tag)
                opening_tags = re.findall(rf'<{tag}(?:\s+[^>]*)?>', html_content, re.IGNORECASE)
                closing_tags = re.findall(rf'</{tag}\s*>', html_content, re.IGNORECASE)
                diff = len(opening_tags) - len(closing_tags)

                if diff > 0:
                    # Add missing closing tags at the very end of the content.
                    print(f"HTML Repair (Sec {section_num}): Adding {diff} missing </{tag}> tags.")
                    html_content += f'</{tag}>' * diff
                    made_change = True
                elif diff < 0:
                    # Remove extra closing tags from the end (basic, greedy approach).
                    print(f"HTML Repair (Sec {section_num}): Removing {-diff} extra </{tag}> tags from end.")
                    for _ in range(-diff):
                         # Only remove if the tag is exactly at the end (ignoring trailing whitespace).
                         if html_content.rstrip().lower().endswith(f'</{tag}>'):
                              html_content = html_content.rstrip()[:-len(f'</{tag}>')].rstrip() + "\n"
                              made_change = True
                         else:
                              break # Stop removing if the expected tag isn't found at the end.

            except Exception as e:
                 print(f"HTML Repair Warning: Error balancing tag <{tag}>: {e}")
        # If a full pass makes no changes, assume stability or irrecoverable state.
        if not made_change:
             break

    # --- Table Structure Repair (thead/tbody) ---
    # Attempt to enforce basic thead/tbody wrapping for semantic structure and styling.
    new_table_content = ""
    last_table_end = 0
    try:
        for table_match in re.finditer(r'(<table[^>]*>)(.*?)(</table\s*>)', html_content, re.DOTALL | re.IGNORECASE):
            # Append content before the current table.
            new_table_content += html_content[last_table_end:table_match.start()]
            original_table = table_match.group(0)
            table_start_tag = table_match.group(1)
            table_inner = table_match.group(2).strip()
            table_end_tag = table_match.group(3)

            modified_inner = table_inner
            has_thead = bool(re.search(r'<thead[^>]*>', modified_inner, re.IGNORECASE))
            has_tbody = bool(re.search(r'<tbody[^>]*>', modified_inner, re.IGNORECASE))
            has_th = bool(re.search(r'<th[^>]*>', modified_inner, re.IGNORECASE))
            has_tr = bool(re.search(r'<tr[^>]*>', modified_inner, re.IGNORECASE))

            # Add <thead> if <th> exists within a <tr> but no <thead> is present.
            if has_tr and has_th and not has_thead:
                # Find the first row containing a <th> (assumed header row).
                header_row_match = re.search(r'(<tr.*?(?:<th.*?>).*?</tr\s*>)', modified_inner, re.IGNORECASE | re.DOTALL)
                if header_row_match:
                    header_row_html = header_row_match.group(1)
                    # Wrap this header row in <thead> tags.
                    modified_inner = modified_inner.replace(header_row_html, f"<thead>\n{header_row_html}\n</thead>", 1)
                    print(f"HTML Repair (Sec {section_num}): Added missing <thead>.")
                    has_thead = True # Mark thead as now present.

            # Add <tbody> if <tr> exists (either after <thead> or if no <thead> exists) and <tbody> is missing.
            if has_tr and not has_tbody:
                tbody_content_start = 0
                if has_thead:
                    # If thead exists, tbody content starts after its closing tag.
                    thead_end_match = re.search(r'</thead\s*>', modified_inner, re.IGNORECASE)
                    if thead_end_match:
                        tbody_content_start = thead_end_match.end()

                # Extract potential body content.
                body_content = modified_inner[tbody_content_start:].strip()
                # Only add tbody if there's actual row content for it.
                if body_content and '<tr' in body_content.lower():
                    # Wrap the remaining content in <tbody>.
                    modified_inner = modified_inner[:tbody_content_start] + f"\n<tbody>\n{body_content}\n</tbody>"
                    print(f"HTML Repair (Sec {section_num}): Added missing <tbody>.")
                    has_tbody = True # Mark tbody as now present.

            # Reconstruct the table with potentially modified inner content.
            new_table_html = table_start_tag + '\n' + modified_inner + '\n' + table_end_tag
            new_table_content += new_table_html
            last_table_end = table_match.end()

        # Append any content remaining after the last table.
        new_table_content += html_content[last_table_end:]
        html_content = new_table_content
    except Exception as e:
        print(f"HTML Repair Warning: Error during table structure repair: {e}")
        # Continue with the potentially unmodified content if table repair fails.

    # --- Final Validation and Fallback ---
    # Check if the repaired HTML passes the basic validation.
    if not validate_html(html_content):
        print(f"HTML Repair Warning: Content failed validation even after repair for section {section_num}.")
        # Fallback to extracting plain text if repair fails validation, to prevent broken HTML display.
        try:
            plain_text = extract_text_from_html(html_content)
            # Escape the extracted text to display safely within HTML <pre> tags.
            escaped_text = html.escape(plain_text[:2000] + "..." if len(plain_text) > 2000 else plain_text)
            default_h2 = f'{section_num or "?"}. {section_title or "Untitled Section"}'
            html_content = f'<div class="section" id="section-{section_num or "unknown"}"><h2 class="error-header">{default_h2}</h2><p class="error">Warning: Original HTML structure invalid after repair attempt. Displaying extracted text:</p><pre style="white-space: pre-wrap; word-wrap: break-word;">{escaped_text}</pre></div>'
            print(f"HTML Repair (Sec {section_num}): Fallback to text extraction.")
        except Exception as fallback_e:
            print(f"HTML Repair Error during fallback text extraction: {fallback_e}")
            # Ultimate fallback if text extraction also fails.
            default_h2 = f'{section_num or "?"}. {section_title or "Untitled Section"}'
            html_content = f'<div class="section" id="section-{section_num or "unknown"}"><h2 class="error-header">{default_h2}</h2><p class="error">Error: Could not repair content or extract text.</p></div>'

    return html_content.strip()

# Note: app_version parameter added for compatibility with previous usage.
def generate_full_html_profile(company_name, sections, section_contents, app_version=""):
    """Generates a complete HTML document from individual section contents."""
    from datetime import datetime
    escaped_company_name = html.escape(company_name) if company_name else "Unknown Company"
    escaped_app_version = html.escape(app_version) if app_version else ""

    # --- Base Styles, Layout, and Print Adjustments ---
    html_head = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Company Profile: {escaped_company_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"; margin: 20px; line-height: 1.6; background-color: #f4f7f6; color: #212529; }}
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
        /* Collapsible Content Styling */
        .section-content {{ padding-left: 10px; border-left: 3px solid #f0f0f0; margin-top: 15px; overflow: hidden; transition: max-height 0.4s ease-out, padding-top 0.4s ease-out, padding-bottom 0.4s ease-out, margin-top 0.4s ease-out, opacity 0.3s ease-out; max-height: 50000px; /* Set high max-height for animation */ padding-top: 15px; padding-bottom: 15px; opacity: 1; }}
        .section-content.collapsed {{ max-height: 0; padding-top: 0; padding-bottom: 0; margin-top: 0; border-left-color: transparent; visibility: hidden; opacity: 0; transition: max-height 0.3s ease-in, visibility 0s 0.3s, opacity 0.2s ease-in, padding-top 0.3s ease-in, padding-bottom 0.3s ease-in, margin-top 0.3s ease-in, border-left-color 0.3s ease-in; }}
        /* End Collapsible */
        .footnotes {{ margin-top: 40px; border-top: 1px solid #eee; padding-top: 15px; font-size: 0.85em; color: #555; }}
        .footnotes ol {{ padding-left: 20px; }}
        ul, ol {{ margin-left: 20px; padding-left: 15px; }}
        li {{ margin-bottom: 5px; }}
        p {{ margin-top: 0; margin-bottom: 1em; color: #343a40; }}
        .error {{ color: #c0392b; padding: 12px; background-color: #fdedec; border: 1px solid #f5c6cb; border-radius: 4px; margin-top: 15px; }}
        strong {{ font-weight: 600; color: #34495e; }}
        .header-wrapper {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
        .company-meta {{ color: #7f8c8d; font-size: 0.9em; margin-top: 5px; }}
        .toc {{ background-color: #f8f9fa; padding: 20px; margin-bottom: 30px; border-radius: 5px; border: 1px solid #eee; }}
        .toc h3 {{ margin-top: 0; color: #34495e; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 15px; }}
        .toc ul {{ list-style-type: none; padding-left: 0; }}
        .toc li {{ margin-bottom: 8px; }}
        .toc a {{ text-decoration: none; color: #2980b9; transition: color 0.2s; }}
        .toc a:hover {{ text-decoration: none; color: #1f618d; }}
        .print-button {{ display: block; width: 120px; margin: 20px auto; padding: 8px 15px; background-color: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; text-align: center; font-size: 0.9em; }}
        .print-button:hover {{ background-color: #2980b9; }}
        pre {{ background-color: #eee; padding: 10px; border-radius: 3px; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; border: 1px solid #ddd;}}
        @media print {{
            body {{ font-size: 10pt; margin: 10mm; box-shadow: none; }}
            .container {{ box-shadow: none; border: none; padding: 0; margin: 0; max-width: 100%; }}
            h1, h2, h3 {{ color: #000; }}
            h2 {{ border-bottom: 1px solid #000; }}
            table.data-table, th, td {{ border: 1px solid #aaa !important; font-size: 9pt; }}
            th {{ background-color: #eee !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            tbody tr:nth-child(even) {{ background-color: #fff !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
            a {{ text-decoration: none; color: #000; }}
            .toc, .no-print, .print-button, .toggle-indicator {{ display: none; }}
            .section {{ page-break-inside: avoid; }}
            /* Ensure collapsible content is visible when printing */
            .section-content {{ max-height: none !important; visibility: visible !important; opacity: 1 !important; border-left: none !important; padding-left: 0 !important; padding-top: 15px !important; padding-bottom: 15px !important; margin-top: 15px !important; }}
            .section-content.collapsed {{ max-height: none !important; visibility: visible !important; opacity: 1 !important; }} /* Override collapsed style for print */
            .footnotes {{ font-size: 8pt; }}
            .error {{ background-color: #fdedec !important; border: 1px solid #f5c6cb !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-wrapper">
            <h1>Company Profile: {escaped_company_name.upper()}</h1>
            <div class="company-meta">
                Generated on: {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}
            </div>
            <div class="company-meta">
                By ProfileDash {escaped_app_version}
            </div>
        </div>

        <div class="toc no-print">
            <h3>Table of Contents</h3>
            <ul>
"""

    # Build table of contents links
    toc_content = ""
    for section in sections:
        section_num = section["number"]
        section_title = section["title"]
        # Escape section title for safe inclusion in HTML
        toc_content += f'                <li><a href="#section-{section_num}">{section_num}. {html.escape(section_title)}</a></li>\n'

    toc_end = """            </ul>
        </div>

        <button onclick="window.print()" class="print-button no-print">Print Profile</button>

        <div class="content">
"""

    html_foot = """
        </div> <!-- content -->
        <div class="footnotes">
            Generated by ProfileDash. Please verify all information independently.
        </div>
    </div> <!-- container -->

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const sectionHeaders = document.querySelectorAll('.content > .section > h2');
            sectionHeaders.forEach(header => {
                // Ensure a toggle indicator span exists or add one dynamically.
                let indicator = header.querySelector('.toggle-indicator');
                if (!indicator) {
                    indicator = document.createElement('span');
                    indicator.className = 'toggle-indicator no-print';
                    // Check if the associated content div (if it exists) is already collapsed by default.
                    const contentWrapper = header.nextElementSibling; // Assumes content div is the immediate sibling initially.
                    const isInitiallyCollapsed = contentWrapper && contentWrapper.classList.contains('section-content') && contentWrapper.classList.contains('collapsed');
                    indicator.innerHTML = isInitiallyCollapsed ? '▶' : '▼'; // Set initial indicator state (▶ for collapsed, ▼ for expanded).
                    header.appendChild(indicator);
                }

                // Find the corresponding content wrapper; it might not be the immediate sibling if structure varies.
                let contentWrapper = null;
                let nextElem = header.nextElementSibling;
                while(nextElem && !nextElem.matches('h2') && !nextElem.classList.contains('footnotes')) {
                     if (nextElem.classList.contains('section-content')) {
                         contentWrapper = nextElem;
                         break; // Found the content wrapper for this header.
                     }
                     nextElem = nextElem.nextElementSibling; // Check the next sibling.
                }

                // Add click listener to the header *only* if a corresponding content wrapper was found.
                if (contentWrapper) {
                    header.addEventListener('click', function(event) {
                        // Toggle the 'collapsed' class on the content wrapper and the header itself.
                        // Update the indicator symbol based on the new state.
                        // Note: This toggles on header click; could be modified to ignore clicks on links within H2 (see commented example).
                        // if (event.target.tagName !== 'A') {
                            const isCollapsed = contentWrapper.classList.toggle('collapsed');
                            header.classList.toggle('collapsed', isCollapsed);
                            indicator.innerHTML = isCollapsed ? '▶' : '▼';
                        // }
                    });
                } else {
                     // If no content wrapper is found for this header, hide the toggle indicator.
                     indicator.style.display = 'none';
                }
            });

            // --- Dynamic Content Wrapping (Post-Generation Fix) ---
            // Automatically wrap content following an H2 within a .section-content div
            // if one doesn't already exist. This handles cases where repair might have missed it.
             const sections = document.querySelectorAll('.content > .section');
             sections.forEach(section => {
                const header = section.querySelector('h2');
                if (!header) return; // Skip if no header found in section.
                let contentWrapper = section.querySelector('.section-content');

                // If no pre-existing .section-content div is found within this section...
                if (!contentWrapper) {
                    console.log('Wrapping content for section:', header.textContent.trim());
                    contentWrapper = document.createElement('div');
                    contentWrapper.className = 'section-content'; // Create the wrapper div.
                    // Add 'collapsed' class here if sections should start collapsed by default.
                    let currentElement = header.nextElementSibling;
                    const elementsToWrap = [];
                    // Collect all sibling elements after the header until the next section's H2 or the footnotes div.
                    while (currentElement) {
                        // Stop collecting if we hit the start of the next section or the footnotes.
                        if ((currentElement.tagName === 'H2' && currentElement.parentNode.classList.contains('section')) || currentElement.classList.contains('footnotes')) {
                           break;
                        }
                        elementsToWrap.push(currentElement);
                        currentElement = currentElement.nextElementSibling;
                    }

                    // If elements were found to wrap...
                    if (elementsToWrap.length > 0) {
                        // Move the collected elements inside the new wrapper div.
                        elementsToWrap.forEach(el => contentWrapper.appendChild(el));
                        // Insert the new wrapper div immediately after the header in the DOM.
                        header.parentNode.insertBefore(contentWrapper, header.nextSibling);

                        // Re-query the indicator (should exist from the earlier loop) and add the click listener now that the wrapper exists.
                        let indicator = header.querySelector('.toggle-indicator');
                        // Assumes indicator was added earlier even if content wrapper wasn't found initially.
                        if(indicator) {
                           header.addEventListener('click', function(event) { // Re-attach listener specifically for dynamically wrapped content
                              const isCollapsed = contentWrapper.classList.toggle('collapsed');
                              header.classList.toggle('collapsed', isCollapsed);
                              indicator.innerHTML = isCollapsed ? '▶' : '▼';
                           });
                        }
                    } else {
                       // If no content elements were found between this header and the next section/footnotes, hide the indicator.
                       let indicator = header.querySelector('.toggle-indicator');
                       if(indicator) indicator.style.display = 'none';
                    }
                }
             });
        });
    </script>
</body>
</html>
"""

    full_profile = html_head + toc_content + toc_end

    # Append each processed section's HTML content
    for i, content_html in enumerate(section_contents):
        section_num = sections[i]['number'] if i < len(sections) else 'Unknown'
        section_title = sections[i]['title'] if i < len(sections) else 'Unknown Section'
        escaped_section_title = html.escape(section_title)

        if content_html and isinstance(content_html, str):
             # Basic check if the content *looks* like it has the main section div wrapper.
             if not re.search(r'<div\s+[^>]*?class=["\']section["\']', content_html, re.IGNORECASE):
                  print(f"HTML Generator Warning: Section {section_num} content missing outer div wrapper - attempting to wrap.")
                  # Wrap the potentially broken content in a minimal error-indicating structure.
                  full_profile += f'<div class="section error-wrapper" id="section-{section_num}"><h2 class="error-header">{section_num}. {escaped_section_title}<span class="toggle-indicator no-print">▼</span></h2><div class="section-content"><p class="error">Warning: Content wrapper missing, attempting recovery:</p>{content_html}</div></div>\n'
             else:
                  # Append the presumably valid/repaired section content.
                  full_profile += content_html + "\n"
        else:
             # Handle cases where section content is missing or not a string.
             full_profile += f'<div class="section" id="section-{section_num}"><h2 class="error-header">{section_num}. {escaped_section_title}<span class="toggle-indicator no-print">▼</span></h2><div class="section-content"><p class="error">Error: Section content was missing or empty.</p></div></div>\n'


    full_profile += html_foot
    # Final cleanup for any stray code fences (should be less needed with earlier cleaning/repair).
    full_profile = full_profile.replace('```html', '').replace('```', '')
    return full_profile


def extract_text_from_html(html_content):
    """Extracts plain text from HTML content, attempting to preserve some structure."""
    if not isinstance(html_content, str):
        return ""

    try:
        # 1. Remove script and style blocks entirely.
        text = re.sub(r'<(script|style).*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # 2. Replace common block-level tags with newlines *before* removing all tags.
        # This helps preserve paragraph/list/table structure.
        text = re.sub(r'</(p|div|li|h[1-6]|tr|table|thead|tbody|th|td)>\s*', '\n', text, flags=re.IGNORECASE)
        # Also treat <br> tags as newlines.
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

        # 3. Remove all remaining HTML tags, replacing them with a space to avoid merging words.
        text = re.sub(r'<[^>]+>', ' ', text)

        # 4. Decode HTML entities (like &amp;, &lt;, &nbsp;).
        try:
            text = html.unescape(text)
        except Exception as e_unescape:
            print(f"HTML Text Extraction Warning: html.unescape failed: {e_unescape}. Proceeding with basic replacements.")
            # Basic manual replacements as a fallback. Order matters, especially for ampersand.
            text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ').replace('&amp;', '&') # Ampersand last

        # 5. Normalize whitespace.
        text = re.sub(r'[ \t]+', ' ', text) # Replace multiple spaces/tabs with a single space.
        text = re.sub(r'\n\s*\n+', '\n\n', text) # Collapse multiple consecutive newlines into max two.
        text = text.strip()

        return text

    except Exception as e:
        print(f"HTML Text Extraction Error: {e}")
        traceback.print_exc()
        # Return an error marker if extraction fails significantly.
        return "[Error extracting text from HTML]"
