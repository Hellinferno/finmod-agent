import pytest
import pandas as pd
import numpy as np
from src.core.etl_engine import SmartImporter

def test_messy_headers():
    """
    Test Case 1: 'The Messy Headers'
    Input: ['Mnth', 'TtL Sales', 'Cost of Gds']
    Expect: ['date', 'revenue', 'cogs']
    """
    df = pd.DataFrame(columns=['Mnth', 'TtL Sales', 'Cost of Gds'])
    mapped_df, report = SmartImporter.fuzzy_map_columns(df)
    
    cols = mapped_df.columns.tolist()
    assert 'date' in cols, "Mnth should map to date"
    assert 'revenue' in cols, "TtL Sales should map to revenue"
    assert 'cogs' in cols, "Cost of Gds should map to cogs"

def test_dirty_numbers():
    """
    Test Case 2: 'The Dirty Numbers'
    Input: "$1,250.00", "(500.00)", "-"
    Expect: 1250.0, -500.0, 0.0
    """
    df = pd.DataFrame({
        'revenue': ["$1,250.00", "(500.00)", "-", "100"],
        'cogs': ["(200)", "$50", " - ", "Garbage"]
    })
    
    cleaned = SmartImporter.clean_financial_values(df)
    
    # Revenue checks
    rev = cleaned['revenue']
    assert rev[0] == 1250.0
    assert rev[1] == -500.0
    assert rev[2] == 0.0
    assert rev[3] == 100.0
    
    # COGS checks
    cogs = cleaned['cogs']
    assert cogs[0] == -200.0
    assert cogs[1] == 50.0
    assert cogs[2] == 0.0
    assert np.isnan(cogs[3])

def test_garbage_check():
    """
    Test Case 3: 'The Garbage Check'
    Input: "Employee Birthday"
    Expect: Score < 85, NOT mapped.
    """
    df = pd.DataFrame(columns=['Employee Birthday', 'Random Stuff', 'Sales'])
    mapped_df, report = SmartImporter.fuzzy_map_columns(df)
    
    assert 'Employee Birthday' in mapped_df.columns, "Garbage column should not be renamed"
    assert 'revenue' in mapped_df.columns, "Sales should still be mapped"
    
    # Check report
    match = report.get('Employee Birthday', '')
    assert "Unmapped" in match, "Should be flagged as Low Confidence/Unmapped"
