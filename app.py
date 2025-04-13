import gradio as gr
import time
import os
import traceback # For error logging
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
from datetime import datetime # Add import for logging
from huggingface_hub import upload_file, HfApi 
import io 
import uuid 
import threading

# --- App Version ---
# Updated version to reflect auto-download change
APP_VERSION = "v1.0.4"
LOG_FILE = "user_log.json"

# --- START: Add Hugging Face Dataset Configuration ---
# IMPORTANT: Replace 'your-username' with your ACTUAL Hugging Face username!
# Use the EXACT dataset name, including spaces: "ProfileDash Data"
DATASET_REPO_ID = "ralfpilarczyk/ProfileDashData" 

# Load the secret token from the Space environment variables (Secrets)
HF_TOKEN = os.environ.get("HF_DATA_TOKEN") 

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

# --- Configuration ---
MAX_WORKERS = 3 # From your original script
MAX_UPLOAD_MB = 20 # Keep restriction reasonable
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_DOMAIN = "sc.com" # Restrict access

# --- Helper Functions ---

def generate_auth_code():
    """Generates a 4-digit authentication code."""
    return str(random.randint(1000, 9999))

# ---  START: New Logging Function ---
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
# --- END: New Logging Function ---

# Paste this function definition alongside your other helper functions

def _background_generate_and_notify(run_id: str, user_email: str, api_key: str, temp_file_paths: list):
    """
    Performs the entire profile generation in a background thread, 
    saves results to dataset, and emails user upon completion or failure.
    NOTE: This function runs in a separate thread and CANNOT directly 
          update Gradio components using 'yield'. It interacts via dataset logs/files.
    """
    start_run_time = time.time()
    print(f"Background Run {run_id}: Started for {user_email}")
    
    # --- LOCAL VARIABLES (Copied/Adapted from run_initial_generation) ---
    # We need local copies or re-derivations of variables used inside the original function
    # Re-create status logging mechanism if needed for internal tracking (won't show in UI)
    background_log = []
    def append_bg_log(message):
         elapsed = time.time() - start_run_time
         minutes = int(elapsed // 60)
         seconds = int(elapsed % 60)
         timestamped_message = f"[{minutes}'{seconds:02d}\"] {message}"
         background_log.insert(0, timestamped_message)
         print(f"BG Run {run_id}: {timestamped_message}") # Print to server logs
         # We could potentially log detailed progress to a specific log file in the dataset too
         # save_log_entry_hf_dataset(user_email, {"event": "ProgressUpdate", "runId": run_id, "detail": message})

    section_processing_error = False
    final_profile_saved_to_dataset = False
    final_profile_repo_path = None # Store the path if saved
    error_message_for_email = None # Store any critical error message

    try:
        # --- 1. Configure Google AI (Essential in thread) ---
        # Must configure within the thread as config might be thread-local or context-specific
        try:
            print(f"BG Run {run_id}: Configuring genai...")
            genai.configure(api_key=api_key)
            # Minimal test call (optional but good practice)
            # test_model = genai.GenerativeModel("gemini-1.5-flash") 
            # _ = test_model.generate_content("test") 
            print(f"BG Run {run_id}: genai configured.")
            append_bg_log("Google AI SDK Configured OK.")
        except Exception as config_e:
             error_msg = f"CRITICAL ERROR configuring Google AI SDK in background thread: {config_e}"
             print(f"BG Run {run_id}: {error_msg}")
             raise RuntimeError(error_msg) from config_e # Raise critical error to stop

        # --- 2. Process Uploaded Documents (Adapted) ---
        # Note: Assumes temp_file_paths are still valid. If not, need to pass file *content*.
        # For simplicity now, assume paths are valid short-term. Robust solution might pass bytes.
        append_bg_log("Reading uploaded documents...")
        uploaded_data = {}
        documents_for_api = []
        company_name = "Uploaded_Company"
        total_size = 0
        
        # Need to re-implement the file reading and processing logic here
        # (Copied & adapted from run_initial_generation, removed yields)
        if not temp_file_paths: raise ValueError("No file paths provided to background task.")
        if not isinstance(temp_file_paths, list): temp_file_paths = [temp_file_paths]
        
        valid_files_count = 0
        for file_path in temp_file_paths:
            # Simplified checks assuming path validity was checked before thread start
            if file_path is None: continue
            filename = os.path.basename(file_path)
            try:
                if not os.path.exists(file_path): continue # Skip if temp file vanished
                if not filename.lower().endswith(".pdf"): continue
                file_size = os.path.getsize(file_path)
                if file_size == 0: continue
                total_size += file_size
                with open(file_path, 'rb') as f: uploaded_data[filename] = f.read()
                valid_files_count += 1
                append_bg_log(f"Read: {filename} ({file_size // 1024} KB)")
            except Exception as read_err:
                append_bg_log(f"Error reading '{filename}': {read_err}")
                continue
                
        if not uploaded_data: raise ValueError("No valid PDF files were read in background task.")
        if total_size > MAX_UPLOAD_BYTES: raise ValueError(f"Total size exceeds {MAX_UPLOAD_MB} MB limit.")
        
        append_bg_log(f"Encoding {valid_files_count} files for API (base64)...")
        documents_for_api = load_document_content(uploaded_data) 
        if not documents_for_api: raise ValueError("Failed to process documents (base64).")
        
        first_filename = next(iter(uploaded_data.keys()))
        company_name = os.path.splitext(first_filename)[0].replace('_', ' ')
        timestamp = time.strftime('%Y%m%d_%H%M%S') # Define timestamp for this run
        append_bg_log(f"Company: {company_name}. Starting generation...")
        
        # Clean up temp files if they were passed by path (important!)
        # This assumes the main thread doesn't need them after starting the background thread.
        # Be cautious if the main thread *does* still need them (e.g., for download link).
        # If using direct download, main thread needs path. If attaching from dataset, can delete.
        # Let's assume we email a link, so we can clean up.
        # for file_path in temp_file_paths:
        #     try:
        #         if file_path and os.path.exists(file_path):
        #             os.remove(file_path)
        #     except Exception as cleanup_e:
        #         print(f"BG Run {run_id}: Warning - could not clean up temp file {file_path}: {cleanup_e}")


        # --- 3. Generate Sections in Parallel (Adapted) ---
        append_bg_log(f"Starting parallel generation ({len(sections)} sections)...")
        initial_results = {}
        insight_model = create_insight_model() # Create model instance within thread
        if not insight_model: raise RuntimeError("Failed to create insight model in background thread.")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_section = {
                executor.submit(generate_initial_section, section, documents_for_api, persona, analysis_specs, output_format, insight_model): section
                for section in sections
            }
            
            for future in as_completed(future_to_section):
                section_def = future_to_section[future]
                section_num = section_def["number"]; section_title = section_def["title"]
                s_num_result, content_result = section_num, None # Defaults
                try:
                    s_num_result, content_result = future.result()
                    if not content_result or '<p class="error">' in content_result:
                        append_bg_log(f"PARTIAL FAIL: Section {s_num_result} ('{section_title}')")
                        section_processing_error = True
                        if not content_result: content_result = f'<div class="section" id="section-{s_num_result}"><h2>{s_num_result}. {section_title}</h2><p class="error">ERROR: Empty content returned.</p></div>'
                    else:
                        append_bg_log(f"SUCCESS: Section {s_num_result} ('{section_title}')")
                    initial_results[s_num_result] = content_result
                except Exception as e:
                    append_bg_log(f"FAIL: Section {section_num} ('{section_title}') - {type(e).__name__}")
                    error_content_html = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Generation failed: {e}</p></div>'
                    initial_results[section_num] = error_content_html
                    content_result = error_content_html # Ensure error content is saved
                    section_processing_error = True
                
                # Save section (now happens inside the loop)
                try:
                    if content_result:
                         save_section_hf_dataset(
                             section_num=s_num_result, section_content=content_result, content_type="html", 
                             run_id=run_id, company_name=company_name, user_email=user_email
                         )
                except Exception as section_save_e:
                    append_bg_log(f"Error saving section {s_num_result} to dataset: {section_save_e}")
        
        append_bg_log("Aggregation complete. Generating final HTML...")

        # --- 4. Aggregate and Save Final Profile (Adapted) ---
        ordered_initial_contents = []
        for section_def in sorted(sections, key=lambda x: x["number"]):
            content = initial_results.get(section_def["number"], f'<div class="section" id="section-{section_def["number"]}"><h2>{section_def["number"]}. {section_title}</h2><p class="error">ERROR: Content missing.</p></div>')
            ordered_initial_contents.append(content)
        
        final_html = generate_full_html_profile(company_name, sections, ordered_initial_contents, APP_VERSION)

        if final_html and isinstance(final_html, str):
            saved_repo_path = save_profile_hf_dataset(
                profile_content=final_html, content_type="html", run_id=run_id, 
                company_name=company_name, user_email=user_email
            )
            if saved_repo_path:
                final_profile_saved_to_dataset = True
                final_profile_repo_path = saved_repo_path # Store for email link
                append_bg_log(f"Final profile saved to dataset: {saved_repo_path}")
            else:
                append_bg_log("Warning: Failed to save final profile to dataset.")
                # Decide if this is a critical failure for notification
                error_message_for_email = "Profile generated but failed to save archive."
        else:
            append_bg_log("Error: Final HTML generation failed or produced empty content.")
            # Decide if this is a critical failure
            raise ValueError("Final HTML generation failed.")

    except Exception as generation_e:
        # Catch errors from any stage above (config, pdf processing, generation, final saving)
        print(f"BG Run {run_id}: CRITICAL ERROR during generation: {generation_e}")
        traceback.print_exc()
        section_processing_error = True # Mark as error
        error_message_for_email = f"Profile generation failed: {type(generation_e).__name__} - {str(generation_e)}"
        # Log RunFailed here
        try:
             log_event = {"event": "RunFailed", "runId": run_id, "status": "Exception", 
                          "errorStage": "BackgroundGeneration", "errorType": type(generation_e).__name__,
                          "errorMessage": str(generation_e)}
             save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
        except Exception as log_fail_e: print(f"Error logging RunFailed: {log_fail_e}")

    # --- 5. Send Email Notification ---
    print(f"BG Run {run_id}: Preparing email notification for {user_email}")
    email_subject = ""
    email_html_content = ""
    
    if not error_message_for_email and final_profile_saved_to_dataset:
        # --- SUCCESS EMAIL ---
        status_string = "completed successfully"
        if section_processing_error:
            status_string += " (with some errors during section generation)"
        
        email_subject = f"ProfileDash: Profile for {company_name} is Ready"
        # Option A: Link to Dataset File (Requires user login to HF)
        # Construct the URL to the file in the private dataset
        # Note: Direct links might change structure, linking to the dataset folder might be safer
        dataset_url = f"https://huggingface.co/datasets/{DATASET_REPO_ID}/tree/main/profiles/{user_email.replace('@','_at_').replace('.', '_')}/{run_id}"
        file_url = f"https://huggingface.co/datasets/{DATASET_REPO_ID}/blob/main/{final_profile_repo_path}" # More direct link

        email_html_content = f"""
        <p>Your ProfileDash profile generation for <strong>{company_name}</strong> {status_string}.</p>
        <p>You can view the generated profile in the private dataset (requires Hugging Face login):</p>
        <p><a href="{file_url}" target="_blank">View Profile: {os.path.basename(final_profile_repo_path)}</a></p>
        <p>(Run ID: {run_id})</p>
        <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
        """
        # # Option B: Attach File (Less Recommended)
        # # Needs download first -> more complex, size limits, security
        # try:
        #    local_path = api.hf_hub_download(...) # Download the file
        #    with open(local_path, 'rb') as f: file_data = f.read()
        #    encoded_file = base64.b64encode(file_data).decode()
        #    attachment = Attachment(FileContent(encoded_file), FileName(...), FileType(...), Disposition(...))
        #    # Add attachment to mail object
        # except Exception as attach_e: print(f"Error attaching file: {attach_e}")
        
        # Log RunCompleted after successful generation & saving confirmation
        try:
             log_event = {"event": "RunCompleted", "runId": run_id, "status": "Success",
                          "finalProfileSaved": final_profile_saved_to_dataset,
                          "sectionProcessingErrorEncountered": section_processing_error}
             save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
        except Exception as log_complete_e: print(f"Error logging RunCompleted: {log_complete_e}")

    else:
        # --- FAILURE EMAIL ---
        email_subject = f"ProfileDash: Profile Generation Failed for {company_name}"
        email_html_content = f"""
        <p>Unfortunately, the ProfileDash profile generation for <strong>{company_name}</strong> failed.</p>
        <p>Error details: {error_message_for_email or 'An unknown error occurred during processing.'}</p>
        <p>Some intermediate sections might have been saved to the dataset archive.</p>
        <p>(Run ID: {run_id})</p>
        <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
        """
        # Ensure RunFailed was logged within the main try/except block

    # Send the email using SendGrid client (sg)
    if sg:
        try:
            message = Mail(
                from_email=Email(SENDER_EMAIL, "ProfileDash Notification"),
                to_emails=To(user_email),
                subject=email_subject,
                html_content=Content("text/html", email_html_content)
            )
            response = sg.client.mail.send.post(request_body=message.get())
            if 200 <= response.status_code < 300:
                print(f"BG Run {run_id}: Notification email sent successfully to {user_email}.")
                # Log EmailSent success
                try:
                    log_event = {"event": "NotificationEmailSent", "runId": run_id, "status": "Success", "outcome": "Completed" if not error_message_for_email else "Failed"}
                    save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
                except Exception as log_email_e: print(f"Error logging EmailSent: {log_email_e}")
            else:
                print(f"BG Run {run_id}: Failed to send notification email to {user_email}. Status: {response.status_code}")
                # Log EmailSent failure
                try:
                    log_event = {"event": "NotificationEmailSent", "runId": run_id, "status": "Failure", "statusCode": response.status_code}
                    save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
                except Exception as log_email_e: print(f"Error logging EmailSent failure: {log_email_e}")

        except Exception as email_ex:
            print(f"BG Run {run_id}: Exception sending notification email: {email_ex}")
            # Log EmailSent exception
            try:
                log_event = {"event": "NotificationEmailSent", "runId": run_id, "status": "Exception", "error": str(email_ex)}
                save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
            except Exception as log_email_e: print(f"Error logging EmailSent exception: {log_email_e}")
    else:
        print(f"BG Run {run_id}: SendGrid client not available. Cannot send email notification.")

    print(f"Background Run {run_id}: Finished for {user_email}")

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

def send_auth_code(email, auth_state):
    """Validates email, sends auth code via SendGrid, updates state, and sends JSON log email."""
    if not email or '@' not in email:
        # Existing text output:
        return "Please enter a valid email address.", auth_state, gr.update(visible=True), gr.update(visible=False)

    try:
        domain = email.split('@')[1]
        if domain.lower() != ALLOWED_DOMAIN.lower():
            # Existing text output:
            return f"Access denied. Only users from the '{ALLOWED_DOMAIN}' domain are permitted.", auth_state, gr.update(visible=True), gr.update(visible=False)
    except IndexError:
         # Existing text output:
         return "Invalid email format.", auth_state, gr.update(visible=True), gr.update(visible=False)

    if not SENDGRID_API_KEY or not sg:
        print("Warning: SendGrid not configured or failed to initialize. Using dummy code '1234'.")
        code = "1234"
        auth_state["email"] = email
        auth_state["code"] = code
        auth_state["code_sent"] = True # Mark as sent for testing flow
        # Existing text output:
        return "SendGrid not configured. For testing, use code 1234.", auth_state, gr.update(visible=False), gr.update(visible=True)

    # # --- Define your tracking email address ---
    # TRACKING_EMAIL = "ProfileDash.NoReply@gmail.com" 

    # Generate User Code
    code = generate_auth_code()
    auth_state["email"] = email
    auth_state["code"] = code
    auth_state["code_sent"] = False # Mark as not sent yet

    # Prepare User Email
    subject = "Your ProfileDash Authentication Code"
    html_content = f"""
    <div style="font-family: sans-serif; padding: 20px; max-width: 400px; margin: auto; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="text-align: center; color: #333;">ProfileDash Authentication</h2>
        <p style="text-align: center; color: #555;">Please use the following code to complete your sign-in:</p>
        <div style="font-size: 36px; font-weight: bold; text-align: center; margin: 20px 0; padding: 10px; background-color: #f0f0f0; border-radius: 3px; letter-spacing: 5px;">
            {code}
        </div>
        <p style="font-size: 12px; color: #888; text-align: center;">If you did not request this code, you can safely ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 10px; color: #aaa; text-align: center;">ProfileDash - Automated Company Profiling</p>
    </div>
    """
    user_message = Mail(
        from_email=Email(SENDER_EMAIL, "ProfileDash"),
        to_emails=To(email),
        subject=subject,
        html_content=Content("text/html", html_content)
    )

    # --- Try sending the email to the USER first ---
    try:
        response = sg.client.mail.send.post(request_body=user_message.get())
        if 200 <= response.status_code < 300:
            print(f"Auth code sent successfully to {email}. Status: {response.status_code}")
            auth_state["code_sent"] = True

            # --- START: Inserted Code for Success Logging ---
            try:
                log_event = {
                    "event": "AuthCodeSent",
                    "status": "Success",
                    "appVersion": APP_VERSION 
                }
                save_log_entry_hf_dataset(user_email=email, event_data=log_event)
            except Exception as dataset_log_e:
                print(f"Non-critical error logging AuthCodeSent success to dataset: {dataset_log_e}")
            # --- END: Inserted Code for Success Logging ---

            # User email sent successfully, proceed to log email attempt (existing code for tracking email)
            # ... (The existing 'if auth_state["code_sent"] and TRACKING_EMAIL:' block follows here) ...
        else:
            # Failed to send to user, report error and stop
            print(f"Failed to send auth code to {email}. Status: {response.status_code}, Body: {response.body}")

            # --- START: Inserted Code for Failure Logging ---
            try:
                log_event = {
                    "event": "AuthCodeSendFailed",
                    "status": "Failure",
                    "statusCode": response.status_code,
                    "responseBody": str(response.body)[:500], # Limit response body size
                    "appVersion": APP_VERSION
                }
                save_log_entry_hf_dataset(user_email=email, event_data=log_event)
            except Exception as dataset_log_e:
                print(f"Non-critical error logging AuthCodeSendFailed to dataset: {dataset_log_e}")
            # --- END: Inserted Code for Failure Logging ---

            # Existing text output:
            return f"Error sending authentication code (Status: {response.status_code}). Try again later or contact support.", auth_state, gr.update(visible=True), gr.update(visible=False)

        # response = sg.client.mail.send.post(request_body=user_message.get())
        # if 200 <= response.status_code < 300:
        #     print(f"Auth code sent successfully to {email}. Status: {response.status_code}")
        #     auth_state["code_sent"] = True
        #     # User email sent successfully, proceed to log email attempt
        # else:
            # Failed to send to user, report error and stop
            # print(f"Failed to send auth code to {email}. Status: {response.status_code}, Body: {response.body}")
            # # Existing text output:
            # return f"Error sending authentication code (Status: {response.status_code}). Try again later or contact support.", auth_state, gr.update(visible=True), gr.update(visible=False)

    # except Exception as e:
    #     # Exception sending to user, report error and stop
    #     print(f"Exception sending email to {email}: {e}")
    #     traceback.print_exc()
    #     # Existing text output:
    #     return f"An error occurred while sending the email: {e}. Please try again.", auth_state, gr.update(visible=True), gr.update(visible=False)

    except Exception as e:
        # Exception sending to user, report error and stop
        print(f"Exception sending email to {email}: {e}")
        traceback.print_exc()

        # --- START: Inserted Code for Exception Logging ---
        try:
            log_event = {
                "event": "AuthCodeSendException",
                "status": "Exception",
                "errorType": type(e).__name__,
                "errorMessage": str(e),
                "appVersion": APP_VERSION
            }
            save_log_entry_hf_dataset(user_email=email, event_data=log_event)
        except Exception as dataset_log_e:
            print(f"Non-critical error logging AuthCodeSendException to dataset: {dataset_log_e}")
        # --- END: Inserted Code for Exception Logging ---

        # Existing text output:
        return f"An error occurred while sending the email: {e}. Please try again.", auth_state, gr.update(visible=True), gr.update(visible=False)

    return f"Authentication code sent to {email}. Enter code below and press Verify Code.", auth_state, gr.update(visible=False), gr.update(visible=True)


def verify_auth_code(entered_code, auth_state):
    """Verifies the entered code against the stored code."""
    print(f"Verifying code. Current auth_state: {auth_state}") # Debug print
    if not auth_state.get("code_sent"):
        return "Please request an authentication code first.", auth_state, gr.update(visible=True), gr.update(visible=True), gr.update(visible=False)

    stored_code = auth_state.get("code")
    if entered_code == stored_code:
        auth_state["authenticated"] = True
        print(f"Authentication successful for {auth_state.get('email')}")
        return "Authentication successful. Please enter your API Key.", auth_state, gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
    else:
        return "Invalid authentication code. Please try again.", auth_state, gr.update(visible=True), gr.update(visible=True), gr.update(visible=False)

# --- API Key Handling ---
def handle_api_key(api_key, auth_state):
    """Stores the API key in state and proceeds to main app."""
    if not api_key:
        return "API Key cannot be empty.", auth_state, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
    auth_state["api_key"] = api_key
    auth_state["api_key_set"] = True
    print(f"API Key received and stored for {auth_state.get('email')}.")
    print(f"API Key set. Current auth_state: {auth_state}") # Debug print
    return "API Key accepted. Upload documents to generate profile.", auth_state, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

# --- Reset Function (Revised outputs) ---
def reset_interface():
    """Resets the main app interface components for a new profile generation."""
    print("Resetting interface elements.")
    return (
        None, # pdf_upload
        "",   # status_output
        # REMOVED html_output
        gr.update(value=None, visible=False), # download_output (reset and hide)
        gr.update(visible=False) # reset_button itself hide
    )

def handle_generate_click(file_paths, auth_state):
    """Starts the background generation thread and returns immediate feedback."""
    user_email = auth_state.get('email')
    api_key = auth_state.get('api_key')
    run_id = str(uuid.uuid4()) # Generate ID here to return to user

    if not user_email or not api_key or not file_paths:
         # Handle missing prerequisites immediately
         return "Error: Missing email, API key, or uploaded files.", None, gr.update(visible=False) # Status, download_output, reset_button
    
    # Make a copy of temp file paths if passing paths
    # If passing content, extract bytes here
    temp_paths_copy = list(file_paths) if isinstance(file_paths, list) else [file_paths]
    
    # Create a snapshot of auth_state needed by the thread (avoid passing the whole mutable state) 
    
    # auth_state_snapshot = {
    #     'email': user_email,
    #     # Add any other relevant state if needed by background task
    # }

    print(f"UI Thread: Starting background task for run {run_id} for user {user_email}")
    try:
        # Create and start the background thread
        thread = threading.Thread(
            target=_background_generate_and_notify, 
            args=(run_id, user_email, api_key, temp_paths_copy),
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

        # Return immediate feedback to the user
        status_message = f"Profile generation for run ID '{run_id[:8]}' started. You will receive an email at {user_email} upon completion (approx. 10-20 mins)."
        # Return: status message, None for download, hide reset button initially
        return status_message, None, gr.update(visible=False) 
    
    except Exception as thread_e:
        print(f"UI Thread: Error starting background thread for run {run_id}: {thread_e}")
        traceback.print_exc()
        return f"Error: Could not start generation process. {thread_e}", None, gr.update(visible=False)
    
# --- Main Gradio Processing Function (Revised outputs) ---
# --- START: Complete Background Task Function ---
def _background_generate_and_notify(run_id: str, user_email: str, api_key: str, temp_file_paths: list):
    """
    Performs the entire profile generation in a background thread, 
    saves results to dataset, and emails user upon completion or failure.
    NOTE: This function runs in a separate thread and CANNOT directly 
          update Gradio components using 'yield'. It interacts via dataset logs/files 
          and prints status to server logs.
    """
    start_run_time = time.time()
    print(f"BG Run {run_id}: Started for {user_email}")
    
    # --- Function-local Helper for Background Logging ---
    background_log_internal = [] # Keep internal track if needed, primarily use print
    def get_run_elapsed():
        """Calculates elapsed time for logging within this thread."""
        elapsed = time.time() - start_run_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"[{minutes}'{seconds:02d}\"]"

    def append_bg_log(message):
        """Logs message to server console with timestamp and run ID."""
        timestamped_message = f"{get_run_elapsed()} {message}"
        background_log_internal.insert(0, timestamped_message) # Optional internal list
        print(f"BG Run {run_id}: {timestamped_message}") 
        # Optional: Log progress update to dataset (can be verbose)
        # try:
        #    save_log_entry_hf_dataset(user_email, {"event": "ProgressUpdate", "runId": run_id, "detail": message})
        # except Exception as prog_log_e: print(f"BG Run {run_id}: Error logging progress update: {prog_log_e}")
    # --- End of Local Helper ---

    # Initialize status flags and variables for this run
    section_processing_error = False
    error_message_for_email = None
    final_profile_saved_to_dataset = False
    final_profile_repo_path = None 
    error_message_for_email = None 
    company_name = "Unknown_Company" # Default
    timestamp_for_filename = time.strftime('%Y%m%d_%H%M%S') # Timestamp for final filename if needed

    try:
        # --- 1. Configure Google AI (Essential in thread) ---
        append_bg_log("Configuring Google AI SDK...")
        if not api_key:
            raise ValueError("ERROR: API Key was not provided to the background task.")
        try:
            genai.configure(api_key=api_key)
            # Minimal test call (optional - uncomment if needed, ensure model exists)
            # test_model = genai.GenerativeModel("gemini-1.5-flash") 
            # _ = test_model.generate_content("test: say ok") 
            append_bg_log("Google AI SDK Configured OK.")
        except Exception as config_e:
             error_msg = f"CRITICAL ERROR configuring Google AI SDK: {type(config_e).__name__} - {str(config_e)}"
             append_bg_log(error_msg)
             raise RuntimeError(error_msg) from config_e

        # --- 2. Process Uploaded Documents (Adapted from original) ---
        append_bg_log("Processing uploaded documents...")
        if not temp_file_paths: 
            raise ValueError("No file paths provided to background task.")
            
        # Ensure it's a list
        if not isinstance(temp_file_paths, list): 
            temp_file_paths = [temp_file_paths]
            
        uploaded_data = {}
        total_size = 0
        valid_files_count = 0

        for file_path in temp_file_paths:
            if file_path is None: 
                append_bg_log("Warning: Invalid file input (None). Skipping.")
                continue
            filename = os.path.basename(file_path)
            try:
                # Check existence *again* as temp files can vanish
                if not os.path.exists(file_path): 
                    append_bg_log(f"Warning: Temp file path not found: {file_path}. Skipping.")
                    continue
                if not filename.lower().endswith(".pdf"):
                    append_bg_log(f"Warning: Skipping non-PDF: {filename}")
                    continue
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    append_bg_log(f"Warning: File '{filename}' is empty. Skipping.")
                    continue
                
                total_size += file_size
                with open(file_path, 'rb') as f:
                    uploaded_data[filename] = f.read() # Read content into memory
                valid_files_count += 1
                append_bg_log(f"Read: {filename} ({file_size // 1024} KB)")
            except Exception as read_err:
                 append_bg_log(f"Error reading '{filename}': {read_err}")
                 # Decide if one read error should stop the whole process - perhaps not
                 # section_processing_error = True # Mark potential issue
                 continue # Skip this file

        # Check if any valid files were actually read
        if not uploaded_data: 
            raise ValueError("No valid PDF files were read or processed.")
            
        # Check total size against limits
        if total_size > MAX_UPLOAD_BYTES: 
            raise ValueError(f"Upload failed: Total size ({total_size / (1024*1024):.2f} MB) exceeds {MAX_UPLOAD_MB} MB limit.")

        append_bg_log(f"Encoding {valid_files_count} files for API (base64)...")
        # Assume load_document_content takes the dict of {filename: bytes}
        documents_for_api = load_document_content(uploaded_data) 
        if not documents_for_api: 
            raise ValueError("Failed to process documents (base64 conversion).")
            
        # Determine Company Name (using the same logic as original)
        first_filename = next(iter(uploaded_data.keys())) # Get first filename
        company_name = os.path.splitext(first_filename)[0].replace('_', ' ')
        append_bg_log(f"Company: {company_name}. Starting parallel generation...")
        
        # --- Optional: Clean up temporary files ---
        # Uncomment if you are sure the main thread doesn't need them and 
        # you want explicit cleanup within the thread.
        # append_bg_log("Cleaning up temporary upload files...")
        # for file_path in temp_file_paths:
        #     try:
        #         if file_path and os.path.exists(file_path):
        #             os.remove(file_path)
        #     except Exception as cleanup_e:
        #         append_bg_log(f"Warning - could not clean up temp file {file_path}: {cleanup_e}")
        # --- End Optional Cleanup ---

        # --- 3. Generate Sections in Parallel (Adapted) ---
        total_sections = len(sections)
        initial_results = {} # Stores generated content (HTML string or error HTML)
        completed_sections_count = 0 # Track progress for logging
        
        append_bg_log(f"Creating Gemini model instance for section generation...")
        insight_model = create_insight_model() 
        if not insight_model: 
            raise RuntimeError("Failed to create insight model in background thread.")
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
                s_num_result, content_result = section_num, None # Defaults
                
                try:
                    # Get the result from the generation function
                    s_num_result, content_result = future.result() 
                    
                    # Basic check for error indicators within the returned content
                    if not content_result or '<p class="error">' in str(content_result): # Check if error string is present
                        append_bg_log(f"PARTIAL FAIL: Section {s_num_result} ('{section_title}') generation reported error.")
                        section_processing_error = True
                        if not content_result: # Handle completely empty return
                            content_result = f'<div class="section" id="section-{s_num_result}"><h2>{s_num_result}. {section_title}</h2><p class="error">ERROR: Generation function returned empty content.</p></div>'
                    else:
                        append_bg_log(f"SUCCESS: Section {s_num_result} ('{section_title}') generated.")
                    
                    # Store the result (HTML or error HTML string)
                    initial_results[s_num_result] = content_result

                except Exception as e:
                    # Handle exceptions *during* the execution of generate_initial_section
                    append_bg_log(f"FAIL: Section {section_num} ('{section_title}') hit exception - {type(e).__name__}: {e}")
                    # traceback.print_exc() # Uncomment for detailed debugging if needed
                    error_content_html = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Generation process failed unexpectedly: {e}</p></div>'
                    initial_results[section_num] = error_content_html
                    content_result = error_content_html # Use error content for saving
                    section_processing_error = True
                
                # --- Save Section to Dataset (Success or Error Stub) ---
                try:
                    if content_result: # Save whatever content we have (success HTML or error HTML)
                         save_section_hf_dataset(
                             section_num=s_num_result, # Use result number if available, else loop number
                             section_content=str(content_result), # Ensure it's a string
                             content_type="html", # Hardcoded HTML for now
                             run_id=run_id,       
                             company_name=company_name, 
                             user_email=user_email 
                         )
                         # Function prints its own success/error messages
                    else:
                         # This case should be rare now due to error HTML generation above
                         append_bg_log(f"Warning: Skipping dataset save for truly empty section {s_num_result}")
                except Exception as section_save_e:
                     append_bg_log(f"Non-critical error during save attempt for section {s_num_result}: {section_save_e}")
                
                # --- Update internal progress log ---
                completed_sections_count += 1
                progress_percent = int((completed_sections_count / total_sections) * 100)
                append_bg_log(f"Progress: {completed_sections_count}/{total_sections} ({progress_percent}%) sections processed.")

        append_bg_log("All sections processed. Aggregating final profile...")

        # --- 4. Aggregate and Save Final Profile (Adapted) ---
        ordered_initial_contents = []
        for section_def in sorted(sections, key=lambda x: x["number"]):
            content = initial_results.get(section_def["number"], 
                                          f'<div class="section" id="section-{section_def["number"]}"><h2>{section_def["number"]}. {section_def["title"]}</h2><p class="error">ERROR: Content missing during final aggregation.</p></div>')
            ordered_initial_contents.append(str(content)) # Ensure string
        
        final_html = generate_full_html_profile(company_name, sections, ordered_initial_contents, APP_VERSION)

        if final_html and isinstance(final_html, str):
            append_bg_log("Final HTML generated. Saving to dataset...")
            saved_repo_path = save_profile_hf_dataset(
                profile_content=final_html, content_type="html", run_id=run_id, 
                company_name=company_name, user_email=user_email
            )
            if saved_repo_path:
                final_profile_saved_to_dataset = True
                final_profile_repo_path = saved_repo_path # Store for email link
                append_bg_log(f"Final profile saved successfully to dataset: {saved_repo_path}")
            else:
                append_bg_log("Warning: Failed to save final profile to dataset.")
                error_message_for_email = "Profile generated but failed to save archive to dataset." # Set error for email
                # This is considered a failure state for the run completion log
        else:
            append_bg_log("Error: Final HTML generation failed or produced empty content.")
            raise ValueError("Final HTML generation failed, cannot save profile.") # Raise to trigger failure email

    except Exception as generation_e:
        # Catch errors from any stage within the main try block
        print(f"BG Run {run_id}: CRITICAL ERROR during generation pipeline: {generation_e}")
        traceback.print_exc() # Log full traceback to server logs
        section_processing_error = True # Mark as error
        error_message_for_email = f"Profile generation failed: {type(generation_e).__name__} - {str(generation_e)}"
        
        # Log RunFailed if a critical error occurred
        try:
             log_event = {"event": "RunFailed", "runId": run_id, "status": "Exception", 
                          "errorStage": "BackgroundGenerationPipeline", "errorType": type(generation_e).__name__,
                          "errorMessage": str(generation_e)}
             save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
        except Exception as log_fail_e: print(f"Error logging RunFailed after main exception: {log_fail_e}")

    # --- 5. Send Email Notification ---
    # This block executes regardless of success/failure in the try block above
    append_bg_log("Preparing email notification...")
    email_subject = ""
    email_html_content = ""
    
    # Check flags set during the try block to determine outcome
    generation_succeeded_fully = not section_processing_error and final_profile_saved_to_dataset
    generation_failed_critically = error_message_for_email is not None # Check if a critical error was caught

    if generation_succeeded_fully:
        # --- SUCCESS EMAIL ---
        status_string = "completed successfully"
        email_subject = f"ProfileDash: Profile for {company_name} is Ready"
        if final_profile_repo_path:
            file_url = f"https://huggingface.co/datasets/{DATASET_REPO_ID}/blob/main/{final_profile_repo_path}"
            email_html_content = f"""
            <p>Your ProfileDash profile generation for <strong>{company_name}</strong> {status_string}.</p>
            <p>You can view the generated profile in the private dataset (requires Hugging Face login):</p>
            <p><a href="{file_url}" target="_blank">View Profile: {os.path.basename(final_profile_repo_path)}</a></p>
            <p>(Run ID: {run_id})</p>
            <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
            """
        else: # Fallback if path missing but somehow marked success (shouldn't happen often)
             dataset_folder_url = f"https://huggingface.co/datasets/{DATASET_REPO_ID}/tree/main/profiles/{user_email.replace('@','_at_').replace('.', '_')}/{run_id}"
             email_html_content = f"""
             <p>Your ProfileDash profile generation for <strong>{company_name}</strong> {status_string}, but the final file link could not be determined.</p>
             <p>You can check the output folder in the private dataset (requires Hugging Face login):</p>
             <p><a href="{dataset_folder_url}" target="_blank">View Run Folder</a></p>
             <p>(Run ID: {run_id})</p>
             <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
             """
        # Log RunCompleted only on full success
        try:
             log_event = {"event": "RunCompleted", "runId": run_id, "status": "Success",
                          "finalProfileSaved": final_profile_saved_to_dataset,
                          "sectionProcessingErrorEncountered": section_processing_error}
             save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
        except Exception as log_complete_e: print(f"Error logging RunCompleted: {log_complete_e}")

    elif section_processing_error and not generation_failed_critically:
         # --- PARTIAL SUCCESS / COMPLETED WITH ERRORS EMAIL ---
         status_string = "completed with some errors during section generation"
         email_subject = f"ProfileDash: Profile for {company_name} Completed (with errors)"
         # Link to folder is safer here as final file might be inconsistent
         dataset_folder_url = f"https://huggingface.co/datasets/{DATASET_REPO_ID}/tree/main/profiles/{user_email.replace('@','_at_').replace('.', '_')}/{run_id}"
         email_html_content = f"""
         <p>Your ProfileDash profile generation for <strong>{company_name}</strong> {status_string}.</p>
         <p>Some sections may contain errors or be incomplete. Please review the output carefully.</p>
         <p>You can view the generated files in the private dataset (requires Hugging Face login):</p>
         <p><a href="{dataset_folder_url}" target="_blank">View Run Folder</a></p>
         <p>(Run ID: {run_id})</p>
         <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
         """
         # Log RunCompleted with Error status
         try:
             log_event = {"event": "RunCompleted", "runId": run_id, "status": "CompletedWithErrors",
                          "finalProfileSaved": final_profile_saved_to_dataset, # May or may not have saved
                          "sectionProcessingErrorEncountered": section_processing_error}
             save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
         except Exception as log_complete_e: print(f"Error logging RunCompletedWithErrors: {log_complete_e}")
    
    else:
        # --- FAILURE EMAIL ---
        email_subject = f"ProfileDash: Profile Generation Failed for {company_name}"
        # error_message_for_email should have been set in the main except block
        error_details = error_message_for_email if error_message_for_email else 'An unspecified critical error occurred.'
        email_html_content = f"""
        <p>Unfortunately, the ProfileDash profile generation for <strong>{company_name}</strong> failed.</p>
        <p>Error details: {error_details}</p>
        <p>Please check the logs or contact support if the issue persists.</p>
        <p>(Run ID: {run_id})</p>
        <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
        """
        # RunFailed log was already attempted in the except block

    # Send the email using SendGrid client (sg)
    if sg: # Check if SendGrid client is available
        try:
            message = Mail(
                from_email=Email(SENDER_EMAIL, "ProfileDash Notification"),
                to_emails=To(user_email),
                subject=email_subject,
                html_content=Content("text/html", email_html_content)
            )
            response = sg.client.mail.send.post(request_body=message.get())
            log_email_event_type = "NotificationEmailSent"
            email_log_status = "Unknown"
            email_outcome = "Unknown"
            status_code = None

            if 200 <= response.status_code < 300:
                append_bg_log(f"Notification email sent successfully to {user_email}.")
                email_log_status = "Success"
                email_outcome = "Completed" if generation_succeeded_fully else ("CompletedWithErrors" if section_processing_error else "Failed")
            else:
                append_bg_log(f"Failed to send notification email to {user_email}. Status: {response.status_code}")
                email_log_status = "Failure"
                status_code = response.status_code
                email_outcome = "Completed" if generation_succeeded_fully else ("CompletedWithErrors" if section_processing_error else "Failed")
            
            # Log EmailSent status
            try:
                log_event = {"event": log_email_event_type, "runId": run_id, "status": email_log_status, "outcome": email_outcome}
                if status_code: log_event["statusCode"] = status_code
                save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
            except Exception as log_email_e: print(f"Error logging {log_email_event_type} {email_log_status}: {log_email_e}")

        except Exception as email_ex:
            append_bg_log(f"Exception sending notification email: {email_ex}")
            # Log EmailSent exception
            try:
                log_event = {"event": "NotificationEmailSent", "runId": run_id, "status": "Exception", "error": str(email_ex)}
                save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
            except Exception as log_email_e: print(f"Error logging EmailSent exception: {log_email_e}")
    else:
        append_bg_log("SendGrid client not available. Cannot send email notification.")

    append_bg_log(f"Background task finished.")
    # --- End of function ---
# --- END: Complete Background Task Function ---
# --- Build the Gradio Blocks Interface (REVISED - No HTML Preview) ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:

    # --- State Variables ---
    auth_state = gr.State({
        "email": None, "code": None, "code_sent": False,
        "authenticated": False, "api_key": None, "api_key_set": False
    })

    # --- 1. Introduction ---
    with gr.Column(visible=True) as intro_section:
        gr.Markdown(f"""
        # **ProfileDash**
        {APP_VERSION}

        By Ralf Pilarczyk

        Generates company profiles by analyzing uploaded PDFs using Google Gemini.
        
        Disclaimer: Use is at your own risk. Outputs may contain inaccuracies.

        **2-Step Authentication:** Enter your company email, then Google AI API Key.

        """)

    # --- 2. Authentication ---
    with gr.Column(visible=True) as auth_section:
        auth_status = gr.Textbox(label="Authentication Status", value="Enter your email address below, then press Send Code", interactive=False)
        with gr.Row(visible=True) as email_input_row:
            email_input = gr.Textbox(label="Enter Your Email", placeholder=f"your.email@{ALLOWED_DOMAIN}")
            send_code_button = gr.Button("Send Code")
        with gr.Row(visible=False) as code_input_row:
            code_input = gr.Textbox(label="Enter 4-Digit Code")
            verify_code_button = gr.Button("Verify Code")

    # --- 3. API Key Input ---
    with gr.Column(visible=False) as api_key_section:
        gr.Markdown("### Enter Your Google AI API Key")
        api_key_input = gr.Textbox(label="API Key", type="password", placeholder="Paste key here")
        gr.Markdown("""Get key from Google AI Studio:(https://aistudio.google.com/) (login via your Gmail account) ("Get API key") (Copy & paste).""")
        submit_api_key_button = gr.Button("Submit API Key")

    # --- 4. Main Application Interface (REVISED - No HTML Preview) ---
    with gr.Column(visible=False) as main_app_section:
        gr.Markdown("# ProfileDash")
        gr.Markdown(f"Version {APP_VERSION}")
        gr.Markdown("Upload PDF documents. Generation takes ~10 mins. Keep device awake and this tab active.")
        gr.Markdown(f"Max upload size: {MAX_UPLOAD_MB} MB. Desktop: Ctrl/Cmd+Click for multiple files.")
        gr.Markdown("Once profile is generated, download the file from your browser download folder.")

        with gr.Row():
            pdf_upload = gr.File(
                label="Upload PDF Documents",
                file_count="multiple",
                file_types=[".pdf"],
                type="filepath"
            )
            with gr.Column(scale=2):
                status_output = gr.Textbox(label="Status / Log", lines=15, interactive=False, max_lines=20)
                # progress_bar = gr.Progress(track_tqdm=True)
                # Hidden File component to receive the temp file path & trigger JS
                download_output = gr.File(
                    label="Download Trigger", # Not user-visible
                    visible=False,
                    interactive=False,
                    elem_id="download-trigger-file" # Crucial ID for JS
                )
                reset_button = gr.Button("Produce New Profile", visible=False)

        generate_button = gr.Button("Generate Profile & Download", variant="primary")

        # --- NO HTML Preview Component or CSS block here ---

    # --- Event Handling Logic ---

    # Auth and API Key handlers (Keep as before)
    send_code_button.click(fn=send_auth_code, inputs=[email_input, auth_state], outputs=[auth_status, auth_state, email_input_row, code_input_row])
    verify_code_button.click(fn=verify_auth_code, inputs=[code_input, auth_state], outputs=[auth_status, auth_state, auth_section, code_input_row, api_key_section])
    submit_api_key_button.click(fn=handle_api_key, inputs=[api_key_input, auth_state], outputs=[auth_status, auth_state, api_key_section, main_app_section, intro_section])

    # # Generate Button Click (REVISED Outputs and .then() for JS)
    # generate_button.click(
    #     fn=run_initial_generation,
    #     inputs=[pdf_upload, auth_state],
    #     # Outputs: Status Textbox, Hidden File Component, Reset Button Visibility
    #     outputs=[status_output, download_output, reset_button],
    #     show_progress="hidden" # Use the explicit progress bar component
    # ).then( # Execute JS AFTER python function finishes and updates download_output
    #     fn=None, # No python function needed here
    #     inputs=None,
    #     outputs=None,
    #     # JavaScript to find the hidden download link and click it
    #     js="""
    #     () => {
    #       // Wait briefly for Gradio to update the hidden File component's value (the temp file path)
    #       setTimeout(() => {
    #         console.log("JS: Attempting to trigger download...");
    #         // Find the hidden wrapper div for the gr.File component using its elem_id
    #         const fileWrapper = document.getElementById('download-trigger-file');
    #         if (fileWrapper) {
    #           // Find the actual download anchor (<a>) tag within the wrapper.
    #           // Gradio usually structures it like this, but inspect element if needed.
    #           const downloadLink = fileWrapper.querySelector('a[download]');
    #           if (downloadLink && downloadLink.href && !downloadLink.href.endsWith('#') && downloadLink.href.includes('/file=')) {
    #             // Check if href is valid (not just '#' or empty, contains '/file=')
    #             console.log('JS: Found valid download link:', downloadLink.href);
    #             try {
    #                 // Trigger the click event on the link
    #                 downloadLink.click();
    #                 console.log('JS: Download click triggered.');
    #             } catch (e) {
    #                 console.error('JS: Error triggering download click:', e);
    #                 alert('Error: Failed to automatically trigger the file download. Check browser console.');
    #             }
    #           } else {
    #             console.error('JS: Download link (<a> tag with valid href) not found within #download-trigger-file. Auto-download failed.');
    #             // Optional: Alert user if link is missing/invalid after generation completes
    #             // alert('Error: Could not find the download link element. Auto-download failed.');
    #           }
    #         } else {
    #           console.error('JS: Download trigger component (#download-trigger-file) not found. Auto-download failed.');
    #           // alert('Error: Could not find the download component. Auto-download failed.');
    #         }
    #       }, 500); // 500ms delay seems reasonable, adjust if downloads fail occasionally
    #     }
    #     """
    # )

    # Generate Button Click (Now triggers background task)
    generate_button.click(
        fn=handle_generate_click, # Call the new handler that starts the thread
        inputs=[pdf_upload, auth_state],
        # Output only updates the status textbox initially.
        # We list download_output and reset_button so Gradio knows the components exist,
        # but the handle_generate_click function returns None and gr.update(visible=False) for them.
        outputs=[status_output, download_output, reset_button], 
        show_progress="hidden" # Progress bar isn't directly tied to this initial click anymore
    )

    # Reset Button (REVISED Outputs)
    reset_button.click(
        fn=reset_interface,
        inputs=[],
        # Reset Upload, Status, Download File component, Reset Button
        outputs=[pdf_upload, status_output, download_output, reset_button]
    )

# --- Launch the Gradio app ---
if __name__ == "__main__":
    demo.queue()
    demo.launch(share=False, server_name="0.0.0.0") # Allow local network access
# --- END OF REVISED app.py ---