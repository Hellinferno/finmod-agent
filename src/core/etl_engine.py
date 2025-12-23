import pandas as pd
import numpy as np
from thefuzz import process
import re

class SmartImporter:
    
    STANDARD_SCHEMA = {
        'date': ['date', 'period', 'month', 'timestamp'],
        'revenue': ['revenue', 'sales', 'gross_income', 'turnover', 'top_line'],
        'cogs': ['cogs', 'cost_of_goods_sold', 'direct_costs', 'cost_of_sales'],
        'opex': ['opex', 'operating_expenses', 'indirect_costs', 'sg&a'],
        'net_income': ['net_income', 'profit', 'bottom_line', 'net_profit']
    }

    @staticmethod
    def fuzzy_map_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """
        Maps DataFrame columns to STANDARD_SCHEMA using fuzzy matching.
        Threshold: > 85.
        Returns: (Mapped DataFrame, Report Dict)
        """
        mapped_df = df.copy()
        
        # Build choices list from all variation lists
        # We need a reverse map to know which standard key a variation belongs to
        variation_map = {}
        for std, variations in SmartImporter.STANDARD_SCHEMA.items():
            variation_map[std] = std # Map canonical to itself
            for v in variations:
                variation_map[v] = std
                
        choices = list(variation_map.keys())
        
        mapping_report = {}
        new_columns = {}
        
        for col in df.columns:
            col_clean = str(col).lower().strip()
            
            # extractOne returns (match, score)
            # Use score_cutoff to optimize? process.extractOne(query, choices, score_cutoff=0)
            best_match, score = process.extractOne(col_clean, choices)
            
            if score > 85:
                canonical = variation_map[best_match]
                # Avoid duplicate mapping if multiple cols map to same canonical?
                # For now, simplistic mapping.
                new_columns[col] = canonical
                mapping_report[col] = canonical
            else:
                mapping_report[col] = "Unmapped (Low Confidence)"
                
        mapped_df.rename(columns=new_columns, inplace=True)
        return mapped_df, mapping_report

    @staticmethod
    def clean_financial_values(df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans financial columns (Revenue, COGS, etc.) and Date column.
        """
        cleaned_df = df.copy()
        
        # Identify financial columns (those in STANDARD_SCHEMA keys) that are present
        financial_keys = [k for k in SmartImporter.STANDARD_SCHEMA.keys() if k != 'date']
        present_fin_cols = [c for c in cleaned_df.columns if c in financial_keys]
        
        for col in present_fin_cols:
            # Convert to string to clean
            series = cleaned_df[col].astype(str).str.strip()
            
            # Remove symbols: $, €, ,
            series = series.str.replace(r'[$,€]', '', regex=True)
            series = series.str.replace(',', '', regex=False)
            
            # Handle Accounting Negatives: (100) -> -100
            # Regex to find (digits)
            # We can use a lambda to be precise
            def parse_accounting(val):
                if pd.isna(val) or val == 'nan':
                    return np.nan
                val = val.strip()
                if val == '-':
                    return 0.0
                if val.startswith('(') and val.endswith(')'):
                    val = val[1:-1]
                    return -1.0 * float(val)
                try:
                    return float(val)
                except:
                    return np.nan # Garbage
            
            cleaned_df[col] = series.apply(parse_accounting)

        # Date Parsing
        if 'date' in cleaned_df.columns:
            # Coerce errors to NaT, try inferring format
            cleaned_df['date'] = pd.to_datetime(cleaned_df['date'], errors='coerce')
            
        return cleaned_df
