# --- START OF FILE app.py ---

import gradio as gr
import time
import os
import traceback # For error logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile # <-- ADDED IMPORT FOR TEMP FILES

# --- Import necessary functions from your modules within the 'src' directory ---
# Note the 'src.' prefix because app.py is at the root
try:
    from src.document_processor import load_document_content
    from src.html_generator import create_profile_folder, generate_full_html_profile, save_section # Saving sections is currently bypassed
    from src.section_processor import generate_initial_section
    from src.section_definitions import sections
    from src.prompts import persona, analysis_specs, output_format
    from src.utils import get_elapsed_time # Moved helper function

    # For API key loading (will use HF Secrets when deployed)
    from dotenv import load_dotenv
    load_dotenv() # Load .env file for local development
    # Initialize API client if needed
    import src.api_client
    import google.generativeai as genai

    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        print("Warning: GOOGLE_API_KEY not found. Set it in .env for local testing or HF Secrets for deployment.")
    else:
        # Configure the API client globally
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            print("Google AI SDK configured successfully.")
        except Exception as config_e:
            print(f"Error configuring Google AI SDK: {config_e}")
            # Handle configuration error appropriately

except ImportError as e:
    print(f"Error importing ProfileDash modules: {e}")
    print("Please ensure app.py is in the root directory and the 'src' directory with all modules exists.")
    print("Also ensure modules within 'src' use relative imports (e.g., 'from .api_client import ...') if necessary.")
    raise # Stop execution if core modules can't be imported
except Exception as general_e:
    print(f"An unexpected error occurred during setup: {general_e}")
    traceback.print_exc()
    raise

# --- Configuration ---
MAX_WORKERS = 3 # From your original script

# --- Main Gradio Processing Function (Initial Generation) ---
def run_initial_generation(file_paths, progress=gr.Progress(track_tqdm=True)):
    """
    Takes uploaded file paths, runs the initial profile generation in parallel,
    yields status updates, and returns the final HTML.
    """
    start_run_time = time.time() # For tracking this specific run's time

    # Helper for elapsed time specific to this run, using 'yield' updates
    def get_run_elapsed():
        elapsed = time.time() - start_run_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"[{minutes}'{seconds:02d}\"]"

    # --- Initial Check ---
    if not file_paths:
        yield f"{get_run_elapsed()} No PDF files uploaded. Please upload documents.", None, gr.update(visible=False)
        return f"{get_run_elapsed()} No PDF files uploaded. Please upload documents.", None, gr.update(visible=False)

    yield f"{get_run_elapsed()} Starting processing...", None, gr.update(visible=False)

    # --- 1. Process Uploaded Documents ---
    uploaded_data = {}
    documents_for_api = []
    company_name = "Uploaded_Company"
    profile_folder = f"temp_profile_{time.strftime('%Y%m%d_%H%M%S')}" # Used conceptually if saving were enabled
    timestamp = time.strftime('%Y%m%d_%H%M%S')

    try:
        yield f"{get_run_elapsed()} Reading uploaded documents...", None, gr.update(visible=False)
        valid_files_count = 0
        for file_path in file_paths:
            if file_path is None:
                yield f"{get_run_elapsed()} Warning: Received an invalid file input (None). Skipping.", None, gr.update(visible=False)
                continue
            filename = os.path.basename(file_path)
            try:
                with open(file_path, 'rb') as f:
                    file_content_binary = f.read()
                if not file_content_binary:
                     yield f"{get_run_elapsed()} Warning: File '{filename}' is empty. Skipping.", None, gr.update(visible=False)
                     continue

                uploaded_data[filename] = file_content_binary
                valid_files_count += 1
                yield f"{get_run_elapsed()} Read file: {filename} ({len(uploaded_data[filename]) // 1024} KB)", None, gr.update(visible=False)
            except FileNotFoundError:
                 yield f"{get_run_elapsed()} Error: File not found at path '{filename}'. Check Gradio temp file handling.", None, gr.update(visible=False)
                 continue
            except Exception as read_err:
                 yield f"{get_run_elapsed()} Error reading file '{filename}': {read_err}", None, gr.update(visible=False)
                 continue

        if not uploaded_data:
            yield f"{get_run_elapsed()} No valid files were successfully read.", None, gr.update(visible=False)
            return f"{get_run_elapsed()} No valid files were successfully read.", None, gr.update(visible=False)

        yield f"{get_run_elapsed()} Successfully read {valid_files_count} files. Processing for API...", None, gr.update(visible=False)

        documents_for_api = load_document_content(uploaded_data)
        if not documents_for_api:
             yield f"{get_run_elapsed()} Failed to process documents into API format.", None, gr.update(visible=False)
             return f"{get_run_elapsed()} Failed to process documents into API format.", None, gr.update(visible=False)

        first_filename = next(iter(uploaded_data.keys()), "Unknown_Company")
        company_name = first_filename.split('.')[0].replace('_', ' ')

        # --- Optional: Create local directory (Commented out) ---
        # try:
        #     full_profile_folder_path = os.path.abspath(profile_folder)
        #     os.makedirs(full_profile_folder_path, exist_ok=True)
        #     yield f"{get_run_elapsed()} Created local output directory: {profile_folder}", None, gr.update(visible=False)
        # except Exception as dir_e:
        #     yield f"{get_run_elapsed()} Warning: Could not create local directory '{profile_folder}': {dir_e}", None, gr.update(visible=False)
        # --- End Optional Directory Creation ---

        yield f"{get_run_elapsed()} Company Name (guess): {company_name}. Starting section generation...", None, gr.update(visible=False)

    except Exception as e:
        yield f"{get_run_elapsed()} Error during document processing phase: {traceback.format_exc()}", None, gr.update(visible=False)
        return f"{get_run_elapsed()} Error during document processing phase: {e}", None, gr.update(visible=False)

    # --- 2. Generate Sections in Parallel ---
    total_sections = len(sections)
    initial_results = {}
    completed_sections = 0

    progress(0, desc="Starting section generation...")
    yield f"{get_run_elapsed()} Starting parallel generation for {total_sections} sections (Max Workers: {MAX_WORKERS})... (This may take 10-15 mins)", None, gr.update(visible=False)

    section_processing_error = False

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_section = {
                executor.submit(generate_initial_section, section, documents_for_api, persona, analysis_specs, output_format, profile_folder): section
                for section in sections
            }

            for future in as_completed(future_to_section):
                section_def = future_to_section[future]
                section_num = section_def["number"]
                section_title = section_def["title"]
                status_update = ""
                try:
                    _, content = future.result()
                    if not content or '<p class="error">' in content:
                        if not content: content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Generation returned empty content.</p></div>'
                        initial_results[section_num] = content
                        status_update = f"PARTIAL FAIL: Section {section_num} ('{section_title}') completed with errors."
                        section_processing_error = True
                    else:
                        initial_results[section_num] = content
                        status_update = f"SUCCESS: Section {section_num} ('{section_title}') generated."

                except Exception as e:
                    original_error_msg = str(e)
                    error_msg = f"FAIL: Section {section_num} ('{section_title}') failed: {original_error_msg}"
                    print(f"{get_elapsed_time()} {error_msg}") # Log error to server console
                    # traceback.print_exc() # Optionally print full traceback
                    error_content = f'''<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Could not generate content for section {section_num}: {original_error_msg}</p></div>'''
                    initial_results[section_num] = error_content
                    status_update = error_msg
                    section_processing_error = True

                completed_sections += 1
                progress(completed_sections / total_sections, desc=status_update)
                yield f"{get_run_elapsed()} {status_update}", None, gr.update(visible=False)

    except Exception as e:
        yield f"{get_run_elapsed()} Error managing parallel section generation: {traceback.format_exc()}", None, gr.update(visible=False)
        return f"{get_run_elapsed()} Error managing parallel section generation: {e}", None, gr.update(visible=False)

    yield f"{get_run_elapsed()} Parallel generation finished. Aggregating final profile...", None, gr.update(visible=False)
    progress(1.0, desc="Aggregating profile...")

    # --- 3. Aggregate and Generate Final HTML ---
    ordered_initial_contents = []
    for section_def in sorted(sections, key=lambda x: x["number"]):
        sec_num = section_def["number"]
        if sec_num not in initial_results:
             print(f"Warning: Section {sec_num} missing from results! Adding error placeholder.")
             content = f'<div class="section" id="section-{sec_num}"><h2>{sec_num}. {section_def["title"]}</h2><p class="error">ERROR: Content generation result was missing.</p></div>'
             section_processing_error = True
        else:
            content = initial_results[sec_num]
        ordered_initial_contents.append(content)

    final_status_message = f"{get_run_elapsed()} Initial profile generation complete!"
    if section_processing_error:
        final_status_message += " WARNING: One or more sections failed or had errors. Review output carefully."

    yield final_status_message + " Generating final HTML...", None, gr.update(visible=False)

    try:
        final_html = generate_full_html_profile(company_name, sections, ordered_initial_contents)
        output_filename = f"{company_name}_Profile_Initial_{timestamp}.html"

        # --- Use Temporary File for Download ---
        temp_file_path = None
        try:
            # Create a temporary file and write the HTML bytes to it
            with tempfile.NamedTemporaryFile(mode='wb', suffix=".html", delete=False) as temp_f:
                temp_f.write(final_html.encode('utf-8'))
                temp_file_path = temp_f.name # Get the path

            # Prepare the update dictionary for the File component using the path
            final_file_output = gr.update(
                value=temp_file_path,
                label=f"Download {output_filename}",
                visible=True
            )
            # Yield the final update
            yield final_status_message, final_html, final_file_output
            # Final return value for the function
            return final_status_message, final_html, final_file_output

        except Exception as temp_file_e:
             # Fallback if creating temp file fails
             print(f"Error creating temporary file for download: {temp_file_e}")
             # Try returning bytes directly as a last resort (might cause the original error)
             yield final_status_message + " (Download may fail)", final_html, gr.update(value=final_html.encode('utf-8'), label=f"Download {output_filename}", visible=True)
             return final_status_message + " (Download may fail)", final_html, gr.update(value=final_html.encode('utf-8'), label=f"Download {output_filename}", visible=True)
        # --- End of Temporary File Handling ---

    except Exception as e:
         error_final = f"{get_run_elapsed()} Error generating final HTML or preparing download: {e}"
         yield error_final + f"\nTraceback:\n{traceback.format_exc()}", None, gr.update(visible=False)
         return error_final, None, gr.update(visible=False)


# --- Build the Gradio Blocks Interface ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# ProfileDash - Initial Profile Generator")
    gr.Markdown("Upload PDF documents for the company you want to profile.")
    gr.Markdown("**Important:** Initial generation can take 10-15 minutes. Please keep this tab active. Progress updates will appear below.")
    gr.Markdown("*Tip: If using a mobile device, consider changing your screen timeout setting to 'Never' or the longest duration before starting.*")

    with gr.Row():
        # Inputs
        pdf_upload = gr.File(
            label="Upload PDF Documents",
            file_count="multiple",
            file_types=[".pdf"],
            type="filepath" # Pass temporary file paths to the backend function
        )
        # Outputs
        with gr.Column(scale=2):
            status_output = gr.Textbox(label="Status / Log", lines=15, interactive=False, max_lines=20)
            # Define File component for download output
            download_output = gr.File(
                label="Download Full Profile",
                visible=False,
                interactive=False
            )

    generate_button = gr.Button("Generate Initial Profile", variant="primary")

    # HTML output below button
    html_output = gr.HTML(label="Generated Profile Preview")

    # Connect button click to the function
    generate_button.click(
        fn=run_initial_generation,
        inputs=[pdf_upload],
        outputs=[status_output, html_output, download_output] # Order matches function return/yield
    )

# --- Launch the Gradio app ---
if __name__ == "__main__":
    demo.queue() # Enable queuing
    demo.launch(share=False, server_name="0.0.0.0") # Allow local network access

# --- END OF FILE app.py ---