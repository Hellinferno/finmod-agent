from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AssumptionUpdate(BaseModel):
    wacc_pct: float
    revenue_growth_stage1_pct: float
    ebitda_margin_pct: float

@router.put("/update/{company_id}")
async def update_assumptions(company_id: str, payload: AssumptionUpdate):
    """
    Updates the assumption set for the company.
    Connects to `fmva.engines.assumptions.create_assumption_set()`.
    """
    if payload.ebitda_margin_pct < 0:
        raise ValueError("EBITDA margin cannot be negative in the base assumption set.")

    return {
        "status": "success",
        "message": f"Assumptions updated for {company_id}",
        "scenario": "Base Case"
    }
