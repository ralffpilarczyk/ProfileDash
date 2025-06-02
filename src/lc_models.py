# src/lc_models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class AppendixDataItem(BaseModel):
    value: str = Field(description="The extracted numerical or text value")
    unit: Optional[str] = Field(None, description="Unit of the value, if applicable (e.g., S$ million, %)")
    context_snippet: str = Field(description="Short surrounding text for context")
    category: str = Field(description="Broad category (e.g., Operating Data, Financial Data, Other Data)")
    sub_category: Optional[str] = Field(None, description="More specific sub-category or table name from source")
    period: Optional[str] = Field(None, description="Time period or point in time (e.g., FY2024, Q1 2025)")
    source_document_hint: Optional[str] = Field(None, description="Filename or type of source document inferred by the LLM") # Clarified source
    source_page_hint: Optional[str] = Field(None, description="Page number in source, if discernible by the LLM") # Clarified source

class AppendixStructuredData(BaseModel):
    data_points: List[AppendixDataItem] = Field(description="A list of all extracted data items for the appendix")

class HtmlOutput(BaseModel): # Simple wrapper if you wanted structured HTML output, but we'll use StrOutputParser
    html_content: str = Field(description="The generated HTML content")