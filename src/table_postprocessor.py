# --- START OF FILE src/tools/table_postprocessor.py ---
#!/usr/bin/env python3
"""
Table Post-Processor for ProfileDash
Cleans up markdown formatting and creates metadata - preserves all raw data
"""

import re
import json
from typing import Dict, List

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

    def process_text_content(self, markdown_content: str) -> Dict:
        """
        Main entry point to process raw markdown text containing tables.
        Returns a dictionary of all extracted table metadata.
        """
        cleaned_content = self.fix_markdown_formatting(markdown_content)
        tables_metadata = self.extract_table_metadata(cleaned_content)
        return tables_metadata

    def fix_markdown_formatting(self, content: str) -> str:
        """
        Fix only broken markdown table formatting - preserve all content
        """
        lines = content.split('\n')
        fixed_lines = []
        in_table = False

        for i, line in enumerate(lines):
            if line.strip().startswith('|') and '|' in line.strip()[1:]:
                in_table = True
                fixed_lines.append(self.fix_table_line(line))
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('|'):
                        if i + 2 < len(lines) and lines[i + 2].strip().startswith('|'):
                            col_count = line.count('|') - 1
                            if col_count > 0:
                                separator = '|' + '---|' * col_count
                                fixed_lines.append(separator)
            elif in_table and line.strip().startswith('|'):
                fixed_lines.append(self.fix_table_line(line))
            elif in_table and (not line.strip() or not line.strip().startswith('|')):
                in_table = False
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_table_line(self, line: str) -> str:
        """Fix issues in a single table line."""
        line = line.strip()
        if not line.startswith('|'):
            line = '| ' + line
        if not line.endswith('|'):
            line = line + ' |'
        line = re.sub(r'\s*\|\s*', ' | ', line)
        line = re.sub(r'^\s*\|\s*', '| ', line)
        line = re.sub(r'\s*\|\s*$', ' |', line)
        return line

    def extract_table_metadata(self, content: str) -> List[Dict]:
        """Extract metadata about tables without modifying content."""
        tables = []
        # Find all distinct tables, each starting with '## Table'
        table_blocks = re.split(r'(?=^## Table)', content, flags=re.MULTILINE)

        for block in table_blocks:
            if not block.strip().startswith('## Table'):
                continue

            table_match = re.match(r'^## Table [^:]+:\s*(.+)', block.strip(), re.IGNORECASE)
            title = table_match.group(1).strip() if table_match else "Untitled Table"
            page_match = re.search(r'\*\*Page:\*\*\s*([^\n]+)', block, re.IGNORECASE)
            page = page_match.group(1).strip() if page_match else "Unknown"
            
            # Extract only the markdown table content from the block
            table_content_lines = [line for line in block.split('\n') if line.strip().startswith('|')]
            table_content = '\n'.join(table_content_lines)

            if not table_content:
                continue

            metrics = self.extract_key_metrics(table_content)
            
            tables.append({
                'title': title,
                'page': page,
                'type': self.classify_table_type(title),
                'content': table_content,
                'metrics': metrics
            })
        return tables

    def classify_table_type(self, title: str) -> str:
        """Classify table type based on title keywords."""
        title_lower = title.lower()
        for table_type, keywords in self.table_types.items():
            if any(keyword in title_lower for keyword in keywords):
                return table_type
        return "other"

    def extract_key_metrics(self, table_content: str) -> Dict:
        """Extract key financial metrics and structural info from table content."""
        content_lower = table_content.lower()
        lines = [line for line in table_content.split('\n') if line.strip().startswith('|')]
        
        parsed_data = self.parse_table_to_structured_data(table_content)
        
        metrics = {
            'contains_financial_data': False,
            'currencies': list(set(re.findall(r'([A-Z]{1,3}\$|\$)', table_content))),
            'has_percentages': '%' in table_content,
            'row_count': len(lines),
            'column_count': lines[0].count('|') - 1 if lines else 0,
            'financial_keywords': [kw for kw in self.financial_keywords if kw in content_lower],
            'parsed_data': parsed_data
        }
        
        if metrics['currencies'] or metrics['financial_keywords']:
            metrics['contains_financial_data'] = True
            
        return metrics

    def parse_table_to_structured_data(self, table_content: str) -> Dict:
        """Parse table content into structured data with headers and rows."""
        lines = [line.strip() for line in table_content.split('\n') if line.strip().startswith('|')]
        if not lines:
            return {'headers': [], 'rows': []}

        headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
        data_start = 1
        if len(lines) > 1 and re.match(r'^[\|\-\s:]+$', lines[1]):
            data_start = 2
            
        rows = []
        for line in lines[data_start:]:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
            else: # Handle rows with mismatched column counts
                rows.append({'raw_row_data': cells})
                
        return {
            'headers': headers,
            'rows': rows,
            'total_rows': len(rows),
            'total_columns': len(headers)
        }
# --- END OF FILE src/tools/table_postprocessor.py ---