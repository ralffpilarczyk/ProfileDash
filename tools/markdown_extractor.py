#!/usr/bin/env python3
"""
Simple Markdown Table Extractor
Just gets all tables as markdown - no JSON headaches
"""

import os
import time
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, Tk

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Import the table post-processor
from table_postprocessor import TablePostProcessor

class SimpleMarkdownExtractor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            'gemini-2.0-flash',
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

    def select_pdf_file(self):
        root = Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        root.destroy()
        return file_path if file_path else None

    def upload_pdf(self, pdf_path: str):
        print(f"Uploading PDF...")
        
        uploaded_file = genai.upload_file(pdf_path)
        
        while uploaded_file.state.name == "PROCESSING":
            print("Processing...")
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)
        
        print("Ready!")
        return uploaded_file

    def get_pdf_page_count(self, pdf_path: str) -> int:
        try:
            import fitz
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            return page_count
        except ImportError:
            return int(input("How many pages in the PDF? "))

    def extract_tables_from_chunk(self, uploaded_file, start_page: int, end_page: int, chunk_num: int):
        page_desc = f"page {start_page}" if start_page == end_page else f"pages {start_page}-{end_page}"
        
        prompt = f"""
Look at {page_desc} of this PDF.

Find ALL tables and convert them to markdown format.

For each table you find:

## Table [Number]: [Title if visible, or brief description]
**Page:** {start_page if start_page == end_page else f"{start_page}-{end_page}"}

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |

---

Rules:
- Include ALL tables you see
- If a table has no clear title, describe it briefly (e.g. "Financial Summary" or "Revenue Breakdown")
- Don't skip tables because they're complex - just do your best
- Use "---" to separate different tables
- If you see no tables, just write "No tables found on {page_desc}"

Start extracting now:
"""

        try:
            print(f"Processing {page_desc}...")
            
            response = self.model.generate_content([prompt, uploaded_file])
            
            if response and response.text:
                return response.text.strip()
            else:
                return f"No response for {page_desc}"
                
        except Exception as e:
            return f"Error processing {page_desc}: {str(e)}"

    def extract_all_tables(self, pdf_path: str, pages_per_chunk: int = 10):
        uploaded_file = self.upload_pdf(pdf_path)
        total_pages = self.get_pdf_page_count(pdf_path)
        
        print(f"PDF has {total_pages} pages, processing {pages_per_chunk} at a time")
        
        all_results = []
        
        for start_page in range(1, total_pages + 1, pages_per_chunk):
            end_page = min(start_page + pages_per_chunk - 1, total_pages)
            chunk_num = len(all_results) + 1
            
            result = self.extract_tables_from_chunk(uploaded_file, start_page, end_page, chunk_num)
            all_results.append(result)
            
            time.sleep(1)  # Rate limiting
        
        # Cleanup
        try:
            genai.delete_file(uploaded_file.name)
        except:
            pass
        
        return all_results

    def save_results(self, results, pdf_path: str):
        pdf_name = Path(pdf_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_file = Path(f"extracted_tables_{pdf_name}_{timestamp}.md")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Extracted Tables from {pdf_name}\n\n")
            f.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"# Chunk {i}\n\n")
                f.write(result)
                f.write(f"\n\n{'='*50}\n\n")
        
        print(f"Results saved to: {output_file}")
        return output_file

def main():
    print("=== Simple Markdown Table Extractor ===")
    print("Extracts tables as markdown in 10-page chunks")
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        api_key = input("Enter your Google API key: ").strip()
    
    if not api_key:
        print("Error: Need API key")
        return
    
    # Fixed chunk size of 10 pages
    pages_per_chunk = 10
    
    extractor = SimpleMarkdownExtractor(api_key)
    
    # Select file
    pdf_path = extractor.select_pdf_file()
    if not pdf_path:
        print("No file selected")
        return
    
    print(f"Selected: {pdf_path}")
    print(f"Processing in {pages_per_chunk}-page chunks...")
    
    try:
        start_time = time.time()
        
        # Extract tables
        results = extractor.extract_all_tables(pdf_path, pages_per_chunk)
        
        # Save results
        output_file = extractor.save_results(results, pdf_path)
        
        # Post-process the extracted markdown
        print(f"\n=== POST-PROCESSING ===")
        print("Cleaning up markdown and creating structured JSON metadata...")
        
        processor = TablePostProcessor()
        post_process_results = processor.process_file(str(output_file))
        
        # Summary
        processing_time = time.time() - start_time
        print(f"\n=== COMPLETE ===")
        print(f"Processing time: {processing_time:.1f} seconds")
        print(f"Processed {len(results)} chunks ({pages_per_chunk} pages each)")
        print(f"\nFiles created:")
        print(f"- Original markdown: {output_file}")
        print(f"- Cleaned markdown: {post_process_results['cleaned_file']}")
        print(f"- JSON metadata: {post_process_results['metadata_file']}")
        print(f"- Tables found: {post_process_results['tables_found']}")
        print(f"- Financial tables: {post_process_results['financial_tables']}")
        print(f"\nOpen the JSON file for structured table data!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()