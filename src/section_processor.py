# --- START OF FILE src/section_processor.py ---
"""
Section processor module for ProfileDash
Handles processing of individual sections.
"""

import time
import re
import traceback # Import traceback for detailed errors

# Use relative imports for modules within the src package
from .api_client import cached_generate_content # create_insight_model is usually called before this
from .html_generator import validate_html, repair_html, clean_llm_output
# Prompts are passed as arguments now, so direct import might not be needed
# from .prompts import persona, analysis_specs, output_format


# --- Function to Generate the Initial (and for now, final) Content for Sections 1-31 ---
def generate_initial_section(
    section_def: dict,                # Definition for the current section
    documents_for_api: list,          # List of Gemini File objects (full PDFs)
    persona_prompt_text: str,         # The persona string
    analysis_specs_text: str,         # The analysis_specs string
    output_format_text: str,          # The output_format string for HTML rules
    model: any,                       # Pre-configured Gemini model instance
    internal_structured_appendix_data: list  # NEW: List of AppendixDataItem-like dicts
                                             # (will be empty list for S1-31 in current parent call)
):
    """
    Generates, cleans, repairs, and returns the HTML content for a single section.
    Accepts a pre-configured model instance and structured appendix data (though not fully used yet).
    Returns: (section_number, html_content_string)
    """
    section_num = section_def["number"]
    section_title = section_def["title"]
    section_specs = section_def["specs"]

    # Log entry into the function for this section
    print(f"Section Processor: S{section_num}: GENERATING content for '{section_title}'.")

    # --- Construct the prompt ---
    # For THIS iteration, sections 1-31 will NOT use internal_structured_appendix_data in their prompt.
    # They will operate as before, using the full documents_for_api.
    # We add a placeholder/note to the prompt if appendix data *were* to be used more deeply later.
    appendix_data_usage_note = ""
    if internal_structured_appendix_data: # This will be False when called for sections 1-31 in current workflow
        appendix_data_usage_note = (
            "\n\n**Note on Pre-Extracted Appendix Data:** While pre-extracted data from an appendix is available, "
            "for this section, please primarily derive your analysis and facts directly from the comprehensive "
            "source documents provided as input. You may cross-reference with general knowledge if explicitly stated "
            "in section specifications but prioritize source documents.\n"
        )
    else:
        appendix_data_usage_note = "\n\n**Note:** Base your analysis and data extraction *strictly* on the provided input documents.\n"


    section_instruction = f"""{persona_prompt_text}

Please create section {section_num}: "{section_title}" for a company profile, focusing *only* on this section.
{appendix_data_usage_note}
SECTION SPECIFICATIONS FOR {section_num} ("{section_title}"):
{section_specs}

GENERAL ANALYSIS SPECIFICATIONS (Apply to Section {section_num} content):
{analysis_specs_text}

OUTPUT FORMATTING INSTRUCTIONS (Apply to Section {section_num} content):
{output_format_text}

IMPORTANT: Generate *only* the HTML content for section {section_num}, starting exactly with '<div class="section" id="section-{section_num}">' and ending exactly with '</div>'.
"""

    # Prepare the `contents` list for the Gemini API call
    # This list will contain the PDF File objects and the text prompt.
    api_input_contents = []
    api_input_contents.extend(documents_for_api) # Add PDF File objects
    api_input_contents.append(section_instruction)   # Add the text prompt

    # print(f"Section Processor: S{section_num}: Input prepared ({len(api_input_contents)} parts).") # Verbose

    try:
        # print(f"Section Processor: S{section_num}: Calling API (cached_generate_content)") # Verbose
        # The `model` is a pre-configured GenerativeModel instance from api_client.py
        if not model:
            raise ValueError("No valid model instance provided to generate_initial_section")

        section_response = cached_generate_content(
            model,
            api_input_contents, # Pass the list containing File objects and prompt text
            section_num=section_num,
            cache_enabled=True, # Or from a global config
            timeout=300 # Or from a global config
        )

        # Defensive checks for the response
        if section_response is None:
             raise ValueError("API response object was None.")
        if hasattr(section_response, 'prompt_feedback') and section_response.prompt_feedback:
             feedback = section_response.prompt_feedback
             if hasattr(feedback, 'block_reason') and feedback.block_reason and feedback.block_reason != "OTHER": # Allow "OTHER" if it still has text
                  # Check if there's actual content despite a block reason "OTHER"
                  has_text_content = hasattr(section_response, 'text') and section_response.text and section_response.text.strip()
                  if not has_text_content:
                    raise ValueError(f"Content blocked for section {section_num}. Reason: {feedback.block_reason}. Safety Ratings: {getattr(feedback, 'safety_ratings', 'N/A')}")
                  else:
                    print(f"Section Processor: S{section_num}: Content blocked with reason '{feedback.block_reason}' but text exists. Proceeding.")
        if not hasattr(section_response, 'text'): # Should always have .text if not blocked severely
             # This might indicate a different kind of API issue or unexpected response structure
             candidate_text = ""
             if hasattr(section_response, 'candidates') and section_response.candidates:
                 if hasattr(section_response.candidates[0],'content') and hasattr(section_response.candidates[0].content,'parts') and section_response.candidates[0].content.parts:
                     candidate_text = "".join(p.text for p in section_response.candidates[0].content.parts if hasattr(p,'text'))
             if not candidate_text:
                raise ValueError("API response object is valid but missing 'text' attribute and no recoverable candidate text.")
             else: # Recovered text from candidates
                section_response.text = candidate_text


        generated_html_raw = section_response.text
        # print(f"Section Processor: S{section_num}: API call complete (received {len(generated_html_raw)} chars)") # Verbose

        if not generated_html_raw or not generated_html_raw.strip():
             print(f"Section Processor: S{section_num}: Warning - API returned empty content.")
             generated_html_repaired = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">Error: API returned empty content for this section.</p></div>'
        else:
            generated_html_cleaned = clean_llm_output(generated_html_raw, section_num, section_title)
            generated_html_repaired = repair_html(generated_html_cleaned, section_num, section_title)
            if not validate_html(generated_html_repaired):
                 print(f"Section Processor: S{section_num}: Warning - Invalid HTML structure detected after repair.")
                 if not generated_html_repaired or not generated_html_repaired.strip(): # If repair made it empty
                      generated_html_repaired = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">Error: Failed to generate or repair valid HTML content.</p></div>'

        # print(f"Section Processor: S{section_num}: Content generated and processed.") # Verbose
        return section_num, generated_html_repaired

    except TimeoutError as e_timeout: # Specific exception
        error_msg = f"TIMEOUT generating S{section_num}: {str(e_timeout)}"
        print(f"Section Processor: {error_msg}")
        error_html = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Processing timed out for section {section_num}.</p></div>'
        return section_num, error_html

    except ValueError as e_value: # Specific exception (includes our blocking error)
        error_msg = f"VALUE ERROR generating S{section_num}: {str(e_value)}"
        print(f"Section Processor: {error_msg}")
        # traceback.print_exc() # Keep this commented unless deep debugging value errors
        error_html = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: {str(e_value)}</p></div>'
        return section_num, error_html

    except Exception as e_general: # Catch-all for other unexpected errors
        error_msg = f"UNEXPECTED ERROR S{section_num}: {type(e_general).__name__} - {str(e_general)}"
        print(f"Section Processor: {error_msg}")
        traceback.print_exc()
        error_html = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Could not generate content due to an unexpected issue: {type(e_general).__name__}</p></div>'
        return section_num, error_html

# --- END OF FILE src/section_processor.py ---