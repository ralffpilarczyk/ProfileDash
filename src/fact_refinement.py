"""
Fact Refinement module for ProfileDash
Handles fact-checking and factual improvements
"""
import traceback # Import traceback
from .api_client import cached_generate_content, create_fact_model
# Import from html_generator now
from .html_generator import repair_html, clean_llm_output, validate_html


def get_fact_critique(initial_instruction, answer):
    """
    Generate a fact critique for the given answer

    Args:
        initial_instruction: The original instruction/question for the section
        answer: The answer content to be critiqued (HTML expected)

    Returns:
        tuple: (critique_response, critique_text)
    """
    instruction = (
        f"Context: {initial_instruction}\n"
        f"Draft Answer to Critique:\n```html\n{answer}\n```\n\n"
        "Please critique the draft answer. "
        "Do a careful assessment of whether the answer is correct or not, and why."
        "Please focus **exclusively on factual correctness**. "
        # ... (rest of instructions) ...
    )

    from .prompts import persona
    prompt = f"{persona} {instruction}"
    from .document_processor import get_current_documents
    fact_critique_docs = get_current_documents()
    fact_critique_docs.append(prompt)
    fact_model = create_fact_model()

    fact_critique_response = None
    fact_critique_text = "Error: Could not generate fact critique."
    try:
        # Pass start_time_ref if available and needed for logging
        # from profile_meister import script_start_time
        # fact_critique_response = cached_generate_content(fact_model, fact_critique_docs, start_time_ref=script_start_time)
        fact_critique_response = cached_generate_content(fact_model, fact_critique_docs) # Assuming start_time isn't critical here
        critique_raw_text = getattr(fact_critique_response, 'text', '')
        fact_critique_text = critique_raw_text.replace("```", "").strip()
        if not fact_critique_text:
             fact_critique_text = "Error: Generated fact critique was empty."
    except Exception as e:
        print(f"ERROR generating fact critique: {e}")
        traceback.print_exc()

    return fact_critique_response, fact_critique_text


# MODIFIED to accept start_time_ref for logging
def fact_improvement_response(initial_instruction, answer, fact_critique_text, section_num=None, section_title=None, start_time_ref=None):
    """
    Generate an improved answer based on fact critique

    Args:
        initial_instruction: Original instruction/context.
        answer: Original answer HTML.
        fact_critique_text: Critique text.
        section_num: Section number.
        section_title: Section title.
        start_time_ref: Script start time for logging.

    Returns:
        tuple: (response_object, cleaned_repaired_html_text) - Raises Exception on API failure.
    """
    instruction = (
        f"Context: {initial_instruction}\n"
        f"Original Draft Answer:\n```html\n{answer}\n```\n\n"
        f"Fact Critique:\n```\n{fact_critique_text}\n```\n\n"
        "Please revise the original draft answer to fix ONLY the factual inaccuracies identified in the critique. "
        # ... (rest of instructions) ...
        "\nCRITICAL HTML REQUIREMENTS FOR YOUR REVISED ANSWER:\n"
        # ... (HTML requirements) ...
    )

    from prompts import persona, output_format
    prompt = f"{persona} {instruction} {output_format}"
    from document_processor import get_current_documents
    improved_docs = get_current_documents()
    improved_docs.append(prompt)
    fact_model = create_fact_model()

    fact_improvement_response = None
    fact_improvement_text_raw = ""
    try:
        # Pass start_time_ref for logging inside cached_generate_content
        fact_improvement_response = cached_generate_content(fact_model, improved_docs, section_num, start_time_ref=start_time_ref)
        if fact_improvement_response is None or not hasattr(fact_improvement_response, 'text'):
            raise ValueError(f"API call for fact improvement (Section {section_num}) did not return a valid response object.")
        fact_improvement_text_raw = fact_improvement_response.text
        if not fact_improvement_text_raw:
             raise ValueError(f"API returned an empty text response for fact improvement (Section {section_num}).")

    except Exception as e:
        # Error is logged within cached_generate_content if it happens there
        # Re-raise to signal failure to the caller (section_processor)
        raise e

    # Clean and repair only if API call succeeded
    fact_improvement_text_cleaned = clean_llm_output(fact_improvement_text_raw, section_num, section_title)
    fact_improvement_text = repair_html(fact_improvement_text_cleaned, section_num, section_title)

    if not validate_html(fact_improvement_text):
         print(f"Warning: Fact-improved HTML for section {section_num} failed validation after repair.")

    return fact_improvement_response, fact_improvement_text