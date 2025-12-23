import pytest
import pandas as pd
import numpy as np
from src.core.forecasting import ForecastEngine
from src.models.forecast_schemas import ForecastInput

def test_flat_line():
    """
    Test Case 2: 'The Flat Line'
    Feed constant values. Ensure forecast is constant and seasonality close to 0.
    """
    # 24 months of 100
    dates = pd.date_range(start='2020-01-01', periods=24, freq='MS').strftime('%Y-%m-%d').tolist()
    values = [100.0] * 24
    
    input_data = ForecastInput(
        dates=dates,
        values=values,
        periods=12,
        seasonality_mode='additive'
    )
    
    output = ForecastEngine.generate_forecast(input_data)
    
    # Check Forecast
    forecast_vals = np.array(output.forecast_values)
    assert np.allclose(forecast_vals, 100.0, atol=1.0), "Forecast should remain ~100 for flat input"
    
    # Check Seasonality
    seasonal_vals = np.array(output.seasonal)
    # Seasonal component of a flat line in additive model should be 0
    # statsmodels decomp might produce tiny noise, so we check near zero
    assert np.allclose(seasonal_vals, 0.0, atol=1.0), "Seasonality should be ~0 for flat input"

def test_perfect_sine_wave():
    """
    Test Case 1: 'The Perfect Sine Wave'
    Feed 24 months of a sine wave. Ensure prediction follows the wave.
    """
    # Create Sine Wave: y = 100 + 50*sin(...)
    # Period 12 months
    t = np.arange(24)
    # 2*pi*t / 12
    values = 100 + 50 * np.sin(2 * np.pi * t / 12)
    dates = pd.date_range(start='2020-01-01', periods=24, freq='MS').strftime('%Y-%m-%d').tolist()
    
    input_data = ForecastInput(
        dates=dates,
        values=values.tolist(),
        periods=12,
        seasonality_mode='additive'
    )
    
    output = ForecastEngine.generate_forecast(input_data)
    
    # Forecast should match the next 12 months (indices 24-35)
    # t_future = np.arange(24, 36)
    # expected = 100 + 50 * np.sin(2 * np.pi * t_future / 12)
    
    t_next = np.arange(24, 36)
    expected_values = 100 + 50 * np.sin(2 * np.pi * t_next / 12)
    forecast_values = np.array(output.forecast_values)
    
    # Allow some tolerance because Holt-Winters estimates "Local Level/Trend" which takes time to converge perfectly
    # But for a perfect repeated component, it should be very close.
    # We use a loose tolerance (atol=10) to pass typical HW convergence, 
    # but strictly enough to ensure it's wavy, not flat.
    
    # Check correlation or RMSE?
    # Let's check mean error is low
    mae = np.mean(np.abs(forecast_values - expected_values))
    assert mae < 15.0, f"MAE {mae} too high. Forecast didn't match sine wave closely."
    
    # Check seasonality captured
    # Peak should be around 150, Trough around 50.
    assert np.max(forecast_values) > 130
    assert np.min(forecast_values) < 70
