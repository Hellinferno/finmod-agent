"""
WACC calculator — CAPM-based with yfinance beta fetch and bounds validation.
"""

from __future__ import annotations
from typing import Optional
from loguru import logger
from fmva.audit.trail import AuditTrail
from fmva.config import DEFAULT_BETA, DEFAULT_EQUITY_RISK_PREMIUM, DEFAULT_RISK_FREE_RATE, WACC_MAX, WACC_MIN
from fmva.core.schemas import WACCResult
from fmva.exceptions import WACCBoundsError


def fetch_beta_yfinance(ticker: str) -> float:
    """Fetch equity beta from yfinance. Falls back to DEFAULT_BETA."""
    try:
        import yfinance as yf
        beta = yf.Ticker(ticker).info.get("beta")
        if beta and beta > 0:
            return float(beta)
        return DEFAULT_BETA
    except Exception:
        return DEFAULT_BETA


def calculate_wacc(
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    equity_risk_premium: float = DEFAULT_EQUITY_RISK_PREMIUM,
    beta: Optional[float] = None, ticker: Optional[str] = None,
    debt_rate: float = 0.06, tax_rate: float = 0.21,
    target_d_to_e: float = 0.30, audit: AuditTrail = None,
) -> WACCResult:
    """Calculate WACC = Ke*We + Kd(1-t)*Wd using CAPM."""
    if audit is None:
        audit = AuditTrail()
    if beta is None:
        beta = fetch_beta_yfinance(ticker) if ticker else DEFAULT_BETA

    ke = risk_free_rate + beta * equity_risk_premium
    audit.log("Cost of Equity", "Ke = Rf + β×ERP", {"Rf": risk_free_rate, "β": beta, "ERP": equity_risk_premium}, ke, "%", "wacc")

    kd_at = debt_rate * (1 - tax_rate)
    audit.log("Cost of Debt (AT)", "Kd_at = Kd×(1-τ)", {"Kd": debt_rate, "τ": tax_rate}, kd_at, "%", "wacc")

    we = 1 / (1 + target_d_to_e)
    wd = target_d_to_e / (1 + target_d_to_e)
    wacc = ke * we + kd_at * wd
    audit.log("WACC", "WACC = Ke×We + Kd_at×Wd", {"Ke": ke, "We": we, "Kd_at": kd_at, "Wd": wd}, wacc, "%", "wacc")

    if wacc < WACC_MIN or wacc > WACC_MAX:
        raise WACCBoundsError(wacc)

    logger.info(f"WACC: {wacc:.2%} (Ke={ke:.2%}, β={beta:.2f})")
    return WACCResult(wacc=wacc, cost_of_equity=ke, cost_of_debt_after_tax=kd_at, beta=beta,
                      risk_free_rate=risk_free_rate, equity_risk_premium=equity_risk_premium,
                      weight_equity=we, weight_debt=wd)
