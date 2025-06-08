# --- START OF FILE src/phase_0_processor.py ---
import os
import time
import re
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple
import io

import google.generativeai as genai
import PyPDF2
from huggingface_hub import HfApi, upload_file

from .tools.table_postprocessor import TablePostProcessor

def _get_pdf_page_count(file_bytes: bytes) -> int:
    """Gets the total number of pages from PDF bytes."""
    try:
        # Use strict=False to handle some malformed PDFs
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes), strict=False)
        return len(reader.pages)
    except Exception as e:
        print(f"PyPDF2 ERROR reading page count: {e}. Returning a high default (250).")
        return 250 # Fallback to a reasonable high number

def _save_artifact_to_hf(content: str, repo_path: str, run_id: str, hf_api_client: HfApi, hf_token: str, dataset_repo_id: str):
    """Helper to upload a string content to a specified path in the HF Dataset."""
    if not all([hf_api_client, hf_token, dataset_repo_id]):
        print(f"HF save skipped for {repo_path} due to missing HF credentials.")
        return None
    try:
        content_bytes = io.BytesIO(content.encode('utf-8'))
        upload_file(
            path_or_fileobj=content_bytes,
            path_in_repo=repo_path,
            repo_id=dataset_repo_id,
            repo_type="dataset",
            token=hf_token,
            commit_message=f"Add Phase 0 artifact for run {run_id[:8]}"
        )
        print(f"Phase 0: Successfully saved artifact to {repo_path}")
        return repo_path
    except Exception as e:
        print(f"Phase 0 ERROR saving artifact to {repo_path}: {e}")
        return None

def _process_single_pdf(
    doc_index: int,
    filename: str,
    file_bytes: bytes,
    run_id: str,
    user_email: str,
    hf_api_client: HfApi,
    hf_token: str,
    dataset_repo_id: str
) -> Dict:
    """
    Processes a single PDF file: uploads to Gemini, extracts content in chunks,
    post-processes tables, and saves artifacts to Hugging Face.
    """
    print(f"Phase 0 Worker: Starting processing for '{filename}'")
    sanitized_email = user_email.replace('@', '_at_').replace('.', '_')
    # Use a generic name for artifacts to avoid issues with special characters in company names
    safe_artifact_name = f"doc_{doc_index:02d}_{os.path.splitext(filename)[0].replace(' ', '_')}"
    
    # Setup for extraction
    extraction_model = genai.GenerativeModel('gemini-1.5-flash-latest')
    extraction_prompt_template = """
    Analyze pages {start_page}-{end_page} of the provided PDF and extract two types of content: Tables and Narrative Text.

    # PART 1: TABLES
    Identify ALL tables on these pages. For each table, convert it to a clean Markdown format. Use this EXACT structure:
    ## Table [Number]: [Title if visible, or a brief 3-5 word description]
    **Page:** {page_ref}
    | Header 1 | Header 2 |
    |---|---|
    | Data 1 | Data 2 |
    ---

    # PART 2: NARRATIVE TEXT
    Extract all main textual content from these pages that is NOT part of a table you extracted above. Preserve paragraph structure.
    ## Text Content: [Main heading of the text section, or a brief 3-5 word description]
    **Page:** {page_ref}
    [The narrative text content here.]
    ---

    RULES:
    - Be comprehensive. Do not omit any tables or significant text.
    - Use "---" as a separator between each distinct item.
    - If no tables are found, state "No tables found on pages {page_ref}".
    - If no narrative text is found, state "No narrative text found on pages {page_ref}".
    - It is critical that you only analyze the specified page range.
    """
    
    gemini_file = None
    try:
        # 1. Upload to Gemini File API
        print(f"Phase 0 Worker '{filename}': Uploading to File API...")
        gemini_file = genai.upload_file(path=file_bytes, display_name=filename, mime_type="application/pdf")
        while gemini_file.state.name == "PROCESSING":
            time.sleep(5)
            gemini_file = genai.get_file(name=gemini_file.name)
        if gemini_file.state.name != "ACTIVE":
            raise RuntimeError(f"File API processing failed for {filename}, final state: {gemini_file.state.name}")
        print(f"Phase 0 Worker '{filename}': File is ACTIVE.")

        # 2. Extract content in chunks
        total_pages = _get_pdf_page_count(file_bytes)
        PAGES_PER_CHUNK = 10
        all_raw_extracted_content = ""
        
        for start_page in range(1, total_pages + 1, PAGES_PER_CHUNK):
            end_page = min(start_page + PAGES_PER_CHUNK - 1, total_pages)
            page_ref = f"{start_page}-{end_page}" if start_page != end_page else f"{start_page}"
            print(f"Phase 0 Worker '{filename}': Extracting content for pages {page_ref}...")
            
            prompt = extraction_prompt_template.format(start_page=start_page, end_page=end_page, page_ref=page_ref)
            response = extraction_model.generate_content([prompt, gemini_file])
            all_raw_extracted_content += response.text + "\n\n"
            time.sleep(2) # Rate limiting

        # 3. Separate content types
        table_markdown_raw = ""
        narrative_text_raw = ""
        # Split by the header for the text part. Everything before the first split is table content.
        parts = re.split(r'# PART 2: NARRATIVE TEXT', all_raw_extracted_content, flags=re.IGNORECASE)
        # The first part is always table content
        table_markdown_raw = parts[0].replace('# PART 1: TABLES', '').strip()
        # The rest of the parts are text, potentially with repeated table prompts from subsequent chunks
        for part in parts[1:]:
            # Remove any repeated table prompts from the text parts
            text_only_part = re.split(r'# PART 1: TABLES', part, flags=re.IGNORECASE)[0]
            narrative_text_raw += text_only_part.strip() + "\n\n"
        
        # 4. Post-process tables
        table_processor = TablePostProcessor()
        cleaned_table_md = table_processor.fix_markdown_formatting(table_markdown_raw)
        tables_metadata = table_processor.process_text_content(cleaned_table_md)

        # 5. Save artifacts to Hugging Face
        base_path_in_repo = f"profiles/{sanitized_email}/{run_id}/{safe_artifact_name}"
        
        text_path = _save_artifact_to_hf(narrative_text_raw, f"{base_path_in_repo}_text.md", run_id, hf_api_client, hf_token, dataset_repo_id)
        tables_path = _save_artifact_to_hf(cleaned_table_md, f"{base_path_in_repo}_tables.md", run_id, hf_api_client, hf_token, dataset_repo_id)
        json_path = _save_artifact_to_hf(json.dumps(tables_metadata, indent=2), f"{base_path_in_repo}_tables_metadata.json", run_id, hf_api_client, hf_token, dataset_repo_id)

        if text_path and tables_path and json_path:
            return {
                "status": "success",
                "filename": filename,
                "text_file": text_path,
                "tables_file": tables_path,
                "json_file": json_path,
            }
        else:
            raise RuntimeError("One or more artifacts failed to save to Hugging Face.")

    except Exception as e:
        print(f"Phase 0 Worker '{filename}': CRITICAL FAILURE. Error: {e}")
        traceback.print_exc()
        return {"status": "failure", "filename": filename, "error": str(e)}
    
    finally:
        # Cleanup Gemini File regardless of success or failure
        if gemini_file:
            try:
                genai.delete_file(gemini_file.name)
                print(f"Phase 0 Worker '{filename}': Cleaned up Gemini File.")
            except Exception as delete_e:
                print(f"Phase 0 Worker '{filename}': Non-critical error cleaning up Gemini file: {delete_e}")


def run_phase_0_extraction(
    uploaded_data: Dict[str, bytes], run_id: str, user_email: str, 
    hf_api_client: HfApi, hf_token: str, dataset_repo_id: str
) -> List[Dict]:
    """
    Orchestrates the parallel processing of all uploaded PDF files.
    """
    results = []
    # Use max_workers=3 as per specification
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(
                _process_single_pdf, i + 1, filename, file_bytes,
                run_id, user_email, hf_api_client, hf_token, dataset_repo_id
            )
            for i, (filename, file_bytes) in enumerate(uploaded_data.items())
        ]
        for future in as_completed(futures):
            results.append(future.result())
    return results

def extract_company_name(text_md_contents: List[str]) -> str:
    """Determines the primary company name from all extracted text content."""
    print("Extracting primary company name...")
    if not text_md_contents:
        return "Unknown Company"
    
    # Combine a sample from each document to get a good cross-section
    combined_sample = ""
    for content in text_md_contents:
        combined_sample += content[:2000] + "\n\n"

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"""
    Based on the following text extracted from one or more corporate documents, what is the primary, official name of the company being discussed?
    Provide only the company name and nothing else (e.g., no "The company name is...").

    Example: "Apple Inc."
    Example: "The Coca-Cola Company"

    Text sample:
    ---
    {combined_sample[:10000]}
    ---
    Company Name:
    """
    try:
        response = model.generate_content(prompt)
        company_name = response.text.strip().replace("*", "")
        print(f"Determined company name: {company_name}")
        return company_name if company_name else "Unknown Company"
    except Exception as e:
        print(f"ERROR extracting company name: {e}")
        return "Unknown Company"
# --- END OF FILE src/phase_0_processor.py ---