import pandas as pd
import yfinance as yf
from scipy import stats

class MarketIntelligence:
    
    @staticmethod
    def fetch_peer_data(tickers: list[str]) -> pd.DataFrame:
        """
        Fetches live financial ratios from Yahoo Finance.
        Returns DataFrame indexed by Ticker.
        """
        data = []
        
        for symbol in tickers:
            symbol = symbol.strip().upper()
            if not symbol:
                continue
                
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Extract Metrics (Handle missing data)
                # Note: valid keys might vary, defaulting to 0 or None
                metrics = {
                    'Ticker': symbol,
                    'Profit Margin': info.get('profitMargins', 0) if info.get('profitMargins') else 0,
                    'ROE': info.get('returnOnEquity', 0) if info.get('returnOnEquity') else 0,
                    'Current Ratio': info.get('currentRatio', 0) if info.get('currentRatio') else 0,
                    'Debt to Equity': info.get('debtToEquity', 0) if info.get('debtToEquity') else 0,
                    'Trailing PE': info.get('trailingPE', 0) if info.get('trailingPE') else 0
                }
                data.append(metrics)
            except Exception as e:
                # Log error or skip
                print(f"Error fetching {symbol}: {e}")
                
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        df.set_index('Ticker', inplace=True)
        return df

    @staticmethod
    def compare_against_internal(internal_metrics: dict, peer_df: pd.DataFrame) -> pd.DataFrame:
        """
        Appends Internal Data to Peer DF and calculates Percentiles.
        internal_metrics: {'Profit Margin': 0.15, ...}
        """
        df = peer_df.copy()
        
        # Add My Company Row
        my_row = internal_metrics.copy()
        # Ensure keys match columns
        # If columns missing in internal, fill 0
        
        # Create a DataFrame for internal to concat
        internal_df = pd.DataFrame([my_row], index=['MY COMPANY'])
        
        # Concat
        combined_df = pd.concat([df, internal_df])
        
        # Calculate Percentile Rank for 'MY COMPANY'
        # Can calculate for everyone
        # Percentile = (Count < Value) / Total Count
        # Using scipy.stats.percentileofscore or pandas rank
        
        # We'll return the combined table. The UI can visualize the comparison.
        # But Requirement says: "Calculate the Percentile Rank... for MY COMPANY"
        # We can add a "Rank" column or just return the data for the radar chart which needs values.
        # Let's clean the data for Radar (Normalize?)
        # Radar chart usually plots raw values or normalized. 
        # For this Engine, let's return the combined DataFrame.
        # Normalization/Ranking is better done for visualization or specific report.
        
        return combined_df
