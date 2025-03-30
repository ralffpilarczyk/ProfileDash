# --- START OF FILE src/section_processor.py ---

"""
Section processor module for ProfileDash
Handles processing of individual sections
"""

import time
import re
import traceback # Import traceback for detailed errors

# Use relative imports for modules within the src package
from .api_client import cached_generate_content, create_insight_model, create_fact_model # Added create_fact_model
# Import from html_generator now using relative import
from .html_generator import save_section, load_section, validate_html, repair_html, clean_llm_output
# Import refinement functions here using relative import
from .fact_refinement import get_fact_critique, fact_improvement_response
from .insight_refinement import get_insight_critique, insight_improvement_response
# --- REMOVED import for question_refinement ---
from .utils import get_elapsed_time # Assuming get_elapsed_time is in src/utils.py
from .prompts import persona, analysis_specs, output_format
# from .section_definitions import sections # sections is passed in, no need to import here

# --- Function to Generate ONLY the Initial Section ---
# MODIFIED - REMOVED start_time_ref argument
def generate_initial_section(section, documents, persona, analysis_specs, output_format, profile_folder):
    """Generates, cleans, repairs, and returns the initial content for a single section."""
    section_num = section["number"]
    section_title = section["title"]
    section_specs = section["specs"]

    # get_elapsed_time is imported from .utils at the top

    print(f"\n{get_elapsed_time()} Section {section_num}: GENERATING initial content for '{section_title}'")

    section_instruction = f"""
    Please create section {section_num}: {section_title} for a company profile.
    Specs: {section_specs}
    <analysis_specs>{analysis_specs}</analysis_specs>
    HTML REQUIREMENTS:
    <div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><!-- content --></div>
    RULES: Valid HTML, closed tags (<br/> self-closing), tables need thead/tbody.
    """

    try:
        section_start_time_local = time.time() # Local timer for this section attempt
        # section_timeout = 600 # This timeout wasn't actively used in the original logic, keeping for reference

        print(f"{get_elapsed_time()} Section {section_num}: Preparing API call")
        section_docs = documents.copy() # Use the passed-in documents
        prompt = f"{persona} {section_instruction} {output_format}"
        section_docs.append(prompt)

        # Create the appropriate model for initial generation (using insight model as before)
        print(f"{get_elapsed_time()} Section {section_num}: Creating insight model instance")
        insight_model = create_insight_model() # Call the imported function

        print(f"{get_elapsed_time()} Section {section_num}: Calling API (cached_generate_content)")
        # Pass the created model instance
        section_response = cached_generate_content(insight_model, section_docs, section_num=section_num, timeout=240)

        # Defensive check for response and text attribute
        if section_response is None or not hasattr(section_response, 'text'):
             raise ValueError("API response object is invalid or missing 'text' attribute.")

        initial_content_raw = section_response.text
        print(f"{get_elapsed_time()} Section {section_num}: API call complete (received {len(initial_content_raw)} chars)")

        if not initial_content_raw.strip():
             print(f"{get_elapsed_time()} Section {section_num}: Warning - API returned empty content.")
             # Handle empty content appropriately - maybe return error HTML?
             initial_content_repaired = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">Error: API returned empty content.</p></div>'
        else:
            print(f"{get_elapsed_time()} Section {section_num}: Cleaning LLM output")
            initial_content_cleaned = clean_llm_output(initial_content_raw, section_num, section_title)

            print(f"{get_elapsed_time()} Section {section_num}: Repairing HTML")
            initial_content_repaired = repair_html(initial_content_cleaned, section_num, section_title)

            if not validate_html(initial_content_repaired):
                 print(f"{get_elapsed_time()} Section {section_num}: Warning - Invalid HTML structure detected even after repair.")
                 # Fallback if repair still results in invalid or empty HTML
                 if not initial_content_repaired or not initial_content_repaired.strip():
                      initial_content_repaired = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">Error: Failed to generate or repair content.</p></div>'

        # --- AVOID SAVING INTERMEDIATE FILES IN GRADIO CONTEXT ---
        # save_section(profile_folder, section_num, initial_content_repaired)
        # print(f"{get_elapsed_time()} Section {section_num}: Saved initial section {section_num}")
        print(f"{get_elapsed_time()} Section {section_num}: Content generated (saving skipped).")
        # --- END OF CHANGE ---

        return section_num, initial_content_repaired

    except TimeoutError as e:
        error_msg = f"TIMEOUT generating Section {section_num}: {str(e)}"
        print(f"{get_elapsed_time()} {error_msg}")
        error_content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Processing timed out for section {section_num}</p></div>'
        # --- AVOID SAVING INTERMEDIATE FILES IN GRADIO CONTEXT ---
        # save_section(profile_folder, section_num, error_content)
        # --- END OF CHANGE ---
        # Return the error content so app.py knows it failed but has placeholder
        return section_num, error_content
    except Exception as e:
        error_msg = f"ERROR generating initial content for section {section_num}: {str(e)}"
        print(f"{get_elapsed_time()} {error_msg}")
        traceback.print_exc() # Print full traceback to console for debugging
        error_content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Could not generate initial content for section {section_num}: {str(e)}</p></div>'
        # --- AVOID SAVING INTERMEDIATE FILES IN GRADIO CONTEXT ---
        # save_section(profile_folder, section_num, error_content)
        # --- END OF CHANGE ---
        # Re-raise the exception so the ThreadPoolExecutor knows the future failed
        # This allows app.py to catch it in the future.result() call
        raise Exception(f"Error generating initial content for section {section_num}: {e}")


# --- Function to Refine a Single Section ---
# (Imports are handled at module level now with relative paths)
# MODIFIED - REMOVED start_time_ref argument
def refine_section_content(section, initial_content, documents, persona, analysis_specs, output_format, profile_folder):
    """Performs Fact and Insight refinement sequence on initial content."""
    section_num = section["number"]
    section_title = section["title"]
    section_specs = section["specs"]

    # get_elapsed_time is imported from .utils at the top

    print(f"{get_elapsed_time()} Section {section_num}: Starting refinement for '{section_title}'")

    # Prepare context instruction (might be slightly different for refinement)
    section_instruction_context = f"""
    Context: Refining section {section_num}: {section_title}. Original Spec: {section_specs}
    Analysis Specs: <analysis_specs>{analysis_specs}</analysis_specs>
    """
    # Output format reminder is handled within the refinement functions' prompts

    current_content = initial_content
    content_after_fact = initial_content # Start assuming failure

    # --- Fact Refinement ---
    print(f"\n{get_elapsed_time()} Section {section_num}: --- Fact Refinement ---")
    try:
        print(f"{get_elapsed_time()} Section {section_num}: Performing fact critique")
        # Pass context, not full prompt format specifiers
        _, fact_critique_text = get_fact_critique(section_instruction_context, current_content)

        if "Error: Could not generate" in fact_critique_text or not fact_critique_text.strip():
             print(f"{get_elapsed_time()} Section {section_num}: Skipping fact improvement due to critique error or empty critique.")
             content_after_fact = current_content
        else:
            try:
                print(f"{get_elapsed_time()} Section {section_num}: Applying fact improvements")
                # Call fact_improvement_response which uses relative imports internally
                _, fact_improved_content = fact_improvement_response(
                    section_instruction_context, current_content, fact_critique_text, section_num, section_title
                )
                content_after_fact = fact_improved_content
                print(f"{get_elapsed_time()} Section {section_num}: Fact improvement successful.")
            except Exception as fact_improve_e:
                 print(f"{get_elapsed_time()} Section {section_num}: Fact improvement API call FAILED: {fact_improve_e}. Using content from before this step.")
                 traceback.print_exc()
                 content_after_fact = current_content # Revert to content before fact improvement attempt

    except Exception as fact_critique_e:
        print(f"{get_elapsed_time()} Section {section_num}: Fact critique generation FAILED: {fact_critique_e}. Skipping fact refinement.")
        traceback.print_exc()
        content_after_fact = current_content # Keep original if critique failed

    # Update current content for the next stage
    current_content = content_after_fact

    # --- Insight Refinement ---
    print(f"\n{get_elapsed_time()} Section {section_num}: --- Insight Refinement ---")
    try:
        print(f"{get_elapsed_time()} Section {section_num}: Performing insight critique")
        # Pass context, not full prompt format specifiers
        _, insight_critique_text = get_insight_critique(section_instruction_context, current_content)

        if "Error: Could not generate" in insight_critique_text or not insight_critique_text.strip():
            print(f"{get_elapsed_time()} Section {section_num}: Skipping insight improvement due to critique error or empty critique.")
            # Keep current_content (which holds result after fact refinement)
        else:
            try:
                print(f"{get_elapsed_time()} Section {section_num}: Applying insight improvements")
                # Call insight_improvement_response which uses relative imports internally
                _, insight_improved_content = insight_improvement_response(
                    section_instruction_context, current_content, insight_critique_text, section_num, section_title
                )
                current_content = insight_improved_content # Update current content if successful
                print(f"{get_elapsed_time()} Section {section_num}: Insight improvement successful.")
            except Exception as insight_improve_e:
                print(f"{get_elapsed_time()} Section {section_num}: Insight improvement API call FAILED: {insight_improve_e}. Using content from before this step.")
                traceback.print_exc()
                # current_content remains unchanged (holds result after fact refinement)

    except Exception as insight_critique_e:
        print(f"{get_elapsed_time()} Section {section_num}: Insight critique generation FAILED: {insight_critique_e}. Skipping insight refinement.")
        traceback.print_exc()
        # current_content remains unchanged (holds result after fact refinement)

    # --- Final Output ---
    final_refined_content = current_content # This holds the result after all successful/attempted refinements
    print(f"\n{get_elapsed_time()} Section {section_num}: --- Finalizing Refined Content ---")

    # Final clean and repair just in case refinement steps introduced issues
    final_refined_content = clean_llm_output(final_refined_content, section_num, section_title)
    final_refined_content = repair_html(final_refined_content, section_num, section_title)

    # --- AVOID SAVING INTERMEDIATE FILES IN GRADIO CONTEXT ---
    # save_section(profile_folder, f"{section_num}_refined", final_refined_content)
    # print(f"{get_elapsed_time()} Section {section_num}: Saved refined section {section_num}")
    print(f"{get_elapsed_time()} Section {section_num}: Refined content generated (saving skipped).")
    # --- END OF CHANGE ---

    return final_refined_content

# --- END OF FILE src/section_processor.py ---