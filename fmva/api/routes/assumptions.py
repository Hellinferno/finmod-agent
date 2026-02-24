from fastapi import APIRouter
from pydantic import BaseModel, Field

from fmva.core.schemas import Scenario
from fmva.engines.assumptions import get_preset

router = APIRouter()


class AssumptionUpdate(BaseModel):
    wacc_pct: float = Field(gt=0, lt=100)
    revenue_growth_stage1_pct: float = Field(gt=-100, lt=200)
    ebitda_margin_pct: float = Field(ge=0, le=100)


@router.put("/update/{company_id}")
async def update_assumptions(company_id: str, payload: AssumptionUpdate):
    """
    Build a normalized custom assumption profile from percent inputs.
    """
    base = get_preset("base")
    custom = base.model_copy(
        update={
            "scenario": Scenario.CUSTOM,
            "wacc": payload.wacc_pct / 100.0,
            "revenue_growth_rates": [
                payload.revenue_growth_stage1_pct / 100.0
            ] * base.projection_years,
            "ebitda_margin": payload.ebitda_margin_pct / 100.0,
        }
    )

    return {
        "status": "success",
        "message": f"Assumptions updated for {company_id}",
        "scenario": custom.scenario.value,
        "assumptions": custom.model_dump(mode="json"),
    }
