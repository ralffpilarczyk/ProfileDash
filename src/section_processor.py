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
from .html_generator import validate_html, repair_html, clean_llm_output
# Import refinement functions here using relative import
from .fact_refinement import get_fact_critique, fact_improvement_response
from .insight_refinement import get_insight_critique, insight_improvement_response
# --- REMOVED import for question_refinement ---
from .utils import get_elapsed_time # Assuming get_elapsed_time is in src/utils.py
from .prompts import persona, analysis_specs, output_format
# from .section_definitions import sections # sections is passed in, no need to import here

# --- Function to Generate ONLY the Initial Section ---
def generate_initial_section(section, documents, persona, analysis_specs, output_format, model):
    """Generates, cleans, repairs, and returns the initial content for a single section."""
    section_num = section["number"]
    section_title = section["title"]
    section_specs = section["specs"]

    print(f"\n{get_elapsed_time()} Section {section_num}: GENERATING initial content for '{section_title}'")

    # Construct the full prompt with document content
    section_instruction = f"""
    Please create section {section_num}: {section_title} for a company profile.
    
    SECTION SPECIFICATIONS:
    {section_specs}
    
    ANALYSIS SPECIFICATIONS:
    {analysis_specs}
    
    DOCUMENTS TO ANALYZE:
    {documents}
    
    HTML REQUIREMENTS:
    <div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><!-- content --></div>
    RULES: Valid HTML, closed tags (<br/> self-closing), tables need thead/tbody.
    """

    try:
        section_start_time_local = time.time()
        print(f"{get_elapsed_time()} Section {section_num}: Preparing API call")
        
        # Use the passed model instance
        if not model:
            raise Exception("No model instance provided")

        # Generate content with proper error handling
        try:
            response = cached_generate_content(
                model=model,
                prompt=section_instruction,
                section_num=section_num,
                cache_enabled=True,
                max_retries=3,
                timeout=180
            )
        except Exception as e:
            print(f"Error generating content for section {section_num}: {e}")
            raise

        if not response or not response.text:
            raise Exception(f"Empty response from API for section {section_num}")

        # Clean the response
        content = clean_llm_output(response.text)
        if not content:
            raise Exception(f"Empty content after cleaning for section {section_num}")

        # FIXED: Don't assign the result of validate_html to content
        # Just check if the HTML is valid
        if not validate_html(content):
            raise Exception(f"Invalid HTML for section {section_num}")

        # Now repair the HTML (content is still the HTML string)
        content = repair_html(content, section_num, section_title)
        if not content:
            raise Exception(f"Failed to repair HTML for section {section_num}")

        # Create the final section HTML
        final_content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2>{content}</div>'
        
        print(f"{get_elapsed_time()} Section {section_num}: Successfully generated content")
        return section_num, final_content

    except Exception as e:
        error_msg = f"Error in section {section_num}: {str(e)}"
        print(f"{get_elapsed_time()} {error_msg}")
        traceback.print_exc()
        error_content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: {error_msg}</p></div>'
        return section_num, error_content


# --- Function to Refine a Single Section ---
# (Imports are handled at module level now with relative paths)
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
    
    # FIXED: Don't assign the result of validate_html to content
    # Just check for validation
    if not validate_html(final_refined_content):
        print(f"{get_elapsed_time()} Section {section_num}: Warning - refined content failed validation, attempting repair")
    
    final_refined_content = repair_html(final_refined_content, section_num, section_title)

    # --- AVOID SAVING INTERMEDIATE FILES IN GRADIO CONTEXT ---
    # save_section(profile_folder, f"{section_num}_refined", final_refined_content)
    # print(f"{get_elapsed_time()} Section {section_num}: Saved refined section {section_num}")
    print(f"{get_elapsed_time()} Section {section_num}: Refined content generated (saving skipped).")
    # --- END OF CHANGE ---

    return final_refined_content