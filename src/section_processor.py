"""
Section processor module for ProfileDash
Handles processing of individual sections (Initial Generation Only for now)
"""

import time
import re
import traceback # Import traceback for detailed errors

# Use relative imports for modules within the src package
from .api_client import cached_generate_content, create_insight_model # Keep create_fact_model if refinement might be added later
# Import from html_generator now using relative import
from .html_generator import validate_html, repair_html, clean_llm_output
# Refinement functions are imported but refine_section_content is removed/commented
# from .fact_refinement import get_fact_critique, fact_improvement_response
# from .insight_refinement import get_insight_critique, insight_improvement_response
# Prompts
from .prompts import persona, analysis_specs, output_format

# Removed utils import

# --- Function to Generate ONLY the Initial Section ---
def generate_initial_section(section, documents, persona, analysis_specs, output_format, model):
    """
    Generates, cleans, repairs, and returns the initial HTML content for a single section.
    Accepts a pre-configured model instance.
    """
    section_num = section["number"]
    section_title = section["title"]
    section_specs = section["specs"]

    print(f"Section Processor: Section {section_num}: GENERATING initial content for '{section_title}'")

    # Construct the full prompt including the document list (now base64 encoded PDFs)
    # Gemini's generate_content can handle a list containing text and multimodal parts.
    # We'll structure the prompt text first, then the documents.
    section_instruction = f"""
{persona}

Please create section {section_num}: "{section_title}" for a company profile, focusing *only* on this section.

SECTION SPECIFICATIONS:
{section_specs}

ANALYSIS SPECIFICATIONS (Apply to Section {section_num} content):
{analysis_specs}

OUTPUT FORMATTING INSTRUCTIONS (Apply to Section {section_num} content):
{output_format}

IMPORTANT: Generate *only* the HTML content for section {section_num}, starting with '<div class="section" id="section-{section_num}">' and ending with '</div>'. Base your analysis *strictly* on the provided documents.
"""

    # Prepare the input list for generate_content: instruction text + document parts
    api_input = [section_instruction] + documents # Combine instruction string with list of document dicts

    try:
        print(f"Section Processor: Section {section_num}: Preparing API call")

        # Use the passed model instance
        if not model:
            # This shouldn't happen if app.py checks, but defensive coding
            raise ValueError("No valid model instance provided to generate_initial_section")

        print(f"Section Processor: Section {section_num}: Calling API (cached_generate_content)")
        # Pass the combined input list and the model instance
        # Timeout increased slightly as multi-modal processing can take longer
        section_response = cached_generate_content(model, api_input, section_num=section_num, cache_enabled=True, timeout=300)

        # Defensive check for response and text attribute
        if section_response is None or not hasattr(section_response, 'text'):
             # Attempt to get feedback if available
             feedback = getattr(section_response, 'prompt_feedback', 'No feedback available.')
             raise ValueError(f"API response object is invalid or missing 'text' attribute. Feedback: {feedback}")

        initial_content_raw = section_response.text
        print(f"Section Processor: Section {section_num}: API call complete (received {len(initial_content_raw)} chars)")

        if not initial_content_raw or not initial_content_raw.strip():
             print(f"Section Processor: Section {section_num}: Warning - API returned empty content.")
             # Create standard error HTML
             initial_content_repaired = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">Error: API returned empty content for this section.</p></div>'
        else:
            # Proceed with cleaning and repair
            print(f"Section Processor: Section {section_num}: Cleaning LLM output")
            initial_content_cleaned = clean_llm_output(initial_content_raw, section_num, section_title)

            print(f"Section Processor: Section {section_num}: Repairing HTML")
            initial_content_repaired = repair_html(initial_content_cleaned, section_num, section_title)

            # Final validation check after repair
            if not validate_html(initial_content_repaired):
                 print(f"Section Processor: Section {section_num}: Warning - Invalid HTML structure detected even after repair.")
                 # Fallback if repair still results in invalid or empty HTML
                 if not initial_content_repaired or not initial_content_repaired.strip():
                      initial_content_repaired = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">Error: Failed to generate or repair valid HTML content.</p></div>'
                 # Optionally, keep the invalid HTML but wrap it in an error message? Less ideal.

        print(f"Section Processor: Section {section_num}: Content generated and processed.")
        # Return the section number and the final HTML string (could be error HTML)
        return section_num, initial_content_repaired

    except TimeoutError as e:
        error_msg = f"TIMEOUT generating Section {section_num}: {str(e)}"
        print(f"Section Processor: {error_msg}")
        error_content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Processing timed out for section {section_num}.</p></div>'
        # Return the error content so app.py knows it failed but has a placeholder
        return section_num, error_content # Return error HTML, don't raise

    except Exception as e:
        error_msg = f"ERROR generating initial content for section {section_num}: {type(e).__name__} - {str(e)}"
        print(f"Section Processor: {error_msg}")
        traceback.print_exc() # Print full traceback to console for debugging
        error_content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Could not generate initial content for section {section_num}: {str(e)}</p></div>'
        # Instead of re-raising, return the error content. App.py will check for <p class="error">.
        return section_num, error_content


# --- Refinement Function (Kept structurally but not called by app.py) ---
# def refine_section_content(section, initial_content, documents, persona, analysis_specs, output_format):
#    """Performs Fact and Insight refinement sequence on initial content."""
#    # ... (Keep internal logic but ensure it doesn't rely on removed globals/timers)
#    # ... (This function would need 'documents' passed if activated)
#    print(f"Section Processor: refine_section_content called for section {section['number']} (Currently Inactive in Gradio App)")
#    # Return initial content for now if called accidentally
#    return initial_content