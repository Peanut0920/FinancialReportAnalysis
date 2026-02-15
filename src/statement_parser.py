import re
import pandas as pd
import json
from datetime import datetime

class StatementParser:
    """Parses financial statements using company-specific mapping."""
    
    def __init__(self, mapping_path):
        """
        Initialize parser with company mapping.
        
        Args:
            mapping_path (str): Path to JSON mapping file
        """
        with open(mapping_path, 'r') as f:
            self.mapping = json.load(f)
        
        # Common patterns for number extraction
        self.number_pattern = r'\(?\$?[\d,]+\.?[\d]*\)?'
        self.date_pattern = r'[A-Za-z]+ \d{1,2}, \d{4}'
    
    def _extract_dates(self, lines):
        """Extract column headers (dates) from text."""
        dates = []
        for line in lines[:10]:  # Check first 10 lines for headers
            date_matches = re.findall(self.date_pattern, line)
            if date_matches:
                dates.extend(date_matches[:2])  # Take first two dates
                break
        return dates
    
    def _find_line(self, lines, keyword):
        """
        Find line containing keyword and extract numeric values.
        
        Args:
            lines (list): List of text lines
            keyword (str): Keyword to search for
            
        Returns:
            list: Extracted numeric values
        """
        for line in lines:
            if keyword.lower() in line.lower():
                # Extract all numbers (including negative in parentheses)
                nums = re.findall(self.number_pattern, line)
                
                # Convert to float, handle parentheses for negative
                values = []
                for n in nums:
                    # Remove $ and commas
                    n_clean = n.replace('$', '').replace(',', '')
                    
                    # Handle parentheses for negative numbers
                    if '(' in n and ')' in n:
                        n_clean = '-' + n_clean.replace('(', '').replace(')', '')
                    
                    try:
                        values.append(float(n_clean))
                    except ValueError:
                        continue
                
                return values
        return None
    
    def _create_dataframe(self, items_data, dates):
        """
        Create DataFrame from extracted items.
        
        Args:
            items_data (dict): Dictionary with items and their values
            dates (list): List of date strings
            
        Returns:
            pd.DataFrame: Parsed statement
        """
        if not dates:
            dates = ['Period 1', 'Period 2']
        
        df = pd.DataFrame(items_data).T
        df.columns = dates[:len(df.columns)]
        return df
    
    def parse_balance_sheet(self, text):
        """
        Parse balance sheet from text.
        
        Args:
            text (str): Extracted text
            
        Returns:
            pd.DataFrame: Balance sheet data
        """
        lines = text.split('\n')
        dates = self._extract_dates(lines)
        
        items_data = {}
        
        # Find balance sheet section
        start_idx = 0
        for i, line in enumerate(lines):
            if 'ASSETS' in line.upper():
                start_idx = i
                break
        
        # Process each mapped item
        for std_name, keywords in self.mapping['balance_sheet'].items():
            for kw in keywords:
                values = self._find_line(lines[start_idx:], kw)
                if values and len(values) >= 2:
                    items_data[std_name] = values[:2]
                    break
        
        return self._create_dataframe(items_data, dates)
    
    def parse_income_statement(self, text):
        """
        Parse income statement from text.
        
        Args:
            text (str): Extracted text
            
        Returns:
            pd.DataFrame: Income statement data
        """
        lines = text.split('\n')
        dates = self._extract_dates(lines)
        
        items_data = {}
        
        # Look for income statement section
        income_keywords = ['REVENUES', 'INCOME STATEMENT', 'OPERATING INCOME']
        
        start_idx = 0
        for i, line in enumerate(lines):
            if any(kw in line.upper() for kw in income_keywords):
                start_idx = i
                break
        
        for std_name, keywords in self.mapping['income_statement'].items():
            for kw in keywords:
                values = self._find_line(lines[start_idx:], kw)
                if values and len(values) >= 2:
                    items_data[std_name] = values[:2]
                    break
        
        return self._create_dataframe(items_data, dates)
    
    def parse_cash_flow(self, text):
        """
        Parse cash flow statement from text.
        
        Args:
            text (str): Extracted text
            
        Returns:
            pd.DataFrame: Cash flow data
        """
        lines = text.split('\n')
        dates = self._extract_dates(lines)
        
        items_data = {}
        
        # Find cash flow section
        cf_keywords = ['OPERATING ACTIVITIES', 'CASH FLOWS']
        
        start_idx = 0
        for i, line in enumerate(lines):
            if any(kw in line.upper() for kw in cf_keywords):
                start_idx = i
                break
        
        for std_name, keywords in self.mapping['cash_flow'].items():
            for kw in keywords:
                values = self._find_line(lines[start_idx:], kw)
                if values and len(values) >= 2:
                    items_data[std_name] = values[:2]
                    break
        
        return self._create_dataframe(items_data, dates)
    
    def parse_all(self, bs_text, is_text, cf_text):
        """
        Parse all three statements.
        
        Args:
            bs_text (str): Balance sheet text
            is_text (str): Income statement text
            cf_text (str): Cash flow text
            
        Returns:
            tuple: (balance_sheet_df, income_statement_df, cash_flow_df)
        """
        bs_df = self.parse_balance_sheet(bs_text)
        is_df = self.parse_income_statement(is_text)
        cf_df = self.parse_cash_flow(cf_text)
        
        return bs_df, is_df, cf_df
