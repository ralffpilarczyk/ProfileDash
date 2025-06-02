# src/lc_prompts.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

# --- Prompts for Appendix Generation ---

# System Prompt for Structured Data Extraction (Chain A)
APPENDIX_EXTRACTION_SYSTEM_PROMPT_TEXT = """You are an expert financial data analyst. Your task is to meticulously extract all relevant numerical data points and key textual facts from the provided PDF document(s). This extracted data will form a comprehensive data appendix for a company profile.

You MUST adhere strictly to the JSON output format defined by the Pydantic schema that will be provided in the user's prompt via '{format_instructions}'.

For each distinct data point you identify, ensure you capture:
- 'value': The extracted numerical or text value itself.
- 'unit': The unit of the value if applicable (e.g., "S$ million", "%", "mobile customers"). If no unit, use null or omit.
- 'context_snippet': A short, verbatim surrounding text phrase (approx. 5-15 words) that gives context to the value.
- 'category': A broad category for the data point. Choose from: 'Operating Data', 'Financial Data - Income Statement', 'Financial Data - Balance Sheet', 'Financial Data - Cash Flow', 'Financial Data - Ratios', 'Shareholder Data', 'Strategic Data', 'Segment Data - [Segment Name]', 'Other Data'. For segment data, replace '[Segment Name]' with the actual segment name if discernible.
- 'sub_category': A more specific sub-category or the name of the table/heading from the source document if apparent (e.g., "Operating Revenue", "Mobile Subscribers India", "Nxera Data Centre Capacity").
- 'period': The time period or point in time the data refers to (e.g., "FY2024", "Q1 2025", "As of 31 March 2024", "For the year ended Dec 31, 2023"). Be as specific as the document allows.
- 'source_document_hint': A brief hint about which document this data might be from if multiple are provided (e.g., "Annual Report", "Q1 Earnings Release", "Investor Deck"). If only one document, you can state its general nature.
- 'source_page_hint': The page number in the source document where the information was found, if this is clearly discernible. If not, use null or omit.

Key Instructions:
- Extract comprehensively: Aim to capture all meaningful figures and key factual statements.
- Accuracy is paramount: Ensure extracted values and context are precise.
- Do not perform calculations or aggregations: Extract data as it appears in the document.
- Duplicates: If the same data point appears multiple times (e.g., in a summary and a detailed table), extract it each time with its respective context if the context or presentation differs.
- If a field (like 'unit', 'sub_category', 'source_page_hint') is not applicable or clearly found for a data point, you may omit it or use a null value in the JSON.
- Ensure your final output is a single, valid JSON object adhering to the provided Pydantic schema, typically a root object containing a list called "data_points".
"""

# Human Prompt for Structured Data Extraction (Chain A)
# This prompt is simpler. The actual PDF File objects will be passed to the LLM
# either via a specific key in the chain's input dictionary that ChatGoogleGenerativeAI
# recognizes for multimodal content, or by constructing the HumanMessage content list explicitly
# before calling the LLM.
APPENDIX_EXTRACTION_HUMAN_PROMPT_TEXT = """Please analyze the provided document(s) and extract data points for the appendix.
Ensure your output is a valid JSON object that strictly follows this Pydantic schema:
{format_instructions}
"""

# Create ChatPromptTemplate for Appendix Data Extraction
appendix_data_extraction_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=APPENDIX_EXTRACTION_SYSTEM_PROMPT_TEXT),
    HumanMessage(content=APPENDIX_EXTRACTION_HUMAN_PROMPT_TEXT)
])


# --- Prompts for HTML Appendix Generation (Chain B) ---

# System Prompt for HTML Appendix Generation
HTML_APPENDIX_SYSTEM_PROMPT_TEXT = """You are an expert at formatting structured financial and operational data into clear, human-readable HTML for a company profile appendix.
You will be given a JSON string representing a list of structured data points.
Your task is to organize these data points into logical HTML tables (using class="data-table") and lists (ul/ol/li).
Group related data points by their 'category' and 'sub_category' from the input JSON.
Use the general HTML formatting rules provided below.
Ensure all provided data points are accurately represented in the HTML output.

IMPORTANT:
- The main section wrapper (<div class="section" id="section-32">) and the H2 header (<h2>32. Appendix</h2>) will be added EXTERNALLY to your output.
- Your output should start DIRECTLY with the first HTML element of the appendix content (e.g., the first `<h3>` for a category, or the first `<table class="data-table">`).
- For each table, include appropriate `<thead>` with `<th>` for headers (e.g., "Metric", "Period", "Value", "Unit", "Context/Source Page").
- For each data point in a table row (`<tr>`), use `<td>` for the cells.
- Use `<h3>` or `<h4>` for major category or sub-category headings within the appendix.
"""

# Human Prompt for HTML Appendix Generation
HTML_APPENDIX_HUMAN_PROMPT_TEMPLATE = """Here is the structured data extracted from the company documents:
<structured_data_json>
{structured_appendix_data_json_string}
</structured_data_json>

Here are the general HTML formatting guidelines to follow:
<html_formatting_rules>
{output_format_rules}
</html_formatting_rules>

Please generate ONLY the inner HTML content for the Appendix (Section 32), starting with the first major heading (e.g., <h3>Financial Data</h3>) or table.
"""

# Create ChatPromptTemplate for HTML Appendix Generation
html_appendix_generation_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=HTML_APPENDIX_SYSTEM_PROMPT_TEXT),
    HumanMessage(content=HTML_APPENDIX_HUMAN_PROMPT_TEMPLATE)
])