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
from .lc_chains import get_appendix_data_extraction_chain, get_html_appendix_generation_chain, get_gemini_llm
# from .lc_models import AppendixDataItem, AppendixStructuredData # Potentially not needed directly here if chains handle it
from .prompts import output_format # Make sure this is imported for HTML rules
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

    base_filename = f"section_{section_num:02d}{filename_suffix}"
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

# --- Helper task for Appendix HTML generation via LangChain ---
def _generate_html_appendix_task_lc(
    internal_structured_appendix_data: list, # List of AppendixDataItem like dicts
    output_format_rules: str, # The 'output_format' string from prompts.py
    chain_b_format_appendix_html_lc: any, # The pre-configured LangChain chain
    append_log_func # For logging
):
    section_num = 32; had_error = False; html_content = ""
    append_log_func(f"S{section_num}_HTML_Task: Starting Appendix HTML generation via LangChain.")

    if not internal_structured_appendix_data: # Check if list is empty or None
        append_log_func(f"S{section_num}_HTML_Task: No structured appendix data provided.")
        html_content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. Appendix</h2><p class="error">Could not generate Appendix HTML as structured data extraction failed or yielded no data.</p></div>'
        had_error = True
        return section_num, html_content, had_error
    try:
        # Ensure data is list of dicts for json.dumps
        data_to_serialize = [item.model_dump() if hasattr(item, 'model_dump') else item for item in internal_structured_appendix_data]
        structured_data_json_str = json.dumps(data_to_serialize, indent=2)

        input_dict_chain_b = {
            "structured_appendix_data_json_string": structured_data_json_str,
            "output_format_rules": output_format_rules
        }
        # Assuming chain_b_format_appendix_html_lc is (prompt | llm | StrOutputParser)
        html_output_from_chain = chain_b_format_appendix_html_lc.invoke(input_dict_chain_b)
        
        # The prompt for Chain B was told not to include the wrapper, so add it here.
        html_content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. Appendix</h2>\n{html_output_from_chain}\n</div>'
        append_log_func(f"S{section_num}_HTML_Task: HTML for Appendix generated successfully via LangChain.")
    except Exception as e:
        append_log_func(f"S{section_num}_HTML_Task: ERROR during LangChain HTML Formatting: {e}"); traceback.print_exc()
        html_content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. Appendix</h2><p class="error">Error formatting Appendix HTML from structured data via LangChain: {e}</p></div>'
        had_error = True
    return section_num, html_content, had_error

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
    run_id: str, user_email: str, api_key: str, company_name: str,
    initial_results: dict,
    internal_structured_appendix_data: list, # <<< ADD THIS ARGUMENT
    documents_for_api: list,
    append_log_func,
    sg_client, hf_api_client, hf_token: str, dataset_repo_id: str,
    sender_email: str, app_version: str, max_workers: int
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

# In src/background_processor.py
# REPLACE the existing execute_full_profile_workflow function with this:

def execute_full_profile_workflow(
    run_id: str, user_email: str, api_key: str, temp_file_paths: list,
    sg_client, hf_api_client, hf_token: str, dataset_repo_id: str,
    sender_email: str, app_version: str, max_workers: int, max_upload_bytes: int
):
    start_run_time = time.time()
    background_log_internal = []
    def get_run_elapsed():
        elapsed = time.time() - start_run_time; minutes = int(elapsed // 60); seconds = int(elapsed % 60)
        return f"[{minutes}'{seconds:02d}\"]"
    def append_bg_log(message):
        ts_msg = f"{get_run_elapsed()} {message}"; background_log_internal.insert(0, ts_msg)
        print(f"BG Processor: Run {run_id}: {ts_msg}")
    append_bg_log("Workflow started.")

    # Workflow variables
    initial_results_for_sections = {}
    internal_structured_appendix_data = []
    documents_for_api_gemini_files = []
    company_name = "Unknown_Company"
    initial_draft_final_html = ""
    initial_draft_profile_saved = False
    initial_draft_profile_path = None
    any_error_in_initial_draft_processing = False # Tracks errors in initial section drafts + appendix HTML
    workflow_critical_failure_message = None

    # --- Initialize LangChain LLMs and Chains for Appendix ---
    append_bg_log("Initializing LangChain components for Appendix...")
    chain_a_extract_appendix_data = None
    appendix_data_parser_lc_instance = None # Store the parser from chain_a
    chain_b_format_appendix_html_lc = None
    gemini_llm_for_lc_appendix = None
    try:
        # This uses the get_gemini_llm from your lc_chains.py
        gemini_llm_for_lc_appendix = get_gemini_llm(api_key, temperature=0.1)
        chain_a_extract_appendix_data, appendix_data_parser_lc_instance = get_appendix_data_extraction_chain(gemini_llm_for_lc_appendix)
        chain_b_format_appendix_html_lc = get_html_appendix_generation_chain(gemini_llm_for_lc_appendix)
        append_bg_log("LangChain Appendix components initialized.")
    except Exception as lc_init_e:
        append_bg_log(f"CRITICAL ERROR initializing LangChain components: {lc_init_e}"); traceback.print_exc()
        workflow_critical_failure_message = f"LangChain setup failed: {lc_init_e}"

    try:
        if workflow_critical_failure_message: raise RuntimeError(workflow_critical_failure_message)

        genai.configure(api_key=api_key)
        append_bg_log("Google AI SDK Configured for direct calls.")

        append_bg_log("Processing uploaded PDFs...")
        # ... (Your full PDF processing logic from the file you provided)
        if not temp_file_paths: raise ValueError("No file paths provided.")
        uploaded_data = {}; total_size = 0; valid_files_count = 0
        for file_path in temp_file_paths: # Use a different loop var name
            if file_path is None: continue
            filename = os.path.basename(file_path)
            try:
                if not os.path.exists(file_path): continue
                if not filename.lower().endswith(".pdf"): continue
                file_size = os.path.getsize(file_path);
                if file_size == 0: continue
                total_size += file_size
                with open(file_path, 'rb') as f: uploaded_data[filename] = f.read()
                valid_files_count += 1
            except Exception as read_err: append_bg_log(f"Error reading '{filename}': {read_err}"); continue
        if not uploaded_data: raise ValueError("No valid PDF files processed.")
        if total_size > max_upload_bytes: raise ValueError(f"Upload failed: Size ({total_size / (1024*1024):.2f} MB) exceeds {max_upload_bytes / (1024*1024):.0f} MB.")
        
        append_bg_log(f"Preparing {valid_files_count} documents for Gemini API...")
        documents_for_api_gemini_files = load_document_content(uploaded_data) # This uses File API
        if not documents_for_api_gemini_files: raise ValueError("Failed to prepare documents for API.")
        first_filename = next(iter(uploaded_data.keys())); company_name = os.path.splitext(first_filename)[0].replace('_', ' ')
        append_bg_log(f"Company: {company_name}. Documents prepared.")

        # --- STAGE: Generate Internal Structured Appendix Data (LangChain) ---
        append_bg_log("Extracting structured Appendix data via LangChain...")
        try:
             # To pass files to ChatGoogleGenerativeAI in LangChain,
             # the HumanMessage content should be a list containing text and File objects.
             from langchain_core.messages import HumanMessage, SystemMessage
             from .lc_prompts import APPENDIX_EXTRACTION_SYSTEM_PROMPT_TEXT, APPENDIX_EXTRACTION_HUMAN_PROMPT_TEXT

             # Prepare the text part of the human message using the format instructions from the parser
             human_prompt_text_for_extraction = APPENDIX_EXTRACTION_HUMAN_PROMPT_TEXT.format(
                 format_instructions=appendix_data_parser_lc_instance.get_format_instructions()
             )

             # Construct the content for the HumanMessage: text followed by File objects
             human_message_content_parts = [human_prompt_text_for_extraction]
             human_message_content_parts.extend(documents_for_api_gemini_files)

             # Create the list of messages for the LLM
             messages_for_llm_extraction = [
                 SystemMessage(content=APPENDIX_EXTRACTION_SYSTEM_PROMPT_TEXT),
                 HumanMessage(content=human_message_content_parts)
             ]

             # Invoke the LLM component of chain_a directly with these crafted messages
             # chain_a_extract_appendix_data is: prompt_template | llm | parser
             # We are calling chain_a_extract_appendix_data.steps[1] which is the llm
             llm_response_obj = chain_a_extract_appendix_data.steps[1].invoke(messages_for_llm_extraction)
             
             # Now parse using the parser component of the chain
             parsed_appendix_data_obj = chain_a_extract_appendix_data.steps[2].parse(llm_response_obj.content)
             
             internal_structured_appendix_data = parsed_appendix_data_obj.data_points
             append_bg_log(f"Internal Appendix Data: {len(internal_structured_appendix_data)} points extracted.")
             save_log_entry_hf_dataset(user_email, {"event": "AppendixDataExtracted", "runId": run_id, "status": "Success", "points": len(internal_structured_appendix_data)}, hf_api_client, hf_token, dataset_repo_id)
        except Exception as appendix_e:
            append_bg_log(f"ERROR extracting Internal Appendix Data: {appendix_e}"); traceback.print_exc()
            internal_structured_appendix_data = [] # Ensure it's a list for downstream safety
            # Store error HTML directly for Appendix if its data extraction fails
            initial_results_for_sections[32] = f'<div class="section" id="section-32"><h2>32. Appendix</h2><p class="error">Error extracting structured appendix data: {appendix_e}</p></div>'
            any_error_in_initial_draft_processing = True
            save_log_entry_hf_dataset(user_email, {"event": "AppendixDataExtracted", "runId": run_id, "status": "Failure", "error": str(appendix_e)}, hf_api_client, hf_token, dataset_repo_id)

        # --- STAGE: Generate Initial Content for Sections (1-32) in Parallel ---
        append_bg_log(f"Generating initial content for sections 1-32 ({max_workers} workers)...")
        insight_model_for_std_sections = create_insight_model() # For sections 1-31
        if not insight_model_for_std_sections: raise RuntimeError("Failed to create insight_model for sections 1-31.")

        processed_tasks_count = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_sec_def = {}
            for sec_def_item in sections: # Ensure `sections` is defined/imported
                if sec_def_item["number"] == 32: # Appendix HTML generation using LangChain Chain B
                    future = executor.submit(_generate_html_appendix_task_lc,
                                             internal_structured_appendix_data,
                                             output_format, # Global HTML rules string from prompts.py
                                             chain_b_format_appendix_html_lc, # The LangChain chain
                                             append_bg_log)
                else: # Sections 1-31 use the original `generate_initial_section`
                    future = executor.submit(generate_initial_section,
                                             sec_def_item, documents_for_api_gemini_files,
                                             persona, analysis_specs, output_format, # From prompts.py
                                             insight_model_for_std_sections,
                                             [] # Pass empty list for appendix data for S1-31 for now
                                            )
                future_to_sec_def[future] = sec_def_item
            
            append_bg_log(f"All initial section tasks submitted ({len(future_to_sec_def)}). Waiting...")
            for future in as_completed(future_to_sec_def):
                sec_def_done = future_to_sec_def[future]
                s_num, s_title = sec_def_done["number"], sec_def_done["title"]
                try:
                    result_from_future = future.result()
                    html_content_from_task = ""; task_had_error_flag = False

                    if s_num == 32: 
                        _, html_content_from_task, task_had_error_flag = result_from_future
                    else: 
                        _, html_content_from_task = result_from_future
                        if not html_content_from_task or '<p class="error">' in str(html_content_from_task):
                            task_had_error_flag = True
                            if not html_content_from_task: html_content_from_task = f'<div class="section" id="section-{s_num}"><h2>{s_num}. {s_title}</h2><p class="error">Empty content returned.</p></div>'
                    
                    initial_results_for_sections[s_num] = html_content_from_task
                    if task_had_error_flag: any_error_in_initial_draft_processing = True
                    append_bg_log(f"S{s_num} ('{s_title}') initial content done {'with errors' if task_had_error_flag else 'OK'}.")
                except Exception as e_future:
                    append_bg_log(f"ERROR processing S{s_num} ('{s_title}') future: {e_future}"); traceback.print_exc()
                    initial_results_for_sections[s_num] = f'<div class="section" id="section-{s_num}"><h2>{s_num}. {s_title}</h2><p class="error">Task failed: {e_future}</p></div>'
                    any_error_in_initial_draft_processing = True
                
                if initial_results_for_sections.get(s_num):
                    save_section_hf_dataset(s_num, str(initial_results_for_sections[s_num]), "html_initial", run_id, company_name, user_email, hf_api_client, hf_token, dataset_repo_id)
                processed_tasks_count += 1
                append_bg_log(f"Progress: {processed_tasks_count}/{len(sections)} initial sections processed.")
        
        append_bg_log("Aggregating initial draft profile...")
        ordered_initial_draft_contents = [initial_results_for_sections.get(s["number"], f"Error S{s['number']} HTML missing") for s in sorted(sections, key=lambda x:x["number"])]
        initial_draft_final_html = generate_full_html_profile(company_name, sections, ordered_initial_draft_contents, app_version)

        if initial_draft_final_html:
            saved_draft_path = save_profile_hf_dataset(initial_draft_final_html, "html_initial_draft", run_id, company_name, user_email, hf_api_client, hf_token, dataset_repo_id, "_initial_draft") # Added suffix for clarity
            if saved_draft_path: initial_draft_profile_saved = True; initial_draft_profile_path = saved_draft_path
            else: any_error_in_initial_draft_processing = True; append_bg_log("Error saving initial draft profile.")
        else: any_error_in_initial_draft_processing = True; append_bg_log("Error: Initial draft final HTML is empty.")

    except Exception as e_outer_workflow:
        append_bg_log(f"CRITICAL WORKFLOW ERROR (Initial Gen): {e_outer_workflow}"); traceback.print_exc()
        workflow_critical_failure_message = f"Critical error: {type(e_outer_workflow).__name__} ({str(e_outer_workflow)[:100]})"
        save_log_entry_hf_dataset(user_email, {"event": "RunFailed", "status": "Critical", "error": workflow_critical_failure_message, "stage": "InitialGeneration"}, hf_api_client, hf_token, dataset_repo_id)
    
    # --- Send Initial Draft Email (if no critical failure) ---
    if not workflow_critical_failure_message:
        append_bg_log("Preparing initial draft email notification...")
        subject_init = f"ProfileDash: Initial Draft for {company_name} Ready"
        body_init = f"<p>Your initial ProfileDash draft for <strong>{company_name}</strong> is ready. A final, refined version will follow after further processing.</p>"
        attach_init = None
        if initial_draft_profile_saved and initial_draft_final_html:
            try:
                encoded_init = base64.b64encode(initial_draft_final_html.encode('utf-8')).decode('ascii')
                fname_init = os.path.basename(initial_draft_profile_path) if initial_draft_profile_path else f"{company_name}_draft.html"
                attach_init = Attachment(FileContent(encoded_init), FileName(fname_init), FileType('text/html'), Disposition('attachment'))
                body_init += "<p>The initial draft is attached.</p>"
            except Exception as e_att_init: append_bg_log(f"Error attaching initial draft: {e_att_init}")
        if any_error_in_initial_draft_processing: body_init += "<p><i>Note: This draft may contain errors or incomplete sections.</i></p>"
        body_init += f"<p>(Run ID: {run_id})</p><hr><p style='font-size:small;'>ProfileDash {app_version}</p>"
        if sg_client:
            try:
                msg_init = Mail(Email(sender_email, "ProfileDash (Initial Draft)"), To(user_email), subject_init, Content("text/html", body_init))
                if attach_init: msg_init.attachment = attach_init
                response_init_email = sg_client.client.mail.send.post(request_body=msg_init.get()) # Renamed var
                append_bg_log(f"Initial draft email sent (status: {response_init_email.status_code}).")
                save_log_entry_hf_dataset(user_email, {"event": "InitialDraftEmailSent", "runId": run_id, "status": response_init_email.status_code}, hf_api_client, hf_token, dataset_repo_id)
            except Exception as e_mail_init: append_bg_log(f"ERROR sending initial draft email: {e_mail_init}")
        else: append_bg_log("SendGrid not configured, initial draft email skipped.")
 
    # --- Call Refinement Stage (if initial generation didn't critically fail) ---
    if not workflow_critical_failure_message:
        append_bg_log("Initial processing done. Starting separate refinement stage...")
        try:
            run_refinement_stage(
                run_id, user_email, api_key, company_name,
                initial_results=initial_results_for_sections.copy(),
                internal_structured_appendix_data=internal_structured_appendix_data, # Pass this
                documents_for_api=documents_for_api_gemini_files,
                append_log_func=append_bg_log,
                sg_client=sg_client, hf_api_client=hf_api_client, hf_token=hf_token,
                dataset_repo_id=dataset_repo_id, sender_email=sender_email, app_version=app_version,
                max_workers=max_workers
            )
        except Exception as refine_call_e:
            append_bg_log(f"ERROR calling/during run_refinement_stage: {refine_call_e}"); traceback.print_exc()
            save_log_entry_hf_dataset(user_email, {"event": "RefinementStageCallFailed", "runId": run_id, "error": str(refine_call_e)}, hf_api_client, hf_token, dataset_repo_id)
    else:
        append_bg_log("Skipping refinement stage due to critical failure in initial processing.")
        if sg_client: # Send failure email if critically failed and no initial email was sent
             try:
                 fail_subject = f"ProfileDash: Profile Generation FAILED for {company_name}"
                 fail_body = f"<p>Profile generation for <strong>{company_name}</strong> failed critically.</p><p>Error: {workflow_critical_failure_message}</p><p>(Run ID: {run_id})</p><hr><p style='font-size:small;'>ProfileDash {app_version}</p>"
                 fail_msg = Mail(Email(sender_email,"ProfileDash"), To(user_email), fail_subject, Content("text/html", fail_body))
                 sg_client.client.mail.send.post(request_body=fail_msg.get())
                 append_bg_log("Critical failure notification email sent.")
             except Exception as final_fail_email_e: append_bg_log(f"Error sending critical failure email: {final_fail_email_e}")

    append_bg_log("Background task fully finished.")

