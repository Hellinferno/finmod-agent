from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator
import numpy as np

class ForecastInput(BaseModel):
    dates: List[str] = Field(..., description="ISO format 'YYYY-MM-DD'")
    values: List[float] = Field(..., description="Historical data points (Must not contain NaNs)")
    periods: int = Field(default=12, gt=0, description="Number of months to forecast")
    seasonality_mode: Literal["additive", "multiplicative"] = Field(..., description="Seasonality mode")

    @field_validator('values')
    @classmethod
    def check_nans(cls, v):
        if any(np.isnan(x) for x in v):
            raise ValueError("Values must not contain NaNs")
        return v
    
    @field_validator('dates')
    @classmethod
    def check_dates_match_values(cls, v, info):
        # We can perform a rough check or rely on logic to align. 
        # Ideally, Pydantic 2 validation context allows checking against 'values'.
        # For simplicity in this step, we assume the caller ensures matching definition.
        return v

class ForecastOutput(BaseModel):
    history_dates: List[str]
    history_values: List[float]
    forecast_dates: List[str]
    forecast_values: List[float]
    lower_bound: List[float]
    upper_bound: List[float]
    trend: List[float]
    seasonal: List[float]
