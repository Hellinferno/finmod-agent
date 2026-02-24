from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from fmva.core.ingestion import load_json
from fmva.core.normalization import normalize
from fmva.engines.assumptions import get_preset
from fmva.engines.dcf import run_full_dcf
from fmva.exceptions import FMVAError

router = APIRouter()

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_BY_COMPANY = {
    "TECH": REPO_ROOT / "data" / "fixtures" / "techcorp.json",
    "MFG": REPO_ROOT / "data" / "fixtures" / "manufactureco.json",
    "RETAIL": REPO_ROOT / "data" / "fixtures" / "retailchain.json",
}


class DCFRunRequest(BaseModel):
    company_id: str = Field(min_length=1)
    wacc_pct: float = Field(gt=0, lt=100)
    tgr_pct: float = Field(gt=-50, lt=50)
    run_llm: bool = False


class DCFRunResponse(BaseModel):
    status: str
    implied_share_price: float | None
    enterprise_value_m: float | None
    equity_value_m: float | None
    pv_ufcfs: list[float]
    pv_terminal_value: float | None
    warnings: list[str]
    audit_trail_id: str


def _resolve_fixture_path(company_id: str) -> Path:
    key = company_id.strip().upper()
    path = FIXTURE_BY_COMPANY.get(key)
    if path is None:
        valid = ", ".join(sorted(FIXTURE_BY_COMPANY.keys()))
        raise HTTPException(
            status_code=404,
            detail=f"Unknown company_id '{company_id}'. Use one of: {valid}",
        )
    if not path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Fixture data not found for company_id '{company_id}'",
        )
    return path


@router.post("/run", response_model=DCFRunResponse)
async def run_dcf_valuation(payload: DCFRunRequest):
    """
    Execute a full DCF run against fixture-backed financial statements.
    """
    if payload.wacc_pct <= payload.tgr_pct:
        raise HTTPException(
            status_code=400,
            detail="WACC must be strictly greater than the Terminal Growth Rate (TGR).",
        )

    fixture_path = _resolve_fixture_path(payload.company_id)

    try:
        raw = load_json(str(fixture_path))
        financials = normalize(raw)
        assumptions = get_preset("base").model_copy(
            update={
                "wacc": payload.wacc_pct / 100.0,
                "terminal_growth_rate": payload.tgr_pct / 100.0,
            }
        )
        result = run_full_dcf(financials, assumptions)
    except FMVAError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"DCF execution failed: {exc}",
        ) from exc

    implied_share_price = result.implied_price_gordon
    if implied_share_price is None:
        implied_share_price = result.implied_price_exit_multiple

    warnings = [str(v) for v in (result.warnings or {}).values()]
    audit_trail_id = f"audit_{payload.company_id.strip().upper()}_dcf"

    return DCFRunResponse(
        status="success",
        implied_share_price=implied_share_price,
        enterprise_value_m=result.enterprise_value_gordon,
        equity_value_m=result.equity_value_gordon,
        pv_ufcfs=[float(result.pv_ufcf[t]) for t in sorted(result.pv_ufcf.keys())],
        pv_terminal_value=result.pv_terminal_value_gordon,
        warnings=warnings,
        audit_trail_id=audit_trail_id,
    )
