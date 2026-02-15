from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime

class PDFReport(FPDF):
    """Custom PDF class for financial reports."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
    
    def header(self):
        """Add header to each page."""
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, 'Financial Analysis Report', 0, 1, 'C')
        self.set_font('DejaVu', '', 8)
        self.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'R')
        self.ln(5)
    
    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title):
        """Add chapter title."""
        self.set_font('DejaVu', 'B', 14)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(5)
    
    def chapter_body(self, text):
        """Add chapter body text."""
        self.set_font('DejaVu', '', 10)
        self.multi_cell(0, 6, text)
        self.ln(5)
    
    def add_table(self, df, title, max_rows=15):
        """
        Add a formatted table to the PDF.
        
        Args:
            df (pd.DataFrame): Data to display
            title (str): Table title
            max_rows (int): Maximum rows to display
        """
        self.set_font('DejaVu', 'B', 11)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(2)
        
        # Limit rows if too many
        if len(df) > max_rows:
            df = df.head(max_rows)
            note = f"(Showing first {max_rows} rows)"
            self.set_font('DejaVu', 'I', 8)
            self.cell(0, 5, note, 0, 1, 'R')
        
        # Calculate column widths
        col_widths = []
        # Item column width
        col_widths.append(max(40, max([len(str(idx)) * 3 for idx in df.index])))
        # Data columns
        for col in df.columns:
            col_widths.append(max(25, len(str(col)) * 3))
        
        # Adjust to fit page width
        total_width = sum(col_widths)
        if total_width > self.w - 20:
            scale = (self.w - 20) / total_width
            col_widths = [w * scale for w in col_widths]
        
        # Table header
        self.set_font('DejaVu', 'B', 9)
        self.set_fill_color(200, 220, 240)
        
        # Item header
        self.cell(col_widths[0], 8, 'Item', 1, 0, 'L', 1)
        # Column headers
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i+1], 8, str(col), 1, 0, 'C', 1)
        self.ln()
        
        # Table rows
        self.set_font('DejaVu', '', 8)
        fill = False
        for idx, row in df.iterrows():
            # Item cell
            self.cell(col_widths[0], 6, str(idx)[:30], 'LR', 0, 'L', fill)
            # Data cells
            for i, val in enumerate(row):
                if isinstance(val, (int, float)):
                    text = f"{val:,.2f}"
                else:
                    text = str(val)
                self.cell(col_widths[i+1], 6, text, 'LR', 0, 'R', fill)
            self.ln()
            fill = not fill
        
        # Bottom border
        self.cell(sum(col_widths), 0, '', 'T')
        self.ln(8)
    
    def add_image(self, image_path, caption=''):
        """
        Add an image to the PDF.
        
        Args:
            image_path (str): Path to image file
            caption (str): Image caption
        """
        if image_path and os.path.exists(image_path):
            try:
                # Calculate image dimensions to fit page
                self.image(image_path, x=10, w=self.w - 20)
                if caption:
                    self.set_font('DejaVu', 'I', 8)
                    self.cell(0, 5, caption, 0, 1, 'C')
                self.ln(5)
            except Exception as e:
                print(f"Could not add image {image_path}: {e}")
    
    def add_metric_box(self, title, value, description=''):
        """
        Add a metric box for key figures.
        
        Args:
            title (str): Metric title
            value (str): Metric value
            description (str): Additional description
        """
        self.set_fill_color(240, 240, 240)
        self.set_draw_color(100, 100, 100)
        
        self.cell(90, 25, '', 1, 0, 'C', 1)
        x, y = self.get_x() - 90, self.get_y() - 25
        
        # Title
        self.set_xy(x, y + 2)
        self.set_font('DejaVu', 'B', 8)
        self.cell(90, 5, title, 0, 0, 'C')
        
        # Value
        self.set_xy(x, y + 9)
        self.set_font('DejaVu', 'B', 12)
        self.cell(90, 8, value, 0, 0, 'C')
        
        # Description
        self.set_xy(x, y + 18)
        self.set_font('DejaVu', 'I', 7)
        self.cell(90, 5, description, 0, 0, 'C')
        
        self.set_xy(x + 90, y + 25)

class ReportGenerator:
    """Generates comprehensive PDF financial reports."""
    
    def __init__(self, output_dir='../output'):
        """
        Initialize report generator.
        
        Args:
            output_dir (str): Directory to save reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, company_name, summary_text, bs_df, inc_df, cf_df, 
                ratios_df, chart_paths, output_filename=None):
        """
        Generate complete PDF report.
        
        Args:
            company_name (str): Name of the company
            summary_text (str): Executive summary
            bs_df, inc_df, cf_df: Financial statements
            ratios_df (pd.DataFrame): Computed ratios
            chart_paths (dict): Dictionary of chart paths
            output_filename (str): Optional output filename
            
        Returns:
            str: Path to generated PDF
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{company_name.lower().replace(' ', '_')}_report_{timestamp}.pdf"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Create PDF
        pdf = PDFReport()
        pdf.add_page()
        
        # Title
        pdf.set_font('DejaVu', 'B', 20)
        pdf.cell(0, 20, f'{company_name} Financial Analysis', 0, 1, 'C')
        pdf.ln(5)
        
        # Executive Summary
        pdf.chapter_title('Executive Summary')
        pdf.chapter_body(summary_text)
        
        # Key Metrics Dashboard
        pdf.chapter_title('Key Financial Metrics')
        
        # Create metric boxes (2 per row)
        metrics = [
            ('Revenue', f"${inc_df.loc['Revenue'].iloc[0]:,.0f}M" if 'Revenue' in inc_df.index else 'N/A', 'Latest quarter'),
            ('Net Income', f"${inc_df.loc['Net Income'].iloc[0]:,.0f}M" if 'Net Income' in inc_df.index else 'N/A', 'Latest quarter'),
            ('Total Assets', f"${bs_df.loc['Total Assets'].iloc[0]:,.0f}M" if 'Total Assets' in bs_df.index else 'N/A', 'End of period'),
            ('Total Equity', f"${bs_df.loc['Total Equity'].iloc[0]:,.0f}M" if 'Total Equity' in bs_df.index else 'N/A', 'End of period')
        ]
        
        # Arrange metrics in a grid
        pdf.set_font('DejaVu', '', 10)
        for i, (title, value, desc) in enumerate(metrics):
            if i % 2 == 0:
                pdf.ln(30) if i > 0 else None
                pdf.set_x(10)
            pdf.add_metric_box(title, value, desc)
        pdf.ln(30)
        
        # Balance Sheet
        pdf.add_page()
        pdf.chapter_title('Balance Sheet Analysis')
        pdf.add_table(bs_df, 'Balance Sheet (Selected Items)')
        
        if 'balance_sheet' in chart_paths:
            pdf.add_image(chart_paths['balance_sheet'], 'Balance Sheet Trend')
        
        if 'asset_composition' in chart_paths:
            pdf.add_image(chart_paths['asset_composition'], 'Asset Composition')
        
        # Income Statement
        pdf.add_page()
        pdf.chapter_title('Income Statement Analysis')
        pdf.add_table(inc_df, 'Income Statement')
        
        if 'income_statement' in chart_paths:
            pdf.add_image(chart_paths['income_statement'], 'Income Statement Trends')
        
        # Cash Flow Statement
        pdf.add_page()
        pdf.chapter_title('Cash Flow Analysis')
        pdf.add_table(cf_df, 'Cash Flow Statement')
        
        if 'cash_flow' in chart_paths:
            pdf.add_image(chart_paths['cash_flow'], 'Cash Flow Waterfall')
        
        # Financial Ratios
        pdf.add_page()
        pdf.chapter_title('Financial Ratios Analysis')
        pdf.add_table(ratios_df, 'Key Financial Ratios')
        
        if 'ratios' in chart_paths:
            pdf.add_image(chart_paths['ratios'], 'Ratios Comparison')
        
        # Common-size statements
        pdf.add_page()
        pdf.chapter_title('Common-Size Analysis')
        
        # Common-size balance sheet
        cs_bs, cs_inc = Analyzer.common_size(bs_df, inc_df)
        
        if not cs_bs.empty:
            pdf.add_table(cs_bs, 'Common-Size Balance Sheet (% of Total Assets)')
        
        if not cs_inc.empty:
            pdf.add_table(cs_inc, 'Common-Size Income Statement (% of Revenue)')
        
        # Additional Insights
        pdf.add_page()
        pdf.chapter_title('Key Insights & Observations')
        
        insights = []
        
        # Generate insights based on ratios
        if 'Current Ratio' in ratios_df.index:
            cr = ratios_df.loc['Current Ratio'].iloc[0]
            if cr < 1:
                insights.append("• Current ratio below 1 indicates potential liquidity concerns")
            elif cr > 2:
                insights.append("• Strong current ratio indicates good short-term liquidity")
        
        if 'Debt-to-Equity' in ratios_df.index:
            dte = ratios_df.loc['Debt-to-Equity'].iloc[0]
            if dte > 2:
                insights.append("• High leverage may indicate increased financial risk")
            elif dte < 0.5:
                insights.append("• Conservative capital structure with low debt")
        
        if 'Net Profit Margin' in ratios_df.index:
            npm = ratios_df.loc['Net Profit Margin'].iloc[0]
            if npm > 20:
                insights.append("• Excellent profitability with margins above 20%")
            elif npm < 5:
                insights.append("• Thin profit margins may indicate pricing pressure")
        
        if 'Revenue Growth (%)' in ratios_df.index:
            growth = ratios_df.loc['Revenue Growth (%)'].iloc[0]
            if growth > 10:
                insights.append(f"• Strong revenue growth of {growth:.1f}%")
            elif growth < 0:
                insights.append(f"• Revenue contraction of {abs(growth):.1f}% requires attention")
        
        if 'Free Cash Flow' in ratios_df.index:
            fcf = ratios_df.loc['Free Cash Flow'].iloc[0]
            if fcf > 0:
                insights.append(f"• Positive free cash flow of ${fcf:,.0f}M provides financial flexibility")
            else:
                insights.append(f"• Negative free cash flow of ${abs(fcf):,.0f}M may require external financing")
        
        if not insights:
            insights = ["• No significant observations available"]
        
        pdf.chapter_body("\n".join(insights))
        
        # Generate PDF
        pdf.output(output_path, 'F')
        print(f"Report generated: {output_path}")
        
        return output_path
