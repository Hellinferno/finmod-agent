from typing import List
from pydantic import BaseModel, Field, field_validator

class ProjectInput(BaseModel):
    name: str
    initial_investment: float = Field(..., gt=0, description="Initial investment must be positive.")
    cash_flows: List[float] = Field(..., min_length=1, description="List of expected annual cash flows.")
    volatility: float = Field(..., ge=0, le=1.0, description="Volatility/Standard Deviation (e.g. 0.15 for 15%).")
    discount_rate: float = Field(..., gt=0, le=1.0, description="WACC / Discount Rate (e.g. 0.10 for 10%).")

    @field_validator('cash_flows')
    @classmethod
    def check_non_empty(cls, v):
        if not v:
            raise ValueError("Cash flows cannot be empty.")
        return v
