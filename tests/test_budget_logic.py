import pytest
import pandas as pd
import numpy as np
from datetime import date
from src.core.variance import BudgetEngine

def test_zero_division():
    """
    Ensure a line item with $0 Budget and $100 Actual does NOT crash the app.
    Should return 0.0 or handle gracefully as per logic.
    """
    budget_data = {
        'department': ['Sales'],
        'gl_code': ['5000'],
        'month': [date(2024, 1, 1)],
        'amount': [0.0]
    }
    actual_data = {
        'department': ['Sales'],
        'gl_code': ['5000'],
        'month': [date(2024, 1, 1)],
        'amount': [100.0]
    }
    
    budget_df = pd.DataFrame(budget_data)
    actual_df = pd.DataFrame(actual_data)
    
    engine = BudgetEngine()
    result = engine.calculate_variance(budget_df, actual_df)
    
    # Check Row 0
    row = result.iloc[0]
    
    # Var Pct should be 0.0 (as per our logic: where budget==0 -> 0.0)
    assert row['variance_pct'] == 0.0
    
    # Status should be Unfavorable (Actual 100 > Budget 0)
    assert row['status'] == "Unfavorable"

def test_aggregation():
    """
    Ensure the engine correctly sums up total spend for the "Engineering" department.
    We test this by feeding multiple rows and checking the merged dataframe correctness.
    Note: The Engine returns line-item variances. Aggregation usually happens in UI or another step.
    But we can verify the data integrity allows aggregation.
    """
    budget_data = {
        'department': ['Engineering', 'Engineering'],
        'gl_code': ['5000', '6000'],
        'month': [date(2024, 1, 1), date(2024, 1, 1)],
        'amount': [1000.0, 2000.0]
    }
    actual_data = {
        'department': ['Engineering', 'Engineering'],
        'gl_code': ['5000', '6000'],
        'month': [date(2024, 1, 1), date(2024, 1, 1)],
        'amount': [900.0, 2100.0]
    }
    
    budget_df = pd.DataFrame(budget_data)
    actual_df = pd.DataFrame(actual_data)
    
    engine = BudgetEngine()
    result = engine.calculate_variance(budget_df, actual_df)
    
    # Check total actuals
    eng_df = result[result['department'] == 'Engineering']
    total_actual = eng_df['amount_actual'].sum()
    
    assert total_actual == 3000.0
    
    # Check individual variances
    # Row 1: Budget 1000, Actual 900. Var +100. Favorable.
    r1 = eng_df[eng_df['gl_code'] == '5000'].iloc[0]
    assert r1['variance_abs'] == 100.0
    assert r1['status'] == "Favorable"

def test_forecast_logic():
    # Setup: 2 months. Jan (Actual=500), Feb (Actual=0/NaN, Budget=1000).
    # Burn Rate from Jan = 500.
    # Feb Budget should become 500.
    
    data = {
        'department': ['Marketing', 'Marketing'],
        'gl_code': ['7000', '7000'],
        'month': [date(2024, 1, 1), date(2024, 2, 1)],
        'amount_budget': [1000.0, 1000.0],
        'amount_actual': [500.0, 0.0] # Jan has actual, Feb is future
    }
    df = pd.DataFrame(data)
    
    engine = BudgetEngine()
    result = engine.generate_forecast(df)
    
    # Check Feb (index 1)
    feb_row = result.iloc[1]
    assert feb_row['forecasted_budget'] == 500.0
