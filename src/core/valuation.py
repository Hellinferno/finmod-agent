from typing import Dict
import numpy as np
from src.models.schemas import FinancialInput

def calculate_dcf(data: FinancialInput) -> Dict[str, float]:
    """
    Calculates DCF Valuation.
    Supports two modes:
    1. Explicit Cash Flows (from UI)
    2. Revenue Projection (from Config/Internal)
    """
    wacc = data.wacc
    g_term = data.terminal_growth_rate
    
    if data.cash_flows:
        # Mode 1: Explicit Cash Flows
        fcfs = np.array(data.cash_flows)
        # Assume years 1..N
        years = len(fcfs)
        projected_years = np.arange(1, years + 1)
        discount_factors = (1 + wacc) ** projected_years
        pv_fcfs = fcfs / discount_factors
        npv_fcf = np.sum(pv_fcfs)
        
        # Terminal Value
        fcf_final = fcfs[-1]
        terminal_value = fcf_final * (1 + g_term) / (wacc - g_term)
        pv_terminal_value = terminal_value / ((1 + wacc) ** years)
        
    elif data.revenue_historical:
        # Mode 2: Revenue Projection
        last_revenue = data.revenue_historical[-1]
        years = 5
        projected_years = np.arange(1, years + 1)
        
        growth_rate = data.growth_rate_projection
        revenues = last_revenue * ((1 + growth_rate) ** projected_years)
        
        FCF_MARGIN = 0.20 
        fcfs = revenues * FCF_MARGIN
        
        discount_factors = (1 + wacc) ** projected_years
        pv_fcfs = fcfs / discount_factors
        npv_fcf = np.sum(pv_fcfs)
        
        fcf_final = fcfs[-1]
        terminal_value = fcf_final * (1 + g_term) / (wacc - g_term)
        pv_terminal_value = terminal_value / ((1 + wacc) ** years)
    else:
        raise ValueError("Insufficient data for DCF: provide cash_flows or revenue_historical")
    
    # Enterprise Value
    enterprise_value = npv_fcf + pv_terminal_value
    
    # Equity Value
    equity_value = enterprise_value
    
    return {
        "npv": float(npv_fcf),
        "irr": 0.0,
        "enterprise_value": float(enterprise_value),
        "equity_value": float(equity_value),
        "pv_terminal_value": float(pv_terminal_value), # Added for Waterfall helpfulness
        "cash_flows": fcfs.tolist() # Return calculated/parsed flows
    }

def run_sensitivity_analysis(data: FinancialInput) -> np.ndarray:
    """
    Varies WACC (+/- 2%) and Growth Rate (+/- 1%).
    """
    # Base values
    base_wacc = data.wacc
    base_growth = data.growth_rate_projection # Usually 0.0 if explicit flows used, or user provided 'implicit' growth?
    
    # If using explicit cash flows, what does "varying growth" mean?
    # We will treat `base_growth` as 0.0 relative to the provided flows, 
    # and applying delta means scaling the provided flows?
    # Or we assume the provided flows HAVE a growth rate embedded and we adjust it?
    # Simplest: "Scenario Growth". New Flow_t = Base_Flow_t * (1 + g_scenario)^t.
    
    # Ranges
    wacc_steps = np.linspace(base_wacc - 0.02, base_wacc + 0.02, 5)
    growth_steps = np.linspace(base_growth - 0.01, base_growth + 0.01, 5)
    
    W, G = np.meshgrid(wacc_steps, growth_steps, indexing='ij')
    
    ev_matrix = np.zeros_like(W)
    
    # Resolve Base Flows
    if data.cash_flows:
        base_fcfs = np.array(data.cash_flows)
    elif data.revenue_historical:
        last_revenue = data.revenue_historical[-1]
        years = 5
        base_revenues = last_revenue * ((1 + base_growth) ** np.arange(1, years + 1))
        FCF_MARGIN = 0.20
        base_fcfs = base_revenues * FCF_MARGIN
    else:
        return np.zeros((5,5))

    years = len(base_fcfs)
    projected_years = np.arange(1, years + 1)
    
    # Loop for readability/broadcasting handling
    # We apply G (which is e.g. -0.01 to +0.01) as ADDITIVE growth to the base stream?
    # Or is G absolute growth?
    # If base_growth is 0.0 (explicit flows), then G goes -0.01 to 0.01.
    # Flow_t(new) = Flow_t(base) * (1 + G_delta)^t. 
    # Yes, let's use G - base_growth as the delta.
    
    growth_delta = G - base_growth
    
    # EV Calculation inside matrix
    # Sum PV(FCF)
    for t_idx, t in enumerate(projected_years):
        # We broadcast base_fcfs[t_idx] across the grid
        flow_t = base_fcfs[t_idx] * ((1 + growth_delta) ** t)
        discount_factor = (1 + W) ** t
        ev_matrix += flow_t / discount_factor
        
    # Terminal Value
    # TV uses the LAST flow.
    # FCF_final_scenario = Base_Final * (1+delta)**5
    last_flow_scenario = base_fcfs[-1] * ((1 + growth_delta) ** years)
    
    g_term = data.terminal_growth_rate
    tv_num = last_flow_scenario * (1 + g_term)
    tv_den = (W - g_term)
    
    pv_tv = (tv_num / tv_den) / ((1 + W) ** years)
    
    ev_matrix += pv_tv
    
    return ev_matrix
