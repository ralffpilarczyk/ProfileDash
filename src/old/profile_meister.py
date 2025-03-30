#!/usr/bin/env python3
"""
ProfileMeister - Company Profile Generator
Main script that orchestrates the profile generation process
"""

import os
import json
import time
import re
from datetime import datetime
import webbrowser
import glob
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

# Import ProfileMeister modules
from document_processor import upload_documents, load_document_content
from api_client import create_fact_model, create_insight_model, cached_generate_content 
from html_generator import create_profile_folder, save_section, load_section, validate_html, repair_html

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
MAX_WORKERS = 2
REFINEMENT_ITERATIONS = 0
Q_NUMBER = 5

# Start timing
start_time = time.time()

def get_elapsed_time():
    """Return a formatted string with elapsed time"""
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    return f"{minutes}'{seconds:02d}\""

def main():
    """Main function to run the ProfileMeister script"""
    print("ProfileMeister: Company Profile Generator")
    print("----------------------------------------")
    
    # Create specialized models
    fact_model = create_fact_model()
    insight_model = create_insight_model()
    
    # Upload documents
    print(f"{get_elapsed_time()}: Uploading documents...")
    uploaded = upload_documents()
    
    if not uploaded:
        print("No documents uploaded. Exiting.")
        return
    
    # Process document content
    print(f"{get_elapsed_time()}: Processing documents...")
    documents = load_document_content(uploaded)
    
    # Extract company name
    company_names = []
    for fn in uploaded.keys():
        match = re.match(r'^([A-Za-z]+)', fn)
        if match and match.group(1) not in ["monthly", "ProfileMeister"]:
            company_names.append(match.group(1))
    
    company_name = company_names[0] if company_names else "Unknown_Company"
    print(f"{get_elapsed_time()}: Extracted company name: {company_name}")
    
    # Create profile folder
    profile_folder, timestamp = create_profile_folder(company_name)
    print(f"{get_elapsed_time()}: Created profile folder: {profile_folder}")
    
    # Load section definitions
    from section_definitions import sections
    
    # Process sections in parallel
    print(f"\n{get_elapsed_time()}: PROCESSING SECTIONS IN PARALLEL")
    from prompts import persona, analysis_specs, output_format
    
    # Helper function to process a section
    def process_section(section):
        """Process a single section and return its content"""
        try:
            section_num = section["number"]
            section_title = section["title"]
            
            # Check if we already have a refined version of this section saved
            existing_refined_content = load_section(profile_folder, f"{section_num}_refined")
            if existing_refined_content:
                print(f"{get_elapsed_time()} Section {section_num}: Loaded previously refined section")
                return section_num, existing_refined_content
            
            # Process the section
            from section_processor import process_section_in_parallel
            return process_section_in_parallel(
                section, documents, persona, analysis_specs, output_format, profile_folder, 
                refinement_iterations=REFINEMENT_ITERATIONS
            )
        except Exception as e:
            print(f"{get_elapsed_time()} Error processing section {section['number']}: {str(e)}")
            error_content = f'''
            <div class="section" id="section-{section["number"]}">
              <h2>{section["number"]}. {section["title"]}</h2>
              <p class="error">ERROR: Could not process section {section["number"]}: {str(e)}</p>
            </div>
            '''
            return section["number"], error_content
    
    # Process sections with ThreadPoolExecutor
    results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit section processing tasks
        future_to_section = {executor.submit(process_section, section): section for section in sections}
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_section):
            section = future_to_section[future]
            try:
                section_num, content = future.result()
                results[section_num] = content
                print(f"{get_elapsed_time()} Section {section_num}: Successfully completed")
            except Exception as e:
                print(f"{get_elapsed_time()} Section {section['number']}: Error: {str(e)}")
                error_content = f'''
                <div class="section" id="section-{section["number"]}">
                  <h2>{section["number"]}. {section["title"]}</h2>
                  <p class="error">ERROR: Could not process section {section["number"]}: {str(e)}</p>
                </div>
                '''
                results[section["number"]] = error_content
    
    # Generate complete HTML profile
    print(f"\n{get_elapsed_time()}: Generating complete HTML profile...")
    from html_generator import generate_full_html_profile
    
    # Get section contents in correct order
    ordered_section_contents = []
    for section in sections:
        section_content = results.get(section["number"], f'''
        <div class="section" id="section-{section["number"]}">
          <h2>{section["number"]}. {section["title"]}</h2>
          <p class="error">ERROR: No result for section {section["number"]}</p>
        </div>
        ''')
        ordered_section_contents.append(section_content)
    
    # Generate the complete HTML
    full_profile = generate_full_html_profile(company_name, sections, ordered_section_contents)
    
    # Save the final compiled profile as HTML
    final_profile_path = f"{profile_folder}/{company_name}_Company_Profile_{timestamp}.html"
    with open(final_profile_path, "w", encoding="utf-8") as f:
        f.write(full_profile)
    print(f"{get_elapsed_time()} Project: Complete HTML profile saved to {final_profile_path}")
    
    # Try to open the HTML file
    try:
        webbrowser.open(f"file://{os.path.abspath(final_profile_path)}")
        print(f"{get_elapsed_time()}: Opened HTML file in browser")
    except:
        print(f"{get_elapsed_time()}: Could not open HTML file automatically. Please open it manually")
    
    # Save metadata about the profile
    metadata = {
        "company_name": company_name,
        "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "document_count": len(documents)
    }
    metadata_path = f"{profile_folder}/metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"{get_elapsed_time()}: Profile metadata saved to {metadata_path}")
    
    # Fix any HTML issues
    fix_html_file(company_name)
    
    # End timing and calculate elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_minutes = elapsed_time / 60
    
    print(f"\n{get_elapsed_time()}: EXECUTION COMPLETE")
    print(f"{get_elapsed_time()}: Total execution time: {elapsed_time:.2f} seconds ({elapsed_minutes:.2f} minutes)")

def fix_html_file(company_name=None):
    """Clean up HTML with a more direct approach to remove duplicate section titles"""
    # Find and open the HTML file
    if company_name:
        profile_folders = glob.glob(f"profile_{company_name}_*")
        if not profile_folders:
            print(f"No profile folders found for company: {company_name}")
            return
        latest_folder = max(profile_folders, key=os.path.getctime)
    else:
        profile_folders = glob.glob("profile_*_*")
        if not profile_folders:
            print("No profile folders found")
            return
        latest_folder = max(profile_folders, key=os.path.getctime)
    
    html_files = glob.glob(f"{latest_folder}/*.html")
    company_profile_files = [f for f in html_files if "company_profile" in f]
    
    if not company_profile_files:
        print(f"No company profile HTML files found in {latest_folder}")
        return
    
    html_file_path = max(company_profile_files, key=os.path.getctime)
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove code markers
    content = content.replace('```html', '')
    content = content.replace('```', '')
    
    # Split content by section divs to process each section separately
    sections = re.split(r'(<div class="section"[^>]*>)', content)
    
    cleaned_content = sections[0]  # Start with content before first section
    
    for i in range(1, len(sections), 2):
        if i+1 < len(sections):
            div_start = sections[i]
            section_content = sections[i+1]
            
            # Extract section number from div
            section_num_match = re.search(r'id="section-(\d+)"', div_start)
            if section_num_match:
                section_num = section_num_match.group(1)
                
                # Remove standalone section title if it exists at start of section content
                section_content = re.sub(f'^\s*{section_num}\.[^<>\n]+▼\s*', '', section_content)
                
                # Add cleaned div and content
                cleaned_content += div_start + section_content
            else:
                # If no section number found, just add as is
                cleaned_content += div_start + section_content
                
    # Write cleaned content back to file
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"Cleaned up HTML file: {html_file_path}")
    return html_file_path

if __name__ == "__main__":
    main()