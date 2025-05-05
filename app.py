import gradio as gr
import time
import os
import traceback # For error logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
from datetime import datetime # Add import for logging
from huggingface_hub import upload_file, HfApi 
import io 
import uuid 
import threading
import base64
from huggingface_hub import HfApi, hf_hub_download 
from sendgrid.helpers.mail import (
    Mail, Email, To, Content, Attachment, FileContent, FileName,
    FileType, Disposition
)

# --- Variables ---
APP_VERSION = "v1.1.1"
LOG_FILE = "user_log.json"
DATASET_REPO_ID = "ralfpilarczyk/ProfileDashData" 
PERMITTED_USERS_FILE = "permitted_users.json"
HF_TOKEN = os.environ.get("HF_DATA_TOKEN") 
MAX_WORKERS = 3 # From your original script
MAX_UPLOAD_MB = 20 # Keep restriction reasonable
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_DOMAIN = "sc.com" # Restrict access

# --- Get Google API Key ---
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') # Fetch the key from environment/secrets
if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY secret not found. Profile generation will not work.")
# --- END Get Google API Key ---

# Initialize the Hub API client 
try:
    if HF_TOKEN:
        api = HfApi(token=HF_TOKEN)
        print("Hugging Face API client initialized with token.")
    else:
        api = HfApi() 
        print("WARNING: HF_DATA_TOKEN secret not found. Uploads to private dataset will fail.")
except Exception as api_init_e:
    print(f"ERROR initializing HfApi: {api_init_e}")
    api = None # Ensure api is None if init fails

# Basic check for username placeholder and correct dataset name format
if "your-username" in DATASET_REPO_ID or "/" not in DATASET_REPO_ID:
     print(f"CRITICAL WARNING: Check DATASET_REPO_ID variable! Currently: '{DATASET_REPO_ID}'. Ensure username is replaced and format is 'username/Dataset Name'.")
# --- END: Add HF Dataset Configuration ---

# --- Import necessary functions from your modules within the 'src' directory ---
try:
    # Using base64 processing
    from src.document_processor import load_document_content
    # HTML generation logic
    from src.html_generator import generate_full_html_profile
    # Initial section generation logic (accepting model instance)
    from src.section_processor import generate_initial_section
    # Section definitions (ensure this file exists in src)
    from src.section_definitions import sections
    # Prompts
    from src.prompts import persona, analysis_specs, output_format
    # API client functions (will be configured dynamically)
    from src.api_client import create_insight_model

    # For API key and SendGrid key loading
    from dotenv import load_dotenv
    load_dotenv() # Load .env file for local development

    # --- SendGrid Setup ---
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content

    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDER_EMAIL = "ProfileDash.NoReply@gmail.com" # Your verified SendGrid sender

    if not SENDGRID_API_KEY:
        print("Warning: SENDGRID_API_KEY not found. Set it in .env or HF Secrets.")
        sg = None # Indicate SendGrid is not available
    else:
        try:
            sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
            print("SendGrid client initialized.")
        except Exception as sg_init_e:
            print(f"Error initializing SendGrid client: {sg_init_e}")
            sg = None # Indicate SendGrid is not available

    # --- Google AI Setup (will be configured dynamically per request) ---
    import google.generativeai as genai
    # No global genai.configure() here anymore

except ImportError as e:
    print(f"Error importing ProfileDash modules: {e}")
    print("Please ensure app.py is in the root directory and the 'src' directory with all modules exists.")
    raise
except Exception as general_e:
    print(f"An unexpected error occurred during setup: {general_e}")
    traceback.print_exc()
    raise



# --- Helper Functions ---

def get_permitted_users():
    """
    Downloads and parses the permitted users config from the HF Dataset.
    Returns a dictionary with 'allowed_domains' and 'allowed_emails' lists (lowercase).
    Returns fallback defaults if download/parsing fails or config is invalid.
    """
    # Define fallback defaults INSIDE the function
    # You can keep ALLOWED_DOMAIN defined globally if you still want it as a code-level default
    fallback_config = {"allowed_domains": [ALLOWED_DOMAIN.lower()], "allowed_emails": []} 
    
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID: # Check base config
        print(f"WARNING: Cannot fetch permitted users config. HF Token/Repo ID not configured. Using code default: {fallback_config}")
        return fallback_config

    try:
        print(f"Attempting to download {PERMITTED_USERS_FILE} from {DATASET_REPO_ID}")
        # Use hf_hub_download to get file content (returns path)
        downloaded_path = api.hf_hub_download(
            repo_id=DATASET_REPO_ID,
            filename=PERMITTED_USERS_FILE,
            repo_type="dataset",
            token=HF_TOKEN,
            force_download=True, # Get latest version each time
            resume_download=False, 
            # Consider cache strategy later if file rarely changes & perf is issue
        )
        
        if downloaded_path and os.path.exists(downloaded_path):
             with open(downloaded_path, 'r', encoding='utf-8') as f:
                 permitted_data = json.load(f)
             print("Permitted users config loaded successfully from dataset.")
             
             # Validate structure and ensure keys exist, converting to lowercase
             valid_structure = True
             if not isinstance(permitted_data, dict):
                 valid_structure = False
             else:
                 domains = permitted_data.get("allowed_domains")
                 emails = permitted_data.get("allowed_emails")
                 if not isinstance(domains, list) or not isinstance(emails, list):
                     valid_structure = False
             
             if not valid_structure:
                  print(f"WARNING: {PERMITTED_USERS_FILE} has incorrect structure. Using code default: {fallback_config}")
                  return fallback_config
             
             # Return data with lists converted to lowercase
             return {
                 "allowed_domains": [domain.lower() for domain in domains],
                 "allowed_emails": [email.lower() for email in emails]
             }
        else:
            print(f"Warning: {PERMITTED_USERS_FILE} not found or empty path returned from download. Using code default: {fallback_config}")
            return fallback_config

    except json.JSONDecodeError as json_err:
         print(f"ERROR parsing {PERMITTED_USERS_FILE}: {json_err}. Using code default: {fallback_config}")
         return fallback_config
    except Exception as e:
        print(f"ERROR downloading or processing {PERMITTED_USERS_FILE}: {e}")
        # traceback.print_exc() # Uncomment for detailed debugging
        print(f"Using code default due to error: {fallback_config}")
        return fallback_config

# ---  START: Logging Function ---
def save_log_entry_hf_dataset(user_email: str, event_data: dict):
    """Uploads a structured log entry as a JSON file to the private HF Dataset."""
    # Check configuration before proceeding
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print("Log saving skipped: HF Token or Repo ID not configured correctly.")
        return 

    timestamp = datetime.now().isoformat()
    log_payload = {"timestamp": timestamp, "user": user_email, **event_data}
    
    # Use try-except for JSON dumping, although it's less likely to fail here
    try:
        log_content = json.dumps(log_payload, indent=2) 
    except TypeError as json_type_err:
         print(f"ERROR creating log JSON: {json_type_err}. Data: {log_payload}")
         # Fallback: create a simple error log entry
         log_payload = {"timestamp": timestamp, "user": user_email, "event": "LoggingError", "error": f"JSON TypeError: {json_type_err}"}
         log_content = json.dumps(log_payload, indent=2)
         
    # Create a unique filename using timestamp and sanitized email
    sanitized_email = user_email.replace('@', '_at_').replace('.', '_') 
    log_filename_in_repo = f"logs/{sanitized_email}/{timestamp}.json" 
    
    try:
        # Convert the JSON string to bytes and wrap it in BytesIO
        log_bytes = io.BytesIO(log_content.encode('utf-8'))
        
        print(f"Attempting to upload log to: {DATASET_REPO_ID}/{log_filename_in_repo}")
        
        # Upload the data
        upload_file(
            path_or_fileobj=log_bytes,
            path_in_repo=log_filename_in_repo,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset", 
            token=HF_TOKEN, 
            commit_message=f"Add log: {event_data.get('event', 'Unknown Event')} for {user_email}" 
        )
        print(f"Successfully uploaded log: {log_filename_in_repo}")
        
    except Exception as e:
        # Log errors but don't crash the main application
        print(f"ERROR uploading log to HF Dataset '{DATASET_REPO_ID}': {e}")
        # traceback.print_exc() # Uncomment only if needed for deep debugging
# --- END:  Logging Function ---

# --- START: Complete Background Task Function (with Direct String Base64 Attachment) ---
def _background_generate_and_notify(run_id: str, user_email: str, temp_file_paths: list):
    """
    Performs the entire profile generation in a background thread, 
    saves results to dataset, attempts to email result as Base64 attachment, 
    and logs status.
    """
    start_run_time = time.time()
    print(f"BG Run {run_id}: Started for {user_email}")
    
    # --- Function-local Helper for Background Logging ---
    background_log_internal = [] 
    def get_run_elapsed():
        elapsed = time.time() - start_run_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"[{minutes}'{seconds:02d}\"]"

    def append_bg_log(message):
        timestamped_message = f"{get_run_elapsed()} {message}"
        background_log_internal.insert(0, timestamped_message) 
        print(f"BG Run {run_id}: {timestamped_message}") 
    # --- End of Local Helper ---

    # Initialize status flags and variables
    section_processing_error = False
    error_message_for_email = None
    final_profile_saved_to_dataset = False
    final_profile_repo_path = None 
    company_name = "Unknown_Company" 
    timestamp_for_filename = time.strftime('%Y%m%d_%H%M%S') 
    final_html = "" # Initialize final_html

    try:
        # --- 1. Configure Google AI ---
        append_bg_log("Configuring Google AI SDK...")
        # Check the global variable directly
        if not GOOGLE_API_KEY:
            raise ValueError("ERROR: API Key was not found in environment.") # Adjusted error message
        try:
            # Use the global variable directly
            genai.configure(api_key=GOOGLE_API_KEY)
            append_bg_log("Google AI SDK Configured OK.")
        except Exception as config_e:
             error_msg = f"CRITICAL ERROR configuring Google AI SDK: {type(config_e).__name__} - {str(config_e)}"
             append_bg_log(error_msg)
             raise RuntimeError(error_msg) from config_e

        # --- 2. Process Uploaded Documents ---
        append_bg_log("Processing uploaded documents...")
        if not temp_file_paths: 
            raise ValueError("No file paths provided.")
            
        if not isinstance(temp_file_paths, list): 
            temp_file_paths = [temp_file_paths]
            
        uploaded_data = {}
        total_size = 0
        valid_files_count = 0

        for file_path in temp_file_paths:
            if file_path is None: 
                append_bg_log("Warning: Invalid file input (None).")
                continue
            filename = os.path.basename(file_path)
            try:
                if not os.path.exists(file_path): 
                    append_bg_log(f"Warning: Temp file not found: {file_path}.")
                    continue
                if not filename.lower().endswith(".pdf"):
                    append_bg_log(f"Warning: Skipping non-PDF: {filename}")
                    continue
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    append_bg_log(f"Warning: File '{filename}' is empty.")
                    continue
                
                total_size += file_size
                with open(file_path, 'rb') as f:
                    uploaded_data[filename] = f.read()
                valid_files_count += 1
                append_bg_log(f"Read: {filename} ({file_size // 1024} KB)")
            except Exception as read_err:
                 append_bg_log(f"Error reading '{filename}': {read_err}")
                 continue 

        if not uploaded_data: 
            raise ValueError("No valid PDF files processed.")
            
        if total_size > MAX_UPLOAD_BYTES: 
            raise ValueError(f"Upload failed: Size ({total_size / (1024*1024):.2f} MB) exceeds {MAX_UPLOAD_MB} MB.")

        append_bg_log(f"Encoding {valid_files_count} files for API (base64)...")
        documents_for_api = load_document_content(uploaded_data) 
        if not documents_for_api: 
            raise ValueError("Failed to process documents (base64).")
            
        first_filename = next(iter(uploaded_data.keys())) 
        company_name = os.path.splitext(first_filename)[0].replace('_', ' ')
        append_bg_log(f"Company: {company_name}. Starting parallel generation...")
        
        # --- 3. Generate Sections in Parallel ---
        total_sections = len(sections)
        initial_results = {} 
        completed_sections_count = 0 
        
        append_bg_log(f"Creating Gemini model instance...")
        insight_model = create_insight_model() 
        if not insight_model: 
            raise RuntimeError("Failed to create insight model.")
        append_bg_log("Model instance created. Submitting tasks...")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_section = {
                executor.submit(generate_initial_section, section, documents_for_api, persona, analysis_specs, output_format, insight_model): section
                for section in sections
            }
            
            append_bg_log(f"Tasks submitted. Waiting for completion...")
            for future in as_completed(future_to_section):
                section_def = future_to_section[future]
                section_num = section_def["number"]; section_title = section_def["title"]
                s_num_result, content_result = section_num, None 
                
                try:
                    s_num_result, content_result = future.result() 
                    if not content_result or '<p class="error">' in str(content_result):
                        append_bg_log(f"PARTIAL FAIL: Section {s_num_result} ('{section_title}') generation reported error.")
                        section_processing_error = True
                        if not content_result: content_result = f'<div class="section" id="section-{s_num_result}"><h2>{s_num_result}. {section_title}</h2><p class="error">ERROR: Generation function returned empty content.</p></div>'
                    else:
                        append_bg_log(f"SUCCESS: Section {s_num_result} ('{section_title}') generated.")
                    initial_results[s_num_result] = content_result
                except Exception as e:
                    append_bg_log(f"FAIL: Section {section_num} ('{section_title}') hit exception - {type(e).__name__}: {e}")
                    error_content_html = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Generation process failed unexpectedly: {e}</p></div>'
                    initial_results[section_num] = error_content_html
                    content_result = error_content_html 
                    section_processing_error = True
                
                # Save Section to Dataset
                try:
                    if content_result:
                         save_section_hf_dataset(
                             section_num=s_num_result, 
                             section_content=str(content_result), 
                             content_type="html", 
                             run_id=run_id, company_name=company_name, user_email=user_email 
                         )
                    else:
                         append_bg_log(f"Warning: Skipping dataset save for truly empty section {s_num_result}")
                except Exception as section_save_e:
                     append_bg_log(f"Non-critical error during save attempt for section {s_num_result}: {section_save_e}")
                
                completed_sections_count += 1
                progress_percent = int((completed_sections_count / total_sections) * 100)
                append_bg_log(f"Progress: {completed_sections_count}/{total_sections} ({progress_percent}%) sections processed.")

        append_bg_log("All sections processed. Aggregating final profile...")

        # --- 4. Aggregate and Save Final Profile ---
        ordered_initial_contents = []
        for section_def in sorted(sections, key=lambda x: x["number"]):
            content = initial_results.get(section_def["number"], 
                                          f'<div class="section" id="section-{section_def["number"]}"><h2>{section_def["number"]}. {section_def["title"]}</h2><p class="error">ERROR: Content missing during final aggregation.</p></div>')
            ordered_initial_contents.append(str(content))
        
        # ** Generate final_html string **
        final_html = generate_full_html_profile(company_name, sections, ordered_initial_contents, APP_VERSION)

        if final_html and isinstance(final_html, str):
            append_bg_log("Final HTML generated. Saving to dataset...")
            # ** Save final_html to dataset **
            saved_repo_path = save_profile_hf_dataset(
                profile_content=final_html, content_type="html", run_id=run_id, 
                company_name=company_name, user_email=user_email
            )
            if saved_repo_path:
                final_profile_saved_to_dataset = True
                final_profile_repo_path = saved_repo_path 
                append_bg_log(f"Final profile saved successfully to dataset: {saved_repo_path}")
            else:
                append_bg_log("Warning: Failed to save final profile to dataset.")
                if not error_message_for_email: 
                    error_message_for_email = "Profile generated but failed to save archive to dataset."
                final_profile_saved_to_dataset = False
        else:
            append_bg_log("Error: Final HTML generation failed or produced empty content.")
            raise ValueError("Final HTML generation failed, cannot save profile.") 

    except Exception as generation_e:
        # Catch errors from any stage within the main try block
        print(f"BG Run {run_id}: CRITICAL ERROR during generation pipeline: {generation_e}")
        traceback.print_exc() 
        section_processing_error = True 
        error_message_for_email = f"Profile generation failed: {type(generation_e).__name__} - {str(generation_e)}"
        
        # Log RunFailed
        try:
             log_event = {"event": "RunFailed", "runId": run_id, "status": "Exception", 
                          "errorStage": "BackgroundGenerationPipeline", "errorType": type(generation_e).__name__,
                          "errorMessage": str(generation_e)}
             save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
        except Exception as log_fail_e: print(f"Error logging RunFailed after main exception: {log_fail_e}")

    # --- 5. Send Email Notification ---
    append_bg_log("Preparing email notification...")
    email_subject = ""
    email_html_content = ""
    attachment_object = None # Initialize attachment object variable

    # Determine Final Outcome
    generation_succeeded_fully = not error_message_for_email and final_profile_saved_to_dataset
    generation_completed_with_errors = (section_processing_error or not final_profile_saved_to_dataset) and not error_message_for_email
    generation_failed_critically = error_message_for_email is not None

    # --- Compose Email Based on Outcome ---
    if generation_succeeded_fully:
        # --- SUCCESS: Encode final_html directly and attach ---
        status_string = "completed successfully"
        email_subject = f"ProfileDash: Profile for {company_name} is Ready"

        # Use the final_html string generated earlier AND final_profile_repo_path for filename
        if final_html and isinstance(final_html, str) and final_profile_repo_path: 
            try:
                append_bg_log("Encoding HTML content to Base64 for attachment...")
                
                # *** Encode the final_html string directly to Base64 ***
                encoded_content = base64.b64encode(final_html.encode('utf-8')).decode('ascii')
                
                append_bg_log("Base64 encoding complete. Creating attachment object...")
                
                # Construct a filename for the attachment
                attachment_filename = os.path.basename(final_profile_repo_path) 
                if not attachment_filename.lower().endswith('.html'):
                    attachment_filename += ".html"

                # Create the SendGrid Attachment object using encoded content
                attachment_object = Attachment(
                    FileContent(encoded_content), # Base64 encoded string
                    FileName(attachment_filename),
                    FileType('text/html'),
                    Disposition('attachment')
                )
                append_bg_log("Attachment object created successfully.")
                
                # Set success email body mentioning attachment
                email_html_content = f"""
                <p>Your ProfileDash profile generation for <strong>{company_name}</strong> {status_string}.</p>
                <p>The generated profile is attached to this email.</p>
                <p>(Run ID: {run_id})</p>
                <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
                """
            except Exception as attach_prep_e:
                # Handle errors during encoding or Attachment object creation
                append_bg_log(f"ERROR preparing Base64 attachment from string: {attach_prep_e}.")
                traceback.print_exc()
                # Fallback email content (No link, just notification of error)
                email_html_content = f"""
                <p>Your ProfileDash profile generation for <strong>{company_name}</strong> {status_string}, but there was an error preparing the file for attachment.</p>
                <p>Please try generating the profile again or contact support if the issue persists.</p> 
                <p>(Run ID: {run_id})</p>
                <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
                """
        else:
            # Case where final_html was empty/invalid or final profile wasn't saved
            append_bg_log("Final HTML content or repo path not available, cannot attach. Sending note.")
            email_html_content = f"""
            <p>Your ProfileDash profile generation for <strong>{company_name}</strong> completed, but the final profile could not be located or generated correctly for attachment.</p>
            <p>Please try generating the profile again or contact support.</p> 
            <p>(Run ID: {run_id})</p>
            <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
            """
        
        # Log RunCompleted status for full success
        try:
             log_event = {"event": "RunCompleted", "runId": run_id, "status": "Success",
                          "finalProfileSaved": final_profile_saved_to_dataset,
                          "sectionProcessingErrorEncountered": section_processing_error}
             save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
        except Exception as log_complete_e: print(f"Error logging RunCompleted success: {log_complete_e}")

    elif generation_completed_with_errors:
         # --- PARTIAL SUCCESS / COMPLETED WITH ERRORS EMAIL ---
         status_string = "completed with some errors"
         if section_processing_error: status_string += " during section generation"
         if not final_profile_saved_to_dataset: status_string += " (final profile save failed)"
         email_subject = f"ProfileDash: Profile for {company_name} Completed (with errors)"
         email_html_content = f"""
         <p>Your ProfileDash profile generation for <strong>{company_name}</strong> {status_string}.</p>
         <p>Some sections may contain errors or be incomplete. You may want to try generating the profile again or check the logs.</p> 
         <p>(Run ID: {run_id})</p>
         <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
         """
         # Log RunCompleted with Error status
         try:
             log_event = {"event": "RunCompleted", "runId": run_id, "status": "CompletedWithErrors",
                          "finalProfileSaved": final_profile_saved_to_dataset, 
                          "sectionProcessingErrorEncountered": section_processing_error}
             save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
         except Exception as log_complete_e: print(f"Error logging RunCompletedWithErrors: {log_complete_e}")
    
    else: # generation_failed_critically is True
        # --- FAILURE EMAIL ---
        email_subject = f"ProfileDash: Profile Generation Failed for {company_name}"
        error_details = error_message_for_email if error_message_for_email else 'An unspecified critical error occurred.'
        email_html_content = f"""
        <p>Unfortunately, the ProfileDash profile generation for <strong>{company_name}</strong> failed.</p>
        <p>Error details: {error_details}</p>
        <p>Please check the logs or contact support if the issue persists.</p>
        <p>(Run ID: {run_id})</p>
        <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
        """
        # RunFailed log should have already been attempted in the main except block

    # --- Send the Email (Common logic for all outcomes) ---
    if sg: 
        try:
            message = Mail(
                from_email=Email(SENDER_EMAIL, "ProfileDash Notification"),
                to_emails=To(user_email),
                subject=email_subject,
                html_content=Content("text/html", email_html_content) 
            )
            
            if attachment_object:
                message.attachment = attachment_object
                append_bg_log("Base64 Attachment added to email message.")
                
            response = sg.client.mail.send.post(request_body=message.get())
            
            log_email_event_type = "NotificationEmailSent"
            email_log_status = "Unknown"; email_outcome = "Unknown"; status_code = None

            if 200 <= response.status_code < 300:
                append_bg_log(f"Notification email sent successfully to {user_email}.")
                email_log_status = "Success"
            else:
                response_body_str = str(response.body)[:1000] 
                append_bg_log(f"Failed to send notification email to {user_email}. Status: {response.status_code} Body: {response_body_str}") 
                email_log_status = "Failure"
                status_code = response.status_code

            if generation_succeeded_fully: email_outcome = "Completed"
            elif generation_completed_with_errors: email_outcome = "CompletedWithErrors"
            else: email_outcome = "Failed"
            
            try:
                log_event = {"event": log_email_event_type, "runId": run_id, "status": email_log_status, "outcome": email_outcome}
                if status_code: log_event["statusCode"] = status_code
                if email_log_status == "Failure": log_event["sendgridResponseBody"] = response_body_str 
                save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
            except Exception as log_email_e: print(f"Error logging {log_email_event_type} {email_log_status}: {log_email_e}")

        except Exception as email_ex:
            append_bg_log(f"Exception sending notification email: {email_ex}")
            traceback.print_exc() 
            try:
                log_event = {"event": "NotificationEmailSent", "runId": run_id, "status": "Exception", "error": str(email_ex)}
                save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
            except Exception as log_email_e: print(f"Error logging EmailSent exception: {log_email_e}")
    else:
        append_bg_log("SendGrid client not available. Cannot send email notification.")

    append_bg_log(f"Background task finished.")
    # --- END: Complete Background Task Function (with Direct String Base64 Attachment) ---


def save_section_hf_dataset(section_num: int, section_content: str, content_type: str, run_id: str, company_name: str, user_email: str):
    """Uploads an individual generated section's content to the private HF Dataset."""
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print(f"Section {section_num} saving skipped: HF Token/Repo ID not configured.")
        return False # Indicate failure

    # Sanitize names for use in file paths
    safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
    sanitized_email = user_email.replace('@', '_at_').replace('.', '_')
    
    file_extension = "html" if content_type == "html" else "json" # Prepare for future
    
    # Define path within the dataset repo using the run_id
    # Example: profiles/user_at_domain_com/RUN_ID_UUID/section_1.html
    section_filename_in_repo = f"profiles/{sanitized_email}/{run_id}/section_{section_num}.{file_extension}"

    try:
        # Convert the section content string to bytes
        section_bytes = io.BytesIO(section_content.encode('utf-8'))
        
        print(f"Attempting to upload section {section_num} to: {DATASET_REPO_ID}/{section_filename_in_repo}")
        
        upload_file(
            path_or_fileobj=section_bytes,
            path_in_repo=section_filename_in_repo,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=HF_TOKEN,
            commit_message=f"Add section {section_num} ({content_type}): {safe_company_name} for {user_email} (Run: {run_id[:8]})" # Shorten run_id in commit
        )
        print(f"Successfully uploaded section {section_num}: {section_filename_in_repo}")
        return True # Indicate success
        
    except Exception as e:
        print(f"ERROR uploading section {section_num} to HF Dataset '{DATASET_REPO_ID}': {e}")
        # traceback.print_exc() # Uncomment for debugging upload issues
        return False # Indicate failure

def save_profile_hf_dataset(profile_content: str, content_type: str, run_id: str, company_name: str, user_email: str):
    """Uploads the final aggregated profile (HTML or JSON string) to the private HF Dataset."""
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print(f"Final profile saving skipped for run {run_id}: HF Token/Repo ID not configured.")
        return None 

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') # Use current time for final file name
    
    # Sanitize names
    safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
    sanitized_email = user_email.replace('@', '_at_').replace('.', '_')
    
    file_extension = "html" if content_type == "html" else "json"
    
    # Define path within the specific run's directory
    # Example: profiles/user_at_domain_com/RUN_ID_UUID/final_profile_20240101_120000.html
    profile_filename_in_repo = f"profiles/{sanitized_email}/{run_id}/final_profile_{timestamp}.{file_extension}"

    try:
        # Convert the profile string to bytes
        profile_bytes = io.BytesIO(profile_content.encode('utf-8'))
        
        print(f"Attempting to upload final profile ({content_type}) to: {DATASET_REPO_ID}/{profile_filename_in_repo}")
        
        upload_file(
            path_or_fileobj=profile_bytes,
            path_in_repo=profile_filename_in_repo,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=HF_TOKEN,
            commit_message=f"Add final {content_type.upper()} profile: {safe_company_name} for {user_email} (Run: {run_id[:8]})"
        )
        print(f"Successfully uploaded final profile: {profile_filename_in_repo}")
        return profile_filename_in_repo 
        
    except Exception as e:
        print(f"ERROR uploading final profile for run {run_id} to HF Dataset '{DATASET_REPO_ID}': {e}")
        # traceback.print_exc() # Uncomment for debugging
        return None 

# --- Authentication Backend ---
# (Function formerly known as send_auth_code)
def verify_email_and_check_key(email, auth_state):
    """
    Validates email against permitted list, checks for API key,
    logs events, and updates state to grant access.
    """
    # 1. Basic Email Format Check
    if not email or '@' not in email:
        # Return: Status message, original auth_state, keep email input visible, keep main app hidden
        return "Please enter a valid email address.", auth_state, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

    # 2. Check Permission using Dataset File
    print(f"Checking permissions for email: {email}")
    email_lower = email.lower()
    is_permitted = False
    permitted_users_config = get_permitted_users()

    if permitted_users_config:
        allowed_emails = permitted_users_config.get("allowed_emails", [])
        allowed_domains = permitted_users_config.get("allowed_domains", [])
        if email_lower in allowed_emails:
            is_permitted = True
            print(f"Email {email} permitted via allowed_emails list.") # Added print
        else:
            try:
                domain = email_lower.split('@')[1]
                if domain in allowed_domains:
                    is_permitted = True
                    print(f"Email {email} permitted via allowed_domains list ({domain}).") # Added print
            except IndexError:
                 print(f"Invalid email format encountered during domain check: {email}") # Added print
                 is_permitted = False
    else:
        print("CRITICAL ERROR: Could not retrieve permitted users configuration.")
        # Return: Error status, original state, keep email visible, keep main app hidden
        return "Error checking permissions. Please try again later.", auth_state, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

    if not is_permitted:
         print(f"Access denied for email: {email}")
         try: # Log denial
            log_event = {"event": "AuthAttemptDenied", "reason": "Email/Domain not permitted", "appVersion": APP_VERSION}
            save_log_entry_hf_dataset(user_email=email, event_data=log_event)
         except Exception as log_denial_e: print(f"Error logging AuthAttemptDenied: {log_denial_e}")
         # Return: Denial status, original state, keep email visible, keep main app hidden
         # Return generic denial message to user
         return "Access denied. Your email address is not authorized.", auth_state, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

    # 3. Check if API Key was loaded successfully at startup
    print(f"Email {email} permitted. Checking for API Key...")
    if not GOOGLE_API_KEY:
        print(f"CRITICAL ERROR: GOOGLE_API_KEY not found for permitted user {email}.")
        try: # Log key missing error
            log_event = {"event": "AuthAttemptFailed", "reason": "GOOGLE_API_KEY not found", "appVersion": APP_VERSION}
            save_log_entry_hf_dataset(user_email=email, event_data=log_event)
        except Exception as log_key_e: print(f"Error logging AuthAttemptFailed (API Key): {log_key_e}")
        # Return: API Key error status, original state, keep email visible, keep main app hidden
        return "Configuration Error: API key not found. Cannot proceed.", auth_state, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

    # 4. All checks passed: Authenticate user in state
    print(f"Email {email} verified and API key found. Authenticating.")
    auth_state["email"] = email
    auth_state["authenticated"] = True
    try: # Log success
         log_event = {"event": "AuthSuccess", "appVersion": APP_VERSION}
         save_log_entry_hf_dataset(user_email=email, event_data=log_event)
    except Exception as log_succ_e: print(f"Error logging AuthSuccess: {log_succ_e}")

    # Return: Success message, UPDATED state, HIDE email section, SHOW main app section
    return f"Email {email} verified. Proceed to upload documents.", auth_state, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

# --- Reset Function (Revised for new UI structure) ---
def reset_interface():
    """Resets the main app interface components for a new profile generation."""
    print("Resetting interface elements.")
    return (
        gr.update(value=None, visible=True),  # pdf_upload (make visible)
        gr.update(visible=True),              # generate_row (make visible)
        gr.update(visible=False),             # generation_inprogress_message (hide)
        "",                                   # status_output (clear text)
        gr.update(value=None, visible=False), # download_output (reset and hide)
        gr.update(visible=False),             # reset_button (hide itself)
        gr.update(visible=False)              # status_container (hide)
    ) # Now returns 7 values

# --- REVISED handle_generate_click function ---
def handle_generate_click(file_paths, auth_state):
    """Starts the background generation thread and returns immediate feedback."""
    user_email = auth_state.get('email')
    # api_key = auth_state.get('api_key') # DELETE THIS LINE
    run_id = str(uuid.uuid4()) # Generate ID here to return to user

    # Modify the check: Check for 'authenticated' flag and user_email
    if not auth_state.get('authenticated') or not user_email or not file_paths:
         # Handle missing prerequisites immediately
         return "Error: Not authenticated or missing uploaded files.", None, gr.update(visible=False) # Status, download_output, reset_button

    # Make a copy of temp file paths if passing paths
    temp_paths_copy = list(file_paths) if isinstance(file_paths, list) else [file_paths]

    print(f"UI Thread: Starting background task for run {run_id} for user {user_email}")
    try:
        # Create and start the background thread
        thread = threading.Thread(
            target=_background_generate_and_notify,
             # REMOVE api_key from args list below
            args=(run_id, user_email, temp_paths_copy),
            daemon=True # Allows main program to exit even if thread is running (optional)
        )
        thread.start()

        # --- Log RunSubmitted (optional but good) ---
        try:
            # Reuse metadata logic from background task start if desired
            input_file_metadata = [{"name": os.path.basename(fp) if fp else "None"} for fp in temp_paths_copy]
            first_valid_filename = next((meta['name'] for meta in input_file_metadata if meta['name'] != "None"), "Unknown_Company")
            run_company_name = os.path.splitext(first_valid_filename)[0].replace('_', ' ')
            log_event = {"event": "RunSubmitted", "runId": run_id, "companyName": run_company_name}
            save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
        except Exception as log_submit_e: print(f"Error logging RunSubmitted: {log_submit_e}")
        # --- End Log RunSubmitted ---

        # Update the status message string below:
        status_message = f"Profile generation has started. The profile will be emailed to {user_email} upon completion (approx. 10-20 mins). You can close this window now."

        # Return values to update UI (remains the same structure)
        return (
            gr.update(visible=False),             # pdf_upload
            gr.update(visible=False),             # generate_row
            gr.update(visible=True),              # generation_inprogress_message
            status_message,                       # status_output
            None,                                 # download_output
            gr.update(visible=False),             # reset_button
            gr.update(visible=False)              # generate_loading
        )

    except Exception as thread_e:
        # Return values on error need to be adjusted too, to match the expected number (7)
        # Keep inputs visible, show error in status, hide message/download/reset/loading
        print(f"UI Thread: Error starting background thread for run {run_id}: {thread_e}")
        traceback.print_exc()
        error_message = f"Error: Could not start generation process. {thread_e}"
        return (
            gr.update(),                          # pdf_upload (no change)
            gr.update(),                          # generate_row (no change)
            gr.update(visible=False),             # generation_inprogress_message
            error_message,                        # status_output
            None,                                 # download_output
            gr.update(visible=False),             # reset_button
            gr.update(visible=False)              # generate_loading
        )

# --- REVISED handle_generate_click_with_status function ---
def handle_generate_click_with_status(file_paths, auth_state):
    """Enhanced version of handle_generate_click that also manages UI visibility"""
    # Show the status container first
    result = handle_generate_click(file_paths, auth_state)
    # Return result plus visibility update for status container
    return [*result, gr.update(visible=True)]

# --- Build the Gradio Blocks Interface (ENHANCED UI/UX) ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:

    # --- Add enhanced CSS for improved UI/UX ---
    gr.Markdown("""
    <style>
        /* Responsive container */
        .container {
            max-width: 500px !important;
            margin: 0 auto !important;
            padding: 0 15px !important;
        }
        
        /* Loading indicator */
        .loading-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 3px solid rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            border-top-color: #2196F3;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            to {transform: rotate(360deg);}
        }
        
        /* Tooltip styles */
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
            margin-left: 5px;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
            line-height: 1.4;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* Validation feedback */
        .error-text {
            color: #d32f2f;
            font-size: 12px;
            margin-top: 4px;
            margin-bottom: 8px;
            transition: all 0.3s ease;
        }
        .success-text {
            color: #388e3c;
            font-size: 12px;
            margin-top: 4px; 
            margin-bottom: 8px;
            transition: all 0.3s ease;
        }
        
        /* Dark mode additions */
        .dark-mode {
            background-color: #222 !important;
            color: #eee !important;
        }
        .dark-mode .gradio-container {
            background-color: #333 !important;
        }
        .dark-mode .dark-text {
            color: #eee !important;
        }
        .dark-mode input, .dark-mode textarea {
            background-color: #444 !important;
            color: #eee !important;
            border-color: #555 !important;
        }
        .dark-mode .step-circle {
            background-color: #444;
            color: #eee;
        }
        .dark-mode .step-text {
            color: #bbb;
        }
        .dark-mode .progress-bar {
            background-color: #555;
        }
        
        /* Status output container transitions */
        #status-output-container {
            transition: all 0.3s ease;
            max-height: 0;
            overflow: hidden;
        }
        #status-output-container.visible {
            max-height: 400px;
        }
    </style>
    
    <script>
        // JavaScript for enhanced UI functionality
        document.addEventListener('DOMContentLoaded', function() {
            // Setup dark mode toggle
            const darkModeToggle = document.getElementById('dark-mode-toggle');
            if (darkModeToggle) {
                darkModeToggle.addEventListener('change', function() {
                    document.body.classList.toggle('dark-mode');
                    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
                });
                
                // Check for saved preference
                if (localStorage.getItem('darkMode') === 'true') {
                    document.body.classList.add('dark-mode');
                    darkModeToggle.checked = true;
                }
            }
            
            // Initialize tooltips
            const tooltips = document.querySelectorAll('.tooltip');
            tooltips.forEach(tooltip => {
                tooltip.innerHTML += '<span class="tooltiptext">' + tooltip.getAttribute('data-tooltip') + '</span>';
            });
        });
    </script>
    """)

    # --- State Variables ---
    auth_state = gr.State({
        "email": None,         # Will store verified email
        "authenticated": False # Will flag successful verification + API key check
    })
    
    with gr.Column(visible=True, elem_classes="container") as intro_section:
        gr.Markdown(f"""
        # **ProfileDash**
        {APP_VERSION}

        By Ralf Pilarczyk

        Generates company profiles by analyzing uploaded PDFs using Google Gemini.
        
        Disclaimer: Use at your own risk. Outputs may contain inaccuracies.

        """)

    # --- Authentication Section ---
    with gr.Column(visible=True, elem_classes="container") as auth_section:
        # Status message with validation feedback
        auth_status = gr.Markdown("Enter your email address below, then press Verify Email or hit Enter")
        
        # Email input section
        with gr.Column(visible=True) as email_input_row:
            email_input = gr.Textbox(
                label="Enter Your Email", 
                placeholder="your.email@domain.com"
            )
            # Rename button variable and update text
            verify_email_button = gr.Button(
                "Verify Email", # <-- Renamed text
                variant="primary", 
                scale=1
            )
            # Rename loading variable and update text
            verify_email_loading = gr.HTML(
                visible=False,
                value='<div class="loading-spinner"></div> Verifying email...', # <-- Updated text
                elem_id="verify-email-loading-id" # <-- ADD THIS LINE
            )
                
    # --- Main Application Interface ---
    with gr.Column(visible=False, elem_classes="container") as main_app_section:
        # Add information about file upload
        gr.Markdown("Select one or more PDF files containing company information. Maximum of 20MB in aggregate.")
        
        # File upload with enhanced label
        pdf_upload = gr.File(
            label="Upload PDF Documents",
            file_count="multiple",
            file_types=[".pdf"],
            type="filepath"
        )
        
        # File validation feedback
        file_validation = gr.HTML(
            visible=False,
            value='<div class="error-text">Please upload at least one PDF file</div>'
        )
        
        # Generate button with loading state
        with gr.Row() as generate_row:
            generate_button = gr.Button(
                "Generate Profile", 
                variant="primary", 
                scale=1
            )
            generate_loading = gr.HTML(
                visible=False,
                value='<div class="loading-spinner"></div> Starting profile generation...'
            )

        # Add the new message component (initially hidden)
        generation_inprogress_message = gr.Markdown(
            "**Profile is being generated and will be emailed to you.**",
            visible=False
        )

        # Status output (initially hidden, shown after generate is clicked)
        with gr.Column(visible=False, elem_id="status-output-container") as status_container:
            gr.Markdown("### Generation Status")
            status_output = gr.Textbox(
                label="Status Log", 
                lines=10, 
                interactive=False, 
                max_lines=15
            )
            # Hidden File component to receive the temp file path & trigger JS
            download_output = gr.File(
                label="Download Trigger", # Not user-visible
                visible=False,
                interactive=False,
                elem_id="download-trigger-file" # Crucial ID for JS
            )
            reset_button = gr.Button(
                "Produce New Profile", 
                visible=False, 
                variant="secondary"
            )

    # --- Simplified Event Connections ---

    # Connect Email input submit/button click to the new verification function
    verify_email_button.click(
        fn=verify_email_and_check_key,
        inputs=[email_input, auth_state],
        # Outputs: Status text, state, hide auth_section, show main_app_section, loading indicator
        outputs=[auth_status, auth_state, auth_section, main_app_section, verify_email_loading]
        # JS removed for now for simplicity, can be added back if loading indicator doesn't show reliably
    )
    email_input.submit(
        fn=verify_email_and_check_key,
        inputs=[email_input, auth_state],
        outputs=[auth_status, auth_state, auth_section, main_app_section, verify_email_loading]
        # JS removed for now
    )

    # Connect Generate profile button
    generate_button.click(
        fn=handle_generate_click_with_status, # Returns 8 values now
        inputs=[pdf_upload, auth_state],
        # List 8 output components in the correct order
        outputs=[
            pdf_upload,                     # 1st return value
            generate_row,                   # 2nd return value
            generation_inprogress_message,  # 3rd return value
            status_output,                  # 4th return value
            download_output,                # 5th return value
            reset_button,                   # 6th return value
            generate_loading,               # 7th return value
            status_container                # 8th return value (controls container visibility)
        ]
    )

    # Reset Button connection remains the same logic, but outputs list changes
    reset_button.click(
        fn=reset_interface,
        inputs=[],
        # Update outputs list to match the 7 return values from reset_interface
        outputs=[
            pdf_upload,                    # Corresponds to 1st return value
            generate_row,                  # Corresponds to 2nd return value
            generation_inprogress_message, # Corresponds to 3rd return value
            status_output,                 # Corresponds to 4th return value
            download_output,               # Corresponds to 5th return value
            reset_button,                  # Corresponds to 6th return value
            status_container               # Corresponds to 7th return value
        ]
    )

# --- Launch the Gradio app ---
if __name__ == "__main__":
    demo.queue()
    demo.launch(share=False, server_name="0.0.0.0") # Allow local network access# --- END OF REVISED app.py ---
