#!/usr/bin/env python3
"""
Financial Report Generator Main Script
Generates comprehensive financial reports from image files.
"""

import os
import sys
import argparse
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import DataLoader
from statement_parser import StatementParser
from analyzer import Analyzer
from visualizer import Visualizer
from report_generator import ReportGenerator

def setup_company_directory(company_name, base_data_dir='../data'):
    """
    Create company directory structure if it doesn't exist.
    
    Args:
        company_name (str): Name of the company
        base_data_dir (str): Base data directory
        
    Returns:
        str: Path to company directory
    """
    company_dir = os.path.join(base_data_dir, company_name.lower().replace(' ', '_'))
    os.makedirs(company_dir, exist_ok=True)
    return company_dir

def validate_input_files(company_dir, file_names):
    """
    Validate that all required input files exist.
    
    Args:
        company_dir (str): Company directory
        file_names (dict): Dictionary of required files
        
    Returns:
        bool: True if all files exist
    """
    missing = []
    for key, filename in file_names.items():
        path = os.path.join(company_dir, filename)
        if not os.path.exists(path):
            missing.append(filename)
    
    if missing:
        print(f"Error: Missing required files: {', '.join(missing)}")
        return False
    return True

def create_sample_mapping(company_dir):
    """
    Create a sample mapping file if it doesn't exist.
    
    Args:
        company_dir (str): Company directory
    """
    mapping_path = os.path.join(company_dir, 'mapping.json')
    if not os.path.exists(mapping_path):
        sample_mapping = {
            "balance_sheet": {
                "Cash and cash equivalents": ["Cash and cash equivalents", "Cash"],
                "Receivables, net": ["Receivables", "Accounts receivable"],
                "Inventories": ["Inventories", "Inventory"],
                "Total Current Assets": ["Total current assets", "Current assets"],
                "Total Assets": ["Total assets"],
                "Total Current Liabilities": ["Total current liabilities", "Current liabilities"],
                "Total Liabilities": ["Total liabilities"],
                "Total Equity": ["Total equity", "Total shareholders’ equity"]
            },
            "income_statement": {
                "Revenue": ["Revenue", "Sales", "Total revenues"],
                "Cost of Revenue": ["Cost of revenue", "Cost of sales"],
                "Operating Income": ["Operating income", "Income from operations"],
                "Net Income": ["Net income", "Net earnings"]
            },
            "cash_flow": {
                "Operating Cash Flow": ["Cash provided by operations", "Net cash from operating activities"],
                "Investing Cash Flow": ["Cash used in investing activities", "Net cash used in investing"],
                "Financing Cash Flow": ["Cash provided by (used in) financing activities"],
                "Capital Expenditure": ["Investments in parks", "Purchase of property", "Capital expenditures"]
            }
        }
        
        import json
        with open(mapping_path, 'w') as f:
            json.dump(sample_mapping, f, indent=2)
        print(f"Created sample mapping file: {mapping_path}")
        print("Please review and customize the mapping for your company.")

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Generate financial report from images')
    parser.add_argument('company', help='Company name')
    parser.add_argument('--data-dir', default='../data', help='Base data directory')
    parser.add_argument('--output-dir', default='../output', help='Output directory')
    parser.add_argument('--no-ocr', action='store_true', help='Skip OCR, expect CSV files instead')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Financial Report Generator - {args.company}")
    print(f"{'='*60}\n")
    
    # Setup directories
    company_dir = setup_company_directory(args.company, args.data_dir)
    output_dir = os.path.join(args.output_dir, args.company.lower().replace(' ', '_'))
    os.makedirs(output_dir, exist_ok=True)
    
    # Define required files
    if args.no_ocr:
        required_files = {
            'bs': 'balance_sheet.csv',
            'is': 'income_statement.csv',
            'cf': 'cash_flow.csv'
        }
    else:
        required_files = {
            'bs': 'balance_sheet.jpg',
            'is': 'income_statement.jpg',
            'cf': 'cash_flow.jpg'
        }
    
    # Check mapping file
    mapping_path = os.path.join(company_dir, 'mapping.json')
    if not os.path.exists(mapping_path):
        print("Mapping file not found. Creating sample...")
        create_sample_mapping(company_dir)
        print("Please update the mapping file with your company's terminology and run again.")
        return
    
    # Validate input files
    if not validate_input_files(company_dir, required_files):
        print("\nPlease ensure all required files are in the company directory:")
        for key, filename in required_files.items():
            print(f"  - {filename}")
        return
    
    try:
        # Step 1: Load data
        print("Loading data...")
        loader = DataLoader()
        
        if args.no_ocr:
            bs_df = loader.from_csv(os.path.join(company_dir, required_files['bs']))
            is_df = loader.from_csv(os.path.join(company_dir, required_files['is']))
            cf_df = loader.from_csv(os.path.join(company_dir, required_files['cf']))
        else:
            bs_text = loader.from_image(os.path.join(company_dir, required_files['bs']))
            is_text = loader.from_image(os.path.join(company_dir, required_files['is']))
            cf_text = loader.from_image(os.path.join(company_dir, required_files['cf']))
            
            # Step 2: Parse statements
            print("Parsing financial statements...")
            parser = StatementParser(mapping_path)
            bs_df, is_df, cf_df = parser.parse_all(bs_text, is_text, cf_text)
        
        # Check if parsing was successful
        if bs_df.empty or is_df.empty or cf_df.empty:
            print("Warning: Some statements could not be parsed completely.")
            print("Balance sheet rows:", len(bs_df))
            print("Income statement rows:", len(is_df))
            print("Cash flow rows:", len(cf_df))
        
        print(f"Balance sheet: {len(bs_df)} items found")
        print(f"Income statement: {len(is_df)} items found")
        print(f"Cash flow: {len(cf_df)} items found")
        
        # Step 3: Analyze
        print("Computing financial ratios...")
        ratios_df = Analyzer.compute_ratios(bs_df, is_df, cf_df)
        
        # Step 4: Generate summary
        print("Generating summary...")
        summary = Analyzer.generate_summary(bs_df, is_df, cf_df, ratios_df)
        print("\n" + summary + "\n")
        
        # Step 5: Create visualizations
        print("Creating visualizations...")
        viz = Visualizer(output_dir=output_dir)
        chart_paths = viz.plot_all(bs_df, is_df, cf_df, ratios_df)
        print(f"Generated {len(chart_paths)} charts")
        
        # Step 6: Generate PDF report
        print("Generating PDF report...")
        report_gen = ReportGenerator(output_dir=output_dir)
        report_path = report_gen.generate(
            company_name=args.company,
            summary_text=summary,
            bs_df=bs_df,
            inc_df=is_df,
            cf_df=cf_df,
            ratios_df=ratios_df,
            chart_paths=chart_paths
        )
        
        print(f"\n{'='*60}")
        print(f"Report generation complete!")
        print(f"PDF report: {report_path}")
        print(f"Charts saved in: {output_dir}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\nError during processing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
