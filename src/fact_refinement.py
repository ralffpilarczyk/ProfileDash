"""
Fact Refinement module for ProfileDash
Handles fact-checking and factual improvements.
(Currently inactive in Gradio App, kept for potential future use)
"""
import traceback
# Use relative imports consistently
from .api_client import cached_generate_content, create_fact_model
from .html_generator import repair_html, clean_llm_output, validate_html
# Prompts needed if this module is activated
from .prompts import persona, output_format

# Removed global document dependency

def get_fact_critique(initial_instruction, answer, documents): # Expects documents if called
    """
    Generate a fact critique for the given answer.

    Args:
        initial_instruction: The original instruction/question for the section.
        answer: The answer content to be critiqued (HTML expected).
        documents (list): The list of document parts (base64) for context.

    Returns:
        tuple: (critique_response, critique_text)
    """
    instruction = (
        f"Context: {initial_instruction}\n"
        f"Draft Answer to Critique:\n```html\n{answer}\n```\n\n"
        "Please critique the draft answer based *only* on the provided documents. "
        "Focus **exclusively on factual correctness and verifiability** against the documents. "
        "Identify specific statements in the draft that are unsupported or contradicted by the documents. "
        "Do not critique style, insight, or completeness unless it relates to factual accuracy."
        "Output only the critique text."
    )

    prompt = f"{persona}\n{instruction}"
    # Combine prompt + documents for the API call
    fact_critique_input = [prompt] + documents
    fact_model = create_fact_model()

    fact_critique_response = None
    fact_critique_text = "Error: Could not generate fact critique."
    try:
        print(f"Fact Refinement: Generating critique...")
        # Pass the combined input list
        fact_critique_response = cached_generate_content(fact_model, fact_critique_input)
        critique_raw_text = getattr(fact_critique_response, 'text', '')
        fact_critique_text = critique_raw_text.replace("```", "").strip()
        if not fact_critique_text:
             fact_critique_text = "Critique: No factual inaccuracies found or critique generation failed."
        print(f"Fact Refinement: Critique generated.")
    except Exception as e:
        print(f"Fact Refinement ERROR generating fact critique: {e}")
        traceback.print_exc()
        fact_critique_text = f"Error: Could not generate fact critique due to exception: {e}"

    return fact_critique_response, fact_critique_text


def fact_improvement_response(initial_instruction, answer, fact_critique_text, documents, section_num=None, section_title=None):
    """
    Generate an improved answer based on fact critique.

    Args:
        initial_instruction: Original instruction/context.
        answer: Original answer HTML.
        fact_critique_text: Critique text.
        documents (list): The list of document parts (base64) for context.
        section_num: Section number.
        section_title: Section title.

    Returns:
        tuple: (response_object, cleaned_repaired_html_text) - Raises Exception on API failure.
    """
    instruction = (
        f"Context: {initial_instruction}\n"
        f"Original Draft Answer:\n```html\n{answer}\n```\n\n"
        f"Fact Critique (points to address):\n```\n{fact_critique_text}\n```\n\n"
        "INSTRUCTIONS: Revise the 'Original Draft Answer' based *only* on the provided documents and addressing *only* the factual issues raised in the 'Fact Critique'. "
        "Do NOT add new information not present in the documents. "
        "Do NOT change the style or structure significantly unless required to fix a factual error. "
        "Ensure the revised answer remains grounded in the provided documents. "
        "Output *only* the revised HTML for the section, adhering to the original HTML requirements."
    )

    prompt = f"{persona}\n{instruction}\n{output_format}" # Add output format reminder
    # Combine prompt + documents for the API call
    improved_input = [prompt] + documents
    fact_model = create_fact_model()

    fact_improvement_response = None
    fact_improvement_text_raw = ""
    try:
        print(f"Fact Refinement: Generating fact-improved response for section {section_num}...")
        # Pass the combined input list
        fact_improvement_response = cached_generate_content(fact_model, improved_input, section_num)

        if fact_improvement_response is None or not hasattr(fact_improvement_response, 'text'):
            raise ValueError(f"API call for fact improvement (Section {section_num}) did not return a valid response object.")

        fact_improvement_text_raw = fact_improvement_response.text
        if not fact_improvement_text_raw:
             # Don't raise error, just return original if revision is empty
             print(f"Fact Refinement Warning: API returned empty text for fact improvement (Section {section_num}). Returning original.")
             return fact_improvement_response, answer # Return original answer

        print(f"Fact Refinement: Fact-improved response generated for section {section_num}.")

    except Exception as e:
        print(f"Fact Refinement ERROR during improvement API call for section {section_num}: {e}")
        # Don't re-raise, just return the original answer on failure
        # traceback.print_exc() # Keep for debugging if needed
        return None, answer # Return original answer

    # Clean and repair only if API call succeeded and returned text
    fact_improvement_text_cleaned = clean_llm_output(fact_improvement_text_raw, section_num, section_title)
    fact_improvement_text = repair_html(fact_improvement_text_cleaned, section_num, section_title)

    if not validate_html(fact_improvement_text):
         print(f"Fact Refinement Warning: Fact-improved HTML for section {section_num} failed validation after repair.")
         # Decide whether to return the potentially broken HTML or revert to original
         # return fact_improvement_response, answer # Option: Revert on validation failure
         return fact_improvement_response, fact_improvement_text # Option: Return repaired but invalid

    return fact_improvement_response, fact_improvement_text