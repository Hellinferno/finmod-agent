"""
DCF valuation engine — terminal value, discounting, enterprise value, equity bridge.
"""

from __future__ import annotations
from typing import Optional
from loguru import logger
from fmva.audit.trail import AuditTrail
from fmva.core.schemas import (
    AssumptionSet, BalanceSheet, DCFResult, FinancialStatements,
    ProjectionTable, WACCResult,
)
from fmva.engines.projection import project_income_statement
from fmva.engines.wacc import calculate_wacc
from fmva.exceptions import ComputationError, GordonGrowthError


def calculate_discount_factors(
    wacc: float, n_years: int, mid_year: bool = True, audit: AuditTrail = None,
) -> dict[int, float]:
    """Calculate discount factors for each year."""
    if audit is None:
        audit = AuditTrail()
    factors = {}
    for t in range(1, n_years + 1):
        exp = t - 0.5 if mid_year else float(t)
        df = 1.0 / ((1.0 + wacc) ** exp)
        factors[t] = df
        audit.log(f"Discount Factor Year {t}", "DF = 1/(1+WACC)^t",
                  {"WACC": wacc, "t": exp}, df, "x", "dcf")
    return factors


def calculate_terminal_value_gordon(
    last_ufcf: float, wacc: float, tgr: float, audit: AuditTrail = None,
) -> float:
    """TV = UFCF_n × (1+g) / (WACC - g). Raises GordonGrowthError if WACC ≤ g."""
    if audit is None:
        audit = AuditTrail()
    if wacc <= tgr:
        raise GordonGrowthError(wacc, tgr)
    tv = last_ufcf * (1 + tgr) / (wacc - tgr)
    audit.log("Terminal Value (Gordon)", "TV = UFCF×(1+g)/(WACC-g)",
              {"UFCF_n": last_ufcf, "g": tgr, "WACC": wacc}, tv, "$M", "dcf")
    return tv


def calculate_terminal_value_exit_multiple(
    last_ebitda: float, exit_multiple: float, audit: AuditTrail = None,
) -> float:
    """TV = EBITDA_n × Exit Multiple."""
    if audit is None:
        audit = AuditTrail()
    tv = last_ebitda * exit_multiple
    audit.log("Terminal Value (Exit Multiple)", "TV = EBITDA×M",
              {"EBITDA_n": last_ebitda, "M": exit_multiple}, tv, "$M", "dcf")
    return tv


def run_full_dcf(
    financials: FinancialStatements,
    assumptions: AssumptionSet,
    wacc_result: Optional[WACCResult] = None,
    audit: AuditTrail = None,
) -> DCFResult:
    """
    Run the complete DCF valuation: projection → discount → TV → EV → equity bridge.
    """
    if audit is None:
        audit = AuditTrail(company_name=financials.metadata.company_name)

    n = assumptions.projection_years
    latest_is = financials.latest_income_statement
    latest_bs = financials.latest_balance_sheet

    if latest_is is None or latest_is.revenue is None:
        raise ComputationError("Cannot run DCF: missing latest income statement or revenue")

    base_revenue = latest_is.revenue

    # ── WACC ───────────────────────────────────────────────────────────────
    if wacc_result is None:
        if assumptions.wacc is not None:
            from fmva.core.schemas import WACCResult as WR
            wacc_result = WR(wacc=assumptions.wacc, cost_of_equity=assumptions.wacc,
                             cost_of_debt_after_tax=0, beta=1.0, risk_free_rate=0.045,
                             equity_risk_premium=0.055, weight_equity=1.0, weight_debt=0.0)
        else:
            wacc_result = calculate_wacc(
                ticker=financials.metadata.ticker,
                tax_rate=assumptions.tax_rate,
                audit=audit,
            )
    wacc = wacc_result.wacc

    # ── Projection ─────────────────────────────────────────────────────────
    proj = project_income_statement(base_revenue, assumptions, n, audit)

    # ── Discount Factors ───────────────────────────────────────────────────
    dfs = calculate_discount_factors(wacc, n, assumptions.mid_year_convention, audit)

    # ── PV of UFCFs ────────────────────────────────────────────────────────
    pv_ufcf = {}
    for t in range(1, n + 1):
        pv = proj.ufcf[t] * dfs[t]
        pv_ufcf[t] = pv
        audit.log(f"PV UFCF Year {t}", "PV = UFCF × DF",
                  {"UFCF": proj.ufcf[t], "DF": dfs[t]}, pv, "$M", "dcf")
    sum_pv = sum(pv_ufcf.values())
    audit.log("Sum PV UFCFs", "Σ PV(UFCF)", {"pv_ufcfs": list(pv_ufcf.values())}, sum_pv, "$M", "dcf")

    # ── Terminal Values ────────────────────────────────────────────────────
    last_ufcf = proj.ufcf[n]
    last_ebitda = proj.ebitda[n]

    tv_gordon = calculate_terminal_value_gordon(last_ufcf, wacc, assumptions.terminal_growth_rate, audit)
    tv_exit = calculate_terminal_value_exit_multiple(last_ebitda, assumptions.exit_multiple, audit)

    # PV of terminal values
    tv_df = dfs[n]  # Discount at the last year
    if not assumptions.mid_year_convention:
        tv_df = 1.0 / ((1.0 + wacc) ** n)

    pv_tv_gordon = tv_gordon * tv_df
    pv_tv_exit = tv_exit * tv_df
    audit.log("PV TV (Gordon)", "PV_TV = TV × DF_n", {"TV": tv_gordon, "DF": tv_df}, pv_tv_gordon, "$M", "dcf")
    audit.log("PV TV (Exit)", "PV_TV = TV × DF_n", {"TV": tv_exit, "DF": tv_df}, pv_tv_exit, "$M", "dcf")

    # ── Enterprise Value ───────────────────────────────────────────────────
    ev_gordon = sum_pv + pv_tv_gordon
    ev_exit = sum_pv + pv_tv_exit
    audit.log("EV (Gordon)", "EV = ΣPV + PV_TV", {"ΣPV": sum_pv, "PV_TV": pv_tv_gordon}, ev_gordon, "$M", "dcf")
    audit.log("EV (Exit)", "EV = ΣPV + PV_TV", {"ΣPV": sum_pv, "PV_TV": pv_tv_exit}, ev_exit, "$M", "dcf")

    # ── Equity Bridge ──────────────────────────────────────────────────────
    net_debt = 0.0
    if latest_bs:
        net_debt = latest_bs.net_debt
    audit.log("Net Debt", "ND = STD + LTD - Cash - STI",
              {"net_debt": net_debt}, net_debt, "$M", "dcf")

    eq_gordon = ev_gordon - net_debt
    eq_exit = ev_exit - net_debt
    audit.log("Equity Value (Gordon)", "EqV = EV - ND", {"EV": ev_gordon, "ND": net_debt}, eq_gordon, "$M", "dcf")
    audit.log("Equity Value (Exit)", "EqV = EV - ND", {"EV": ev_exit, "ND": net_debt}, eq_exit, "$M", "dcf")

    # ── Implied Share Price ────────────────────────────────────────────────
    shares = financials.metadata.diluted_shares_outstanding
    ip_gordon = eq_gordon / shares if shares else None
    ip_exit = eq_exit / shares if shares else None

    # TV as % of EV
    tv_pct_gordon = (pv_tv_gordon / ev_gordon * 100) if ev_gordon else None
    tv_pct_exit = (pv_tv_exit / ev_exit * 100) if ev_exit else None

    # Warnings
    warns = {}
    if tv_pct_gordon and tv_pct_gordon > 80:
        warns["tv_high_pct_gordon"] = f"TV is {tv_pct_gordon:.0f}% of EV (Gordon)"
    if tv_pct_exit and tv_pct_exit > 80:
        warns["tv_high_pct_exit"] = f"TV is {tv_pct_exit:.0f}% of EV (Exit Multiple)"

    logger.info(
        f"DCF complete: EV(Gordon)=${ev_gordon:,.0f}M, EV(Exit)=${ev_exit:,.0f}M, "
        f"Implied price: ${ip_gordon:,.2f}–${ip_exit:,.2f}"
        if ip_gordon and ip_exit else
        f"DCF complete: EV(Gordon)=${ev_gordon:,.0f}M, EV(Exit)=${ev_exit:,.0f}M"
    )

    return DCFResult(
        projection=proj, discount_factors=dfs, pv_ufcf=pv_ufcf, sum_pv_ufcf=sum_pv,
        terminal_value_gordon=tv_gordon, terminal_value_exit_multiple=tv_exit,
        pv_terminal_value_gordon=pv_tv_gordon, pv_terminal_value_exit_multiple=pv_tv_exit,
        enterprise_value_gordon=ev_gordon, enterprise_value_exit_multiple=ev_exit,
        net_debt=net_debt, equity_value_gordon=eq_gordon, equity_value_exit_multiple=eq_exit,
        implied_price_gordon=ip_gordon, implied_price_exit_multiple=ip_exit,
        tv_pct_of_ev_gordon=tv_pct_gordon, tv_pct_of_ev_exit_multiple=tv_pct_exit,
        wacc_result=wacc_result, assumptions=assumptions, warnings=warns,
    )
