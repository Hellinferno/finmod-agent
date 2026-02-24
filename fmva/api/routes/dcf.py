from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DCFRunRequest(BaseModel):
    company_id: str
    wacc_pct: float
    tgr_pct: float
    run_llm: bool = False

@router.post("/run")
async def run_dcf_valuation(payload: DCFRunRequest):
    """
    Executes the DCF valuation process.
    Connects to the `fmva.engines.dcf.run_dcf()` function.
    """
    # Validation against "Golden Path" rules
    if payload.wacc_pct <= payload.tgr_pct:
        raise ValueError("WACC must be strictly greater than the Terminal Growth Rate (TGR).")
        
    # TODO: In real implementation, load company data from `fmva.core.ingestion` 
    # and execute `fmva.engines.dcf.run_dcf()`

    # Mock success path
    return {
        "status": "success",
        "implied_share_price": 9.52,
        "enterprise_value_m": 1102,
        "warnings": [],
        "audit_trail_id": f"audit_{payload.company_id}_dcf"
    }
