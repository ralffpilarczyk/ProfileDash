import time
import os
import traceback
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed # Ensure these are imported
import tempfile
from datetime import datetime
from huggingface_hub import upload_file, HfApi # Need HfApi defined or passed
import io
import uuid
import base64
from sendgrid.helpers.mail import (
    Mail, Email, To, Content, Attachment, FileContent, FileName,
    FileType, Disposition
)
import google.generativeai as genai
import sendgrid # Need this to potentially check if sg object is valid

# --- Import necessary functions/variables from OTHER src modules ---
# Use relative imports because this file is inside src
from .document_processor import load_document_content
from .html_generator import generate_full_html_profile
from .section_processor import generate_initial_section
from .section_definitions import sections
from .prompts import persona, analysis_specs, output_format
from .api_client import create_insight_model, create_fact_model # Import both models
# Import the core refinement functions
from .refinement import (
    get_fact_critique,
    fact_improvement_response,
    get_insight_critique,
    insight_improvement_response
)

# --- Moved HF Data Saving Functions ---
# These now explicitly require api, HF_TOKEN, DATASET_REPO_ID to be passed

def save_log_entry_hf_dataset(
    user_email: str,
    event_data: dict,
    api: HfApi, # Expect initialized HfApi client
    HF_TOKEN: str,
    DATASET_REPO_ID: str
):
    """Uploads a structured log entry as a JSON file to the private HF Dataset."""
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print(f"Log saving skipped (called from background_processor): HF Token/Repo ID not configured or passed.")
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
        print(f"HF Saver (background_processor): Attempting to upload log to: {DATASET_REPO_ID}/{log_filename_in_repo}")

        upload_file(
            path_or_fileobj=log_bytes,
            path_in_repo=log_filename_in_repo,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=HF_TOKEN,
            commit_message=f"Add log: {event_data.get('event', 'Unknown Event')} for {user_email}"
        )
        print(f"HF Saver (background_processor): Successfully uploaded log: {log_filename_in_repo}")
    except Exception as e:
        print(f"HF Saver (background_processor) ERROR uploading log to HF Dataset '{DATASET_REPO_ID}': {e}")
        # traceback.print_exc()


def save_section_hf_dataset(
    section_num: int,
    section_content: str,
    content_type: str, # e.g., "html", "html_refined"
    run_id: str,
    company_name: str,
    user_email: str,
    api: HfApi, # Expect initialized HfApi client
    HF_TOKEN: str,
    DATASET_REPO_ID: str,
    filename_suffix: str = "" # <<< ADDED Optional Suffix
):
    """Uploads an individual generated section's content to the private HF Dataset."""
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print(f"Section {section_num}{filename_suffix} saving skipped (called from background_processor): HF Token/Repo ID not configured or passed.")
        return False

    safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
    sanitized_email = user_email.replace('@', '_at_').replace('.', '_')
    file_extension = "html"

    base_filename = f"section_{section_num}{filename_suffix}"
    section_filename_in_repo = f"profiles/{sanitized_email}/{run_id}/{base_filename}.{file_extension}"

    try:
        section_bytes = io.BytesIO(section_content.encode('utf-8'))
        print(f"HF Saver (background_processor): Attempting to upload section {section_num}{filename_suffix} to: {DATASET_REPO_ID}/{section_filename_in_repo}")

        upload_file(
            path_or_fileobj=section_bytes,
            path_in_repo=section_filename_in_repo,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=HF_TOKEN,
            commit_message=f"Add section {section_num} ({content_type}): {safe_company_name} for {user_email} (Run: {run_id[:8]})"
        )
        print(f"HF Saver (background_processor): Successfully uploaded section {section_num}{filename_suffix}: {section_filename_in_repo}")
        return True
    except Exception as e:
        print(f"HF Saver (background_processor) ERROR uploading section {section_num}{filename_suffix} to HF Dataset '{DATASET_REPO_ID}': {e}")
        return False

def save_profile_hf_dataset(
    profile_content: str,
    content_type: str, # e.g., "html", "html_refined"
    run_id: str,
    company_name: str,
    user_email: str,
    api: HfApi, # Expect initialized HfApi client
    HF_TOKEN: str,
    DATASET_REPO_ID: str,
    filename_suffix: str = "" # <<< ADDED Optional Suffix
):
    """Uploads the final aggregated profile (HTML or JSON string) to the private HF Dataset."""
    if not HF_TOKEN or not api or "your-username" in DATASET_REPO_ID:
        print(f"Final profile ({content_type}{filename_suffix}) saving skipped for run {run_id} (called from background_processor): HF Token/Repo ID not configured or passed.")
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
    sanitized_email = user_email.replace('@', '_at_').replace('.', '_')
    file_extension = "html"

    base_filename = f"final_profile_{timestamp}{filename_suffix}"
    profile_filename_in_repo = f"profiles/{sanitized_email}/{run_id}/{base_filename}.{file_extension}"

    try:
        profile_bytes = io.BytesIO(profile_content.encode('utf-8'))
        print(f"HF Saver (background_processor): Attempting to upload final profile ({content_type}) to: {DATASET_REPO_ID}/{profile_filename_in_repo}")

        upload_file(
            path_or_fileobj=profile_bytes,
            path_in_repo=profile_filename_in_repo,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=HF_TOKEN,
            commit_message=f"Add final {content_type.upper()} profile: {safe_company_name} for {user_email} (Run: {run_id[:8]})"
        )
        print(f"HF Saver (background_processor): Successfully uploaded final profile: {profile_filename_in_repo}")
        return profile_filename_in_repo
    except Exception as e:
        print(f"HF Saver (background_processor) ERROR uploading final profile for run {run_id} to HF Dataset '{DATASET_REPO_ID}': {e}")
        return None

# --- Refinement Stage Functions ---

# --- NEW: Helper Function to Refine ONE Section ---
def _refine_single_section(
    section_def, initial_html, documents_for_api, run_id, user_email, company_name,
    hf_api_client, hf_token, dataset_repo_id, append_log_func # Include logger
):
    """Performs the 4-step refinement process for a single section."""
    section_num = section_def["number"]
    section_title = section_def["title"]
    initial_instruction = section_def["specs"]
    section_start_time = time.time()
    step_failed_in_section = False
    last_good_html = initial_html # Start with initial content

    # Log entry for this worker/section
    append_log_func(f"Worker refining Section {section_num} ('{section_title}')...")

    try:
        # --- Fact Refinement ---
        append_log_func(f"S{section_num}: Fact Critique...")
        _, fact_critique_text = get_fact_critique(initial_instruction, last_good_html, documents_for_api)

        append_log_func(f"S{section_num}: Fact Improve...")
        _, fact_improved_html = fact_improvement_response(
            initial_instruction, last_good_html, fact_critique_text, documents_for_api, section_num, section_title
        )
        if not fact_improved_html or '<p class="error">' in fact_improved_html:
             append_log_func(f"S{section_num}: Error during Fact Improvement. Using initial content for insight step.")
             step_failed_in_section = True # Mark error, but continue
        else:
             last_good_html = fact_improved_html # Update last good HTML

        # --- Insight Refinement ---
        append_log_func(f"S{section_num}: Insight Critique...")
        _, insight_critique_text = get_insight_critique(initial_instruction, last_good_html, documents_for_api)

        append_log_func(f"S{section_num}: Insight Improve...")
        _, insight_improved_html = insight_improvement_response(
            initial_instruction, last_good_html, insight_critique_text, documents_for_api, section_num, section_title
        )
        if not insight_improved_html or '<p class="error">' in insight_improved_html:
             append_log_func(f"S{section_num}: Error during Insight Improvement. Using previous step's content.")
             step_failed_in_section = True # Mark error, but continue
        else:
             last_good_html = insight_improved_html # Update last good HTML

    except Exception as section_e:
        # Catch errors from critique/improvement API calls themselves
        error_msg = f"S{section_num} ERROR during refinement API calls: {type(section_e).__name__} - {str(section_e)}"
        append_log_func(error_msg); traceback.print_exc() # Log error from worker
        # Use the last known good HTML and add an error marker
        last_good_html += f'\n<p class="error">Refinement process failed for this section: {type(section_e).__name__}</p>'
        step_failed_in_section = True
        # Log failure for this section to dataset
        try:
            log_event = {"event": "RefinementSectionFailed", "runId": run_id, "section": section_num, "status": "Error", "error": error_msg}
            save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
        except Exception as log_err:
            append_log_func(f"S{section_num}: Error logging section failure: {log_err}")

    # --- Save Refined Section (still within the worker task) ---
    final_refined_html_for_section = last_good_html
    append_log_func(f"S{section_num}: Saving final refined content...")
    save_successful = False # Default to false
    try:
        save_successful = save_section_hf_dataset(
             section_num=section_num, section_content=final_refined_html_for_section, content_type="html_refined",
             run_id=run_id, company_name=company_name, user_email=user_email,
             api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id,
             filename_suffix="_refined"
        )
        if not save_successful: raise Exception("save_section_hf_dataset returned False")
        append_log_func(f"S{section_num}: Refined content saved.")
    except Exception as save_e:
         append_log_func(f"S{section_num}: ERROR saving refined section: {save_e}")
         step_failed_in_section = True # Mark error if saving failed

    section_duration = time.time() - section_start_time
    status_msg = "FAILED" if step_failed_in_section else "OK"
    append_log_func(f"Worker finished Section {section_num} in {section_duration:.1f}s. Status: {status_msg}")

    # Return section number, the resulting HTML, and error status
    return section_num, final_refined_html_for_section, step_failed_in_section


# --- REVISED Refinement Orchestration Function (Parallel) ---
def run_refinement_stage(
    # --- Context Passed from Initial Workflow ---
    run_id: str,
    user_email: str,
    api_key: str,
    company_name: str,
    initial_results: dict,
    documents_for_api: list,
    append_log_func, # Callback for logging
    # --- Clients & Config Passed In ---
    sg_client,
    hf_api_client,
    hf_token: str,
    dataset_repo_id: str,
    sender_email: str,
    app_version: str,
    max_workers: int # <<< ADDED max_workers
    ):
    """
    Orchestrates the refinement process section by section IN PARALLEL
    after initial generation.
    """
    # --- Helper for logging within refinement ---
    def _log_refinement(message):
        append_log_func(f"[Refinement Stage] {message}") # Use the passed logger

    _log_refinement("Starting Refinement Stage...")
    refinement_start_time = time.time()

    # --- Configure Google AI SDK ---
    try:
        genai.configure(api_key=api_key)
        _log_refinement("Google AI SDK configured for refinement.")
    except Exception as config_e:
        error_msg = f"CRITICAL ERROR configuring Google AI SDK for refinement: {type(config_e).__name__} - {str(config_e)}"
        _log_refinement(error_msg)
        log_event = {"event": "RefinementStageFailed", "runId": run_id, "status": "Error", "error": error_msg, "stage": "GenAI Config"}
        save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
        return

    # --- Parallel Refinement Loop ---
    refined_results = {}
    section_processing_error_refinement = False
    total_sections = len(sections)
    processed_count = 0

    _log_refinement(f"Starting parallel refinement with {max_workers} workers...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_section_num = {}
        for section_def in sorted(sections, key=lambda x: x["number"]):
            section_num = section_def["number"]
            initial_html = initial_results.get(section_num)

            # Skip sections that had errors initially
            if not initial_html or '<p class="error">' in initial_html:
                _log_refinement(f"Section {section_num}: Skipping refinement due to missing or error in initial content.")
                refined_results[section_num] = initial_html # Store original error/missing content
                section_processing_error_refinement = True
                processed_count += 1 # Count as processed for progress tracking
                continue

            # Submit the refinement task for this section
            future = executor.submit(
                _refine_single_section, # Call the helper function
                section_def,
                initial_html,
                documents_for_api,
                run_id,
                user_email,
                company_name,
                hf_api_client,
                hf_token,
                dataset_repo_id,
                append_log_func # Pass logger to worker
            )
            future_to_section_num[future] = section_num

        # Process results as they complete
        _log_refinement("Tasks submitted. Waiting for refinement completion...")
        for future in as_completed(future_to_section_num):
            section_num = future_to_section_num[future]
            try:
                s_num_result, refined_html_result, section_had_error = future.result()
                refined_results[s_num_result] = refined_html_result
                if section_had_error:
                    section_processing_error_refinement = True # Mark if any section had an error
                _log_refinement(f"Completed processing for section {s_num_result}.")
            except Exception as exc:
                _log_refinement(f"Section {section_num} refinement generated an exception in future processing: {exc}")
                traceback.print_exc()
                # Store a generic error message if future itself failed
                # Attempt to get title safely
                title = "Unknown Title"
                try: title = sections[section_num-1]["title"]
                except: pass
                refined_results[section_num] = f'<div class="section" id="section-{section_num}"><h2 class="error-header">{section_num}. {title}</h2><p class="error">ERROR: Refinement task failed unexpectedly: {exc}</p></div>'
                section_processing_error_refinement = True

            processed_count += 1
            progress_percent = int((processed_count / total_sections) * 100)
            _log_refinement(f"Overall Refinement Progress: {processed_count}/{total_sections} ({progress_percent}%) sections complete.")


    # --- Aggregation and Final Saving ---
    _log_refinement("Refinement loop completed. Aggregating final refined profile...")
    ordered_refined_contents = []
    for section_def in sorted(sections, key=lambda x: x["number"]):
        content = refined_results.get(section_def["number"], f'<div class="section" id="section-{section_def["number"]}"><h2 class="error-header">{section_def["number"]}. {section_def["title"]}</h2><p class="error">ERROR: Refined content missing during final aggregation.</p></div>')
        ordered_refined_contents.append(str(content))

    final_refined_html = ""
    final_profile_saved_to_dataset = False
    final_profile_repo_path = None
    try:
        final_refined_html = generate_full_html_profile(f"{company_name} (Refined)", sections, ordered_refined_contents, app_version) # Pass app_version
        if final_refined_html:
            _log_refinement("Final refined HTML generated. Saving to dataset...")
            saved_repo_path = save_profile_hf_dataset(
                profile_content=final_refined_html, content_type="html_refined", run_id=run_id, company_name=company_name, user_email=user_email,
                api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id, # Pass context
                filename_suffix="_refined" # Pass suffix
            )
            if saved_repo_path:
                final_profile_saved_to_dataset = True; final_profile_repo_path = saved_repo_path
                _log_refinement(f"Final refined profile saved successfully: {saved_repo_path}")
            else:
                _log_refinement("Warning: Failed to save final refined profile to dataset."); section_processing_error_refinement = True
        else:
            _log_refinement("Error: Final refined HTML generation failed."); section_processing_error_refinement = True
    except Exception as agg_e:
        error_msg = f"ERROR during final refined profile aggregation/saving: {agg_e}"; _log_refinement(error_msg); traceback.print_exc()
        section_processing_error_refinement = True
        log_event = {"event": "RefinementStageFailed", "runId": run_id, "status": "Error", "error": error_msg, "stage": "Aggregation/Save"}
        save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)

    # --- Send Final Refined Email ---
    _log_refinement("Preparing refined profile email notification...")
    email_subject_refined = f"ProfileDash: Refined Profile for {company_name} is Ready"
    email_html_content_refined = ""
    attachment_object_refined = None

    # (Email composition logic based on final_refined_html, final_profile_saved_to_dataset, section_processing_error_refinement - same as before)
    if final_refined_html and final_profile_saved_to_dataset:
        try:
            encoded_content = base64.b64encode(final_refined_html.encode('utf-8')).decode('ascii')
            attachment_filename = os.path.basename(final_profile_repo_path) if final_profile_repo_path else f"{company_name}_refined_profile_{run_id[:8]}.html"
            if not attachment_filename.lower().endswith('.html'): attachment_filename += ".html"
            attachment_object_refined = Attachment(FileContent(encoded_content), FileName(attachment_filename), FileType('text/html'), Disposition('attachment'))
            status_string = "completed successfully"
            if section_processing_error_refinement: status_string = "completed, but some sections may have refinement errors"
            email_html_content_refined = f"""<p>The <strong>refined</strong> ProfileDash profile generation for <strong>{company_name}</strong> {status_string}.</p><p>The refined profile (which includes fact-checking and insight enhancement) is attached to this email.</p>{'<p><i>Note: Some sections might contain errors if the refinement process encountered issues.</i></p>' if section_processing_error_refinement else ''}<p>(Run ID: {run_id})</p><hr><p style='font-size:small; color:grey;'>ProfileDash {app_version}</p>"""
        except Exception as attach_prep_e:
            _log_refinement(f"ERROR preparing refined Base64 attachment: {attach_prep_e}."); traceback.print_exc()
            email_subject_refined = f"ProfileDash: Refined Profile Generation Complete (Attachment Error) for {company_name}"
            email_html_content_refined = f"""<p>The refined ProfileDash profile generation for <strong>{company_name}</strong> completed, but there was an error preparing the refined file for attachment.</p><p>The initial profile was sent previously. You may need to check the logs or saved files directly for the refined version.</p><p>(Run ID: {run_id})</p><hr><p style='font-size:small; color:grey;'>ProfileDash {app_version}</p>"""
            attachment_object_refined = None
    elif section_processing_error_refinement:
        email_subject_refined = f"ProfileDash: Refined Profile Generation Completed (with errors) for {company_name}"
        email_html_content_refined = f"""<p>The refined ProfileDash profile generation for <strong>{company_name}</strong> completed with some errors during the refinement or saving stage.</p><p>An attempt was made to attach the refined profile, but it may be incomplete or contain errors.</p><p>The initial profile was sent previously. Please check the logs or saved files if needed.</p><p>(Run ID: {run_id})</p><hr><p style='font-size:small; color:grey;'>ProfileDash {app_version}</p>"""
        if final_refined_html:
             try:
                 encoded_content = base64.b64encode(final_refined_html.encode('utf-8')).decode('ascii')
                 attachment_filename = f"{company_name}_refined_profile_partial_{run_id[:8]}.html"
                 attachment_object_refined = Attachment(FileContent(encoded_content), FileName(attachment_filename), FileType('text/html'), Disposition('attachment'))
             except Exception as attach_err: _log_refinement(f"Could not attach partially refined HTML: {attach_err}")
    else:
         email_subject_refined = f"ProfileDash: Refined Profile Generation Failed for {company_name}"
         email_html_content_refined = f"""<p>Unfortunately, the refinement stage for the ProfileDash profile for <strong>{company_name}</strong> failed critically during final aggregation or generation.</p><p>The initial profile was sent previously. No refined profile could be generated or attached.</p><p>Please check the logs for details.</p><p>(Run ID: {run_id})</p><hr><p style='font-size:small; color:grey;'>ProfileDash {app_version}</p>"""

    # (Email sending logic - same as before)
    if sg_client:
        try:
            message = Mail(from_email=Email(sender_email, "ProfileDash Notification (Refined)"), to_emails=To(user_email), subject=email_subject_refined, html_content=Content("text/html", email_html_content_refined))
            if attachment_object_refined: message.attachment = attachment_object_refined; _log_refinement("Refined Attachment added to email message.")
            response = sg_client.client.mail.send.post(request_body=message.get())
            email_log_status = "Success" if 200 <= response.status_code < 300 else "Failure"
            _log_refinement(f"Refined notification email send status: {email_log_status}")
            log_event = {"event": "RefinedNotificationEmailSent", "runId": run_id, "status": email_log_status, "outcome": "Completed" if final_profile_saved_to_dataset else "CompletedWithErrors" if section_processing_error_refinement else "Failed"}
            if email_log_status == "Failure": log_event["sendgridResponseStatus"] = response.status_code; log_event["sendgridResponseBody"] = str(response.body)[:1000]
            save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
        except Exception as email_ex:
             _log_refinement(f"Exception sending refined notification email: {email_ex}"); traceback.print_exc()
             log_event = {"event": "RefinedNotificationEmailSent", "runId": run_id, "status": "Exception", "error": str(email_ex)}
             save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
    else: _log_refinement("SendGrid client not available. Cannot send refined email notification.")

    # --- Log Refinement Completion ---
    refinement_duration = time.time() - refinement_start_time
    _log_refinement(f"Refinement Stage finished in {refinement_duration / 60:.1f} minutes.")
    final_status = "Success" if final_profile_saved_to_dataset else "CompletedWithErrors" if section_processing_error_refinement else "Failed"
    log_event = {"event": "RefinementStageCompleted", "runId": run_id, "status": final_status, "durationSeconds": int(refinement_duration)}
    save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)


# --- Main Background Workflow Function ---
# This is the function that app.py will import and run in a thread

def execute_full_profile_workflow(
    # --- Original args from app.py ---
    run_id: str,
    user_email: str,
    api_key: str,
    temp_file_paths: list,
    # --- Dependencies passed from app.py ---
    sg_client,
    hf_api_client,
    hf_token: str,
    dataset_repo_id: str,
    sender_email: str,
    app_version: str,
    max_workers: int,
    max_upload_bytes: int
    ):
    """
    Performs the initial profile generation, emails result, THEN triggers refinement stage.
    This is the main entry point called by app.py's thread.
    """
    start_run_time = time.time()
    print(f"BG Processor: Run {run_id}: Started for {user_email}")

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
        print(f"BG Processor: Run {run_id}: {timestamped_message}")
    # --- End of Local Helper ---

    # Initialize status flags and variables
    initial_section_processing_error = False
    initial_error_message_for_email = None
    initial_profile_saved_to_dataset = False
    initial_profile_repo_path = None
    company_name = "Unknown_Company"
    initial_final_html = ""
    documents_for_api = []
    initial_results = {}

    try:
        # --- 1. Configure Google AI ---
        append_bg_log("Configuring Google AI SDK...")
        if not api_key: raise ValueError("ERROR: API Key was not provided.")
        try:
            genai.configure(api_key=api_key); append_bg_log("Google AI SDK Configured OK.")
        except Exception as config_e: raise RuntimeError(f"CRITICAL ERROR configuring Google AI SDK: {config_e}") from config_e

        # --- 2. Process Uploaded Documents ---
        append_bg_log("Processing uploaded documents...")
        if not temp_file_paths: raise ValueError("No file paths provided.")
        if not isinstance(temp_file_paths, list): temp_file_paths = [temp_file_paths]
        uploaded_data = {}; total_size = 0; valid_files_count = 0
        for file_path in temp_file_paths:
            if file_path is None: continue
            filename = os.path.basename(file_path)
            try:
                if not os.path.exists(file_path): continue
                if not filename.lower().endswith(".pdf"): continue
                file_size = os.path.getsize(file_path);
                if file_size == 0: continue
                total_size += file_size
                with open(file_path, 'rb') as f: uploaded_data[filename] = f.read()
                valid_files_count += 1; append_bg_log(f"Read: {filename} ({file_size // 1024} KB)")
            except Exception as read_err: append_bg_log(f"Error reading '{filename}': {read_err}"); continue
        if not uploaded_data: raise ValueError("No valid PDF files processed.")
        if total_size > max_upload_bytes: raise ValueError(f"Upload failed: Size ({total_size / (1024*1024):.2f} MB) exceeds {max_upload_bytes / (1024*1024):.0f} MB.")
        append_bg_log(f"Encoding {valid_files_count} files for API (base64)...")
        documents_for_api = load_document_content(uploaded_data)
        if not documents_for_api: raise ValueError("Failed to process documents (base64).")
        first_filename = next(iter(uploaded_data.keys())); company_name = os.path.splitext(first_filename)[0].replace('_', ' ')
        append_bg_log(f"Company: {company_name}. Starting parallel generation...")


        # --- 3. Generate Sections in Parallel (Initial Pass) ---
        append_bg_log(f"Creating Gemini model instance...")
        insight_model = create_insight_model()
        if not insight_model: raise RuntimeError("Failed to create insight model.")
        append_bg_log(f"Model instance created. Submitting initial tasks with {max_workers} workers...")
        total_sections = len(sections); completed_sections_count = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_section = { executor.submit(generate_initial_section, section, documents_for_api, persona, analysis_specs, output_format, insight_model): section for section in sections }
            append_bg_log(f"Initial tasks submitted. Waiting for completion...")
            for future in as_completed(future_to_section):
                section_def = future_to_section[future]; section_num = section_def["number"]; section_title = section_def["title"]
                s_num_result, content_result = section_num, None
                try:
                    s_num_result, content_result = future.result()
                    if not content_result or '<p class="error">' in str(content_result):
                        append_bg_log(f"PARTIAL FAIL: Section {s_num_result} ('{section_title}') initial generation reported error.")
                        initial_section_processing_error = True
                        if not content_result: content_result = f'<div class="section" id="section-{s_num_result}"><h2>{s_num_result}. {section_title}</h2><p class="error">ERROR: Generation function returned empty content.</p></div>'
                    else: append_bg_log(f"SUCCESS: Section {s_num_result} ('{section_title}') initial generation.")
                    initial_results[section_num] = content_result
                except Exception as e:
                    append_bg_log(f"FAIL: Section {section_num} ('{section_title}') initial generation hit exception - {type(e).__name__}: {e}")
                    error_content_html = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Generation process failed unexpectedly: {e}</p></div>'
                    initial_results[section_num] = error_content_html; content_result = error_content_html; initial_section_processing_error = True
                try: # Save Initial Section
                    if content_result:
                         save_section_hf_dataset(section_num=s_num_result, section_content=str(content_result), content_type="html", run_id=run_id, company_name=company_name, user_email=user_email, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
                    else: append_bg_log(f"Warning: Skipping dataset save for empty initial section {s_num_result}")
                except Exception as section_save_e: append_bg_log(f"Non-critical error during initial save attempt for section {s_num_result}: {section_save_e}")
                completed_sections_count += 1; progress_percent = int((completed_sections_count / total_sections) * 100); append_bg_log(f"Initial Progress: {completed_sections_count}/{total_sections} ({progress_percent}%) sections processed.")
        append_bg_log("All initial sections processed. Aggregating initial profile...")

        # --- 4. Aggregate and Save Initial Profile ---
        ordered_initial_contents = []
        for section_def in sorted(sections, key=lambda x: x["number"]):
            content = initial_results.get(section_def["number"], f'<div class="section" id="section-{section_def["number"]}"><h2>{section_def["number"]}. {section_def["title"]}</h2><p class="error">ERROR: Content missing during initial aggregation.</p></div>')
            ordered_initial_contents.append(str(content))
        initial_final_html = generate_full_html_profile(company_name, sections, ordered_initial_contents, app_version)
        if initial_final_html and isinstance(initial_final_html, str):
            append_bg_log("Initial HTML generated. Saving to dataset...")
            saved_repo_path = save_profile_hf_dataset(profile_content=initial_final_html, content_type="html", run_id=run_id, company_name=company_name, user_email=user_email, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
            if saved_repo_path: initial_profile_saved_to_dataset = True; initial_profile_repo_path = saved_repo_path; append_bg_log(f"Initial profile saved successfully to dataset: {saved_repo_path}")
            else: append_bg_log("Warning: Failed to save initial profile to dataset."); initial_profile_saved_to_dataset = False; initial_section_processing_error = True
        else: append_bg_log("Error: Initial HTML generation failed or produced empty content."); raise ValueError("Initial HTML generation failed.")


    except Exception as generation_e:
        print(f"BG Processor: Run {run_id}: CRITICAL ERROR during initial generation pipeline: {generation_e}"); traceback.print_exc()
        initial_section_processing_error = True; initial_error_message_for_email = f"Profile generation failed: {type(generation_e).__name__} - {str(generation_e)}"
        try:
            log_event = {"event": "RunFailed", "runId": run_id, "status": "Exception", "errorStage": "InitialGenerationPipeline", "errorType": type(generation_e).__name__, "errorMessage": str(generation_e)}
            save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
        except Exception as log_fail_e: print(f"Error logging RunFailed after main exception: {log_fail_e}")


    # --- 5. Send INITIAL Email Notification ---
    append_bg_log("Preparing INITIAL email notification...")
    # (Initial email composition and sending logic - same as previous version)
    email_subject_initial = ""; email_html_content_initial = ""; attachment_object_initial = None
    initial_generation_succeeded_fully = not initial_error_message_for_email and initial_profile_saved_to_dataset
    initial_generation_completed_with_errors = (initial_section_processing_error or not initial_profile_saved_to_dataset) and not initial_error_message_for_email
    initial_generation_failed_critically = initial_error_message_for_email is not None

    if initial_generation_succeeded_fully or initial_generation_completed_with_errors:
        status_string = "completed successfully" if initial_generation_succeeded_fully else "completed with some errors"
        email_subject_initial = f"ProfileDash: Initial Profile for {company_name} is Ready"
        if initial_generation_completed_with_errors: email_subject_initial = f"ProfileDash: Initial Profile for {company_name} Completed (with errors)"
        if initial_final_html and initial_profile_repo_path:
            try: # Try attach
                encoded_content = base64.b64encode(initial_final_html.encode('utf-8')).decode('ascii')
                attachment_filename = os.path.basename(initial_profile_repo_path);
                if not attachment_filename.lower().endswith('.html'): attachment_filename += ".html"
                attachment_object_initial = Attachment(FileContent(encoded_content), FileName(attachment_filename), FileType('text/html'), Disposition('attachment'))
                email_html_content_initial = f"""<p>Your <strong>initial</strong> ProfileDash profile generation for <strong>{company_name}</strong> {status_string}.</p><p>The initially generated profile is attached.</p>{'<p><i>Note: Some sections might contain errors.</i></p>' if initial_generation_completed_with_errors else ''}<p>A refined version is being generated and will be sent separately (approx. 30-60 mins).</p><p>(Run ID: {run_id})</p><hr><p style='font-size:small; color:grey;'>ProfileDash {app_version}</p>""" # Adjusted time estimate
            except Exception as attach_prep_e:
                 append_bg_log(f"ERROR preparing initial Base64 attachment: {attach_prep_e}.")
                 attachment_object_initial = None
                 email_html_content_initial = f"""<p>Your <strong>initial</strong> ProfileDash profile generation for <strong>{company_name}</strong> {status_string}, but attachment failed.</p><p>A refined version is being generated and will be sent separately (approx. 30-60 mins).</p><p>(Run ID: {run_id})</p><hr><p style='font-size:small; color:grey;'>ProfileDash {app_version}</p>""" # Adjusted time estimate
        else:
            email_html_content_initial = f"""<p>Your <strong>initial</strong> ProfileDash profile generation for <strong>{company_name}</strong> {status_string}, but the final profile could not be generated/saved for attachment.</p><p>A refined version is being generated and will be sent separately (approx. 30-60 mins).</p><p>(Run ID: {run_id})</p><hr><p style='font-size:small; color:grey;'>ProfileDash {app_version}</p>""" # Adjusted time estimate
        log_event_status = "Success" if initial_generation_succeeded_fully else "CompletedWithErrors"
        try: # Log completion
            log_event = {"event": "RunCompleted", "runId": run_id, "status": log_event_status, "stage": "Initial", "finalProfileSaved": initial_profile_saved_to_dataset, "sectionProcessingErrorEncountered": initial_section_processing_error}
            save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
        except Exception as log_complete_e: print(f"Error logging RunCompleted ({log_event_status}) initial: {log_complete_e}")
    else: # Failed critically
        email_subject_initial = f"ProfileDash: Profile Generation Failed for {company_name}"
        error_details = initial_error_message_for_email if initial_error_message_for_email else 'An unspecified critical error occurred during initial generation.'
        email_html_content_initial = f"""<p>Unfortunately, the initial ProfileDash profile generation for <strong>{company_name}</strong> failed critically.</p><p>Error details: {error_details}</p><p>No initial profile could be generated. Refinement stage will not run.</p><p>(Run ID: {run_id})</p><hr><p style='font-size:small; color:grey;'>ProfileDash {app_version}</p>"""

    # Send Initial Email
    if sg_client:
        try:
            message = Mail(from_email=Email(sender_email, "ProfileDash Notification (Initial)"), to_emails=To(user_email), subject=email_subject_initial, html_content=Content("text/html", email_html_content_initial))
            if attachment_object_initial: message.attachment = attachment_object_initial; append_bg_log("Initial Attachment added to email message.")
            response = sg_client.client.mail.send.post(request_body=message.get())
            email_log_status_initial = "Success" if 200 <= response.status_code < 300 else "Failure"
            append_bg_log(f"Initial notification email send status: {email_log_status_initial}")
            try: # Log email send attempt
                log_event = {"event": "InitialNotificationEmailSent", "runId": run_id, "status": email_log_status_initial}
                if email_log_status_initial == "Failure": log_event["sendgridResponseStatus"] = response.status_code; log_event["sendgridResponseBody"] = str(response.body)[:1000]
                save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
            except Exception as log_email_e: print(f"Error logging InitialNotificationEmailSent status: {log_email_e}")
        except Exception as email_ex:
             append_bg_log(f"Exception sending initial notification email: {email_ex}"); traceback.print_exc()
             try: # Log email exception
                 log_event = {"event": "InitialNotificationEmailSent", "runId": run_id, "status": "Exception", "error": str(email_ex)}
                 save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
             except Exception as log_email_e: print(f"Error logging Initial EmailSent exception: {log_email_e}")
    else: append_bg_log("SendGrid client not available. Cannot send initial email notification.")


    # --- *** CALL REFINEMENT STAGE *** ---
    if not initial_generation_failed_critically:
        append_bg_log("Initial processing complete. Starting refinement stage...")
        initial_results_snapshot = initial_results.copy() # Pass snapshot
        try:
            # Call the refinement orchestrator function (defined above in this file)
            run_refinement_stage(
                run_id=run_id,
                user_email=user_email,
                api_key=api_key,
                company_name=company_name,
                initial_results=initial_results_snapshot,
                documents_for_api=documents_for_api,
                append_log_func=append_bg_log, # Pass the logger
                # Pass clients and config needed by refinement stage
                sg_client=sg_client,
                hf_api_client=hf_api_client,
                hf_token=hf_token,
                dataset_repo_id=dataset_repo_id,
                sender_email=sender_email,
                app_version=app_version,
                max_workers=max_workers # <<< Pass max_workers for parallel refinement
            )
            append_bg_log("Refinement stage completed (or attempted).")
        except Exception as refinement_e:
            error_msg = f"CRITICAL ERROR initiating or during refinement stage call: {type(refinement_e).__name__} - {str(refinement_e)}"
            append_bg_log(error_msg); traceback.print_exc()
            log_event = {"event": "RefinementStageFailed", "runId": run_id, "status": "CriticalException", "error": error_msg, "stage": "OrchestratorCall"}
            save_log_entry_hf_dataset(user_email=user_email, event_data=log_event, api=hf_api_client, HF_TOKEN=hf_token, DATASET_REPO_ID=dataset_repo_id)
    else:
         append_bg_log("Skipping refinement stage due to critical failure during initial generation.")

    # --- End of background task ---
    append_bg_log(f"Background task finished.")