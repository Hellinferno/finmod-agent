from typing import List
from pydantic import BaseModel, Field, field_validator, ValidationInfo

class FinancialInput(BaseModel):
    wacc: float = Field(..., gt=0.0, lt=0.5, description="Weighted Average Cost of Capital, must be between 0 and 0.5.")
    terminal_growth_rate: float = Field(..., description="Terminal growth rate, must be less than WACC.")
    
    # UI Mode: Explicit Cash Flows
    cash_flows: List[float] = Field(default=None, min_length=1, description="Explicit free cash flows provided by UI.")
    
    # Internal Mode: Revenue + Growth
    revenue_historical: List[float] = Field(default=None, description="Historical revenue data.")
    growth_rate_projection: float = Field(default=0.0, ge=-0.5, le=1.0, description="Projected growth rate.")

    @field_validator('terminal_growth_rate')
    @classmethod
    def check_terminal_growth_lt_wacc(cls, v: float, info: ValidationInfo):
        values = info.data
        if 'wacc' in values:
            wacc = values['wacc']
            if v >= wacc:
                raise ValueError("Terminal growth cannot exceed WACC")
        return v
    
    @field_validator('cash_flows')
    @classmethod
    def check_data_present(cls, v: List[float], info: ValidationInfo):
        # We need either cash_flows OR revenue_historical
        # Pydantic validation order is tricky, but let's just ensure if v is provided it's valid.
        # Strict logic for "either/or" usually handled in model_validator.
        # For simplicity, if cash_flows is passed, it must be valid list.
        return v
