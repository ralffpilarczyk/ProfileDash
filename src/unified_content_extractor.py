#!/usr/bin/env python3
"""
Unified Content Extractor
Extracts both tables and text content from PDFs in 10-page chunks
Most efficient approach - single pass through PDF
"""

import os
import time
import re
import json
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, Tk
from typing import Dict, List, Tuple

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Import the table post-processor
from table_postprocessor import TablePostProcessor

class TextPostProcessor:
    """Simple text post-processor for organizing and cleaning extracted text"""
    
    def __init__(self):
        self.key_topics_keywords = [
            'strategy', 'market', 'financial', 'performance', 'growth', 'revenue',
            'investment', 'risk', 'opportunity', 'competitive', 'customer', 'product',
            'service', 'technology', 'regulatory', 'sustainability', 'governance'
        ]
    
    def process_text_content(self, content: str, pdf_name: str) -> Dict:
        """Process extracted text content and create metadata"""
        
        cleaned_content = self.clean_text_content(content)
        sections = self.extract_text_sections(cleaned_content)
        
        metadata = {
            'source_pdf': pdf_name,
            'processing_date': datetime.now().isoformat(),
            'total_sections': len(sections),
            'total_word_count': len(cleaned_content.split()),
            'sections': sections,
            'summary': self.create_text_summary(sections)
        }
        
        return {
            'cleaned_content': cleaned_content,
            'metadata': metadata
        }
    
    def clean_text_content(self, content: str) -> str:
        """Basic text cleaning - remove extra whitespace, fix encoding issues"""
        if not content:
            return ""
        
        # Fix common encoding issues
        content = content.replace('â€™', "'").replace('â€œ', '"').replace('â€', '"')
        
        # Normalize whitespace
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single
        content = re.sub(r'\n\s*\n+', '\n\n', content)  # Multiple newlines to double
        
        # Remove trailing spaces from lines
        lines = [line.rstrip() for line in content.split('\n')]
        
        return '\n'.join(lines).strip()
    
    def extract_text_sections(self, content: str) -> List[Dict]:
        """Extract and organize text sections with metadata"""
        sections = []
        chunks = content.split('# Chunk ')
        
        for chunk_idx, chunk in enumerate(chunks[1:], 1):  # Skip first empty split
            chunk_sections = self.parse_chunk_text(chunk, chunk_idx)
            sections.extend(chunk_sections)
        
        return sections
    
    def parse_chunk_text(self, chunk_content: str, chunk_num: int) -> List[Dict]:
        """Parse text sections from a single chunk"""
        sections = []
        lines = chunk_content.split('\n')
        
        current_section = None
        section_content = []
        
        for line in lines:
            # Detect text section header (## Text Content: Title)
            section_match = re.match(r'^## Text Content:\s*(.+)$', line.strip())
            if section_match:
                # Save previous section if exists
                if current_section and section_content:
                    current_section['content'] = '\n'.join(section_content).strip()
                    current_section['word_count'] = len(current_section['content'].split())
                    current_section['key_topics'] = self.extract_key_topics(current_section['content'])
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'chunk': chunk_num,
                    'title': section_match.group(1).strip(),
                    'page': self.extract_page_number(chunk_content),
                    'location': f"Chunk {chunk_num}",
                    'content': '',
                    'word_count': 0,
                    'key_topics': []
                }
                section_content = []
                
            # Detect page info
            elif re.match(r'^\*\*Page:\*\*\s*(.+)$', line.strip()) and current_section:
                page_match = re.match(r'^\*\*Page:\*\*\s*(.+)$', line.strip())
                current_section['page'] = page_match.group(1).strip()
                
            # Collect section content (skip separators and headers)
            elif current_section and line.strip() and line.strip() != '---':
                section_content.append(line)
        
        # Don't forget the last section
        if current_section and section_content:
            current_section['content'] = '\n'.join(section_content).strip()
            current_section['word_count'] = len(current_section['content'].split())
            current_section['key_topics'] = self.extract_key_topics(current_section['content'])
            sections.append(current_section)
        
        return sections
    
    def extract_page_number(self, content: str) -> str:
        """Extract page number from chunk content"""
        page_match = re.search(r'\*\*Page:\*\*\s*([^\n]+)', content)
        if page_match:
            return page_match.group(1).strip()
        return "Unknown"
    
    def extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from text content"""
        text_lower = text.lower()
        found_topics = []
        
        for topic in self.key_topics_keywords:
            if topic in text_lower:
                found_topics.append(topic)
        
        return found_topics
    
    def create_text_summary(self, sections: List[Dict]) -> Dict:
        """Create summary statistics for text content"""
        if not sections:
            return {}
        
        total_words = sum([s['word_count'] for s in sections])
        pages_covered = list(set([s['page'] for s in sections if s['page'] != 'Unknown']))
        all_topics = [topic for s in sections for topic in s['key_topics']]
        common_topics = list(set(all_topics))
        
        return {
            'total_sections': len(sections),
            'total_words': total_words,
            'avg_words_per_section': total_words / len(sections) if sections else 0,
            'pages_covered': sorted(pages_covered),
            'common_topics': common_topics,
            'content_included': True
        }

class UnifiedContentExtractor:
    """Extracts both tables and text content in a single efficient pass"""
    
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

    def extract_content_from_chunk(self, uploaded_file, start_page: int, end_page: int, chunk_num: int):
        page_desc = f"page {start_page}" if start_page == end_page else f"pages {start_page}-{end_page}"
        
        prompt = f"""
Look at {page_desc} of this PDF and extract BOTH tables and text content.

# PART 1: TABLES
Find ALL tables and convert them to markdown format:

## Table [Number]: [Title if visible, or brief description]
**Page:** {start_page if start_page == end_page else f"{start_page}-{end_page}"}

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |

---

# PART 2: TEXT CONTENT
Extract all readable text content (excluding tables already captured above):

## Text Content: [Section title or brief description]
**Page:** {start_page if start_page == end_page else f"{start_page}-{end_page}"}

[All the text content here, maintaining paragraph structure and formatting]

---

RULES:
- Include ALL tables and ALL text content you see
- Don't duplicate content between tables and text sections
- If a table has no clear title, describe it briefly (e.g. "Financial Summary")
- For text, maintain paragraph breaks and structure
- Group related text into logical sections with descriptive titles
- Use "---" to separate different items
- If you see no tables, write "No tables found on {page_desc}"
- If you see no text, write "No text content found on {page_desc}"

Start extracting now:
"""

        try:
            print(f"Processing {page_desc} (tables + text)...")
            
            response = self.model.generate_content([prompt, uploaded_file])
            
            if response and response.text:
                return response.text.strip()
            else:
                return f"No response for {page_desc}"
                
        except Exception as e:
            return f"Error processing {page_desc}: {str(e)}"

    def extract_all_content(self, pdf_path: str, pages_per_chunk: int = 10):
        uploaded_file = self.upload_pdf(pdf_path)
        total_pages = self.get_pdf_page_count(pdf_path)
        
        print(f"PDF has {total_pages} pages, processing {pages_per_chunk} at a time")
        
        all_results = []
        
        for start_page in range(1, total_pages + 1, pages_per_chunk):
            end_page = min(start_page + pages_per_chunk - 1, total_pages)
            chunk_num = len(all_results) + 1
            
            result = self.extract_content_from_chunk(uploaded_file, start_page, end_page, chunk_num)
            all_results.append(result)
            
            time.sleep(1)  # Rate limiting
        
        # Cleanup
        try:
            genai.delete_file(uploaded_file.name)
        except:
            pass
        
        return all_results

    def separate_content_types(self, results: List[str]) -> Tuple[List[str], List[str]]:
        """Separate the combined results into tables and text content"""
        table_results = []
        text_results = []
        
        for result in results:
            # Split each result into table and text parts
            parts = result.split('# PART 2: TEXT CONTENT')
            
            if len(parts) >= 2:
                # Extract table part (remove the "# PART 1: TABLES" header)
                table_part = parts[0].replace('# PART 1: TABLES', '').strip()
                text_part = parts[1].strip()
            else:
                # Fallback - try to detect content type
                if '| ' in result and '|' in result:
                    table_part = result
                    text_part = "No text content extracted in this chunk"
                else:
                    table_part = "No tables found in this chunk"
                    text_part = result
            
            table_results.append(table_part)
            text_results.append(text_part)
        
        return table_results, text_results

    def save_results(self, results: List[str], pdf_path: str) -> Dict:
        """Save both table and text results to separate files"""
        pdf_name = Path(pdf_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Separate content types
        table_results, text_results = self.separate_content_types(results)
        
        # Save tables file
        tables_file = Path(f"extracted_tables_{pdf_name}_{timestamp}.md")
        with open(tables_file, 'w', encoding='utf-8') as f:
            f.write(f"# Extracted Tables from {pdf_name}\n\n")
            f.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for i, result in enumerate(table_results, 1):
                f.write(f"# Chunk {i}\n\n")
                f.write(result)
                f.write(f"\n\n{'='*50}\n\n")
        
        # Save text file
        text_file = Path(f"extracted_text_{pdf_name}_{timestamp}.md")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"# Extracted Text from {pdf_name}\n\n")
            f.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for i, result in enumerate(text_results, 1):
                f.write(f"# Chunk {i}\n\n")
                f.write(result)
                f.write(f"\n\n{'='*50}\n\n")
        
        print(f"Tables saved to: {tables_file}")
        print(f"Text saved to: {text_file}")
        
        return {
            'tables_file': str(tables_file),
            'text_file': str(text_file),
            'chunks_processed': len(results)
        }

def main():
    print("=== Unified Content Extractor ===")
    print("Extracts both tables and text content in 10-page chunks")
    print("Single pass through PDF - most efficient approach!")
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        api_key = input("Enter your Google API key: ").strip()
    
    if not api_key:
        print("Error: Need API key")
        return
    
    # Fixed chunk size of 10 pages
    pages_per_chunk = 10
    
    extractor = UnifiedContentExtractor(api_key)
    
    # Select file
    pdf_path = extractor.select_pdf_file()
    if not pdf_path:
        print("No file selected")
        return
    
    print(f"Selected: {pdf_path}")
    print(f"Processing in {pages_per_chunk}-page chunks...")
    
    try:
        start_time = time.time()
        
        # Extract content (both tables and text)
        results = extractor.extract_all_content(pdf_path, pages_per_chunk)
        
        # Save separated results
        save_results = extractor.save_results(results, pdf_path)
        
        # Post-process tables
        print(f"\n=== POST-PROCESSING TABLES ===")
        print("Cleaning up markdown and creating structured JSON metadata...")
        
        table_processor = TablePostProcessor()
        table_post_results = table_processor.process_file(save_results['tables_file'])
        
        # Post-process text
        print(f"\n=== POST-PROCESSING TEXT ===")
        print("Organizing text content and creating metadata...")
        
        text_processor = TextPostProcessor()
        with open(save_results['text_file'], 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        pdf_name = Path(pdf_path).stem
        text_post_results = text_processor.process_text_content(text_content, pdf_name)
        
        # Save text metadata
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_metadata_file = Path(f"extracted_text_{pdf_name}_{timestamp}_metadata.json")
        
        with open(text_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(text_post_results['metadata'], f, indent=2, ensure_ascii=False)
        
        # Summary
        processing_time = time.time() - start_time
        print(f"\n=== COMPLETE ===")
        print(f"Processing time: {processing_time:.1f} seconds")
        print(f"Processed {len(results)} chunks ({pages_per_chunk} pages each)")
        print(f"\nFiles created:")
        print(f"- Tables (original): {save_results['tables_file']}")
        print(f"- Tables (cleaned): {table_post_results['cleaned_file']}")
        print(f"- Tables (JSON): {table_post_results['metadata_file']}")
        print(f"- Text (original): {save_results['text_file']}")
        print(f"- Text (metadata): {text_metadata_file}")
        print(f"\nExtraction Summary:")
        print(f"- Tables found: {table_post_results['tables_found']}")
        print(f"- Financial tables: {table_post_results['financial_tables']}")
        print(f"- Text sections: {text_post_results['metadata']['total_sections']}")
        print(f"- Total words: {text_post_results['metadata']['total_word_count']}")
        print(f"\nOpen the JSON files for structured data access!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()