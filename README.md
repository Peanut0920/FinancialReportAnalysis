# Financial Report Generator

An automated tool that extracts financial data from images, performs analysis, and generates comprehensive PDF reports.

## Features

- **OCR-based data extraction** from financial statement images
- **Company-specific mapping** for flexible terminology handling
- **Comprehensive financial analysis** including ratios, trends, and common-size statements
- **Multiple visualizations** (bar charts, line charts, pie charts, waterfall charts)
- **Professional PDF report** generation with executive summary and insights
- **Support for CSV/Excel** input as alternative to OCR

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd financial_report_generator


2. Installation of package
pip install -r requirements.txt
Install Tesseract OCR:
Windows: Download from GitHub
macOS: brew install tesseract
Linux: sudo apt install tesseract-ocr



financial_report_generator/
├── data/                           # Company data directories
│   └── [company_name]/             # Per-company folder
│       ├── balance_sheet.jpg       # Balance sheet image
│       ├── income_statement.jpg    # Income statement image
│       ├── cash_flow.jpg           # Cash flow image
│       └── mapping.json            # Term mapping file
├── src/                            # Source code
│   ├── data_loader.py              # Data loading (OCR/CSV/Excel)
│   ├── statement_parser.py         # Statement parsing with mapping
│   ├── analyzer.py                 # Financial analysis
│   ├── visualizer.py               # Chart generation
│   ├── report_generator.py         # PDF report creation
│   └── main.py                      # Main orchestrator
├── output/                          # Generated reports and charts
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
