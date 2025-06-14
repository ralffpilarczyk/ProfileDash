import time
import os
import traceback
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from huggingface_hub import HfApi, upload_file, hf_hub_download
from huggingface_hub.utils import HfHubHTTPError
import io
import base64
import google.generativeai as genai
from typing import List, Dict, Tuple
from email.utils import formataddr
from src.gmail_api_sender import send_html_email
from .hf_retry import upload_file_with_retry

# Import new v1.3 processors and components
from .phase_0_processor import run_phase_0_extraction, extract_company_name
from .llamaindex_processor import create_semantic_index, query_top_chunks, combine_all_markdown

# Import refactored/stable components
from .html_generator import generate_full_html_profile, repair_html
from .section_definitions import sections
from .prompts import persona, analysis_specs, output_format
from .api_client import create_insight_model # <<< MODIFIED: Only import create_insight_model
from .refinement import get_fact_critique, fact_improvement_response, get_insight_critique, insight_improvement_response


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

        upload_file_with_retry(
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

        upload_file_with_retry(
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

        upload_file_with_retry(
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

# --- Main Background Workflow Function ---

def execute_full_profile_workflow(
    run_id: str, user_email: str, api_key: str, temp_file_paths: list,
    sg_client, hf_api_client, hf_token: str, dataset_repo_id: str,
    sender_email: str, app_version: str, max_workers: int
):
    start_run_time = time.time()
    def append_bg_log(message):
        elapsed = time.time() - start_run_time
        ts_msg = f"[{int(elapsed // 60)}m {int(elapsed % 60)}s] {message}"
        print(f"BG Processor: Run {run_id}: {ts_msg}")

    append_bg_log("Workflow started for ProfileDash v1.3.")
    
    try:
        genai.configure(api_key=api_key)
        append_bg_log("Google AI SDK Configured.")

        # Read uploaded files from temp paths into an in-memory dictionary
        uploaded_data = {}
        for file_path in temp_file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        uploaded_data[os.path.basename(file_path)] = f.read()
                except Exception as read_err:
                    append_bg_log(f"Error reading file {file_path}: {read_err}")
                    continue
        
        if not uploaded_data:
            raise ValueError("No valid files were provided or could be read.")

        # === PHASE 0: PDF EXTRACTION ===
        append_bg_log("--- Starting Phase 0: Parallel PDF Content Extraction ---")
        # THIS FUNCTION IS NOT YET DEFINED - WILL BE ADDED NEXT
        phase_0_results = run_phase_0_extraction(uploaded_data, run_id, user_email, hf_api_client, hf_token, dataset_repo_id)
        
        successful_extractions = [res for res in phase_0_results if res['status'] == 'success']
        if not successful_extractions:
            raise RuntimeError("Phase 0 extraction failed for all documents. Cannot proceed.")
        
        failed_count = len(phase_0_results) - len(successful_extractions)
        append_bg_log(f"Phase 0 finished. Success: {len(successful_extractions)}, Failed: {failed_count}.")
        
        # Collate content by downloading the newly created artifacts from HF
        append_bg_log("Collating extracted content from Hugging Face...")
        markdown_content_map = {}
        json_content_map = {}

        for res in successful_extractions:
            try:
                text_path = hf_hub_download(repo_id=dataset_repo_id, filename=res['text_file'], repo_type="dataset", token=hf_token)
                with open(text_path, 'r', encoding='utf-8') as f:
                    markdown_content_map[res['text_file']] = f.read()

                tables_path = hf_hub_download(repo_id=dataset_repo_id, filename=res['tables_file'], repo_type="dataset", token=hf_token)
                with open(tables_path, 'r', encoding='utf-8') as f:
                    markdown_content_map[res['tables_file']] = f.read()

                json_path = hf_hub_download(repo_id=dataset_repo_id, filename=res['json_file'], repo_type="dataset", token=hf_token)
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_content_map[res['json_file']] = json.load(f)
                    
            except Exception as download_err:
                append_bg_log(f"ERROR downloading artifact for {res['filename']}: {download_err}. Skipping this document.")
                continue
                   
        if not markdown_content_map:
            raise RuntimeError("Could not retrieve any markdown artifacts from Hugging Face. Cannot proceed.")

        text_md_files_content_list = [v for k, v in markdown_content_map.items() if '_text.md' in k]
        
        # === BATCH METADATA EXTRACTION ===
        # THIS FUNCTION IS NOT YET DEFINED - WILL BE ADDED NEXT
        company_name = extract_company_name(text_md_files_content_list)
        save_log_entry_hf_dataset(user_email, {"event": "CompanyNameExtracted", "runId": run_id, "name": company_name}, hf_api_client, hf_token, dataset_repo_id)

        # === PHASE 1: LLAMAINDEX SETUP ===
        append_bg_log("--- Starting Phase 1: Building LlamaIndex Semantic Index ---")
        # THESE FUNCTIONS ARE NOT YET DEFINED - WILL BE ADDED NEXT
        index = create_semantic_index(api_key, markdown_content_map, json_content_map)
        all_markdown_combined = combine_all_markdown(markdown_content_map)

        # === PHASE 1: SECTION GENERATION ===
        append_bg_log(f"--- Starting Phase 1: Parallel Section Generation ({max_workers} workers) ---")
        final_results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_sec = {}
            for s_def in sections:
                if s_def['number'] == 32:
                    all_tables_md = "\n\n".join([v for k, v in markdown_content_map.items() if '_tables.md' in k])
                    # THIS FUNCTION IS NOT YET DEFINED - WILL BE ADDED NEXT
                    future = executor.submit(_generate_appendix_from_markdown, all_tables_md, append_bg_log)
                else:
                    # THIS FUNCTION IS NOT YET DEFINED - WILL BE ADDED NEXT
                    future = executor.submit(_generate_section_with_llamaindex, s_def, index, all_markdown_combined, append_bg_log)
                future_to_sec[future] = s_def['number']
            
            for future in as_completed(future_to_sec):
                s_num = future_to_sec[future]
                try:
                    res_s_num, html_content, had_error = future.result()
                    final_results[res_s_num] = html_content
                    if not had_error:
                        append_bg_log(f"S{s_num}: Successfully generated. Saving to HF Dataset.")
                        save_section_hf_dataset(res_s_num, html_content, "html_final", run_id, company_name, user_email, hf_api_client, hf_token, dataset_repo_id)
                    else:
                        append_bg_log(f"S{s_num}: Generation completed with an error flag.")
                except Exception as exc:
                    append_bg_log(f"Section {s_num} worker generated an exception: {exc}")
                    traceback.print_exc()
                    final_results[s_num] = f"<p>Error generating section {s_num}: {exc}</p>"
        
        # === FINALIZATION ===
        append_bg_log("--- Finalizing Profile ---")
        ordered_contents = [final_results.get(s["number"], f"<p>Error: Content missing for Section {s['number']}</p>") for s in sorted(sections, key=lambda x:x["number"])]
        final_html = generate_full_html_profile(company_name, sections, ordered_contents, app_version)
        
        save_profile_hf_dataset(final_html, "html_final", run_id, company_name, user_email, hf_api_client, hf_token, dataset_repo_id, "_final")

        # -- Send e-mail via Gmail API --
        gmail_user = os.getenv("GMAIL_USER", "ProfileDash.NoReply@gmail.com")
        if final_html:
            append_bg_log("Sending final e-mail via Gmail API…")
            try:
                send_html_email(
                    from_addr=gmail_user,
                    to_addr=user_email,
                    subject=f"ProfileDash: Your Company Profile for {company_name} is Ready",
                    html_body=f"<p>The attached report for <strong>{company_name}</strong> is complete.</p><p>(Run ID: {run_id})</p>",
                    attachment_html=final_html,
                    attachment_name=f"{company_name.replace(' ', '_')}_Profile.html",
                )
                append_bg_log("Final profile e-mail sent (Gmail API).")
            except Exception as e_mail:
                append_bg_log(f"Gmail API send failed: {e_mail}")
        
    except Exception as e:
        append_bg_log(f"CRITICAL WORKFLOW ERROR: {e}"); traceback.print_exc()
        save_log_entry_hf_dataset(user_email, {"event": "RunFailed", "runId": run_id, "error": str(e)}, hf_api_client, hf_token, dataset_repo_id)
        gmail_user = os.getenv("GMAIL_USER", "ProfileDash.NoReply@gmail.com")
        try:
            fail_body = f"<p>Profile generation failed critically.</p><p>Error: {e}</p><p>(Run ID: {run_id})</p>"
            send_html_email(
                from_addr=gmail_user,
                to_addr=user_email,
                subject=f"ProfileDash: Profile Generation FAILED for run {run_id[:8]}",
                html_body=fail_body,
            )
        except Exception as email_fail_e:
            append_bg_log(f"Could not send critical failure e-mail (Gmail API): {email_fail_e}")
            
    append_bg_log("Background task fully finished.")
# --- END OF NEW v1.3 execute_full_profile_workflow ---

# --- START OF NEW v1.3 GENERATION FUNCTIONS ---

def _generate_appendix_from_markdown(all_tables_markdown: str, append_log_func) -> Tuple[int, str, bool]:
    """Generates the Appendix HTML from the combined table markdown content."""
    section_num = 32
    append_log_func(f"S{section_num}: Starting Appendix HTML generation from combined markdown.")
    if not all_tables_markdown:
        error_html = f'<div class="section" id="section-32"><h2>32. Appendix</h2><p class="error">Could not generate Appendix as no table data was extracted.</p></div>'
        return section_num, error_html, True
    
    try:
        # Find the specs for Section 32 from the imported list
        appendix_specs = next((s['specs'] for s in sections if s['number'] == 32), "")
        if not appendix_specs:
            raise ValueError("Could not find specifications for Section 32 in section_definitions.")

        prompt = f"{persona}\n{appendix_specs}\n\n<markdown_tables>\n{all_tables_markdown}\n</markdown_tables>\n\n{output_format}"
        
        model = create_insight_model()
        response = model.generate_content(prompt)
        # The prompt for Section 32 asks it to produce the full div, so we just repair it
        repaired_html = repair_html(response.text, 32, "Appendix")
        
        append_log_func(f"S{section_num}: HTML for Appendix generated successfully.")
        return section_num, repaired_html, False
    except Exception as e:
        append_log_func(f"S{section_num}: ERROR during Appendix Formatting: {e}"); traceback.print_exc()
        error_html = f'<div class="section" id="section-32"><h2>32. Appendix</h2><p class="error">Error formatting Appendix HTML: {e}</p></div>'
        return section_num, error_html, True


def _generate_section_with_llamaindex(
    section_def: Dict, index, all_markdown_combined: str, append_log_func
) -> Tuple[int, str, bool]:
    """Performs the full 5-step generation and refinement process for one section."""
    section_num = section_def["number"]
    section_title = section_def["title"]
    section_specs = section_def["specs"]
    
    try:
        append_log_func(f"S{section_num}: Starting 5-step generation for '{section_title}'")
        model = create_insight_model()
        
        # 1. Initial Generation
        initial_chunks = query_top_chunks(index, section_specs, top_k=10)
        context_for_initial_gen = "\n\n---\n\n".join([f"Source: {node.metadata.get('file_path', 'Unknown')}\n\n{node.get_content()}" for node in initial_chunks])
        initial_gen_prompt = f"{persona}\n{analysis_specs}\nSECTION SPECIFICATIONS FOR {section_num} ('{section_title}'):\n{section_specs}\n\nCONTEXT FROM SOURCE DOCUMENTS:\n{context_for_initial_gen}\n\n{output_format}\n\nGENERATE HTML:"
        initial_response = model.generate_content(initial_gen_prompt)
        current_html = repair_html(initial_response.text, section_num, section_title)
        
        # 2. Fact Critique
        append_log_func(f"S{section_num}: Starting Fact Critique.")
        fact_critique = get_fact_critique(section_specs, current_html, all_markdown_combined)
        
        # 3. Fact Refinement
        append_log_func(f"S{section_num}: Starting Fact Refinement.")
        fact_refine_chunks = query_top_chunks(index, section_specs + "\n" + fact_critique, top_k=10)
        current_html = fact_improvement_response(section_specs, current_html, fact_critique, fact_refine_chunks, section_num, section_title)

        # 4. Insight Critique
        append_log_func(f"S{section_num}: Starting Insight Critique.")
        insight_critique = get_insight_critique(section_specs, current_html, all_markdown_combined)
        
        # 5. Insight Refinement
        append_log_func(f"S{section_num}: Starting Insight Refinement.")
        insight_refine_chunks = query_top_chunks(index, section_specs + "\n" + insight_critique, top_k=10)
        final_html = insight_improvement_response(section_specs, current_html, insight_critique, insight_refine_chunks, section_num, section_title)

        append_log_func(f"S{section_num}: Finished 5-step generation.")
        return section_num, final_html, False
        
    except Exception as e:
        append_log_func(f"S{section_num}: CRITICAL ERROR during 5-step generation: {e}"); traceback.print_exc()
        error_html = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">Processing failed for this section: {e}</p></div>'
        return section_num, error_html, True

# --- END OF NEW v1.3 GENERATION FUNCTIONS ---