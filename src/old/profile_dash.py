#!/usr/bin/env python3
"""
ProfileDash - Company Profile Generator
Main script that orchestrates the profile generation process
"""

import os
import json
import time
import re
from datetime import datetime
import webbrowser
# import glob # No longer needed
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import traceback # Import traceback

# Import ProfileDash modules
from document_processor import upload_documents, load_document_content
from html_generator import create_profile_folder, save_section, load_section, generate_full_html_profile
from section_processor import generate_initial_section, refine_section_content

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Google API Key not found in environment variables!")

# Initialize Google AI API
import google.generativeai as genai
genai.configure(api_key=GOOGLE_API_KEY)

# Configuration variables
MAX_WORKERS = 3 # Keep at 2 for 15 RPM limit reliability

# --- Global Start Time ---
script_start_time = 0.0 # Initialize globally

# --- CORRECTED get_elapsed_time ---
def get_elapsed_time():
    """Return a formatted string with elapsed time based on the GLOBAL start."""
    global script_start_time
    # Initialize if main hasn't run yet (e.g., during module import)
    if script_start_time == 0.0:
        return "0'00\"" # Or maybe return "" or None? Let's keep default
    elapsed = time.time() - script_start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    return f"{minutes}'{seconds:02d}\""
# --- END CORRECTION ---

def main():
    """Main function to run the ProfileDash script"""
    global script_start_time
    script_start_time = time.time() # SET the global start time when main runs

    print("ProfileDash: Company Profile Generator")
    print("----------------------------------------")

    print(f"{get_elapsed_time()}: Uploading documents...") # Now uses global start time
    uploaded = upload_documents()
    if not uploaded: print("No documents uploaded. Exiting."); return

    print(f"{get_elapsed_time()}: Processing documents...")
    documents = load_document_content(uploaded)

    # Extract company name
    company_names = []
    for fn in uploaded.keys():
        match = re.match(r'^([A-Za-z][A-Za-z\s_&.-]+?)[\s_]*(\d{4}|Q\d|H[12]|Annual|Interim|Report|$)', fn, re.IGNORECASE)
        if match:
             name_part = match.group(1).strip().replace('_', ' ')
             if name_part.lower() not in ["monthly", "ProfileDash", "report", "update", "annual", "interim", "q1", "q2", "q3", "q4", "h1", "h2"]:
                  if name_part not in company_names: company_names.append(name_part)
    company_name = company_names[0] if company_names else "Unknown_Company"
    print(f"{get_elapsed_time()}: Extracted company name: {company_name}")

    profile_folder, timestamp = create_profile_folder(company_name)
    print(f"{get_elapsed_time()}: Created profile folder: {profile_folder}")

    from section_definitions import sections
    print(f"\n{get_elapsed_time()}: PHASE 1: GENERATING INITIAL SECTIONS IN PARALLEL")
    from prompts import persona, analysis_specs, output_format

    initial_results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_section = {
            # REMOVED passing script_start_time here
            executor.submit(generate_initial_section, section, documents, persona, analysis_specs, output_format, profile_folder): section
            for section in sections
        }
        for future in concurrent.futures.as_completed(future_to_section):
            section = future_to_section[future]
            try:
                section_num, content = future.result()
                initial_results[section_num] = content
                print(f"{get_elapsed_time()} Section {section_num}: Initial generation successful")
            except Exception as e:
                print(f"{get_elapsed_time()} Section {section['number']} ('{section['title']}') (Initial): Error: {e}")
                traceback.print_exc()
                error_content = f'''<div class="section" id="section-{section["number"]}"><h2>{section["number"]}. {section["title"]}</h2><p class="error">ERROR: Could not generate initial content for section {section["number"]}: {e}</p></div>'''
                initial_results[section["number"]] = error_content

    print(f"\n{get_elapsed_time()}: Generating initial HTML profile...")
    ordered_initial_contents = []
    has_initial_errors = False
    for section in sections:
        content = initial_results.get(section["number"], f'<div class="section" id="section-{section["number"]}"><h2>{section["number"]}. {section["title"]}</h2><p class="error">ERROR: Failed to retrieve initial content.</p></div>')
        if '<p class="error">ERROR:' in content: has_initial_errors = True
        ordered_initial_contents.append(content)
    if has_initial_errors: print(f"{get_elapsed_time()}: WARNING - Errors encountered during initial section generation. Review initial profile.")

    initial_profile_html = generate_full_html_profile(company_name, sections, ordered_initial_contents)
    initial_profile_path = os.path.join(profile_folder, f"{company_name}_Company_Profile_Initial_{timestamp}.html")
    try:
        with open(initial_profile_path, "w", encoding="utf-8") as f: f.write(initial_profile_html)
        print(f"{get_elapsed_time()}: Initial HTML profile saved to {initial_profile_path}")
    except Exception as e: print(f"{get_elapsed_time()}: ERROR saving initial profile: {e}"); return

    try:
        webbrowser.open(f"file://{os.path.abspath(initial_profile_path)}")
        print(f"{get_elapsed_time()}: Opened initial HTML file in browser")
    except Exception as e: print(f"{get_elapsed_time()}: Could not open initial HTML file automatically: {e}")

    print(f"\n{get_elapsed_time()}: PHASE 2: SELECT SECTIONS FOR REFINEMENT")
    while True:
        user_input = input(f"{get_elapsed_time()}: Review the initial profile. Enter section numbers to refine (comma-separated, e.g., 3,8,23), or press Enter to skip: ")
        selected_section_nums = []
        if not user_input.strip(): print(f"{get_elapsed_time()}: No sections selected for refinement."); break
        else:
            try:
                potential_nums = [s.strip() for s in user_input.split(',') if s.strip()]
                if all(s.isdigit() for s in potential_nums): selected_section_nums = [int(s) for s in potential_nums]
                else: raise ValueError("Non-digit input detected")
                valid_section_nums = {s["number"] for s in sections}; invalid_nums = [num for num in selected_section_nums if num not in valid_section_nums]
                selected_section_nums = [num for num in selected_section_nums if num in valid_section_nums]
                if invalid_nums: print(f"{get_elapsed_time()}: Warning - Invalid section numbers ignored: {invalid_nums}.")
                if not selected_section_nums: print(f"{get_elapsed_time()}: No valid sections selected. Try again or press Enter."); continue
                else: print(f"{get_elapsed_time()}: Refining sections: {sorted(selected_section_nums)}"); break
            except ValueError: print(f"{get_elapsed_time()}: Invalid format. Enter comma-separated numbers (e.g., 1,5,10) or press Enter."); continue

    refined_results = initial_results.copy()

    if selected_section_nums:
        print(f"\n{get_elapsed_time()}: REFINING SELECTED SECTIONS (Sequentially)")
        for section_num in sorted(selected_section_nums):
             section_def = next((s for s in sections if s["number"] == section_num), None)
             if not section_def: continue
             initial_content = initial_results.get(section_num)
             if not initial_content or '<p class="error">ERROR:' in initial_content:
                 print(f"{get_elapsed_time()}: Warning - Initial content for section {section_num} has errors. Skipping refinement.")
                 continue
             try:
                 print(f"\n{get_elapsed_time()}: Refining Section {section_num}: {section_def['title']}...")
                 # REMOVED passing script_start_time here
                 refined_content = refine_section_content(
                     section_def, initial_content, documents, persona, analysis_specs, output_format, profile_folder
                 )
                 refined_results[section_num] = refined_content
                 print(f"{get_elapsed_time()}: Section {section_num} refinement complete.")
             except Exception as e:
                 print(f"{get_elapsed_time()}: ERROR during refinement for section {section_num}: {e}. Using initial version.")
                 traceback.print_exc()

        print(f"\n{get_elapsed_time()}: Generating refined HTML profile...")
        ordered_refined_contents = []
        has_refined_errors = False
        for section in sections:
            content = refined_results.get(section["number"], f'<div class="section" id="section-{section["number"]}"><h2>{section["number"]}. {section["title"]}</h2><p class="error">ERROR: Failed to retrieve final content.</p></div>')
            if '<p class="error">ERROR:' in content: has_refined_errors = True
            ordered_refined_contents.append(content)
        if has_refined_errors: print(f"{get_elapsed_time()}: WARNING - Errors present in refined profile sections.")

        refined_profile_html = generate_full_html_profile(company_name, sections, ordered_refined_contents)
        refined_profile_path = os.path.join(profile_folder, f"{company_name}_Company_Profile_Refined_{timestamp}.html")
        try:
            with open(refined_profile_path, "w", encoding="utf-8") as f: f.write(refined_profile_html)
            print(f"{get_elapsed_time()}: Refined HTML profile saved to {refined_profile_path}")
        except Exception as e: print(f"{get_elapsed_time()}: ERROR saving refined profile: {e}")

        try:
            webbrowser.open(f"file://{os.path.abspath(refined_profile_path)}")
            print(f"{get_elapsed_time()}: Opened refined HTML file in browser")
        except Exception as e: print(f"{get_elapsed_time()}: Could not open refined HTML file automatically: {e}")

    metadata = {"company_name": company_name,"creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"document_count": len(documents),"refined_sections": sorted(selected_section_nums) if selected_section_nums else "None"}
    metadata_path = os.path.join(profile_folder, "metadata.json")
    try:
        with open(metadata_path, "w", encoding="utf-8") as f: json.dump(metadata, f, indent=2)
        print(f"{get_elapsed_time()}: Profile metadata saved to {metadata_path}")
    except Exception as e: print(f"{get_elapsed_time()}: ERROR saving metadata: {e}")

    end_time = time.time()
    elapsed_time = end_time - script_start_time
    elapsed_minutes = elapsed_time / 60
    print(f"\n{get_elapsed_time()}: EXECUTION COMPLETE")
    print(f"{get_elapsed_time()}: Total execution time: {elapsed_time:.2f} seconds ({elapsed_minutes:.2f} minutes)")

if __name__ == "__main__":
    main()