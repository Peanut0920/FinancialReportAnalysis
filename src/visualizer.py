import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

class Visualizer:
    """Creates various financial charts and visualizations."""
    
    def __init__(self, output_dir='../output'):
        """
        Initialize visualizer with output directory.
        
        Args:
            output_dir (str): Directory to save charts
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def _save_plot(self, filename):
        """Save plot to file and close."""
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        return path
    
    def plot_balance_sheet_trend(self, bs_df):
        """
        Create bar chart for key balance sheet items.
        
        Args:
            bs_df (pd.DataFrame): Balance sheet data
            
        Returns:
            str: Path to saved chart
        """
        # Select key items for visualization
        key_items = ['Total Current Assets', 'Total Assets', 
                    'Total Current Liabilities', 'Total Liabilities', 'Total Equity']
        
        available_items = [item for item in key_items if item in bs_df.index]
        
        if not available_items:
            return None
        
        # Prepare data for plotting
        plot_data = bs_df.loc[available_items].T
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        plot_data.plot(kind='bar', ax=ax, width=0.8)
        
        ax.set_title('Balance Sheet Overview', fontsize=16, fontweight='bold')
        ax.set_ylabel('$ millions', fontsize=12)
        ax.set_xlabel('Period', fontsize=12)
        ax.legend(title='Items', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for container in ax.containers:
            ax.bar_label(container, fmt='%.0f', fontsize=8)
        
        plt.tight_layout()
        
        return self._save_plot('balance_sheet_trend.png')
    
    def plot_income_statement_trend(self, inc_df):
        """
        Create line chart for income statement items.
        
        Args:
            inc_df (pd.DataFrame): Income statement data
            
        Returns:
            str: Path to saved chart
        """
        key_items = ['Revenue', 'Operating Income', 'Net Income']
        available_items = [item for item in key_items if item in inc_df.index]
        
        if not available_items:
            return None
        
        plot_data = inc_df.loc[available_items].T
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for item in available_items:
            ax.plot(plot_data.index, inc_df.loc[item], marker='o', linewidth=2, markersize=8, label=item)
        
        ax.set_title('Income Statement Trends', fontsize=16, fontweight='bold')
        ax.set_ylabel('$ millions', fontsize=12)
        ax.set_xlabel('Period', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add value labels
        for item in available_items:
            for i, v in enumerate(inc_df.loc[item]):
                ax.annotate(f'{v:.0f}', (plot_data.index[i], v), 
                           textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return self._save_plot('income_trend.png')
    
    def plot_ratios_comparison(self, ratios_df):
        """
        Create horizontal bar chart comparing key ratios across periods.
        
        Args:
            ratios_df (pd.DataFrame): Ratios data
            
        Returns:
            str: Path to saved chart
        """
        # Select key ratios for visualization
        key_ratios = ['Current Ratio', 'Quick Ratio', 'Debt-to-Equity', 
                     'Net Profit Margin', 'ROE', 'ROA']
        
        available_ratios = [r for r in key_ratios if r in ratios_df.index]
        
        if not available_ratios:
            return None
        
        plot_data = ratios_df.loc[available_ratios]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create grouped bar chart
        x = np.arange(len(available_ratios))
        width = 0.35
        
        for i, period in enumerate(plot_data.columns):
            ax.barh(x + i*width, plot_data[period].values, width, label=period)
        
        ax.set_xlabel('Ratio Value')
        ax.set_title('Key Financial Ratios Comparison', fontsize=16, fontweight='bold')
        ax.set_yticks(x + width/2)
        ax.set_yticklabels(available_ratios)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        return self._save_plot('ratios_comparison.png')
    
    def plot_asset_composition(self, bs_df):
        """
        Create pie chart for asset composition (latest period).
        
        Args:
            bs_df (pd.DataFrame): Balance sheet data
            
        Returns:
            str: Path to saved chart
        """
        # Asset categories for pie chart
        asset_categories = ['Cash and cash equivalents', 'Receivables, net', 
                           'Inventories', 'Property, plant and equipment', 
                           'Intangible assets, net', 'Goodwill']
        
        available = [cat for cat in asset_categories if cat in bs_df.index]
        
        if not available:
            return None
        
        # Use latest period
        latest_col = bs_df.columns[-1]
        values = bs_df.loc[available, latest_col]
        
        # Filter out zero values
        mask = values > 0
        values = values[mask]
        labels = [lbl for i, lbl in enumerate(available) if mask.iloc[i]]
        
        if len(values) == 0:
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Pie chart
        colors = sns.color_palette('pastel')[0:len(values)]
        wedges, texts, autotexts = ax1.pie(values, labels=labels, autopct='%1.1f%%',
                                           startangle=90, colors=colors)
        ax1.set_title(f'Asset Composition - {latest_col}', fontsize=14, fontweight='bold')
        
        # Enhance readability
        for text in texts + autotexts:
            text.set_fontsize(9)
        
        # Bar chart for absolute values
        ax2.barh(labels, values, color=colors)
        ax2.set_xlabel('$ millions')
        ax2.set_title('Asset Values', fontsize=14, fontweight='bold')
        
        # Add value labels
        for i, v in enumerate(values):
            ax2.text(v, i, f' ${v:,.0f}', va='center', fontsize=9)
        
        plt.tight_layout()
        
        return self._save_plot('asset_composition.png')
    
    def plot_cash_flow_waterfall(self, cf_df):
        """
        Create waterfall chart for cash flow.
        
        Args:
            cf_df (pd.DataFrame): Cash flow data
            
        Returns:
            str: Path to saved chart
        """
        try:
            ocf = cf_df.loc['Operating Cash Flow'].iloc[0]
            cf_df.loc['Capital Expenditure'].iloc[0]
            fcf = cf_df.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cf_df.index else None
        except (KeyError, IndexError):
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Prepare data for waterfall
        categories = ['Operating CF', 'CapEx', 'Free CF']
        values = [ocf, -abs(cf_df.loc['Capital Expenditure'].iloc[0]), fcf if fcf else 0]
        colors = ['green' if v > 0 else 'red' for v in values]
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7)
        ax.axhline(y=0, color='black', linewidth=0.8, linestyle='-', alpha=0.3)
        
        ax.set_title('Cash Flow Waterfall', fontsize=16, fontweight='bold')
        ax.set_ylabel('$ millions')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:,.0f}M', ha='center', va='bottom' if height > 0 else 'top')
        
        plt.tight_layout()
        
        return self._save_plot('cash_flow_waterfall.png')
    
    def plot_all(self, bs_df, inc_df, cf_df, ratios_df):
        """
        Generate all visualizations.
        
        Args:
            bs_df, inc_df, cf_df, ratios_df: Financial data
            
        Returns:
            dict: Dictionary of chart paths
        """
        chart_paths = {}
        
        # Generate each chart and store path if successful
        charts = [
            ('balance_sheet', self.plot_balance_sheet_trend(bs_df)),
            ('income_statement', self.plot_income_statement_trend(inc_df)),
            ('ratios', self.plot_ratios_comparison(ratios_df)),
            ('asset_composition', self.plot_asset_composition(bs_df)),
            ('cash_flow', self.plot_cash_flow_waterfall(cf_df))
        ]
        
        for name, path in charts:
            if path:
                chart_paths[name] = path
        
        return chart_paths
