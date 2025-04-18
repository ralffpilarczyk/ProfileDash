# --- START OF FILE src/section_processor.py ---
"""
Section processor module for ProfileDash
Handles processing of individual sections (Initial Generation Only for now)
"""

import time
import re
import json
import jsonschema
import traceback # Import traceback for detailed errors

# Use relative imports for modules within the src package
from .api_client import cached_generate_content, create_insight_model
from .prompts import persona, analysis_specs, json_output_format
from .section_definitions import sections, get_section_schema_string, get_section_template_string

def _fix_common_schema_deviations(data):
    """Recursively attempts to fix common, known schema deviations."""
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # --- Fix 1: Rename 'source_ref' to '_source_ref_id' ---
            new_key = "_source_ref_id" if key == "source_ref" else key
            # --- Add other simple fixes here if needed ---
            # e.g., if key == "some_old_name": new_key = "some_new_name"
            new_dict[new_key] = _fix_common_schema_deviations(value) # Recurse
        return new_dict
    elif isinstance(data, list):
        return [_fix_common_schema_deviations(item) for item in data] # Recurse
    else:
        return data # Return other types unchanged

def _validate_schema(section_schema):
    """Validates that a section schema follows the required format."""
    if not isinstance(section_schema, dict):
        raise ValueError("Section schema must be a dictionary")
    
    def validate_object(obj):
        if not isinstance(obj, dict):
            return
        
        # Check for notes field
        if "notes" in obj:
            if not isinstance(obj["notes"], dict):
                raise ValueError("Notes field must be a dictionary with type and description")
            if "type" not in obj["notes"] or "description" not in obj["notes"]:
                raise ValueError("Notes field must contain type and description")
            if obj["notes"]["type"] != ["string", "null"]:
                raise ValueError("Notes field type must be ['string', 'null']")
        
        # Recursively validate nested objects
        for value in obj.values():
            if isinstance(value, dict):
                validate_object(value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                validate_object(value[0])
    
    validate_object(section_schema)

# --- Function to Generate ONLY the Initial Section ---
def generate_initial_section(section, documents, persona, analysis_specs, json_output_format, model):
    """
    Generates and returns the initial JSON content for a single section.
    Accepts a pre-configured model instance.
    """
    # Maximum number of correction attempts
    MAX_CORRECTION_ATTEMPTS = 3
    
    # Removed schema conversion and validation steps here as schema is now directly usable
    
    section_num = section["number"]
    section_title = section["title"]
    section_specs = section["specs"]

    # Log entry into the function for this section
    print(f"Section Processor: Section {section_num}: GENERATING initial content for '{section_title}'")

    # Variables to track across attempts
    validated_json = None
    final_result = None
    correction_prompt = None
    schema_str = get_section_schema_string(section_num)
    template_str = get_section_template_string(section_num)

    # Construct the part of the prompt that presents the schema and example
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

    # Try multiple attempts to generate valid JSON
    for attempt in range(MAX_CORRECTION_ATTEMPTS):
        print(f"Section Processor: Section {section_num}: Starting attempt {attempt + 1}/{MAX_CORRECTION_ATTEMPTS}")
        
        # If this is the first attempt or no correction prompt exists yet, use the initial instruction
        if attempt == 0 or not correction_prompt:
            # Construct the full prompt including the document list
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
            # Use the correction prompt from previous iteration
            api_input = [correction_prompt] + documents
            print(f"Section Processor: Section {section_num}: Input prepared with correction prompt ({len(api_input)} parts)")

        try:
            print(f"Section Processor: Section {section_num}: Calling API (attempt {attempt + 1})")

            # Check model validity
            if not model:
                raise ValueError("No valid model instance provided to generate_initial_section")

            # Call the LLM
            section_response = cached_generate_content(model, api_input, section_num=section_num, 
                                                     cache_enabled=(attempt == 0), timeout=300)

            # Defensive check for response and text attribute
            if section_response is None:
                raise ValueError("API response object was None.")
                
            # Check for feedback first, especially safety feedback
            if hasattr(section_response, 'prompt_feedback') and section_response.prompt_feedback:
                feedback = section_response.prompt_feedback
                print(f"Section Processor: Section {section_num}: API Response Feedback: {feedback}")
                if hasattr(feedback, 'block_reason') and feedback.block_reason:
                    raise ValueError(f"Content blocked for section {section_num}. Reason: {feedback.block_reason}. Safety Ratings: {getattr(feedback, 'safety_ratings', 'N/A')}")
                    
            # Now check for text attribute
            if not hasattr(section_response, 'text'):
                raise ValueError("API response object is valid but missing 'text' attribute.")

            response_text = section_response.text
            print(f"Section Processor: Section {section_num}: API call complete (received {len(response_text)} chars)")

            if not response_text or not response_text.strip():
                print(f"Section Processor: Section {section_num}: Warning - API returned empty content on attempt {attempt + 1}.")
                
                if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                    # Prepare correction prompt for empty response
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
                    continue
                else:
                    # Final attempt failed with empty response
                    final_result = {
                        "error": "API returned empty content for this section after multiple attempts.",
                        "section_num": section_num,
                        "section_title": section_title
                    }
                    break
            
            # Clean the raw text to remove potential markdown fences and whitespace
            cleaned_text = response_text.strip() # Strip whitespace first
            json_string_to_parse = None

            # Try regex to find ```json ... ``` or ``` ... ```
            match = re.match(r'^```(?:json)?\s*(.*?)\s*```$', cleaned_text, re.DOTALL | re.IGNORECASE)
            if match:
                json_string_to_parse = match.group(1).strip()
                print(f"Section {section_num}: Removed markdown fences via regex. Attempting parse.")
            else:
                # Fallback: If no fences match, check if it starts like JSON
                if cleaned_text.startswith('{') and cleaned_text.endswith('}'):
                    json_string_to_parse = cleaned_text
                    print(f"Section {section_num}: No markdown fences found, but looks like JSON. Attempting parse.")
                else:
                    # If it doesn't start like JSON either, it's likely invalid
                    print(f"Section {section_num}: No markdown fences found and doesn't start with {{. Assuming invalid content.")
                    # Raise a specific error or let the json.loads handle it below, 
                    # but set string so the error message includes the (likely non-JSON) text
                    json_string_to_parse = cleaned_text 
            
            # Try to parse the JSON response
            try:
                # Use the cleaned string here
                parsed_json = json.loads(json_string_to_parse)
                print(f"Section {section_num}: Successfully parsed JSON on attempt {attempt + 1}.")
                
                # Apply automatic schema deviation fixes
                try:
                    print(f"Section {section_num}: Attempting automatic schema deviation fixes...")
                    parsed_json = _fix_common_schema_deviations(parsed_json)
                    print(f"Section {section_num}: Automatic fixes applied (if any).")
                except Exception as fix_err:
                    print(f"Section {section_num}: Error during automatic fixing: {fix_err}")
                    # Continue with potentially un-fixed JSON
                
                # Validate JSON against schema
                try:
                    # Retrieve the correct schema for the current section
                    current_schema = section['schema']
                    # Validate the parsed JSON against the schema
                    jsonschema.validate(instance=parsed_json, schema=current_schema)
                    print(f"Section {section_num}: JSON validation SUCCESSFUL on attempt {attempt + 1}.")
                    
                    # Store successful result and exit loop
                    validated_json = parsed_json
                    break
                    
                except jsonschema.ValidationError as validation_error:
                    print(f"Section {section_num}: JSON validation FAILED on attempt {attempt + 1}. Error: {validation_error.message}")
                    
                    if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                        # Prepare correction prompt for validation error
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
                        continue
                    else:
                        # Final attempt failed validation
                        final_result = {
                            "error": "JSON Validation Failed after multiple attempts", 
                            "message": validation_error.message,
                            "section_num": section_num,
                            "section_title": section_title,
                            "parsed_json": parsed_json  # Include the parsed but invalid JSON for debugging
                        }
                        print(f"Section {section_num}: JSON validation failed after {MAX_CORRECTION_ATTEMPTS} attempts.")
                        time.sleep(1)  # Short pause before continuing
                
            except json.JSONDecodeError as json_error:
                print(f"Section {section_num}: JSON parsing FAILED on attempt {attempt + 1}. Error: {json_error}")
                if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                    # Prepare correction prompt for JSON parsing error
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
                    continue
                else:
                    # Final attempt failed parsing
                    final_result = {
                        "error": "JSON Parsing Failed after multiple attempts",
                        "error_details": str(json_error),
                        "raw_text": response_text[:500] + ('...' if len(response_text) > 500 else ''),
                        "section_num": section_num,
                        "section_title": section_title
                    }
                    print(f"Section {section_num}: JSON parsing failed after {MAX_CORRECTION_ATTEMPTS} attempts.")
                    time.sleep(1)  # Short pause before continuing

        except TimeoutError as e:
            error_msg = f"TIMEOUT generating Section {section_num} on attempt {attempt + 1}: {str(e)}"
            print(f"Section Processor: {error_msg}")
            
            if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                print(f"Section Processor: Section {section_num}: Retrying after timeout (attempt {attempt + 2}).")
                continue
            else:
                final_result = {
                    "error": f"Processing timed out for section {section_num} after multiple attempts.",
                    "section_num": section_num,
                    "section_title": section_title
                }
                break

        except ValueError as api_error: # Catch ValueErrors from API response issues
            print(f"Section Processor: Section {section_num}: Error processing API response on attempt {attempt+1}: {api_error}")
            print(f"Detailed Traceback:\n{traceback.format_exc()}")
            if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                # Prepare correction prompt for general API/response error
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
                continue
            else:
                final_result = {
                    "error": f"Could not generate initial content: {type(api_error).__name__}",
                    "error_details": str(api_error),
                    "section_num": section_num,
                    "section_title": section_title
                }
                break

        except Exception as e:
            error_msg = f"UNEXPECTED ERROR generating Section {section_num} on attempt {attempt + 1}: {type(e).__name__} - {str(e)}"
            print(f"Section Processor: {error_msg}")
            traceback.print_exc()
            
            if attempt < MAX_CORRECTION_ATTEMPTS - 1:
                print(f"Section Processor: Section {section_num}: Retrying after unexpected error (attempt {attempt + 2}).")
                continue
            else:
                final_result = {
                    "error": f"Could not generate initial content: {type(e).__name__}",
                    "error_details": str(e),
                    "section_num": section_num,
                    "section_title": section_title
                }
                break

    # After the loop, check if we have a validated result
    if validated_json is not None:
        print(f"Section Processor: Section {section_num}: Successfully generated valid JSON content.")
        return section_num, validated_json
    else:
        # Return the final error state if no valid JSON was generated
        print(f"Section Processor: Section {section_num}: Failed to generate valid JSON after {MAX_CORRECTION_ATTEMPTS} attempts.")
        return section_num, final_result


# --- Refinement Function (Kept structurally but not called by app.py) ---
# def refine_section_content(section, initial_content, documents, persona, analysis_specs, output_format):
#    """Performs Fact and Insight refinement sequence on initial content."""
#    # ... (Keep internal logic but ensure it doesn't rely on removed globals/timers)
#    # ... (This function would need 'documents' passed if activated)
#    print(f"Section Processor: refine_section_content called for section {section['number']} (Currently Inactive in Gradio App)")
#    # Return initial content for now if called accidentally
#    return initial_content
# --- END OF FILE src/section_processor.py ---