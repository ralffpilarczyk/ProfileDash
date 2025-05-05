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
from src.background_processor import execute_full_profile_workflow
from src.background_processor import save_log_entry_hf_dataset

# --- Variables ---
APP_VERSION = "v1.1.1"
LOG_FILE = "user_log.json"
DATASET_REPO_ID = "ralfpilarczyk/ProfileDashData" 
PERMITTED_USERS_FILE = "permitted_users.json"
HF_TOKEN = os.environ.get("HF_DATA_TOKEN") 
MAX_WORKERS = 3 
MAX_UPLOAD_MB = 20 
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_DOMAIN = "sc.com" 

# --- Get Google API Key ---
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') # Fetch the key from environment/secrets
if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY not found. Profile generation will not work.")
# --- END Get Google API Key ---

# Initialize the Hub API client 
try:
    if HF_TOKEN:
        api = HfApi(token=HF_TOKEN)
        print("Hugging Face API client initialized with token.")
    else:
        api = HfApi() 
        print("WARNING: HF_DATA_TOKEN not found. Uploads to private dataset will fail.")
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
            target=execute_full_profile_workflow, # <<< NEW Function Name from background_processor.py
            args=(
                # --- Original args needed by the workflow ---
                run_id,
                user_email,
                GOOGLE_API_KEY,
                temp_paths_copy,
                # --- Dependencies needed by the workflow (pass global objects/constants from app.py) ---
                sg, # Pass the initialized SendGrid client
                api, # Pass the initialized HfApi client
                HF_TOKEN, # Pass the Hugging Face Token
                DATASET_REPO_ID, # Pass the Dataset Repo ID
                SENDER_EMAIL, # Pass the Sender Email
                APP_VERSION, # Pass the App Version
                MAX_WORKERS, # Pass Max Workers
                MAX_UPLOAD_BYTES # Pass Max Upload Bytes
            ),
            daemon=True # Keep daemon True
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
