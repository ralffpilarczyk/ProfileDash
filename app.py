# ============================================================================
# ProfileDash - Main Application
# ============================================================================
# A Gradio-based web application that generates company profiles by analyzing
# uploaded PDFs using Google Gemini.
# ============================================================================

# ----------------------------------------------------------------------------
# Imports and Dependencies
# ----------------------------------------------------------------------------
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
# Import Gemini SDK (used elsewhere)
import google.generativeai as genai
from src.config import GEMINI_MODEL_NAME

# Ensure this module is importable as 'app' even when executed as __main__
import sys as _sys
_sys.modules.setdefault(__name__.split(".")[-1], _sys.modules[__name__])

from src.background_processor import execute_full_profile_workflow, save_log_entry_hf_dataset

# ----------------------------------------------------------------------------
# Configuration and Constants
# ----------------------------------------------------------------------------
# Application version and identifiers
APP_VERSION = "v1.3.0" # MODIFIED
LOG_FILE = "user_log.json"
DATASET_REPO_ID = "ralfpilarczyk/ProfileDashData"
PERMITTED_USERS_FILE = "permitted_users.json"
HF_TOKEN = os.environ.get("HF_DATA_TOKEN")
MAX_WORKERS = 3
MAX_UPLOAD_FILES = 10 # MODIFIED
MAX_UPLOAD_MB_PER_FILE = 20 # MODIFIED
# Gmail configuration (visible variable)
GMAIL_USER = os.getenv('GMAIL_USER', 'ProfileDash.NoReply@gmail.com')
SENDER_EMAIL = GMAIL_USER  # used in outgoing email headers
sg = None  # placeholder for legacy parameter (SendGrid removed)

# --- Get Google API Key ---
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') # Fetch the key from environment/secrets
if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY not found. Profile generation will not work.")
# --- END Get Google API Key ---

# ----------------------------------------------------------------------------
# Service Initialization
# ----------------------------------------------------------------------------
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
    # For API key and SendGrid key loading
    from dotenv import load_dotenv
    load_dotenv() # Load .env file for local development

    # --- Google AI Setup (will be configured dynamically per request) ---
    # No global genai.configure() here anymore

except ImportError as e:
    print(f"Error importing ProfileDash modules: {e}")
    print("Please ensure app.py is in the root directory and the 'src' directory with all modules exists.")
    raise
except Exception as general_e:
    print(f"An unexpected error occurred during setup: {general_e}")
    traceback.print_exc()
    raise

# ----------------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------------
def get_permitted_users():
    """
    Retrieves and validates the list of permitted users from the Hugging Face dataset.
    """
    fallback_config = {"allowed_domains": [], "allowed_emails": []}
    
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print("WARNING: Cannot fetch permitted users config. HF credentials missing. Using empty permissions fallback.")
        return fallback_config

    try:
        print(f"Attempting to download {PERMITTED_USERS_FILE} from {DATASET_REPO_ID}")
        downloaded_path = api.hf_hub_download(
            repo_id=DATASET_REPO_ID,
            filename=PERMITTED_USERS_FILE,
            repo_type="dataset",
            token=HF_TOKEN,
            force_download=True,
            resume_download=False,
        )
        
        if downloaded_path and os.path.exists(downloaded_path):
             with open(downloaded_path, 'r', encoding='utf-8') as f:
                 permitted_data = json.load(f)
             print("Permitted users config loaded successfully from dataset.")
             
             valid_structure = isinstance(permitted_data, dict) and \
                               isinstance(permitted_data.get("allowed_domains"), list) and \
                               isinstance(permitted_data.get("allowed_emails"), list)
             
             if not valid_structure:
                  print(f"WARNING: {PERMITTED_USERS_FILE} has incorrect structure. Using code default: {fallback_config}")
                  return fallback_config
             
             return {
                 "allowed_domains": [domain.lower() for domain in permitted_data["allowed_domains"]],
                 "allowed_emails": [email.lower() for email in permitted_data["allowed_emails"]]
             }
        else:
            print(f"Warning: {PERMITTED_USERS_FILE} not found or empty path returned from download. Using code default: {fallback_config}")
            return fallback_config

    except json.JSONDecodeError as json_err:
         print(f"ERROR parsing {PERMITTED_USERS_FILE}: {json_err}. Using code default: {fallback_config}")
         return fallback_config
    except Exception as e:
        print(f"ERROR downloading or processing {PERMITTED_USERS_FILE}: {e}")
        print(f"Using code default due to error: {fallback_config}")
        return fallback_config


def verify_email_and_check_key(email, email_state, is_authenticated):
    """
    Validates user email and API key configuration for authentication.
    """
    if not email or '@' not in email:
        return "Please enter a valid email address.", email, False, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

    print(f"Checking permissions for email: {email}")
    email_lower = email.lower()
    is_permitted = False
    permitted_users_config = get_permitted_users()

    if email_lower in permitted_users_config.get("allowed_emails", []):
        is_permitted = True
        print(f"Email {email} permitted via allowed_emails list.")
    else:
        try:
            domain = email_lower.split('@')[1]
            if domain in permitted_users_config.get("allowed_domains", []):
                is_permitted = True
                print(f"Email {email} permitted via allowed_domains list ({domain}).")
        except IndexError:
             print(f"Invalid email format encountered during domain check: {email}")
             is_permitted = False
    
    if not is_permitted:
         print(f"Access denied for email: {email}")
         try:
            log_event = {"event": "AuthAttemptDenied", "reason": "Email/Domain not permitted", "appVersion": APP_VERSION}
            save_log_entry_hf_dataset(user_email=email, event_data=log_event, api=api, HF_TOKEN=HF_TOKEN, DATASET_REPO_ID=DATASET_REPO_ID)
         except Exception as log_e: print(f"Error logging AuthAttemptDenied: {log_e}")
         return "Access denied. Your email address is not authorized.", email, False, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

    print(f"Email {email} verified and API key found. Authenticating.")
    email_state = email
    is_authenticated = True
    try:
         log_event = {"event": "AuthSuccess", "appVersion": APP_VERSION}
         save_log_entry_hf_dataset(user_email=email, event_data=log_event, api=api, HF_TOKEN=HF_TOKEN, DATASET_REPO_ID=DATASET_REPO_ID)
    except Exception as log_e: print(f"Error logging AuthSuccess: {log_e}")

    return f"Email {email} verified. Proceed to upload documents.", email, is_authenticated, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

def reset_interface():
    """
    Resets the main application interface to its initial state.
    """
    print("Resetting interface elements.")
    return (
        gr.update(value=None, visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
        "",
        gr.update(value=None, visible=False),
        gr.update(visible=False),
        gr.update(visible=False)
    )

def handle_generate_click(file_paths, email_state, is_authenticated):
    """
    Initiates the profile generation process in a background thread.
    """
    if not is_authenticated or not email_state or not file_paths:
         return "Error: Not authenticated or missing uploaded files.", None, None, None, None, None, None, None

    temp_paths_copy = list(file_paths) if isinstance(file_paths, list) else [file_paths]
    # Generate a unique identifier for this run (used in logging and uploads)
    run_id = uuid.uuid4().hex
    print(f"UI Thread: Starting background task for run {run_id} for user {email_state}")

    try:
        thread = threading.Thread(
            target=execute_full_profile_workflow,
            args=(
                run_id,
                email_state,
                GOOGLE_API_KEY,
                temp_paths_copy,
                sg,
                api,
                HF_TOKEN,
                DATASET_REPO_ID,
                SENDER_EMAIL,
                APP_VERSION,
                MAX_WORKERS # MODIFIED: Pass MAX_WORKERS as required by new signature
            ),
            daemon=True
        )
        thread.start()

        try:
            input_filenames = [os.path.basename(fp) for fp in temp_paths_copy if fp]
            first_filename = input_filenames[0] if input_filenames else "Unknown_Company"
            run_company_name = os.path.splitext(first_filename)[0].replace('_', ' ')
            log_event = {"event": "RunSubmitted", "runId": run_id, "companyName": run_company_name, "fileCount": len(input_filenames)}
            save_log_entry_hf_dataset(user_email=email_state, event_data=log_event, api=api, HF_TOKEN=HF_TOKEN, DATASET_REPO_ID=DATASET_REPO_ID)
        except Exception as log_e: print(f"Error logging RunSubmitted: {log_e}")

        status_message = f"Profile generation has started. The final profile will be emailed to {email_state} upon completion (this may take 20-40 minutes depending on document size). You can close this window now."

        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            status_message,
            None,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        )
    except Exception as e:
        print(f"UI Thread: Error starting background thread for run {run_id}: {e}")
        traceback.print_exc()
        error_message = f"Error: Could not start generation process. {e}"
        return (
            gr.update(),
            gr.update(),
            gr.update(visible=False),
            error_message,
            None,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        )

def handle_generate_click_with_status(file_paths, email_state, is_authenticated):
    """
    Enhanced version of handle_generate_click that includes status container management.
    """
    result = handle_generate_click(file_paths, email_state, is_authenticated)
    return [*result, gr.update(visible=True)]

# ----------------------------------------------------------------------------
# Gradio Interface Definition
# ----------------------------------------------------------------------------
with gr.Blocks(theme=gr.themes.Soft()) as demo:

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
    email_state = gr.State("")
    is_authenticated = gr.State(False)
    
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
        auth_status = gr.Markdown("Enter your email address below, then press Verify Email or hit Enter")
        
        with gr.Column(visible=True) as email_input_row:
            email_input = gr.Textbox(
                label="Enter Your Email", 
                placeholder="your.email@domain.com",
                elem_id="email-input"
            )
            verify_email_button = gr.Button(
                "Verify Email",
                variant="primary"
            )
            verify_email_loading = gr.HTML(
                visible=False,
                value='<div class="loading-spinner"></div> Verifying email...',
                elem_id="verify-email-loading"
            )
                
    # --- Main Application Interface ---
    with gr.Column(visible=False, elem_classes="container") as main_app_section:
        gr.Markdown(f"Select up to **{MAX_UPLOAD_FILES} PDF files**. Maximum of **{MAX_UPLOAD_MB_PER_FILE}MB per file**.")
        
        pdf_upload = gr.File(
            label="Upload PDF Documents",
            file_count="multiple",
            file_types=[".pdf"],
            type="filepath"
        )
        
        file_validation = gr.HTML(
            visible=False,
            value='<div class="error-text">Please upload at least one PDF file</div>'
        )
        
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

        generation_inprogress_message = gr.Markdown(
            "**Profile is being generated and will be emailed to you.**",
            visible=False
        )

        with gr.Column(visible=False, elem_id="status-output-container") as status_container:
            gr.Markdown("### Generation Status")
            status_output = gr.Textbox(
                label="Status Log", 
                lines=10, 
                interactive=False, 
                max_lines=15
            )
            download_output = gr.File(
                label="Download Trigger",
                visible=False,
                interactive=False,
                elem_id="download-trigger-file"
            )
            reset_button = gr.Button(
                "Produce New Profile", 
                visible=False, 
                variant="secondary"
            )

    # --- Simplified Event Connections ---

    verify_email_button.click(
        fn=verify_email_and_check_key,
        inputs=[email_input, email_state, is_authenticated],
        outputs=[auth_status, email_state, is_authenticated, auth_section, main_app_section, verify_email_loading]
    )
    email_input.submit(
        fn=verify_email_and_check_key,
        inputs=[email_input, email_state, is_authenticated],
        outputs=[auth_status, email_state, is_authenticated, auth_section, main_app_section, verify_email_loading]
    )

    generate_button.click(
        fn=handle_generate_click_with_status,
        inputs=[pdf_upload, email_state, is_authenticated],
        outputs=[
            pdf_upload,
            generate_row,
            generation_inprogress_message,
            status_output,
            download_output,
            reset_button,
            generate_loading,
            status_container
        ]
    )

    reset_button.click(
        fn=reset_interface,
        inputs=[],
        outputs=[
            pdf_upload,
            generate_row,
            generation_inprogress_message,
            status_output,
            download_output,
            reset_button,
            status_container
        ]
    )


# --- Launch the Gradio app ---
if __name__ == "__main__":
    demo.queue()
    demo.launch(server_name="0.0.0.0",
                server_port=7860)        # what HF expects

# (Email sending now handled via Gmail inside background_processor)
