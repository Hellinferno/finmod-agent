"""
Income statement projection engine.

Projects revenue, EBITDA, D&A, EBIT, and NOPAT for each forecast year.
Supports two-stage revenue growth and per-year EBITDA margins.
Every computation is audit-logged.
"""

from __future__ import annotations

from loguru import logger

from fmva.audit.trail import AuditTrail
from fmva.core.schemas import AssumptionSet, ProjectionTable
from fmva.engines.assumptions import get_ebitda_margin_for_year, extend_growth_rates


def project_revenue(
    ltm_revenue: float,
    growth_rates: list[float],
    audit: AuditTrail,
) -> dict[int, float]:
    """
    Project revenue for each forecast year using the given growth rates.

    Args:
        ltm_revenue: Last twelve months (base year) revenue.
        growth_rates: List of growth rates per year (decimal, e.g., 0.10 for 10%).
        audit: AuditTrail for logging.

    Returns:
        Dict mapping year index (1-based) to projected revenue.
    """
    revenues = {0: ltm_revenue}
    r = ltm_revenue

    for t, g in enumerate(growth_rates, start=1):
        r = r * (1 + g)
        revenues[t] = r
        audit.log(
            step=f"Revenue Year {t}",
            formula="R_{t} = R_{t-1} × (1 + g)",
            inputs={"R_{t-1}": revenues[t - 1], "growth_rate": g},
            output=r,
            unit="$M",
            module="projection",
        )

    return revenues


def project_income_statement(
    base_revenue: float,
    assumptions: AssumptionSet,
    n_years: int,
    audit: AuditTrail = None,
) -> ProjectionTable:
    """
    Project the full income statement for n_years.

    Produces: Revenue, EBITDA, D&A, EBIT, NOPAT for each year.

    Args:
        base_revenue: Year 0 (LTM) revenue.
        assumptions: Modeling assumptions.
        n_years: Number of projection years.
        audit: AuditTrail (creates new if None).

    Returns:
        ProjectionTable with all projected line items.
    """
    if audit is None:
        audit = AuditTrail()

    # Ensure we have enough growth rates
    assumptions = extend_growth_rates(assumptions, n_years)

    # ── Revenue Projection ─────────────────────────────────────────────────
    revenues = project_revenue(base_revenue, assumptions.revenue_growth_rates[:n_years], audit)

    years = list(range(1, n_years + 1))
    proj = ProjectionTable(years=years, revenue={0: base_revenue})

    for t in years:
        rev = revenues[t]
        proj.revenue[t] = rev

        # EBITDA
        margin = get_ebitda_margin_for_year(assumptions, t - 1)
        ebitda = rev * margin
        proj.ebitda[t] = ebitda
        audit.log(
            step=f"EBITDA Year {t}",
            formula="EBITDA = R × m_EBITDA",
            inputs={"R": rev, "m_EBITDA": margin},
            output=ebitda,
            unit="$M",
            module="projection",
        )

        # D&A
        da = rev * assumptions.da_to_revenue
        proj.da[t] = da
        audit.log(
            step=f"D&A Year {t}",
            formula="D&A = R × m_DA",
            inputs={"R": rev, "m_DA": assumptions.da_to_revenue},
            output=da,
            unit="$M",
            module="projection",
        )

        # EBIT
        ebit = ebitda - da
        proj.ebit[t] = ebit
        audit.log(
            step=f"EBIT Year {t}",
            formula="EBIT = EBITDA - D&A",
            inputs={"EBITDA": ebitda, "DA": da},
            output=ebit,
            unit="$M",
            module="projection",
        )

        # NOPAT
        nopat = ebit * (1 - assumptions.tax_rate)
        proj.nopat[t] = nopat
        audit.log(
            step=f"NOPAT Year {t}",
            formula="NOPAT = EBIT × (1 - τ)",
            inputs={"EBIT": ebit, "tax_rate": assumptions.tax_rate},
            output=nopat,
            unit="$M",
            module="projection",
        )

        # CapEx
        capex = rev * assumptions.capex_to_sales
        proj.capex[t] = capex
        audit.log(
            step=f"CapEx Year {t}",
            formula="CapEx = R × m_CapEx",
            inputs={"R": rev, "m_CapEx": assumptions.capex_to_sales},
            output=capex,
            unit="$M",
            module="projection",
        )

        # ΔNWC
        prev_rev = revenues.get(t - 1, base_revenue)
        delta_nwc = (rev - prev_rev) * assumptions.nwc_to_revenue
        proj.delta_nwc[t] = delta_nwc
        audit.log(
            step=f"ΔNWC Year {t}",
            formula="ΔNWC = ΔR × m_NWC",
            inputs={"ΔR": rev - prev_rev, "m_NWC": assumptions.nwc_to_revenue},
            output=delta_nwc,
            unit="$M",
            module="projection",
        )

        # UFCF
        ufcf = nopat + da - capex - delta_nwc
        proj.ufcf[t] = ufcf
        audit.log(
            step=f"UFCF Year {t}",
            formula="UFCF = NOPAT + D&A - CapEx - ΔNWC",
            inputs={"NOPAT": nopat, "DA": da, "CapEx": capex, "ΔNWC": delta_nwc},
            output=ufcf,
            unit="$M",
            module="projection",
        )

    logger.info(
        f"Income statement projected: {n_years} years, "
        f"Revenue Y1=${proj.revenue[1]:,.1f}M → Y{n_years}=${proj.revenue[n_years]:,.1f}M"
    )

    return proj
