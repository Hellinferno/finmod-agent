import pandas as pd
import numpy as np
from src.core.variance import BudgetEngine

def verify_zero_division():
    print("--- STARTING BUDGET ZERO TEST ---")
    
    # Scene: Budget is 0, Actual is 100.
    budget_df = pd.DataFrame([
        {'department': 'Sales', 'gl_code': '4001', 'month': '2024-01-01', 'amount': 0.0}
    ])
    actual_df = pd.DataFrame([
        {'department': 'Sales', 'gl_code': '4001', 'month': '2024-01-01', 'amount': 100.0}
    ])
    
    try:
        result = BudgetEngine.calculate_variance(budget_df, actual_df)
        var_pct = result.iloc[0]['variance_pct']
        print(f"Budget: 0.0, Actual: 100.0 -> Variance %: {var_pct}")
        
        if var_pct == 0.0:
             print("✅ PASS: Handled Zero Division gracefully (returned 0.0).")
        elif np.isinf(var_pct):
             print("⚠️ PASS: Handled Zero Division (returned Inf), but check if UI expects 0.0.")
        else:
             print(f"❓ UNKNOWN: Got {var_pct}")
             
    except Exception as e:
        print(f"❌ FAIL: Crashed with error: {e}")

if __name__ == "__main__":
    verify_zero_division()
