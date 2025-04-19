# --- START OF FILE src/section_processor.py ---
"""
Section processor module for ProfileDash
Handles processing of individual sections (Initial Generation Only for now)
"""

import time
import re
import json
import jsonschema
import traceback # Used for providing detailed error information in logs.

# Use relative imports for modules within the src package
from .api_client import cached_generate_content, create_insight_model
from .prompts import persona, analysis_specs, json_output_format
from .section_definitions import sections, get_section_schema_string, get_section_template_string

def _fix_common_schema_deviations(data):
    """
    Recursively traverses the generated JSON data and attempts to fix common,
    predictable deviations from the expected schema. This acts as a pre-validation
    step to increase the chances of successful schema validation.
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # Fix 1: Rename 'source_ref' (likely from LLM hallucination) to '_source_ref_id' (expected schema field).
            new_key = "_source_ref_id" if key == "source_ref" else key
            # --- Add other simple, targeted fixes here if new common deviations are observed ---
            # Example: if key == "some_old_name": new_key = "some_new_name"
            new_dict[new_key] = _fix_common_schema_deviations(value) # Recurse for nested structures.
        return new_dict
    elif isinstance(data, list):
        # Recurse into list items.
        return [_fix_common_schema_deviations(item) for item in data]
    else:
        # Return non-dict/list types unchanged.
        return data

def _validate_schema(section_schema):
    """
    Validates that a provided section schema dictionary adheres to the
    internal structural requirements, specifically checking the 'notes' field.
    This is an internal sanity check, not validation of generated data against the schema.
    """
    if not isinstance(section_schema, dict):
        raise ValueError("Section schema must be a dictionary")

    def validate_object(obj):
        """Inner helper function to recursively check objects within the schema."""
        if not isinstance(obj, dict):
            return

        # Check for the optional 'notes' field and its structure.
        if "notes" in obj:
            if not isinstance(obj["notes"], dict):
                raise ValueError("Notes field must be a dictionary with type and description")
            if "type" not in obj["notes"] or "description" not in obj["notes"]:
                raise ValueError("Notes field must contain type and description")
            # Enforce that 'notes' allows string or null values.
            if obj["notes"]["type"] != ["string", "null"]:
                raise ValueError("Notes field type must be ['string', 'null']")

        # Recursively validate nested objects and objects within lists.
        for value in obj.values():
            if isinstance(value, dict):
                validate_object(value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # If it's a list of objects, validate the structure of the first item
                # assuming all items in the list follow the same structure.
                validate_object(value[0])

    validate_object(section_schema)

# --- Main Function for Initial Section Generation ---
def generate_initial_section(section, documents, persona, analysis_specs, json_output_format, model):
    """
    Generates the initial JSON content for a single specified section using an LLM.

    This function orchestrates the process of:
    1. Constructing a detailed prompt including section specs, documents, schema, and formatting instructions.
    2. Calling the LLM via `cached_generate_content`.
    3. Attempting to parse the LLM response as JSON.
    4. Applying automatic fixes for known schema deviations (`_fix_common_schema_deviations`).
    5. Validating the (potentially fixed) JSON against the section's specific schema.
    6. Implementing a retry loop (`MAX_CORRECTION_ATTEMPTS`) with corrective prompts
       if parsing or validation fails, or if the response is empty/blocked.

    Args:
        section (dict): The definition dictionary for the section to generate.
        documents (list): A list of document content strings to be used as context.
        persona (str): The persona string to guide the LLM's tone and style.
        analysis_specs (str): General analysis specifications for the LLM.
        json_output_format (str): Instructions on the expected JSON output format.
        model: An initialized generative model instance (e.g., from `create_insight_model`).

    Returns:
        tuple: A tuple containing:
            - section_num (int): The number of the processed section.
            - result (dict): Either the validated JSON content for the section
                             or a dictionary containing error details if generation failed.
    """
    # Maximum number of attempts to get valid JSON from the LLM.
    MAX_CORRECTION_ATTEMPTS = 3

    # --- Section Identification ---
    section_num = section["number"]
    section_title = section["title"]
    section_specs = section["specs"]

    print(f"Section Processor: Section {section_num}: GENERATING initial content for '{section_title}'")

    # --- State Variables for Retry Loop ---
    validated_json = None # Stores the successfully validated JSON.
    final_result = None   # Stores the final result (error or success).
    correction_prompt = None # Stores the prompt used for retry attempts.
    schema_str = get_section_schema_string(section_num) # Fetch schema string for the prompt.
    template_str = get_section_template_string(section_num) # Fetch template string for the prompt.

    # --- Construct Schema/Template Part of the Prompt ---
    # This part explicitly tells the LLM the target structure and provides an example.
    schema_prompt_part = f"""
TARGET JSON SCHEMA:
```json
{schema_str}
```
Follow this schema EXACTLY. Only include the fields specified.

EXAMPLE DESIRED JSON OUTPUT STRUCTURE (Use this structure, adapt content based on documents):
```json
{template_str}
```

CRITICAL INSTRUCTION: Place the DETAILED analysis, narrative, context, and ALL extracted information requested by the section's `specs` that doesn't fit the specific schema fields directly into the `analysis_text` field. Cite sources using bracketed IDs `[refX]` within the `analysis_text` and populate the `footnotes` array accordingly. Use `notes` field within objects (if present in schema) for localized extra context.
"""

    # --- Generation Attempt Loop ---
    # Tries up to MAX_CORRECTION_ATTEMPTS times to generate valid, schema-compliant JSON.
    for attempt in range(MAX_CORRECTION_ATTEMPTS):
        print(f"Section Processor: Section {section_num}: Starting attempt {attempt + 1}/{MAX_CORRECTION_ATTEMPTS}")

        # --- Prepare API Input ---
        # On the first attempt, or if the last attempt didn't generate a correction prompt
        # (e.g., due to an unexpected error), use the full initial instruction.
        if attempt == 0 or not correction_prompt:
            # Construct the comprehensive initial prompt.
            section_instruction = f"""
{persona}

Please create section {section_num}: "{section_title}" for a company profile, focusing *only* on this section.

SECTION SPECIFICATIONS FOR {section_num} ("{section_title}"):
{section_specs}

EXTRACT AND SUMMARIZE ALL RELEVANT INFORMATION FROM THE DOCUMENTS ACCORDING TO THESE SPECIFICATIONS.

GENERAL ANALYSIS SPECIFICATIONS (Apply to Section {section_num} content):\n{analysis_specs}

OUTPUT FORMATTING INSTRUCTIONS (Apply to Section {section_num} content):\n{json_output_format}\n{schema_prompt_part}

IMPORTANT: Generate *only* valid JSON for section {section_num}. Do NOT include any text before or after the JSON object. Base your analysis *strictly* on the provided documents. Be complete but concise, especially in the `analysis_text` field, to avoid exceeding token limits.
"""
            api_input = [section_instruction] + documents
            print(f"Section Processor: Section {section_num}: Input prepared for initial attempt ({len(api_input)} parts)")
        else:
            # On subsequent attempts, use the specific correction prompt generated
            # based on the failure mode of the previous attempt.
            api_input = [correction_prompt] + documents
            print(f"Section Processor: Section {section_num}: Input prepared with correction prompt ({len(api_input)} parts)")

        # --- Call LLM and Process Response ---
        try:
            print(f"Section Processor: Section {section_num}: Calling API (attempt {attempt + 1})")

            # Ensure a valid model object was passed.
            if not model:
                raise ValueError("No valid model instance provided to generate_initial_section")

            # Call the LLM API (using caching only on the first attempt).
            section_response = cached_generate_content(model, api_input, section_num=section_num,
                                                     cache_enabled=(attempt == 0), timeout=300)

            # --- Basic Response Validation ---
            if section_response is None:
                raise ValueError("API response object was None.")

            # Check for safety feedback/blocking *before* trying to access text.
            if hasattr(section_response, 'prompt_feedback') and section_response.prompt_feedback:
                feedback = section_response.prompt_feedback
                print(f"Section Processor: Section {section_num}: API Response Feedback: {feedback}")
                if hasattr(feedback, 'block_reason') and feedback.block_reason:
                    # If blocked, raise an error immediately to stop processing this section.
                    raise ValueError(f"Content blocked for section {section_num}. Reason: {feedback.block_reason}. Safety Ratings: {getattr(feedback, 'safety_ratings', 'N/A')}")

            # Ensure the response object has the expected 'text' attribute.
            if not hasattr(section_response, 'text'):
                raise ValueError("API response object is valid but missing 'text' attribute.")

            response_text = section_response.text
            print(f"Section Processor: Section {section_num}: API call complete (received {len(response_text)} chars)")

            # --- Handle Empty Response ---
            if not response_text or not response_text.strip():
                print(f"Section Processor: Section {section_num}: Warning - API returned empty content on attempt {attempt + 1}.")
                if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                    # Generate a correction prompt asking the LLM to try again as the response was empty.
                    correction_prompt = f"""
{persona}

CORRECTION NEEDED: Your previous response was empty.

Please create section {section_num}: "{section_title}" for a company profile, following all specifications below.

SECTION SPECIFICATIONS FOR {section_num} ("{section_title}"):
{section_specs}

GENERAL ANALYSIS SPECIFICATIONS:
{analysis_specs}

OUTPUT FORMATTING INSTRUCTIONS:
{json_output_format}
{schema_prompt_part}

IMPORTANT: Generate *only* valid JSON matching the exact schema above. Do NOT include any text before or after the JSON object.
"""
                    print(f"Section Processor: Section {section_num}: Prepared correction prompt for empty response.")
                    continue # Move to the next attempt.
                else:
                    # If the final attempt also resulted in an empty response, record the error.
                    final_result = {
                        "error": "API returned empty content for this section after multiple attempts.",
                        "section_num": section_num,
                        "section_title": section_title
                    }
                    break # Exit the loop.

            # --- Clean and Prepare JSON String ---
            # Remove leading/trailing whitespace and potential markdown code fences (```json ... ``` or ``` ... ```).
            cleaned_text = response_text.strip()
            json_string_to_parse = None

            # Use regex to extract content within JSON markdown fences if present.
            match = re.match(r'^```(?:json)?\s*(.*?)\s*```$', cleaned_text, re.DOTALL | re.IGNORECASE)
            if match:
                json_string_to_parse = match.group(1).strip()
                print(f"Section {section_num}: Removed markdown fences via regex. Attempting parse.")
            else:
                # If no fences, check if it looks like a basic JSON object.
                if cleaned_text.startswith('{') and cleaned_text.endswith('}'):
                    json_string_to_parse = cleaned_text
                    print(f"Section {section_num}: No markdown fences found, but looks like JSON. Attempting parse.")
                else:
                    # If it doesn't look like JSON, assume it's invalid non-JSON text.
                    print(f"Section {section_num}: No markdown fences found and doesn't start with {{. Assuming invalid content.")
                    # Assign the cleaned text so the JSONDecodeError below includes the problematic text.
                    json_string_to_parse = cleaned_text

            # --- Parse and Validate JSON ---
            try:
                # Attempt to parse the extracted/cleaned string as JSON.
                parsed_json = json.loads(json_string_to_parse)
                print(f"Section {section_num}: Successfully parsed JSON on attempt {attempt + 1}.")

                # --- Apply Automatic Schema Fixes ---
                try:
                    print(f"Section {section_num}: Attempting automatic schema deviation fixes...")
                    parsed_json = _fix_common_schema_deviations(parsed_json)
                    print(f"Section {section_num}: Automatic fixes applied (if any).")
                except Exception as fix_err:
                    # Log errors during fixing but continue with the potentially un-fixed JSON.
                    print(f"Section {section_num}: Error during automatic fixing: {fix_err}")

                # --- Schema Validation ---
                try:
                    # Retrieve the authoritative schema for this section.
                    current_schema = section['schema']
                    # Validate the (potentially fixed) parsed JSON against the schema.
                    jsonschema.validate(instance=parsed_json, schema=current_schema)
                    print(f"Section {section_num}: JSON validation SUCCESSFUL on attempt {attempt + 1}.")

                    # Store the valid JSON and exit the retry loop.
                    validated_json = parsed_json
                    break # Success!

                except jsonschema.ValidationError as validation_error:
                    # --- Handle Validation Failure ---
                    print(f"Section {section_num}: JSON validation FAILED on attempt {attempt + 1}. Error: {validation_error.message}")
                    if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                        # Generate a correction prompt detailing the validation error and showing the invalid JSON.
                        correction_prompt = f"""
{persona}

CORRECTION NEEDED: Your previous JSON response failed validation against the schema with the following error:
{validation_error.message}

Here is the invalid JSON you provided:
```json
{json.dumps(parsed_json, indent=2)}
```

Please regenerate the JSON object for section {section_num}: "{section_title}", fixing ONLY the validation error based on the schema and instructions below.

SECTION SPECIFICATIONS FOR {section_num} ("{section_title}"):
{section_specs}

OUTPUT FORMATTING INSTRUCTIONS:
{json_output_format}
{schema_prompt_part}

IMPORTANT: Ensure the regenerated output is *only* the valid JSON object, adhering strictly to the schema and instructions. Be concise to avoid token limits.
"""
                        print(f"Section {section_num}: Prepared correction prompt for validation error.")
                        continue # Move to the next attempt.
                    else:
                        # If validation fails on the final attempt, record the error.
                        final_result = {
                            "error": "JSON Validation Failed after multiple attempts",
                            "message": validation_error.message,
                            "section_num": section_num,
                            "section_title": section_title,
                            "parsed_json": parsed_json # Include the invalid JSON for debugging.
                        }
                        print(f"Section {section_num}: JSON validation failed after {MAX_CORRECTION_ATTEMPTS} attempts.")
                        time.sleep(1) # Short pause before potentially processing the next section.
                        break # Exit loop

            except json.JSONDecodeError as json_error:
                # --- Handle JSON Parsing Failure ---
                print(f"Section {section_num}: JSON parsing FAILED on attempt {attempt + 1}. Error: {json_error}")
                if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                    # Generate a correction prompt indicating a JSON parsing error and showing the problematic text.
                    correction_prompt = f"""
{persona}

CORRECTION NEEDED: Your previous response was not valid JSON. The parser reported the following error:
{json_error}

Here is the invalid text you provided (first 500 chars):
```
{response_text[:500]}...
```

Please regenerate the response for section {section_num}: "{section_title}", ensuring it is *only* a single, valid JSON object matching the schema and instructions below.

SECTION SPECIFICATIONS FOR {section_num} ("{section_title}"):
{section_specs}

OUTPUT FORMATTING INSTRUCTIONS:
{json_output_format}
{schema_prompt_part}

IMPORTANT: Ensure the regenerated output is *only* the valid JSON object, adhering strictly to the schema and instructions. Remove any introductory text, comments, or markdown fences. Be concise.
"""
                    print(f"Section {section_num}: Prepared correction prompt for JSON parsing error.")
                    continue # Move to the next attempt.
                else:
                    # If parsing fails on the final attempt, record the error.
                    final_result = {
                        "error": "JSON Parsing Failed after multiple attempts",
                        "error_details": str(json_error),
                        # Include the start of the raw text for debugging.
                        "raw_text": response_text[:500] + ('...' if len(response_text) > 500 else ''),
                        "section_num": section_num,
                        "section_title": section_title
                    }
                    print(f"Section {section_num}: JSON parsing failed after {MAX_CORRECTION_ATTEMPTS} attempts.")
                    time.sleep(1) # Short pause.
                    break # Exit loop

        except TimeoutError as e:
            # --- Handle API Timeout ---
            error_msg = f"TIMEOUT generating Section {section_num} on attempt {attempt + 1}: {str(e)}"
            print(f"Section Processor: {error_msg}")
            if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                print(f"Section Processor: Section {section_num}: Retrying after timeout (attempt {attempt + 2}).")
                # No specific correction prompt needed, just retry with the last used prompt (or initial if first attempt).
                continue # Move to the next attempt.
            else:
                # If timeout occurs on the final attempt, record the error.
                final_result = {
                    "error": f"Processing timed out for section {section_num} after multiple attempts.",
                    "section_num": section_num,
                    "section_title": section_title
                }
                break # Exit loop

        except ValueError as api_error:
            # --- Handle Specific API/Response ValueErrors (e.g., None response, missing text, blocked content) ---
            print(f"Section Processor: Section {section_num}: Error processing API response on attempt {attempt+1}: {api_error}")
            print(f"Detailed Traceback:\n{traceback.format_exc()}") # Log traceback for debugging.
            if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                # Generate a generic correction prompt asking the LLM to try again, focusing on adherence to instructions.
                correction_prompt = f"""
{persona}

CORRECTION NEEDED: There was an issue processing the previous response, potentially due to blocking or unexpected content. Please try generating the content for section {section_num}: "{section_title}" again, strictly following all instructions.

SECTION SPECIFICATIONS FOR {section_num} ("{section_title}"):
{section_specs}

GENERAL ANALYSIS SPECIFICATIONS:
{analysis_specs}

OUTPUT FORMATTING INSTRUCTIONS:
{json_output_format}
{schema_prompt_part}

IMPORTANT: Generate *only* valid JSON matching the exact schema above. Ensure content adheres to safety policies and all formatting instructions. Be concise.
"""
                print(f"Section Processor: Section {section_num}: Prepared correction prompt for API/response error.")
                continue # Move to the next attempt.
            else:
                # If this error occurs on the final attempt, record it.
                final_result = {
                    "error": f"Could not generate initial content: {type(api_error).__name__}",
                    "error_details": str(api_error),
                    "section_num": section_num,
                    "section_title": section_title
                }
                break # Exit loop

        except Exception as e:
            # --- Handle Unexpected Errors ---
            error_msg = f"UNEXPECTED ERROR generating Section {section_num} on attempt {attempt + 1}: {type(e).__name__} - {str(e)}"
            print(f"Section Processor: {error_msg}")
            traceback.print_exc() # Print stack trace for unexpected errors.
            if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                print(f"Section Processor: Section {section_num}: Retrying after unexpected error (attempt {attempt + 2}).")
                # No specific correction prompt, retry with the last used prompt.
                continue # Move to the next attempt.
            else:
                # If an unexpected error occurs on the final attempt, record it.
                final_result = {
                    "error": f"Could not generate initial content: {type(e).__name__}",
                    "error_details": str(e),
                    "section_num": section_num,
                    "section_title": section_title
                }
                break # Exit loop

    # --- Determine Final Result ---
    if validated_json is not None:
        # Success: Return the validated JSON.
        print(f"Section Processor: Section {section_num}: Successfully generated valid JSON content.")
        return section_num, validated_json
    else:
        # Failure: Return the error details captured in final_result.
        print(f"Section Processor: Section {section_num}: Failed to generate valid JSON after {MAX_CORRECTION_ATTEMPTS} attempts.")
        # If final_result wasn't set due to an unexpected loop exit (shouldn't happen), create a generic error.
        if final_result is None:
             final_result = {
                "error": f"Unknown error prevented generation for section {section_num} after {MAX_CORRECTION_ATTEMPTS} attempts.",
                "section_num": section_num,
                "section_title": section_title
            }
        return section_num, final_result
