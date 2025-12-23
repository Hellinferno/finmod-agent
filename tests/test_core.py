import pytest
from pydantic import ValidationError
import numpy as np
from src.core.valuation import calculate_dcf, run_sensitivity_analysis
from src.models.schemas import FinancialInput

# --- Test Validation ---

def test_validation_wacc_invalid():
    """Attempt to create a FinancialInput model with a wacc of -0.05. Assert that it raises a ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        FinancialInput(
            revenue_historical=[100.0],
            growth_rate_projection=0.05,
            wacc=-0.05, # Invalid
            terminal_growth_rate=0.02
        )
    # Check that the error relates to 'wacc'
    assert 'wacc' in str(excinfo.value)
    # Optional: Check message provided by Pydantic 'gt' validator

def test_validation_terminal_growth_invalid():
    """Attempt to set terminal_growth_rate higher than wacc. Assert that it fails."""
    with pytest.raises(ValidationError) as excinfo:
        FinancialInput(
            revenue_historical=[100.0],
            growth_rate_projection=0.05,
            wacc=0.08,
            terminal_growth_rate=0.09 # > WACC, should fail
        )
    # Check for our custom validator message
    assert "Terminal growth cannot exceed WACC" in str(excinfo.value)

# --- Test Valuation Math ---

def test_valuation_standard_case():
    """
    Standard Case:
    Cash Flows: [100, 100, 100, 100, 100] (Implied Revenue=500, Margin=0.20)
    WACC: 0.10
    Terminal Growth: 0.0 (Note: TV itself is non-zero, but we verify NPV of explicit flows)
    """
    # Setup inputs to produce FCF = 100
    # Logic: FCF = Revenue * 0.20 => 100 = Revenue * 0.20 => Revenue = 500
    # Growth = 0.0 -> Revenue constant at 500
    
    data = FinancialInput(
        revenue_historical=[500.0],
        growth_rate_projection=0.0,
        wacc=0.10,
        terminal_growth_rate=0.00 # For this test we assume TV logic runs but we check NPV
    )
    
    result = calculate_dcf(data)
    
    # Assert that calculate_dcf returns a value close to 379.08 for the NPV component
    # NPV of 5 payments of 100 @ 10%:
    # 100/1.1 + 100/1.21 + 100/1.331 + 100/1.4641 + 100/1.61051
    # 90.909 + 82.645 + 75.131 + 68.301 + 62.092 = ~379.078
    
    expected_npv = 379.08
    assert result["npv"] == pytest.approx(expected_npv, rel=1e-3)

# --- Test Sensitivity ---

def test_sensitivity_matrix_properties():
    """
    Test Sensitivity:
    Run the sensitivity function. Ensure it returns a Matrix of correct shape (e.g., 5x5 grid) 
    and that values increase as Growth increases and WACC decreases.
    """
    data = FinancialInput(
        revenue_historical=[500.0],
        growth_rate_projection=0.05,
        wacc=0.10,
        terminal_growth_rate=0.02
    )
    
    matrix = run_sensitivity_analysis(data)
    
    # 1. Check Shape
    assert matrix.shape == (5, 5)
    
    # 2. Check Directionality
    # Rows = WACC (Increasing index -> Higher WACC -> Lower EV)
    # Cols = Growth (Increasing index -> Higher Growth -> Higher EV)
    
    # Compare top-left (Low WACC, Low Growth) vs Bottom-Left (High WACC, Low Growth)
    # Higher WACC should yield LOWER value
    # matrix[0,0] (Low WACC) vs matrix[4,0] (High WACC)
    assert matrix[0, 0] > matrix[4, 0], "Higher WACC should result in lower Enterprise Value"
    
    # Compare top-left (Low WACC, Low Growth) vs Top-Right (Low WACC, High Growth)
    # Higher Growth should yield HIGHER value
    # matrix[0,0] (Low Growth) vs matrix[0,4] (High Growth)
    assert matrix[0, 4] > matrix[0, 0], "Higher Growth should result in higher Enterprise Value"
