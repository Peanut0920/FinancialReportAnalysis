import pandas as pd
import numpy as np

class Analyzer:
    """Performs financial analysis and computes ratios."""
    
    @staticmethod
    def compute_ratios(bs_df, inc_df, cf_df):
        """
        Compute key financial ratios.
        
        Args:
            bs_df (pd.DataFrame): Balance sheet data
            inc_df (pd.DataFrame): Income statement data
            cf_df (pd.DataFrame): Cash flow data
            
        Returns:
            pd.DataFrame: Computed ratios
        """
        ratios = {}
        
        # Ensure we have required indices
        required_bs = ['Total Current Assets', 'Total Current Liabilities', 
                      'Total Assets', 'Total Liabilities', 'Total Equity']
        required_inc = ['Revenue', 'Net Income']
        required_cf = ['Operating Cash Flow', 'Capital Expenditure']
        
        # Check for missing indices and use available data
        for idx in bs_df.index:
            if idx not in required_bs and idx in ['Inventories', 'Cash and cash equivalents']:
                pass  # These are optional
        
        # Balance sheet ratios
        try:
            current_assets = bs_df.loc['Total Current Assets']
            current_liab = bs_df.loc['Total Current Liabilities']
            
            # Try to get inventories (optional)
            try:
                inventories = bs_df.loc['Inventories']
            except KeyError:
                inventories = pd.Series([0, 0], index=current_assets.index)
            
            total_assets = bs_df.loc['Total Assets']
            total_equity = bs_df.loc['Total Equity']
            total_liab = bs_df.loc['Total Liabilities']
            
            # Liquidity ratios
            ratios['Current Ratio'] = current_assets / current_liab
            ratios['Quick Ratio'] = (current_assets - inventories) / current_liab
            
            # Leverage ratios
            ratios['Debt-to-Equity'] = total_liab / total_equity
            ratios['Debt-to-Assets'] = total_liab / total_assets
            
            # Asset turnover (if we have revenue)
            if 'Revenue' in inc_df.index:
                revenue = inc_df.loc['Revenue']
                ratios['Asset Turnover'] = revenue / total_assets
            
        except KeyError as e:
            print(f"Warning: Missing data for balance sheet ratios: {e}")
        
        # Profitability ratios
        try:
            revenue = inc_df.loc['Revenue']
            net_income = inc_df.loc['Net Income']
            
            ratios['Net Profit Margin'] = (net_income / revenue) * 100
            ratios['Gross Profit Margin'] = 100 - ((inc_df.loc.get('Cost of Revenue', pd.Series([0,0])) / revenue) * 100)
            
            # Return on Equity (ROE)
            if 'Total Equity' in bs_df.index:
                avg_equity = bs_df.loc['Total Equity'].mean()
                ratios['ROE'] = (net_income.mean() / avg_equity) * 100
            
            # Return on Assets (ROA)
            if 'Total Assets' in bs_df.index:
                avg_assets = bs_df.loc['Total Assets'].mean()
                ratios['ROA'] = (net_income.mean() / avg_assets) * 100
                
        except KeyError as e:
            print(f"Warning: Missing data for profitability ratios: {e}")
        
        # Cash flow ratios
        try:
            ocf = cf_df.loc['Operating Cash Flow']
            
            if 'Capital Expenditure' in cf_df.index:
                capex = cf_df.loc['Capital Expenditure']
                fcf = ocf + capex  # capex is negative
                ratios['Free Cash Flow'] = fcf
                
                if 'Revenue' in inc_df.index:
                    ratios['FCF / Revenue'] = (fcf / revenue) * 100
            
            ratios['Operating Cash Flow Margin'] = (ocf / revenue) * 100
            
        except KeyError as e:
            print(f"Warning: Missing data for cash flow ratios: {e}")
        
        # Growth rates (year-over-year)
        try:
            if len(inc_df.columns) >= 2:
                revenue = inc_df.loc['Revenue']
                net_income = inc_df.loc['Net Income']
                
                ratios['Revenue Growth (%)'] = ((revenue.iloc[0] / revenue.iloc[1]) - 1) * 100
                ratios['Net Income Growth (%)'] = ((net_income.iloc[0] / net_income.iloc[1]) - 1) * 100
                
        except (KeyError, IndexError) as e:
            print(f"Warning: Could not compute growth rates: {e}")
        
        # Convert to DataFrame
        ratios_df = pd.DataFrame(ratios).T
        
        # Format for better readability
        for col in ratios_df.columns:
            ratios_df[col] = ratios_df[col].round(2)
        
        return ratios_df
    
    @staticmethod
    def common_size(bs_df, inc_df):
        """
        Convert statements to common-size (percentage) format.
        
        Args:
            bs_df (pd.DataFrame): Balance sheet
            inc_df (pd.DataFrame): Income statement
            
        Returns:
            tuple: (common_size_bs, common_size_inc)
        """
        cs_bs = pd.DataFrame()
        cs_inc = pd.DataFrame()
        
        try:
            # Balance sheet common-size (% of total assets)
            total_assets = bs_df.loc['Total Assets']
            cs_bs = bs_df.div(total_assets, axis=1) * 100
            cs_bs = cs_bs.round(2)
            
        except KeyError:
            print("Warning: Could not compute common-size balance sheet")
        
        try:
            # Income statement common-size (% of revenue)
            revenue = inc_df.loc['Revenue']
            cs_inc = inc_df.div(revenue, axis=1) * 100
            cs_inc = cs_inc.round(2)
            
        except KeyError:
            print("Warning: Could not compute common-size income statement")
        
        return cs_bs, cs_inc
    
    @staticmethod
    def generate_summary(bs_df, inc_df, cf_df, ratios_df):
        """
        Generate text summary of key findings.
        
        Args:
            bs_df, inc_df, cf_df, ratios_df: DataFrames with financial data
            
        Returns:
            str: Summary text
        """
        summary_lines = []
        
        # Get latest period
        latest_period = inc_df.columns[0] if len(inc_df.columns) > 0 else "latest period"
        
        summary_lines.append(f"Financial Analysis Summary for {latest_period}")
        summary_lines.append("=" * 50)
        
        # Profitability summary
        if 'Net Profit Margin' in ratios_df.index:
            npm = ratios_df.loc['Net Profit Margin'].iloc[0]
            summary_lines.append(f"\nProfitability: Net profit margin is {npm:.1f}%")
        
        if 'Revenue' in inc_df.index:
            revenue = inc_df.loc['Revenue'].iloc[0]
            summary_lines.append(f"Revenue: ${revenue:,.0f} million")
        
        if 'Net Income' in inc_df.index:
            net_income = inc_df.loc['Net Income'].iloc[0]
            summary_lines.append(f"Net Income: ${net_income:,.0f} million")
        
        # Liquidity summary
        if 'Current Ratio' in ratios_df.index:
            cr = ratios_df.loc['Current Ratio'].iloc[0]
            status = "healthy" if cr > 1.5 else "adequate" if cr > 1 else "concerning"
            summary_lines.append(f"\nLiquidity: Current ratio of {cr:.2f} is {status}")
        
        # Leverage summary
        if 'Debt-to-Equity' in ratios_df.index:
            dte = ratios_df.loc['Debt-to-Equity'].iloc[0]
            summary_lines.append(f"Leverage: Debt-to-Equity ratio is {dte:.2f}")
        
        # Cash flow summary
        if 'Free Cash Flow' in ratios_df.index:
            fcf = ratios_df.loc['Free Cash Flow'].iloc[0]
            summary_lines.append(f"\nCash Flow: Free cash flow is ${fcf:,.0f} million")
        
        # Growth summary
        if 'Revenue Growth (%)' in ratios_df.index:
            growth = ratios_df.loc['Revenue Growth (%)'].iloc[0]
            direction = "increased" if growth > 0 else "decreased"
            summary_lines.append(f"\nGrowth: Revenue {direction} by {abs(growth):.1f}%")
        
        return "\n".join(summary_lines)
