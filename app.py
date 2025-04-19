import gradio as gr
import time
import os
import traceback # For error logging
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
from datetime import datetime
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
from src.section_definitions import sections
from src.section_processor import generate_initial_section

# --- Configuration & Global Variables ---
APP_VERSION = "v1.0.5"
LOG_FILE = "user_log.json" # Note: This seems unused if logging is only to HF Dataset
DATASET_REPO_ID = "ralfpilarczyk/ProfileDashData"
PERMITTED_USERS_FILE = "permitted_users.json"
HF_TOKEN = os.environ.get("HF_DATA_TOKEN")

# --- Hugging Face API Client Initialization ---
try:
    if HF_TOKEN:
        api = HfApi(token=HF_TOKEN)
        print("Hugging Face API client initialized with token.")
    else:
        api = HfApi()
        print("WARNING: HF_DATA_TOKEN secret not found. Uploads to private dataset will fail.")
except Exception as api_init_e:
    print(f"ERROR initializing HfApi: {api_init_e}")
    api = None

# Basic check for username placeholder and correct dataset name format
if "your-username" in DATASET_REPO_ID or "/" not in DATASET_REPO_ID:
     print(f"CRITICAL WARNING: Check DATASET_REPO_ID variable! Currently: '{DATASET_REPO_ID}'. Ensure username is replaced and format is 'username/Dataset Name'.")

# --- Application Imports ---
try:
    from src.document_processor import load_document_content
    from src.html_generator import generate_full_html_profile
    from src.section_processor import generate_initial_section
    from src.prompts import persona, analysis_specs, json_output_format
    from src.api_client import create_insight_model

    from dotenv import load_dotenv
    load_dotenv() # Load .env file for local development

    # --- SendGrid Setup ---
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content

    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDER_EMAIL = "ProfileDash.NoReply@gmail.com"

    if not SENDGRID_API_KEY:
        print("Warning: SENDGRID_API_KEY not found. Set it in .env or HF Secrets.")
        sg = None
    else:
        try:
            sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
            print("SendGrid client initialized.")
        except Exception as sg_init_e:
            print(f"Error initializing SendGrid client: {sg_init_e}")
            sg = None

    # --- Google AI Setup ---
    # Configured dynamically per request in the background task
    import google.generativeai as genai

except ImportError as e:
    print(f"Error importing ProfileDash modules: {e}")
    print("Please ensure app.py is in the root directory and the 'src' directory with all modules exists.")
    raise
except Exception as general_e:
    print(f"An unexpected error occurred during setup: {general_e}")
    traceback.print_exc()
    raise

# --- Application Settings ---
MAX_WORKERS = 3 # Max concurrent section generation tasks
MAX_UPLOAD_MB = 20 # Max total upload size for PDFs
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_DOMAIN = "sc.com" # Default domain if permitted_users.json fails

# --- Helper Functions ---

def generate_auth_code():
    """Generates a 4-digit authentication code."""
    return str(random.randint(1000, 9999))


def get_permitted_users():
    """
    Downloads and parses the permitted users config from the HF Dataset.
    Returns a dictionary with 'allowed_domains' and 'allowed_emails' lists (lowercase).
    Returns fallback defaults if download/parsing fails or config is invalid.
    """
    fallback_config = {"allowed_domains": [ALLOWED_DOMAIN.lower()], "allowed_emails": []}

    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print(f"WARNING: Cannot fetch permitted users config. HF Token/Repo ID not configured. Using code default: {fallback_config}")
        return fallback_config

    try:
        print(f"Attempting to download {PERMITTED_USERS_FILE} from {DATASET_REPO_ID}")
        downloaded_path = api.hf_hub_download(
            repo_id=DATASET_REPO_ID,
            filename=PERMITTED_USERS_FILE,
            repo_type="dataset",
            token=HF_TOKEN,
            force_download=True, # Always get the latest version
            resume_download=False,
        )

        if downloaded_path and os.path.exists(downloaded_path):
             with open(downloaded_path, 'r', encoding='utf-8') as f:
                 permitted_data = json.load(f)
             print("Permitted users config loaded successfully from dataset.")

             # Validate structure
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
        print(f"Using code default due to error: {fallback_config}")
        return fallback_config

# --- Logging to Hugging Face Dataset ---
def save_log_entry_hf_dataset(user_email: str, event_data: dict):
    """Uploads a structured log entry as a JSON file to the private HF Dataset."""
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print("Log saving skipped: HF Token or Repo ID not configured correctly.")
        return

    timestamp = datetime.now().isoformat()
    log_payload = {"timestamp": timestamp, "user": user_email, **event_data}

    try:
        log_content = json.dumps(log_payload, indent=2)
    except TypeError as json_type_err:
         print(f"ERROR creating log JSON: {json_type_err}. Data: {log_payload}")
         log_payload = {"timestamp": timestamp, "user": user_email, "event": "LoggingError", "error": f"JSON TypeError: {json_type_err}"}
         log_content = json.dumps(log_payload, indent=2)

    sanitized_email = user_email.replace('@', '_at_').replace('.', '_')
    log_filename_in_repo = f"logs/{sanitized_email}/{timestamp}.json"

    try:
        log_bytes = io.BytesIO(log_content.encode('utf-8'))

        print(f"Attempting to upload log to: {DATASET_REPO_ID}/{log_filename_in_repo}")
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
        print(f"ERROR uploading log to HF Dataset '{DATASET_REPO_ID}': {e}")

# --- Background Profile Generation Task ---
def _background_generate_and_notify(run_id: str, user_email: str, api_key: str, temp_file_paths: list):
    """
    Performs the entire profile generation in a background thread,
    saves results to dataset, attempts to email result as Base64 attachment,
    and logs status. Runs independently after being triggered by the UI.
    """
    start_run_time = time.time()
    print(f"BG Run {run_id}: Started for {user_email}")

    # Local helper for logging within this background task
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

    # Initialize status flags and variables
    section_processing_error = False
    error_message_for_email = None
    final_profile_saved_to_dataset = False
    final_profile_repo_path = None
    company_name = "Unknown_Company"
    timestamp_for_filename = time.strftime('%Y%m%d_%H%M%S')
    final_json_profile = None

    try:
        # --- 1. Configure Google AI ---
        append_bg_log("Configuring Google AI SDK...")
        if not api_key:
            raise ValueError("ERROR: API Key was not provided.")
        try:
            genai.configure(api_key=api_key)
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
                executor.submit(generate_initial_section, section, documents_for_api, persona, analysis_specs, json_output_format, insight_model): section
                for section in sections
            }

            append_bg_log(f"Tasks submitted. Waiting for completion...")
            for future in as_completed(future_to_section):
                section_def = future_to_section[future]
                section_num = section_def["number"]; section_title = section_def["title"]
                s_num_result, content_result = section_num, None

                try:
                    s_num_result, content_result = future.result()
                    # Check for error indication within the returned JSON content
                    if not content_result or (isinstance(content_result, dict) and 'error' in content_result):
                        append_bg_log(f"PARTIAL FAIL: Section {s_num_result} ('{section_title}') generation reported error.")
                        section_processing_error = True
                        if not content_result:
                            content_result = {
                                "error": "Generation function returned empty content",
                                "section_num": s_num_result,
                                "section_title": section_title
                            }
                    else:
                        append_bg_log(f"SUCCESS: Section {s_num_result} ('{section_title}') generated.")
                    initial_results[s_num_result] = content_result
                except Exception as e:
                    append_bg_log(f"FAIL: Section {section_num} ('{section_title}') hit exception - {type(e).__name__}: {e}")
                    error_content_json = {
                        "error": f"Generation process failed unexpectedly: {e}",
                        "section_num": section_num,
                        "section_title": section_title
                    }
                    initial_results[section_num] = error_content_json
                    content_result = error_content_json
                    section_processing_error = True

                # Save Section JSON to Dataset
                try:
                    if content_result:
                         save_section_hf_dataset(
                             section_num=s_num_result,
                             section_content=json.dumps(content_result, indent=2),
                             content_type="json",
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

        # --- 4. Aggregate JSON Profile Data ---
        successful_sections_json = {}
        failed_sections_info = {}

        for sec_num, result_obj in initial_results.items():
            # Check if the result is likely a valid JSON object (not an error dict)
            if isinstance(result_obj, dict) and 'error' not in result_obj:
                successful_sections_json[str(sec_num)] = result_obj
            else:
                failed_sections_info[str(sec_num)] = result_obj # Store the error object/info

        # Construct the final JSON structure including metadata
        final_json_profile = {
            "profile_metadata": {
                "run_id": run_id,
                "user_email": user_email,
                "company_name": company_name,
                "generation_timestamp": datetime.now().isoformat(),
                "app_version": APP_VERSION,
                "input_files": [os.path.basename(fp) for fp in temp_file_paths if fp],
                "generation_status": "Completed" if not failed_sections_info else "CompletedWithErrors",
                "failed_sections_count": len(failed_sections_info)
            },
            "sections": successful_sections_json,
            "errors": failed_sections_info
        }

        if final_json_profile:
            append_bg_log("Final JSON profile generated. Saving to dataset...")
            saved_repo_path = save_profile_hf_dataset(
                profile_content=json.dumps(final_json_profile, indent=2),
                content_type="json",
                run_id=run_id,
                company_name=company_name,
                user_email=user_email
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
            append_bg_log("Error: Final JSON profile generation failed or produced empty content.")
            raise ValueError("Final JSON profile generation failed, cannot save profile.")

    except Exception as generation_e:
        # Catch errors from any stage within the main pipeline
        print(f"BG Run {run_id}: CRITICAL ERROR during generation pipeline: {generation_e}")
        traceback.print_exc()
        section_processing_error = True
        error_message_for_email = f"Profile generation failed: {type(generation_e).__name__} - {str(generation_e)}"

        # Log RunFailed event
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
    attachment_object = None # SendGrid attachment object

    # Determine Final Outcome for Email Composition
    generation_succeeded_fully = not error_message_for_email and final_profile_saved_to_dataset
    generation_completed_with_errors = (section_processing_error or not final_profile_saved_to_dataset) and not error_message_for_email
    generation_failed_critically = error_message_for_email is not None

    # Compose Email Content Based on Outcome
    if generation_succeeded_fully:
        status_string = "completed successfully"
        email_subject = f"ProfileDash: Profile for {company_name} is Ready"

        # Prepare the JSON profile as a Base64 encoded attachment
        if final_json_profile and final_profile_repo_path:
            try:
                append_bg_log("Encoding JSON content to Base64 for attachment...")

                json_content = json.dumps(final_json_profile, indent=2)
                encoded_content = base64.b64encode(json_content.encode('utf-8')).decode('ascii')

                append_bg_log("Base64 encoding complete. Creating attachment object...")

                attachment_filename = os.path.basename(final_profile_repo_path)
                if not attachment_filename.lower().endswith('.json'):
                    attachment_filename += ".json"

                attachment_object = Attachment(
                    FileContent(encoded_content),
                    FileName(attachment_filename),
                    FileType('application/json'),
                    Disposition('attachment')
                )
                append_bg_log("Attachment object created successfully.")

                email_html_content = f"""
                <p>Your ProfileDash profile generation for <strong>{company_name}</strong> {status_string}.</p>
                <p>The generated profile is attached to this email as a JSON file.</p>
                <p>(Run ID: {run_id})</p>
                <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
                """
            except Exception as attach_prep_e:
                append_bg_log(f"ERROR preparing Base64 attachment from string: {attach_prep_e}.")
                traceback.print_exc()
                email_html_content = f"""
                <p>Your ProfileDash profile generation for <strong>{company_name}</strong> {status_string}, but there was an error preparing the file for attachment.</p>
                <p>Please try generating the profile again or contact support if the issue persists.</p>
                <p>(Run ID: {run_id})</p>
                <hr><p style='font-size:small; color:grey;'>ProfileDash {APP_VERSION}</p>
                """
        else:
            append_bg_log("Final JSON content or repo path not available, cannot attach. Sending note.")
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

    # Send the Email via SendGrid
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
                response_body_str = str(response.body)[:1000] # Limit body length for logging
                append_bg_log(f"Failed to send notification email to {user_email}. Status: {response.status_code} Body: {response_body_str}")
                email_log_status = "Failure"
                status_code = response.status_code

            if generation_succeeded_fully: email_outcome = "Completed"
            elif generation_completed_with_errors: email_outcome = "CompletedWithErrors"
            else: email_outcome = "Failed"

            # Log email send attempt outcome
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

# --- Hugging Face Dataset Saving Functions ---

def save_section_hf_dataset(section_num: int, section_content: str, content_type: str, run_id: str, company_name: str, user_email: str):
    """Uploads an individual generated section's content to the private HF Dataset."""
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print(f"Section {section_num} saving skipped: HF Token/Repo ID not configured.")
        return False

    # Sanitize names for use in file paths
    safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
    sanitized_email = user_email.replace('@', '_at_').replace('.', '_')

    file_extension = "html" if content_type == "html" else "json"

    # Define path within the dataset repo using the run_id
    section_filename_in_repo = f"profiles/{sanitized_email}/{run_id}/section_{section_num}.{file_extension}"

    try:
        section_bytes = io.BytesIO(section_content.encode('utf-8'))

        print(f"Attempting to upload section {section_num} to: {DATASET_REPO_ID}/{section_filename_in_repo}")
        upload_file(
            path_or_fileobj=section_bytes,
            path_in_repo=section_filename_in_repo,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=HF_TOKEN,
            commit_message=f"Add section {section_num} ({content_type}): {safe_company_name} for {user_email} (Run: {run_id[:8]})"
        )
        print(f"Successfully uploaded section {section_num}: {section_filename_in_repo}")
        return True

    except Exception as e:
        print(f"ERROR uploading section {section_num} to HF Dataset '{DATASET_REPO_ID}': {e}")
        return False

def save_profile_hf_dataset(profile_content: str, content_type: str, run_id: str, company_name: str, user_email: str):
    """Uploads the final aggregated profile (HTML or JSON string) to the private HF Dataset."""
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print(f"Final profile saving skipped for run {run_id}: HF Token/Repo ID not configured.")
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
    sanitized_email = user_email.replace('@', '_at_').replace('.', '_')

    file_extension = "html" if content_type == "html" else "json"

    # Define path within the specific run's directory
    profile_filename_in_repo = f"profiles/{sanitized_email}/{run_id}/final_profile_{timestamp}.{file_extension}"

    try:
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
        return None

# --- Authentication Flow Functions ---

def send_auth_code(email, auth_state):
    """
    Validates email against permitted list from dataset, sends code via SendGrid,
    logs events, and updates state.
    """
    # Basic Email Format Check
    if not email or '@' not in email:
        return "Please enter a valid email address.", auth_state, gr.update(visible=True), gr.update(visible=False)

    # Check Permission using Dataset File
    print(f"Checking permissions for email: {email}")
    email_lower = email.lower()
    is_permitted = False

    permitted_users_config = get_permitted_users()

    if permitted_users_config:
        allowed_emails = permitted_users_config.get("allowed_emails", [])
        allowed_domains = permitted_users_config.get("allowed_domains", [])

        if email_lower in allowed_emails:
            is_permitted = True
            print(f"Email {email} permitted via allowed_emails list.")
        else:
            try:
                domain = email_lower.split('@')[1]
                if domain in allowed_domains:
                    is_permitted = True
                    print(f"Email {email} permitted via allowed_domains list ({domain}).")
            except IndexError:
                print(f"Invalid email format encountered during domain check: {email}")
                is_permitted = False
    else:
        print("CRITICAL ERROR: Could not retrieve or determine permitted users configuration.")
        return "Error checking permissions. Please try again later.", auth_state, gr.update(visible=True), gr.update(visible=False)

    # Deny access if not permitted
    if not is_permitted:
         print(f"Access denied for email: {email}")
         try:
            log_event = {
                "event": "AuthAttemptDenied",
                "reason": "Email/Domain not permitted",
                "appVersion": APP_VERSION
                }
            save_log_entry_hf_dataset(user_email=email, event_data=log_event)
         except Exception as log_denial_e:
             print(f"Error logging AuthAttemptDenied: {log_denial_e}")

         return "Access denied. Your email address is not authorized for this application.", auth_state, gr.update(visible=True), gr.update(visible=False)

    # Check SendGrid Config (if permitted)
    print(f"Email {email} is permitted. Checking SendGrid config...")
    if not SENDGRID_API_KEY or not sg:
        print("Warning: SendGrid not configured or failed to initialize. Using dummy code '1234'.")
        code = "1234"
        auth_state["email"] = email
        auth_state["code"] = code
        auth_state["code_sent"] = True # Mark as sent for testing flow
        try:
             log_event = {"event": "AuthCodeDummyUsed", "reason": "SendGrid not configured"}
             save_log_entry_hf_dataset(user_email=email, event_data=log_event)
        except Exception as log_dummy_e: print(f"Error logging AuthCodeDummyUsed: {log_dummy_e}")
        return "SendGrid not configured. For testing, use code 1234.", auth_state, gr.update(visible=False), gr.update(visible=True)

    # Generate and Prepare Email (if SendGrid OK)
    print(f"Generating auth code for {email}...")
    code = generate_auth_code()
    auth_state["email"] = email
    auth_state["code"] = code
    auth_state["code_sent"] = False

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

    # Attempt to Send Email & Log Outcome
    try:
        print(f"Attempting to send auth code email via SendGrid to {email}...")
        response = sg.client.mail.send.post(request_body=user_message.get())

        if 200 <= response.status_code < 300:
            print(f"Auth code sent successfully to {email}. Status: {response.status_code}")
            auth_state["code_sent"] = True
            try:
                log_event = {
                    "event": "AuthCodeSent", "status": "Success", "appVersion": APP_VERSION
                }
                save_log_entry_hf_dataset(user_email=email, event_data=log_event)
            except Exception as dataset_log_e:
                print(f"Non-critical error logging AuthCodeSent success to dataset: {dataset_log_e}")
            return f"Authentication code sent to {email}. Enter code below and press Verify Code.", auth_state, gr.update(visible=False), gr.update(visible=True)

        else:
            print(f"Failed to send auth code to {email}. Status: {response.status_code}, Body: {response.body}")
            try:
                log_event = {
                    "event": "AuthCodeSendFailed", "status": "Failure",
                    "statusCode": response.status_code,
                    "responseBody": str(response.body)[:500], # Limit logged body size
                    "appVersion": APP_VERSION
                }
                save_log_entry_hf_dataset(user_email=email, event_data=log_event)
            except Exception as dataset_log_e:
                print(f"Non-critical error logging AuthCodeSendFailed to dataset: {dataset_log_e}")
            return f"Error sending authentication code (Status: {response.status_code}). Try again later or contact support.", auth_state, gr.update(visible=True), gr.update(visible=False)

    except Exception as e:
        print(f"Exception sending email to {email}: {e}")
        traceback.print_exc()
        try:
            log_event = {
                "event": "AuthCodeSendException", "status": "Exception",
                "errorType": type(e).__name__, "errorMessage": str(e),
                "appVersion": APP_VERSION
            }
            save_log_entry_hf_dataset(user_email=email, event_data=log_event)
        except Exception as dataset_log_e:
            print(f"Non-critical error logging AuthCodeSendException to dataset: {dataset_log_e}")
        return f"An error occurred while attempting to send the authentication email: {e}. Please try again.", auth_state, gr.update(visible=True), gr.update(visible=False)

def verify_auth_code(entered_code, auth_state):
    """Verifies the entered code against the stored code."""
    print(f"Verifying code. Current auth_state: {auth_state}")
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
    print(f"API Key set. Current auth_state: {auth_state}")
    return "API Key accepted. Upload documents to generate profile.", auth_state, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

# --- UI Interaction Functions ---
def reset_interface():
    """Resets the main app interface components for a new profile generation."""
    print("Resetting interface elements.")
    return (
        None, # pdf_upload
        "",   # status_output
        gr.update(value=None, visible=False), # download_output
        gr.update(visible=False) # reset_button
    )

def handle_generate_click(file_paths, auth_state):
    """Starts the background generation thread and returns immediate feedback."""
    user_email = auth_state.get('email')
    api_key = auth_state.get('api_key')
    run_id = str(uuid.uuid4())

    if not user_email or not api_key or not file_paths:
         return "Error: Missing email, API key, or uploaded files.", None, gr.update(visible=False)

    temp_paths_copy = list(file_paths) if isinstance(file_paths, list) else [file_paths]

    print(f"UI Thread: Starting background task for run {run_id} for user {user_email}")
    try:
        # Create and start the background thread
        thread = threading.Thread(
            target=_background_generate_and_notify,
            args=(run_id, user_email, api_key, temp_paths_copy),
            daemon=True # Allows main program to exit even if thread is running
        )
        thread.start()

        # Log RunSubmitted event
        try:
            input_file_metadata = [{"name": os.path.basename(fp) if fp else "None"} for fp in temp_paths_copy]
            first_valid_filename = next((meta['name'] for meta in input_file_metadata if meta['name'] != "None"), "Unknown_Company")
            run_company_name = os.path.splitext(first_valid_filename)[0].replace('_', ' ')
            log_event = {"event": "RunSubmitted", "runId": run_id, "companyName": run_company_name}
            save_log_entry_hf_dataset(user_email=user_email, event_data=log_event)
        except Exception as log_submit_e: print(f"Error logging RunSubmitted: {log_submit_e}")

        # Return immediate feedback to the user in the UI
        status_message = f"Profile generation for run ID '{run_id[:8]}' started. You will receive an email at {user_email} upon completion (approx. 10-20 mins)."
        return status_message, None, gr.update(visible=False)

    except Exception as thread_e:
        print(f"UI Thread: Error starting background thread for run {run_id}: {thread_e}")
        traceback.print_exc()
        return f"Error: Could not start generation process. {thread_e}", None, gr.update(visible=False)


# --- Gradio Interface Definition ---
with gr.Blocks(theme=gr.themes.Soft(), css="""
    .gradio-container {
        max-width: 600px !important; /* Adjusted width */
        margin-left: auto;
        margin-right: auto;
    }
    /* Theme overrides (Blue instead of default purple) */
    [data-testid="block-title"] { color: #2c7fb8 !important; }
    .dark [data-testid="block-title"] { color: #5aaaff !important; }
    .gradio-button.primary { background-color: #2c7fb8 !important; }
    .dark .gradio-button.primary { background-color: #5aaaff !important; }
    .gr-panel.gr-panel--highlight { background-color: rgba(44, 127, 184, 0.1) !important; }
    .dark .gr-panel.gr-panel--highlight { background-color: rgba(90, 170, 255, 0.1) !important; }
    .gradio-textbox textarea, .gradio-textbox input { width: 100% !important; }
""") as demo:

    # --- State Variable ---
    # Stores user session data (email, authentication status, API key)
    auth_state = gr.State({
        "email": None, "code": None, "code_sent": False,
        "authenticated": False, "api_key": None, "api_key_set": False
    })

    # --- UI Section: Introduction ---
    with gr.Column(visible=True) as intro_section:
        gr.Markdown(f"""
        # **ProfileDash**
        {APP_VERSION}

        By Ralf Pilarczyk

        Generates company profiles by analyzing uploaded PDFs using Google Gemini.

        Disclaimer: Use is at your own risk. Outputs may contain inaccuracies.

        **2-Step Authentication:** Enter your company email, then Google AI API Key.
        """)

    # --- UI Section: Authentication ---
    with gr.Column(visible=True) as auth_section:
        auth_status = gr.Textbox(label="Authentication Status", value="Enter your email address below, then press Send Code", interactive=False)
        with gr.Column(visible=True) as email_input_row:
            email_input = gr.Textbox(label="Enter Your Email", placeholder=f"your.email@domain.com")
            send_code_button = gr.Button("Send Code")
        with gr.Column(visible=False) as code_input_row:
            code_input = gr.Textbox(label="Enter 4-Digit Code")
            verify_code_button = gr.Button("Verify Code")

    # --- UI Section: API Key Input ---
    with gr.Column(visible=False) as api_key_section:
        gr.Markdown("### Enter Your Google AI API Key")
        api_key_input = gr.Textbox(label="API Key", type="password", placeholder="Paste key here")
        gr.Markdown("""Get key from Google AI Studio:(https://aistudio.google.com/) (login via your Gmail account) ("Get API key") (Copy & paste).""")
        submit_api_key_button = gr.Button("Submit API Key")

    # --- UI Section: Main Application ---
    with gr.Column(visible=False) as main_app_section:
        gr.Markdown("# ProfileDash")
        gr.Markdown(f"Version {APP_VERSION}")
        gr.Markdown("Upload PDF documents. Generation takes ~10 mins. Keep device awake and this tab active.")
        gr.Markdown(f"Max upload size: {MAX_UPLOAD_MB} MB. Desktop: Ctrl/Cmd+Click for multiple files.")
        gr.Markdown("Once profile is generated, download the file from your browser download folder (sent via email).")

        with gr.Row():
            pdf_upload = gr.File(
                label="Upload PDF Documents",
                file_count="multiple",
                file_types=[".pdf"],
                type="filepath" # Passes file paths to backend
            )
            with gr.Column(scale=2):
                status_output = gr.Textbox(label="Status / Log", lines=15, interactive=False, max_lines=20)
                # Hidden File component used internally if needed for triggering downloads (not currently used for direct download)
                download_output = gr.File(
                    label="Download Trigger",
                    visible=False,
                    interactive=False,
                    elem_id="download-trigger-file"
                )
                reset_button = gr.Button("Produce New Profile", visible=False)

        generate_button = gr.Button("Generate Profile", variant="primary")

    # --- Event Handling Logic ---

    # Authentication Flow
    send_code_button.click(fn=send_auth_code, inputs=[email_input, auth_state], outputs=[auth_status, auth_state, email_input_row, code_input_row])
    verify_code_button.click(fn=verify_auth_code, inputs=[code_input, auth_state], outputs=[auth_status, auth_state, auth_section, code_input_row, api_key_section])
    submit_api_key_button.click(fn=handle_api_key, inputs=[api_key_input, auth_state], outputs=[auth_status, auth_state, api_key_section, main_app_section, intro_section])

    # Enter key submission for auth fields
    email_input.submit(fn=send_auth_code, inputs=[email_input, auth_state], outputs=[auth_status, auth_state, email_input_row, code_input_row])
    code_input.submit(fn=verify_auth_code, inputs=[code_input, auth_state], outputs=[auth_status, auth_state, auth_section, code_input_row, api_key_section])
    api_key_input.submit(fn=handle_api_key, inputs=[api_key_input, auth_state], outputs=[auth_status, auth_state, api_key_section, main_app_section, intro_section])

    # Main Action: Generate Profile (triggers background task)
    generate_button.click(
        fn=handle_generate_click,
        inputs=[pdf_upload, auth_state],
        outputs=[status_output, download_output, reset_button], # Update status immediately
        show_progress="hidden" # Progress handled by status updates / email
    )

    # Reset Button
    reset_button.click(
        fn=reset_interface,
        inputs=[],
        outputs=[pdf_upload, status_output, download_output, reset_button]
    )

# --- Application Launch ---
if __name__ == "__main__":
    demo.queue() # Enable queuing for handling multiple users/requests
    demo.launch(share=False, server_name="0.0.0.0") # Run on local network