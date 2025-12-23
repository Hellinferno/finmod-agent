import sys
import os
from pydantic import ValidationError

sys.path.append(os.getcwd())

from src.models.schemas import FinancialInput

def test_negative_wacc():
    print("Attempting to create FinancialInput with wacc = -10...")
    try:
        # Minimal valid inputs for other fields to isolate WACC error
        FinancialInput(
            wacc=-10.0, 
            terminal_growth_rate=0.02,
            revenue_historical=[100.0],
            growth_rate_projection=0.05
        )
        print("FAIL: FinancialInput accepted negative WACC!")
    except ValidationError as e:
        print("\nSUCCESS: ValidationError caught as expected.")
        print("--- Error Message (Simulation of UI Alert) ---")
        # Simulate the formatting used in callbacks.py
        msg = "; ".join([err['msg'] for err in e.errors()])
        print(msg)
        print("----------------------------------------------")

if __name__ == "__main__":
    test_negative_wacc()
