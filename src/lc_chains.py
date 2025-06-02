# src/lc_chains.py
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from .lc_models import AppendixStructuredData, HtmlOutput # Assuming lc_models.py
from .lc_prompts import appendix_data_extraction_prompt, html_appendix_generation_prompt # Assuming lc_prompts.py

def get_appendix_data_extraction_chain(llm: ChatGoogleGenerativeAI):
    """
    Creates and returns a LangChain chain for extracting structured appendix data.
    The LLM is expected to be a ChatGoogleGenerativeAI instance.
    """
    parser = PydanticOutputParser(pydantic_object=AppendixStructuredData)
    # The prompt needs to be constructed to correctly include format_instructions
    # and to signal where the PDF File objects should be considered by the LLM.
    # This might require careful structuring of the input to chain.invoke()
    chain = appendix_data_extraction_prompt | llm | parser
    return chain, parser # Return parser to get format_instructions

def get_html_appendix_generation_chain(llm: ChatGoogleGenerativeAI):
    """
    Creates and returns a LangChain chain for generating HTML appendix from structured data.
    """
    # The prompt expects {structured_appendix_data_json_string} and {output_format_rules}
    chain = html_appendix_generation_prompt | llm | StrOutputParser()
    return chain

# Helper to initialize LLM (can be expanded)
def get_gemini_llm(api_key: str, model_name: str = "gemini-2.0-flash", temperature: float = 0.1):
    return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=temperature, convert_system_message_to_human=True)
    # convert_system_message_to_human=True can sometimes help if the model strictly expects user/assistant turns after system.