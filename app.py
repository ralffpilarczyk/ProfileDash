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

# --- Main Gradio Processing Function (Revised outputs) ---
def run_initial_generation(file_paths, auth_state, progress=gr.Progress(track_tqdm=True)):
    """
    Takes uploaded file paths, runs generation, yields status, saves HTML to
    a temp file, and returns the path for download trigger.
    """
    start_run_time = time.time()
    status_log = []
    run_id = str(uuid.uuid4()) # <-- Generate unique ID for this run
    user_email_for_run = auth_state.get('email', 'unknown_user') # Get user email

    # --- START: Log RunStarted ---
    try:
        # Basic file metadata (improve with hashing later if needed for resume check)
        input_file_metadata = []
        if file_paths:
            if not isinstance(file_paths, list): file_paths = [file_paths] # Ensure list
            for fp in file_paths:
                if fp and os.path.exists(fp):
                    input_file_metadata.append({
                        "name": os.path.basename(fp),
                        "size": os.path.getsize(fp)
                        # Add hash later: "sha256": calculate_sha256(fp) 
                    })
                elif fp:
                    input_file_metadata.append({"name": os.path.basename(fp), "error": "File not found/accessible"})
                else:
                    input_file_metadata.append({"name": "None", "error": "Invalid file input"})

        # Derive company name early (might need refinement if logic changes)
        # This duplicates logic from later - consider refactoring later
        first_valid_filename = next((meta['name'] for meta in input_file_metadata if 'error' not in meta and meta['name'] != "None"), "Unknown_Company_RunStart")
        run_company_name = os.path.splitext(first_valid_filename)[0].replace('_', ' ')

        log_event = {
            "event": "RunStarted",
            "runId": run_id,
            "companyName": run_company_name,
            "inputFileMetadata": input_file_metadata,
            "appVersion": APP_VERSION
        }
        save_log_entry_hf_dataset(user_email=user_email_for_run, event_data=log_event)
        print(f"Run {run_id} started for user {user_email_for_run}, company {run_company_name}.")
    except Exception as log_start_e:
        print(f"Non-critical error logging RunStarted to dataset: {log_start_e}")
    # --- END: Log RunStarted ---

    def get_run_elapsed():
        elapsed = time.time() - start_run_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"[{minutes}'{seconds:02d}\"]"

    def append_status(message):
        nonlocal status_log
        timestamped_message = f"{get_run_elapsed()} {message}"
        status_log.insert(0, timestamped_message)
        return "\n".join(status_log[:15])

    # --- Pre-checks: Auth and API Key ---
    print(f"Running generation. Auth State: {auth_state}") # Debug
    if not auth_state.get("authenticated") or not auth_state.get("api_key_set"):
        status = append_status("ERROR: Auth/API Key incomplete. Restart.")
        # Yield/Return: Status, Download Path (None), Reset Button State
        yield status, None, gr.update(visible=False)
        return status, None, gr.update(visible=False)

    api_key = auth_state.get("api_key")
    if not api_key:
        status = append_status("ERROR: API Key missing. Restart.")
        yield status, None, gr.update(visible=False)
        return status, None, gr.update(visible=False)

    # --- Dynamic API Configuration ---
    try:
        print(f"Configuring genai with user key: ...{api_key[-4:]}")
        genai.configure(api_key=api_key)
        test_model = genai.GenerativeModel("gemini-2.0-flash")
        _ = test_model.generate_content("test: say ok")
        print("genai configured and test call successful.")
        status = append_status("Google AI SDK Configured OK.")
        yield status, None, gr.update(visible=False) # Yield only status, dl path, reset state
    except Exception as config_e:
        error_details = f"Error type: {type(config_e).__name__}, Message: {str(config_e)}"
        traceback.print_exc()
        error_msg = f"CRITICAL ERROR configuring Google AI SDK: {error_details}"
        print(error_msg)
        status = append_status(error_msg + "\nPlease check API Key and restart.")
        yield status, None, gr.update(visible=False)
        return status, None, gr.update(visible=False)

    # --- Initial File Check ---
    if not file_paths:
        status = append_status("No PDF files uploaded.")
        yield status, None, gr.update(visible=False)
        return status, None, gr.update(visible=False)

    status = append_status("Starting document processing...")
    yield status, None, gr.update(visible=False)

    # --- 1. Process Uploaded Documents (Base64) ---
    uploaded_data = {}
    documents_for_api = []
    company_name = "Uploaded_Company"
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    total_size = 0
    try:
        status = append_status("Reading uploaded documents...")
        yield status, None, gr.update(visible=False)

        if not isinstance(file_paths, list): file_paths = [file_paths]
        valid_files_count = 0
        for file_path in file_paths:
            if file_path is None:
                status = append_status("Warning: Invalid file input (None). Skipping.")
                yield status, None, gr.update(visible=False); continue
            filename = os.path.basename(file_path)
            try:
                if not os.path.exists(file_path):
                    status = append_status(f"Error: Temp file path not found: {file_path}. Skipping.")
                    yield status, None, gr.update(visible=False); continue
                if not filename.lower().endswith(".pdf"):
                    status = append_status(f"Warning: Skipping non-PDF: {filename}")
                    yield status, None, gr.update(visible=False); continue
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                     status = append_status(f"Warning: File '{filename}' is empty. Skipping.")
                     yield status, None, gr.update(visible=False); continue
                total_size += file_size
                with open(file_path, 'rb') as f:
                    uploaded_data[filename] = f.read()
                valid_files_count += 1
                status = append_status(f"Read: {filename} ({file_size // 1024} KB)")
                yield status, None, gr.update(visible=False)
            except Exception as read_err:
                 status = append_status(f"Error reading '{filename}': {read_err}")
                 yield status, None, gr.update(visible=False); continue

        if not uploaded_data:
            status = append_status("No valid PDF files were read.")
            yield status, None, gr.update(visible=False)
            return status, None, gr.update(visible=False)

        if total_size > MAX_UPLOAD_BYTES:
            error_msg = f"Upload failed: Total size ({total_size / (1024*1024):.2f} MB) exceeds {MAX_UPLOAD_MB} MB limit."
            status = append_status(error_msg)
            yield status, None, gr.update(visible=False)
            return status, None, gr.update(visible=False)

        status = append_status(f"Encoding {valid_files_count} files for API (base64)...")
        yield status, None, gr.update(visible=False)
        documents_for_api = load_document_content(uploaded_data) # Base64 version
        if not documents_for_api:
             status = append_status("Failed to process documents (base64).")
             yield status, None, gr.update(visible=False)
             return status, None, gr.update(visible=False)
        first_filename = next(iter(uploaded_data.keys()), "Unknown_Company")
        company_name = os.path.splitext(first_filename)[0].replace('_', ' ')
        status = append_status(f"Company: {company_name}. Starting generation...")
        yield status, None, gr.update(visible=False)

    except Exception as e:
        error_msg = f"Error during document processing: {str(e)}\n{traceback.format_exc()}"
        status = append_status(error_msg)
        yield status, None, gr.update(visible=False)
        return status, None, gr.update(visible=False)

    # --- 2. Generate Sections in Parallel ---
    total_sections = len(sections)
    initial_results = {}
    completed_sections = 0
    progress(0, desc="Starting section generation...")
    status = append_status(f"Starting parallel generation ({total_sections} sections)...")
    yield status, None, gr.update(visible=False)
    section_processing_error = False
    insight_model = None
    try:
        print("Creating insight model instance...")
        insight_model = create_insight_model()
        if not insight_model: raise Exception("Failed to create insight model")
        print("Insight model created.")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_section = {
                executor.submit(generate_initial_section, section, documents_for_api, persona, analysis_specs, output_format, insight_model): section
                for section in sections
            }
            
            # --- This is the loop to modify ---
            for future in as_completed(future_to_section):
                section_def = future_to_section[future]
                section_num = section_def["number"]; section_title = section_def["title"]
                status_update = f"Processing Section {section_num}..." # Default status
                
                try:
                    # Get the result (section number and HTML content string)
                    s_num_result, content_result = future.result() 
                    
                    # Check for generation errors indicated within the content
                    if not content_result or '<p class="error">' in content_result:
                        status_update = f"PARTIAL FAIL: Section {s_num_result} ('{section_title}')"
                        section_processing_error = True
                        if not content_result: # Handle completely empty return
                            # Create default error HTML if function returned None/empty
                            content_result = f'<div class="section" id="section-{s_num_result}"><h2>{s_num_result}. {section_title}</h2><p class="error">ERROR: Empty content returned.</p></div>'
                    else:
                        status_update = f"SUCCESS: Section {s_num_result} ('{section_title}')"
                    
                    # Store the result (HTML string or error HTML string) for final aggregation
                    initial_results[s_num_result] = content_result

                    # --- START: Save Individual Section to Dataset ---
                    try:
                        # Ensure necessary variables are defined and accessible here
                        # run_id, company_name, user_email_for_run
                        if content_result: # Only save if content exists (even error HTML)
                                section_saved_successfully = save_section_hf_dataset(
                                    section_num=s_num_result,
                                    section_content=content_result,
                                    content_type="html", # Hardcoded HTML for now
                                    run_id=run_id,       # From start of function
                                    company_name=company_name, # Determined before loop
                                    user_email=user_email_for_run # From start of function
                                )
                                if not section_saved_successfully:
                                    # Optionally log a warning to the main status if saving failed
                                    print(f"Warning: Failed to save section {s_num_result} to dataset for run {run_id}.")
                                    # status_update += " (Archive Save Failed)" # Optional: Append to user status
                        else:
                                print(f"Skipping dataset save for empty section {s_num_result}")
                    except Exception as section_save_e:
                            # Log error but don't stop the main generation
                            print(f"Non-critical error saving section {s_num_result} to dataset: {section_save_e}")
                            # status_update += " (Archive Error)" # Optional: Append to user status
                    # --- END: Save Individual Section ---

                except Exception as e:
                    # Handle exceptions during the future.result() call (LLM/processing error)
                    status_update = f"FAIL: Section {section_num} ('{section_title}') - {type(e).__name__}"
                    error_content_html = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Generation failed: {e}</p></div>'
                    initial_results[section_num] = error_content_html
                    section_processing_error = True
                    print(f"{get_run_elapsed()} Error in future for Sec {section_num}: {e}")
                    # traceback.print_exc() # Optional full trace for debugging generation errors

                    # --- START: Save Error Section Stub to Dataset ---
                    # Even if generation fails, save the error stub so we know an attempt was made
                    try:
                        save_section_hf_dataset(
                            section_num=section_num, # Use section_num from the loop context
                            section_content=error_content_html, # Save the generated error HTML
                            content_type="html", 
                            run_id=run_id,
                            company_name=company_name, 
                            user_email=user_email_for_run
                        )
                    except Exception as error_section_save_e:
                        print(f"Non-critical error saving error stub for section {section_num} to dataset: {error_section_save_e}")
                    # --- END: Save Error Section Stub ---

                # Update progress bar and status log after handling result and attempting save
                completed_sections += 1
                progress(completed_sections / total_sections, desc=status_update)
                status = append_status(status_update)
                yield status, None, gr.update(visible=False) # Status, DL Path (None), Reset State (Hidden)


    except Exception as e:
        error_msg = f"Error during parallel generation: {str(e)}\n{traceback.format_exc()}"
        status = append_status(error_msg)
        yield status, None, gr.update(visible=False)
        return status, None, gr.update(visible=False)

    status = append_status("Aggregation complete. Generating final HTML...")
    yield status, None, gr.update(visible=False)
    progress(1.0, desc="Finalizing...")

    # --- START: Replacement Block for Final Aggregation, Saving, and Logging ---
    ordered_initial_contents = []
    # Ensure sections are sorted by number when aggregating
    for section_def in sorted(sections, key=lambda x: x["number"]):
        # Use the content from initial_results, which includes error HTML for failed sections
        content = initial_results.get(section_def["number"], 
                                      # Fallback just in case a section number was missed entirely
                                      f'<div class="section" id="section-{section_def["number"]}"><h2>{section_def["number"]}. {section_def["title"]}</h2><p class="error">ERROR: Content completely missing for aggregation.</p></div>')
        ordered_initial_contents.append(content)

    final_status_message_base = "Profile generation complete!"
    if section_processing_error: 
        final_status_message_base += " (with errors)"

    status = append_status(final_status_message_base + " Saving result...")
    yield status, None, gr.update(visible=False) # Update status before final save attempts

    temp_file_path = None
    final_profile_saved_to_dataset = False # Flag to track dataset save status
    
    try:
        # --- Generate Final HTML ---
        final_html = generate_full_html_profile(company_name, sections, ordered_initial_contents, APP_VERSION)
        
        # --- Determine timestamp for output filename (should be defined earlier in the function) ---
        # Make sure 'timestamp' variable from Step 1.1 or similar is accessible here
        # If not, uncomment and adjust the line below:
        # timestamp = time.strftime('%Y%m%d_%H%M%S') 
        output_filename = f"{company_name}_Profile_{timestamp}.html" 

        # --- Save to Temp File for Download (Required for Gradio download trigger) ---
        # Ensure final_html is not empty before writing
        if final_html and isinstance(final_html, str):
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix=".html", delete=False) as temp_f:
                temp_f.write(final_html)
                temp_file_path = temp_f.name
                print(f"Saved final profile to temporary file: {temp_file_path}")
        else:
             print(f"ERROR: final_html content is empty or invalid for run {run_id}. Cannot save temp file.")
             final_html = "" # Ensure final_html is empty string if invalid
             temp_file_path = None # Ensure no temp file path is passed
             # Log this specific failure
             raise ValueError("Generated final_html was empty or invalid, cannot proceed.")

        # --- Save Final Profile to Private Dataset ---
        try:
            # Only attempt save if final_html was successfully generated
            if final_html: 
                saved_repo_path = save_profile_hf_dataset(
                    profile_content=final_html, 
                    content_type="html", # Hardcoded HTML for now
                    run_id=run_id,       # From start of function
                    company_name=company_name, 
                    user_email=user_email_for_run # Defined at start of function
                )
                if saved_repo_path:
                    print(f"Final profile also saved to private dataset: {DATASET_REPO_ID}/{saved_repo_path}")
                    final_profile_saved_to_dataset = True
                else:
                    # This condition is hit if save_profile_hf_dataset returns None due to error
                    print(f"Warning: Failed to save final profile to private dataset for run {run_id}.")
                    # Optionally update status log for user feedback if critical
                    # status = append_status("Warning: Failed to save profile archive.")
                    # yield status, temp_file_path, gr.update(visible=True) # Re-yield if status changes
            else:
                # This case should ideally not happen if the check above worked, but good for safety
                print(f"Skipping final profile dataset save for run {run_id}: final_html is empty.")
        except Exception as final_save_e:
             # Catch errors during the dataset save attempt
             print(f"Non-critical error saving final profile for run {run_id} to dataset: {final_save_e}")
             # Optionally log this error to the dataset itself? Might be overkill.

        # --- Prepare and Yield Final Status to User ---
        # Only indicate successful download if temp file was created
        if temp_file_path:
            final_status_message = append_status(final_status_message_base + f". Download '{output_filename}' should start automatically.")
            yield final_status_message, temp_file_path, gr.update(visible=True)
        else:
            # If temp file failed (e.g., final_html was empty), yield error status
            error_final = "Error: Failed to generate final profile content."
            status = append_status(error_final)
            yield status, None, gr.update(visible=False) # No download file, hide reset
            # Log failure here before returning
            try:
                log_event = {
                    "event": "RunFailed", "runId": run_id, "status": "Error",
                    "errorStage": "FinalHTMLGeneration", "errorMessage": error_final
                }
                save_log_entry_hf_dataset(user_email=user_email_for_run, event_data=log_event)
            except Exception as log_fail_e: print(f"Error logging RunFailed: {log_fail_e}")
            return status, None, gr.update(visible=False) # Return error state

        # --- Log RunCompleted AFTER successful generation & yielding ---
        try:
            log_event = {
                "event": "RunCompleted",
                "runId": run_id,
                "status": "Success" if temp_file_path else "Error", # Mark success only if file generated
                "finalProfileSavedToDataset": final_profile_saved_to_dataset,
                "sectionProcessingErrorEncountered": section_processing_error # Track if any section failed
            }
            save_log_entry_hf_dataset(user_email=user_email_for_run, event_data=log_event)
        except Exception as log_complete_e:
            print(f"Non-critical error logging RunCompleted to dataset: {log_complete_e}")

        # --- Final Return for Success ---
        return final_status_message, temp_file_path, gr.update(visible=True)

    except Exception as e:
         # --- Handle Exceptions during final_html generation or temp file saving ---
         error_final = f"Error during final profile stage: {type(e).__name__} - {str(e)}"
         print(f"Run {run_id}: {error_final}")
         # traceback.print_exc() # Uncomment for detailed debugging if needed
         status = append_status(error_final)
         yield status, None, gr.update(visible=False) # Yield error status, no download file
         
         # --- Log RunFailed on final stage exception ---
         try:
             log_event = {
                 "event": "RunFailed",
                 "runId": run_id,
                 "status": "Exception",
                 "errorStage": "FinalAggregation/Saving",
                 "errorType": type(e).__name__,
                 "errorMessage": str(e)
             }
             save_log_entry_hf_dataset(user_email=user_email_for_run, event_data=log_event)
         except Exception as log_fail_e:
             print(f"Non-critical error logging RunFailed after exception to dataset: {log_fail_e}")
             
         # --- Final Return for Exception ---
         return status, None, gr.update(visible=False)
    # --- END: Replacement Block ---

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
                progress_bar = gr.Progress(track_tqdm=True)
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

    # Generate Button Click (REVISED Outputs and .then() for JS)
    generate_button.click(
        fn=run_initial_generation,
        inputs=[pdf_upload, auth_state],
        # Outputs: Status Textbox, Hidden File Component, Reset Button Visibility
        outputs=[status_output, download_output, reset_button],
        show_progress="hidden" # Use the explicit progress bar component
    ).then( # Execute JS AFTER python function finishes and updates download_output
        fn=None, # No python function needed here
        inputs=None,
        outputs=None,
        # JavaScript to find the hidden download link and click it
        js="""
        () => {
          // Wait briefly for Gradio to update the hidden File component's value (the temp file path)
          setTimeout(() => {
            console.log("JS: Attempting to trigger download...");
            // Find the hidden wrapper div for the gr.File component using its elem_id
            const fileWrapper = document.getElementById('download-trigger-file');
            if (fileWrapper) {
              // Find the actual download anchor (<a>) tag within the wrapper.
              // Gradio usually structures it like this, but inspect element if needed.
              const downloadLink = fileWrapper.querySelector('a[download]');
              if (downloadLink && downloadLink.href && !downloadLink.href.endsWith('#') && downloadLink.href.includes('/file=')) {
                // Check if href is valid (not just '#' or empty, contains '/file=')
                console.log('JS: Found valid download link:', downloadLink.href);
                try {
                    // Trigger the click event on the link
                    downloadLink.click();
                    console.log('JS: Download click triggered.');
                } catch (e) {
                    console.error('JS: Error triggering download click:', e);
                    alert('Error: Failed to automatically trigger the file download. Check browser console.');
                }
              } else {
                console.error('JS: Download link (<a> tag with valid href) not found within #download-trigger-file. Auto-download failed.');
                // Optional: Alert user if link is missing/invalid after generation completes
                // alert('Error: Could not find the download link element. Auto-download failed.');
              }
            } else {
              console.error('JS: Download trigger component (#download-trigger-file) not found. Auto-download failed.');
              // alert('Error: Could not find the download component. Auto-download failed.');
            }
          }, 500); // 500ms delay seems reasonable, adjust if downloads fail occasionally
        }
        """
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