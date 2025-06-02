#!/usr/bin/env python3
"""
Table Post-Processor for ProfileDash
Cleans up markdown formatting and creates metadata - preserves all raw data
"""

import re
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class TablePostProcessor:
    def __init__(self):
        self.financial_keywords = [
            'revenue', 'ebitda', 'profit', 'loss', 'cash', 'debt', 'assets', 
            'liabilities', 'equity', 'dividend', 'capex', 'margin', 'arpu'
        ]
        
        self.table_types = {
            'income_statement': ['income statement', 'profit', 'revenue', 'ebitda', 'operating'],
            'balance_sheet': ['balance', 'assets', 'liabilities', 'equity', 'financial position'],
            'cash_flow': ['cash flow', 'operating cash', 'investing', 'financing'],
            'performance_metrics': ['performance', 'kpi', 'arpu', 'customers', 'market share'],
            'financial_summary': ['summary', 'highlights', 'glance', 'overview']
        }

    def process_file(self, markdown_file: str) -> Dict:
        """
        Process a markdown file - fix formatting and create metadata
        Returns processing results
        """
        print(f"Processing: {markdown_file}")
        
        # Read original file
        with open(markdown_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Fix markdown formatting issues
        cleaned_content = self.fix_markdown_formatting(original_content)
        
        # Extract table metadata
        tables_metadata = self.extract_table_metadata(cleaned_content)
        
        # Create output files
        results = self.create_output_files(markdown_file, cleaned_content, tables_metadata)
        
        return results

    def fix_markdown_formatting(self, content: str) -> str:
        """
        Fix only broken markdown table formatting - preserve all content
        """
        lines = content.split('\n')
        fixed_lines = []
        
        in_table = False
        
        for i, line in enumerate(lines):
            # Detect table start
            if line.strip().startswith('|') and '|' in line.strip()[1:]:
                in_table = True
                fixed_lines.append(self.fix_table_line(line))
                
                # Check if next line needs a header separator
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('|'):
                        # This was a header, add separator if missing
                        if i + 2 < len(lines) and lines[i + 2].strip().startswith('|'):
                            # Add header separator
                            col_count = line.count('|') - 1
                            separator = '|' + '---|' * col_count
                            fixed_lines.append(separator)
                
            elif in_table and line.strip().startswith('|'):
                fixed_lines.append(self.fix_table_line(line))
                
            elif in_table and not line.strip():
                # Empty line might end table
                in_table = False
                fixed_lines.append(line)
                
            elif in_table and not line.strip().startswith('|'):
                # Non-table line, end table
                in_table = False
                fixed_lines.append(line)
                
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def fix_table_line(self, line: str) -> str:
        """
        Fix issues in a single table line
        """
        # Ensure line starts and ends with |
        line = line.strip()
        if not line.startswith('|'):
            line = '| ' + line
        if not line.endswith('|'):
            line = line + ' |'
        
        # Fix spacing around pipes
        line = re.sub(r'\s*\|\s*', ' | ', line)
        line = re.sub(r'^\s*\|\s*', '| ', line)
        line = re.sub(r'\s*\|\s*$', ' |', line)
        
        return line

    def extract_table_metadata(self, content: str) -> List[Dict]:
        """
        Extract metadata about tables without modifying content
        """
        tables = []
        chunks = content.split('# Chunk ')
        
        for chunk_idx, chunk in enumerate(chunks[1:], 1):  # Skip first empty split
            chunk_tables = self.parse_chunk_tables(chunk, chunk_idx)
            tables.extend(chunk_tables)
        
        return tables

    def parse_chunk_tables(self, chunk_content: str, chunk_num: int) -> List[Dict]:
        """
        Parse tables from a single chunk - include both metadata and actual table content
        """
        tables = []
        lines = chunk_content.split('\n')
        
        current_table = None
        table_content = []
        
        for line in lines:
            # Detect table header (## Table X: Title)
            table_match = re.match(r'^## Table (\d+|[^:]+):\s*(.+)$', line.strip())
            if table_match:
                # Save previous table if exists
                if current_table:
                    current_table['content'] = '\n'.join(table_content)
                    current_table['metrics'] = self.extract_key_metrics('\n'.join(table_content))
                    tables.append(current_table)
                
                # Start new table
                current_table = {
                    'chunk': chunk_num,
                    'table_id': table_match.group(1),
                    'title': table_match.group(2).strip(),
                    'page': self.extract_page_number(chunk_content),
                    'type': self.classify_table_type(table_match.group(2)),
                    'location': f"Chunk {chunk_num}, Table {table_match.group(1)}",
                    'content': ''  # Will be populated with actual table data
                }
                table_content = []
                
            # Detect page info
            page_match = re.match(r'^\*\*Page:\*\*\s*(.+)$', line.strip())
            if page_match and current_table:
                current_table['page'] = page_match.group(1).strip()
                
            # Collect table content
            elif line.strip().startswith('|') and current_table:
                table_content.append(line)
                
            # Table separator (---)
            elif line.strip() == '---' and current_table:
                # End current table
                current_table['content'] = '\n'.join(table_content)
                current_table['metrics'] = self.extract_key_metrics('\n'.join(table_content))
                tables.append(current_table)
                current_table = None
                table_content = []
        
        # Don't forget the last table
        if current_table:
            current_table['content'] = '\n'.join(table_content)
            current_table['metrics'] = self.extract_key_metrics('\n'.join(table_content))
            tables.append(current_table)
        
        return tables

    def extract_page_number(self, content: str) -> str:
        """
        Extract page number from chunk content
        """
        page_match = re.search(r'\*\*Page:\*\*\s*([^\n]+)', content)
        if page_match:
            return page_match.group(1).strip()
        return "Unknown"

    def classify_table_type(self, title: str) -> str:
        """
        Classify table type based on title keywords
        """
        title_lower = title.lower()
        
        for table_type, keywords in self.table_types.items():
            if any(keyword in title_lower for keyword in keywords):
                return table_type
        
        return "other"

    def extract_key_metrics(self, table_content: str) -> Dict:
        """
        Extract key financial metrics and structural info from table content
        """
        metrics = {
            'contains_financial_data': False,
            'currencies': [],
            'has_percentages': False,
            'row_count': 0,
            'column_count': 0,
            'financial_keywords': [],
            'key_figures': [],  # Extract actual numbers for quick reference
            'parsed_data': None  # Structured table data
        }
        
        if not table_content:
            return metrics
        
        content_lower = table_content.lower()
        lines = [line for line in table_content.split('\n') if line.strip().startswith('|')]
        
        # Count rows and columns
        metrics['row_count'] = len(lines)
        if lines:
            metrics['column_count'] = lines[0].count('|') - 1
        
        # Parse table into structured data
        metrics['parsed_data'] = self.parse_table_to_structured_data(table_content)
        
        # Find currencies and amounts
        currency_amounts = re.findall(r'([A-Z]\$)\s*([0-9,]+(?:\.[0-9]+)?)', table_content)
        if currency_amounts:
            metrics['currencies'] = list(set([c[0] for c in currency_amounts]))
            metrics['contains_financial_data'] = True
            # Store some key figures for quick reference
            metrics['key_figures'] = [f"{c[0]} {c[1]}" for c in currency_amounts[:5]]  # First 5
        
        # Check for percentages
        percentages = re.findall(r'([0-9]+\.[0-9]+)%', table_content)
        if percentages or '%' in table_content:
            metrics['has_percentages'] = True
        
        # Find financial keywords
        found_keywords = [kw for kw in self.financial_keywords if kw in content_lower]
        metrics['financial_keywords'] = found_keywords
        
        if found_keywords:
            metrics['contains_financial_data'] = True
        
        return metrics

    def parse_table_to_structured_data(self, table_content: str) -> Dict:
        """
        Parse table content into structured data with headers and rows
        """
        if not table_content:
            return {'headers': [], 'rows': []}
        
        lines = [line.strip() for line in table_content.split('\n') if line.strip().startswith('|')]
        
        if not lines:
            return {'headers': [], 'rows': []}
        
        # Parse headers (first row)
        headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]  # Remove empty first/last elements
        
        # Skip separator row if it exists (contains only dashes and pipes)
        data_start = 1
        if len(lines) > 1 and re.match(r'^[\|\-\s]+$', lines[1]):
            data_start = 2
        
        # Parse data rows
        rows = []
        for line in lines[data_start:]:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove empty first/last elements
            if len(cells) == len(headers):  # Ensure row has correct number of columns
                row_dict = dict(zip(headers, cells))
                rows.append(row_dict)
        
        return {
            'headers': headers,
            'rows': rows,
            'total_rows': len(rows),
            'total_columns': len(headers)
        }

    def create_output_files(self, original_file: str, cleaned_content: str, tables_metadata: List[Dict]) -> Dict:
        """
        Create output files - cleaned markdown and metadata JSON
        """
        base_path = Path(original_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create cleaned markdown file (only if changes were made)
        cleaned_file = base_path.parent / f"{base_path.stem}_cleaned_{timestamp}.md"
        with open(cleaned_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        # Create metadata JSON file
        metadata = {
            'source_file': original_file,
            'cleaned_file': str(cleaned_file),
            'processing_date': datetime.now().isoformat(),
            'total_tables': len(tables_metadata),
            'tables': tables_metadata,
            'summary': self.create_summary(tables_metadata)
        }
        
        metadata_file = base_path.parent / f"{base_path.stem}_metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return {
            'original_file': original_file,
            'cleaned_file': str(cleaned_file),
            'metadata_file': str(metadata_file),
            'tables_found': len(tables_metadata),
            'financial_tables': len([t for t in tables_metadata if t['metrics']['contains_financial_data']])
        }

    def create_summary(self, tables_metadata: List[Dict]) -> Dict:
        """
        Create summary statistics
        """
        total_data_rows = sum([t['metrics']['parsed_data']['total_rows'] for t in tables_metadata if t['metrics']['parsed_data']])
        
        return {
            'total_tables': len(tables_metadata),
            'by_type': {table_type: len([t for t in tables_metadata if t['type'] == table_type]) 
                       for table_type in self.table_types.keys()},
            'financial_tables': len([t for t in tables_metadata if t['metrics']['contains_financial_data']]),
            'pages_covered': list(set([t['page'] for t in tables_metadata if t['page'] != 'Unknown'])),
            'avg_rows_per_table': sum([t['metrics']['row_count'] for t in tables_metadata]) / len(tables_metadata) if tables_metadata else 0,
            'total_data_rows': total_data_rows,
            'content_included': True,  # Flag to indicate table content is included
            'currencies_found': list(set([curr for t in tables_metadata for curr in t['metrics']['currencies']])),
            'common_financial_keywords': list(set([kw for t in tables_metadata for kw in t['metrics']['financial_keywords']]))
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Post-process extracted markdown tables')
    parser.add_argument('markdown_file', help='Path to the extracted markdown file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.markdown_file):
        print(f"Error: File {args.markdown_file} not found")
        return
    
    processor = TablePostProcessor()
    results = processor.process_file(args.markdown_file)
    
    print("\n=== PROCESSING COMPLETE ===")
    print(f"Original file: {results['original_file']}")
    print(f"Cleaned file: {results['cleaned_file']}")
    print(f"Metadata file: {results['metadata_file']}")
    print(f"Tables found: {results['tables_found']}")
    print(f"Financial tables: {results['financial_tables']}")
    
    # Load and display summary
    with open(results['metadata_file'], 'r') as f:
        metadata = json.load(f)
    
    print(f"\nSummary:")
    print(f"- Pages covered: {metadata['summary']['pages_covered']}")
    print(f"- Table types: {metadata['summary']['by_type']}")
    print(f"- Avg rows per table: {metadata['summary']['avg_rows_per_table']:.1f}")
    print(f"- Total data rows: {metadata['summary']['total_data_rows']}")
    print(f"- Table content included: {metadata['summary']['content_included']}")
    if metadata['summary']['currencies_found']:
        print(f"- Currencies found: {metadata['summary']['currencies_found']}")
    if metadata['summary']['common_financial_keywords']:
        print(f"- Financial keywords: {metadata['summary']['common_financial_keywords']}")

if __name__ == "__main__":
    main()