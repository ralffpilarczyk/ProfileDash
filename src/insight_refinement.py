"""
Insight Refinement module for ProfileDash
Handles insight critique and improvements
"""
import traceback # Import traceback
from .api_client import cached_generate_content, create_insight_model
# Import from html_generator now
from .html_generator import repair_html, clean_llm_output, validate_html


def get_insight_critique(initial_instruction, answer):
    """
    Generate an insight critique for the given answer

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
         "Please focus **exclusively on the depth and breath of the reasoning**, "
        # ... (rest of instructions) ...
    )

    from .prompts import persona
    prompt = f"{persona} {instruction}"
    from .document_processor import get_current_documents
    insight_critique_docs = get_current_documents()
    insight_critique_docs.append(prompt)
    insight_model = create_insight_model()

    insight_critique_response = None
    insight_critique_text = "Error: Could not generate insight critique."
    try:
        # MODIFIED - REMOVED start_time_ref argument from call
        insight_critique_response = cached_generate_content(insight_model, insight_critique_docs)
        critique_raw_text = getattr(insight_critique_response, 'text', '')
        insight_critique_text = critique_raw_text.replace("```", "").strip()
        if not insight_critique_text:
             insight_critique_text = "Error: Generated insight critique was empty."
    except Exception as e:
        print(f"ERROR generating insight critique: {e}")
        traceback.print_exc()

    return insight_critique_response, insight_critique_text


# MODIFIED - REMOVED start_time_ref argument
def insight_improvement_response(initial_instruction, answer, insight_critique_text, section_num=None, section_title=None):
    """
    Generate an improved answer based on insight critique

    Args:
        initial_instruction: Original instruction/context.
        answer: Original answer HTML.
        insight_critique_text: Critique text.
        section_num: Section number.
        section_title: Section title.

    Returns:
        tuple: (response_object, cleaned_repaired_html_text) - Raises Exception on API failure.
    """
    instruction = (
        f"Context: {initial_instruction}\n"
        f"Original Draft Answer:\n```html\n{answer}\n```\n\n"
        f"Insight Critique:\n```\n{insight_critique_text}\n```\n\n"
        "Please revise the original draft answer to address the strategic and analytical gaps identified in the insight critique. "
        # ... (rest of instructions) ...
        "\nCRITICAL HTML REQUIREMENTS FOR YOUR REVISED ANSWER:\n"
        # ... (HTML requirements) ...
    )
    from prompts import persona, output_format
    prompt = f"{persona} {instruction} {output_format}"
    from document_processor import get_current_documents
    improved_docs = get_current_documents()
    improved_docs.append(prompt)
    insight_model = create_insight_model()

    insight_improvement_response = None
    insight_improvement_text_raw = ""
    try:
        # MODIFIED - REMOVED start_time_ref argument from call
        insight_improvement_response = cached_generate_content(insight_model, improved_docs, section_num)
        if insight_improvement_response is None or not hasattr(insight_improvement_response, 'text'):
            raise ValueError(f"API call for insight improvement (Section {section_num}) did not return a valid response object.")
        insight_improvement_text_raw = insight_improvement_response.text
        if not insight_improvement_text_raw:
            raise ValueError(f"API returned an empty text response for insight improvement (Section {section_num}).")

    except Exception as e:
        # Error is logged within cached_generate_content if it happens there
        # Re-raise to signal failure to the caller (section_processor)
        raise e

    # Clean and repair only if API call succeeded
    insight_improvement_text_cleaned = clean_llm_output(insight_improvement_text_raw, section_num, section_title)
    insight_improvement_text = repair_html(insight_improvement_text_cleaned, section_num, section_title)

    if not validate_html(insight_improvement_text):
         print(f"Warning: Insight-improved HTML for section {section_num} failed validation after repair.")

    return insight_improvement_response, insight_improvement_text