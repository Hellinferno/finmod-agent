from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class Department(str, Enum):
    SALES = "Sales"
    ENGINEERING = "Engineering"
    MARKETING = "Marketing"
    GA = "G&A"
    OPS = "Ops"

class BudgetRow(BaseModel):
    department: Department
    gl_code: str
    month: date
    amount: float = Field(..., ge=0.0, description="Budget amount must be non-negative.")

class VarianceOutput(BaseModel):
    department: str
    gl_code: str
    budget_amount: float
    actual_amount: float
    variance_abs: float
    variance_pct: float # Allow NaN/Inf conceptually, but float type handles it.
    status: str # Enum: "Favorable", "Unfavorable", "Neutral"
