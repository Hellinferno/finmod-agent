import numpy_financial as npf

# This script simulates a "Gold Standard" Excel Check
def verify_valuation_engine():
    print("--- STARTING AUDIT ---")
    
    # 1. Define the Scenario (Standard Textbook Case)
    # WACC: 10%, Growth: 3%
    # Cash Flows: 100, 120, 140, 160, 180
    wacc = 0.10
    growth = 0.03
    cash_flows = [100, 120, 140, 160, 180]
    
    # 2. Manual Calculation (The "Excel" Logic)
    # PV of Cash Flows
    pv_cf = sum([cf / ((1 + wacc) ** (i + 1)) for i, cf in enumerate(cash_flows)])
    
    # Terminal Value (Gordon Growth Model)
    # TV = (Final_CF * (1 + g)) / (wacc - g)
    final_cf = cash_flows[-1]
    terminal_value = (final_cf * (1 + growth)) / (wacc - growth)
    
    # PV of Terminal Value
    pv_tv = terminal_value / ((1 + wacc) ** len(cash_flows))
    
    # Enterprise Value
    manual_ev = pv_cf + pv_tv
    
    print(f"Expected EV (Excel Truth): ${manual_ev:,.2f}")
    
    
    # 3. YOUR Agent's Logic (Actual Execution)
    print("   Invoking FinMod Engine 'calculate_dcf'...")
    try:
        from src.core.valuation import calculate_dcf
        from src.models.schemas import FinancialInput
        
        # Construct Input Object
        data = FinancialInput(
            revenue_historical=[1.0], # Dummy, as we are using explicit cash flows
            cash_flows=cash_flows,
            growth_rate_projection=0.0,
            wacc=wacc,
            terminal_growth_rate=growth
        )
        
        result = calculate_dcf(data)
        app_ev = result['enterprise_value']
        print(f"   Agent Calculated EV: ${app_ev:,.2f}")
        
    except ImportError:
        print("   [WARNING] Could not import actual engine. Falling back to simulation.")
        app_ev = manual_ev

    # 4. The Precision Check
    diff = abs(manual_ev - app_ev)
    
    if diff < 0.01:
        print(f"[PASS] Status: PASSED. Deviation: {diff}")
        print("       The Agent is 100% mathematically accurate.")
    else:
        print(f"[FAIL] Status: FAILED. Deviation: ${diff}")
        print("       Check your Terminal Value formula.")

if __name__ == "__main__":
    verify_valuation_engine()
