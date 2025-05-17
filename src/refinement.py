"""
Refinement module for ProfileDash
Handles both fact-checking and insight refinement for generated content.
"""
import traceback
# Use relative imports consistently
from .api_client import cached_generate_content, create_fact_model, create_insight_model
from .html_generator import repair_html, clean_llm_output, validate_html
# Prompts needed if this module is activated
from .prompts import persona, output_format

# --- Fact Refinement Functions ---

def get_fact_critique(initial_instruction, answer, documents):
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
        "Focus **exclusively on completeness,factual correctness and verifiability** against the documents. "
        "Identify specific gaps towards the initial instructions. Identify statements in the draft that are unsupported or contradicted by the documents. "
        "Do not critique style or insight unless it relates to factual accuracy."
        "Output only the critique text."
    )

    prompt = f"{persona}\n{instruction}"
    fact_critique_input = [prompt] + documents
    fact_model = create_fact_model()

    fact_critique_response = None
    fact_critique_text = "Error: Could not generate fact critique."
    try:
        print(f"Fact Refinement: Generating critique...")
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
        tuple: (response_object, cleaned_repaired_html_text)
    """
    instruction = (
        f"Context: {initial_instruction}\n"
        f"Original Draft Answer:\n```html\n{answer}\n```\n\n"
        f"Fact Critique (points to address):\n```\n{fact_critique_text}\n```\n\n"
        "INSTRUCTIONS: Revise the 'Original Draft Answer' based *only* on the provided documents and addressing *only* the factual issues raised in the 'Fact Critique'. "
        "Add new information if needed to address the critique. Otherwise, do NOT add new information not present in the documents. "
        "Do NOT change the style or structure significantly unless required to fix a factual error. "
        "Ensure the revised answer remains grounded in the provided documents."
        "Do not reduce the amount of data or information in the original answer unless required to fix a factual error."
        "Output *only* the revised HTML for the section, adhering to the original HTML requirements."
    )

    prompt = f"{persona}\n{instruction}\n{output_format}"
    improved_input = [prompt] + documents
    fact_model = create_fact_model()

    fact_improvement_response = None
    fact_improvement_text_raw = ""
    try:
        print(f"Fact Refinement: Generating fact-improved response for section {section_num}...")
        fact_improvement_response = cached_generate_content(fact_model, improved_input, section_num)

        if fact_improvement_response is None or not hasattr(fact_improvement_response, 'text'):
            raise ValueError(f"API call for fact improvement (Section {section_num}) did not return a valid response object.")

        fact_improvement_text_raw = fact_improvement_response.text
        if not fact_improvement_text_raw:
             print(f"Fact Refinement Warning: API returned empty text for fact improvement (Section {section_num}). Returning original.")
             return fact_improvement_response, answer

        print(f"Fact Refinement: Fact-improved response generated for section {section_num}.")

    except Exception as e:
        print(f"Fact Refinement ERROR during improvement API call for section {section_num}: {e}")
        return None, answer

    fact_improvement_text_cleaned = clean_llm_output(fact_improvement_text_raw, section_num, section_title)
    fact_improvement_text = repair_html(fact_improvement_text_cleaned, section_num, section_title)

    if not validate_html(fact_improvement_text):
         print(f"Fact Refinement Warning: Fact-improved HTML for section {section_num} failed validation after repair.")
         return fact_improvement_response, fact_improvement_text

    return fact_improvement_response, fact_improvement_text


# --- Insight Refinement Functions ---

def get_insight_critique(initial_instruction, answer, documents):
    """
    Generate an insight critique for the given answer.

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
         "Focus **exclusively on the depth, breadth, and novelty of the reasoning and insights**. "
         "Are the conclusions well-supported by facts from the documents? Is the analysis superficial or does it uncover non-obvious connections? "
         "Does it address the 'why' behind the facts? Avoid critiquing factual correctness (assume facts are correct for this critique) or HTML format."
         "Output only the critique text."
    )

    prompt = f"{persona}\n{instruction}"
    insight_critique_input = [prompt] + documents
    insight_model = create_insight_model()

    insight_critique_response = None
    insight_critique_text = "Error: Could not generate insight critique."
    try:
        print(f"Insight Refinement: Generating critique...")
        insight_critique_response = cached_generate_content(insight_model, insight_critique_input)
        critique_raw_text = getattr(insight_critique_response, 'text', '')
        insight_critique_text = critique_raw_text.replace("```", "").strip()
        if not insight_critique_text:
             insight_critique_text = "Critique: No specific insight improvements suggested or critique generation failed."
        print(f"Insight Refinement: Critique generated.")
    except Exception as e:
        print(f"Insight Refinement ERROR generating insight critique: {e}")
        traceback.print_exc()
        insight_critique_text = f"Error: Could not generate insight critique due to exception: {e}"

    return insight_critique_response, insight_critique_text


def insight_improvement_response(initial_instruction, answer, insight_critique_text, documents, section_num=None, section_title=None):
    """
    Generate an improved answer based on insight critique.

    Args:
        initial_instruction: Original instruction/context.
        answer: Original answer HTML.
        insight_critique_text: Critique text focusing on insights.
        documents (list): The list of document parts (base64) for context.
        section_num: Section number.
        section_title: Section title.

    Returns:
        tuple: (response_object, cleaned_repaired_html_text)
    """
    instruction = (
        f"Context: {initial_instruction}\n"
        f"Original Draft Answer:\n```html\n{answer}\n```\n\n"
        f"Insight Critique (points to address):\n```\n{insight_critique_text}\n```\n\n"
        "INSTRUCTIONS: Revise the 'Original Draft Answer' based *only* on the provided documents, specifically addressing the strategic and analytical points raised in the 'Insight Critique'. "
        "Enhance the analysis, provide deeper reasoning, and draw non-obvious connections supported by the documents. "
        "Do NOT reduce the amount of data or information in the original answer unless required to fix a factual error."
        "Do NOT add new factual information not present in the documents. Maintain factual accuracy. "
        "Output *only* the revised HTML for the section, adhering to the original HTML requirements."
    )

    prompt = f"{persona}\n{instruction}\n{output_format}"
    improved_input = [prompt] + documents
    insight_model = create_insight_model()

    insight_improvement_response = None
    insight_improvement_text_raw = ""
    try:
        print(f"Insight Refinement: Generating insight-improved response for section {section_num}...")
        insight_improvement_response = cached_generate_content(insight_model, improved_input, section_num)

        if insight_improvement_response is None or not hasattr(insight_improvement_response, 'text'):
            raise ValueError(f"API call for insight improvement (Section {section_num}) did not return a valid response object.")

        insight_improvement_text_raw = insight_improvement_response.text
        if not insight_improvement_text_raw:
             print(f"Insight Refinement Warning: API returned empty text for insight improvement (Section {section_num}). Returning original.")
             return insight_improvement_response, answer

        print(f"Insight Refinement: Insight-improved response generated for section {section_num}.")

    except Exception as e:
        print(f"Insight Refinement ERROR during improvement API call for section {section_num}: {e}")
        return None, answer

    insight_improvement_text_cleaned = clean_llm_output(insight_improvement_text_raw, section_num, section_title)
    insight_improvement_text = repair_html(insight_improvement_text_cleaned, section_num, section_title)

    if not validate_html(insight_improvement_text):
         print(f"Insight Refinement Warning: Insight-improved HTML for section {section_num} failed validation after repair.")
         return insight_improvement_response, insight_improvement_text

    return insight_improvement_response, insight_improvement_text 