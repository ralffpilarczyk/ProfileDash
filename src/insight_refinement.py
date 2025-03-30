"""
Insight Refinement module for ProfileDash
Handles insight critique and improvements.
(Currently inactive in Gradio App, kept for potential future use)
"""
import traceback
# Use relative imports consistently
from .api_client import cached_generate_content, create_insight_model # Use insight model here
from .html_generator import repair_html, clean_llm_output, validate_html
# Prompts needed if this module is activated
from .prompts import persona, output_format

# Removed global document dependency

def get_insight_critique(initial_instruction, answer, documents): # Expects documents if called
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
    # Combine prompt + documents for the API call
    insight_critique_input = [prompt] + documents
    insight_model = create_insight_model() # Use the insight model

    insight_critique_response = None
    insight_critique_text = "Error: Could not generate insight critique."
    try:
        print(f"Insight Refinement: Generating critique...")
        # Pass the combined input list
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
        tuple: (response_object, cleaned_repaired_html_text) - Raises Exception on API failure.
    """
    instruction = (
        f"Context: {initial_instruction}\n"
        f"Original Draft Answer:\n```html\n{answer}\n```\n\n"
        f"Insight Critique (points to address):\n```\n{insight_critique_text}\n```\n\n"
        "INSTRUCTIONS: Revise the 'Original Draft Answer' based *only* on the provided documents, specifically addressing the strategic and analytical points raised in the 'Insight Critique'. "
        "Enhance the analysis, provide deeper reasoning, and draw non-obvious connections supported by the documents. "
        "Do NOT add new factual information not present in the documents. Maintain factual accuracy. "
        "Output *only* the revised HTML for the section, adhering to the original HTML requirements."
    )

    prompt = f"{persona}\n{instruction}\n{output_format}" # Add output format reminder
    # Combine prompt + documents for the API call
    improved_input = [prompt] + documents
    insight_model = create_insight_model() # Use insight model

    insight_improvement_response = None
    insight_improvement_text_raw = ""
    try:
        print(f"Insight Refinement: Generating insight-improved response for section {section_num}...")
        # Pass the combined input list
        insight_improvement_response = cached_generate_content(insight_model, improved_input, section_num)

        if insight_improvement_response is None or not hasattr(insight_improvement_response, 'text'):
            raise ValueError(f"API call for insight improvement (Section {section_num}) did not return a valid response object.")

        insight_improvement_text_raw = insight_improvement_response.text
        if not insight_improvement_text_raw:
             # Don't raise error, just return original if revision is empty
             print(f"Insight Refinement Warning: API returned empty text for insight improvement (Section {section_num}). Returning original.")
             return insight_improvement_response, answer # Return original answer

        print(f"Insight Refinement: Insight-improved response generated for section {section_num}.")

    except Exception as e:
        print(f"Insight Refinement ERROR during improvement API call for section {section_num}: {e}")
        # Don't re-raise, just return the original answer on failure
        # traceback.print_exc() # Keep for debugging if needed
        return None, answer # Return original answer

    # Clean and repair only if API call succeeded and returned text
    insight_improvement_text_cleaned = clean_llm_output(insight_improvement_text_raw, section_num, section_title)
    insight_improvement_text = repair_html(insight_improvement_text_cleaned, section_num, section_title)

    if not validate_html(insight_improvement_text):
         print(f"Insight Refinement Warning: Insight-improved HTML for section {section_num} failed validation after repair.")
         # Decide whether to return the potentially broken HTML or revert to original
         # return insight_improvement_response, answer # Option: Revert on validation failure
         return insight_improvement_response, insight_improvement_text # Option: Return repaired but invalid

    return insight_improvement_response, insight_improvement_text