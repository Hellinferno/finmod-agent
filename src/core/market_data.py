
import yfinance as yf

def get_market_benchmark(ticker="SPY"):
    """
    Fetches the P/E Ratio (Price-to-Earnings) of a benchmark (e.g., S&P 500 or a specific stock).
    Returns a dictionary with the data.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get Trailing P/E (default to 0 if missing)
        pe_ratio = info.get('trailingPE', 0)
        sector = info.get('sector', 'Unknown')
        price = info.get('currentPrice', 0)
        
        return {
            "ticker": ticker.upper(),
            "pe_ratio": round(pe_ratio, 2),
            "price": price,
            "sector": sector,
            "success": True
        }
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {"success": False, "pe_ratio": 25.0} # Fallback default
