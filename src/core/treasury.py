import pandas as pd
import numpy as np

class TreasuryEngine:
    
    @staticmethod
    def calculate_cash_runway(current_cash: float, avg_monthly_burn: float) -> float:
        """
        Calculates Cash Runway in months.
        Runway = Current Cash / abs(Net Burn)
        If burn >= 0 (Profit), runway is Infinite.
        """
        if avg_monthly_burn >= 0:
            return float('inf')
        
        # Burn is negative, so use abs
        burn = abs(avg_monthly_burn)
        if burn == 0:
            return float('inf')
            
        return current_cash / burn

    @staticmethod
    def calculate_working_capital_metrics(df: pd.DataFrame) -> dict:
        """
        Calculates DSO, DIO, DPO, CCC.
        Formulae:
        DSO = (Receivables / Credit Sales) * 365
        DIO = (Inventory / COGS) * 365
        DPO = (Payables / COGS) * 365.  (Assuming Payables relate to COGS often, or Opex if generic)
        CCC = DIO + DSO - DPO
        
        We calculate based on Annualized or Period totals. 
        Assuming DF has 'date' and we take the latest snapshot for Balances and Sum for Flows?
        Or average over period? Standard is Average Balances / Total Flow * Period Days.
        
        Simplified MVP: 
        Take *Latest* Balance (Receivables, Inventory, Payables)
        Take *Total* Flow (Revenue, COGS) for the period in DF (assuming 1 year?) or annualized.
        
        Let's assume input DF is a period (e.g. 1 year) or we annualize the flow.
        """
        # Required columns check done by caller or we default to 0
        
        # 1. Flows (Total over DataFrame period)
        total_revenue = df['revenue'].sum() if 'revenue' in df.columns else 0
        total_cogs = df['cogs'].sum() if 'cogs' in df.columns else 0
        
        # Avoid zero division
        if total_revenue == 0: total_revenue = 1.0
        if total_cogs == 0: total_cogs = 1.0
        
        # 2. Balances (Latest available)
        # Assuming sorted by date
        latest = df.iloc[-1]
        receivables = latest.get('receivables', 0)
        inventory = latest.get('inventory', 0)
        payables = latest.get('payables', 0)
        
        days_in_period = 365 # Standard Assumption
        
        dso = (receivables / total_revenue) * days_in_period
        dio = (inventory / total_cogs) * days_in_period
        dpo = (payables / total_cogs) * days_in_period
        
        ccc = dio + dso - dpo
        
        return {
            "dso": round(dso, 1),
            "dio": round(dio, 1),
            "dpo": round(dpo, 1),
            "ccc": round(ccc, 1)
        }

    @staticmethod
    def get_weekly_cash_flow(df: pd.DataFrame) -> pd.DataFrame:
        """
        Resamples daily transaction data to Weekly sums.
        Expects 'date' and 'amount' (where + is inflow, - is outflow)
        Returns DataFrame with 'inflow', 'outflow', 'net'.
        """
        if 'date' not in df.columns or 'amount' not in df.columns:
            return pd.DataFrame()
            
        temp = df.copy()
        temp['date'] = pd.to_datetime(temp['date'])
        temp.set_index('date', inplace=True)
        
        # Create Inflow/Outflow columns
        temp['inflow'] = temp['amount'].apply(lambda x: x if x > 0 else 0)
        temp['outflow'] = temp['amount'].apply(lambda x: x if x < 0 else 0)
        
        # Resample Weekly (Sunday default 'W' or 'W-MON')
        weekly = temp.resample('W').sum()
        
        weekly['net'] = weekly['inflow'] + weekly['outflow']
        
        return weekly[['inflow', 'outflow', 'net']]
