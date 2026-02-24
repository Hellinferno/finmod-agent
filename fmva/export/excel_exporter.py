"""
Excel export engine - generates 10-sheet valuation workbook with formatting.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Optional
import pandas as pd
from loguru import logger
from fmva.core.schemas import DCFResult, FinancialStatements, AssumptionSet, CompsResult


def export_to_excel(
    filepath: str,
    financials: FinancialStatements,
    dcf: DCFResult,
    assumptions: AssumptionSet,
    comps: CompsResult = None,
    audit_df: pd.DataFrame = None,
) -> str:
    """Export full valuation to a formatted Excel workbook."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(str(path), engine="openpyxl") as writer:
        # Sheet 1: Cover
        cover = pd.DataFrame([
            ["Company", financials.metadata.company_name],
            ["Ticker", financials.metadata.ticker or "N/A"],
            ["Currency", financials.metadata.currency],
            ["Scenario", assumptions.scenario.value],
            ["WACC", f"{dcf.wacc_result.wacc:.2%}" if dcf.wacc_result else "N/A"],
            ["EV (Gordon)", f"${dcf.enterprise_value_gordon:,.0f}M" if dcf.enterprise_value_gordon else "N/A"],
            ["EV (Exit Multiple)", f"${dcf.enterprise_value_exit_multiple:,.0f}M" if dcf.enterprise_value_exit_multiple else "N/A"],
            ["Implied Price (Gordon)", f"${dcf.implied_price_gordon:,.2f}" if dcf.implied_price_gordon else "N/A"],
            ["Implied Price (Exit)", f"${dcf.implied_price_exit_multiple:,.2f}" if dcf.implied_price_exit_multiple else "N/A"],
        ], columns=["Metric", "Value"])
        cover.to_excel(writer, sheet_name="Cover", index=False)

        # Sheet 2: Historical IS
        is_data = []
        for year in sorted(financials.income_statements.keys()):
            s = financials.income_statements[year]
            is_data.append({"Year": year, "Revenue": s.revenue, "COGS": s.cogs,
                           "Gross Profit": s.gross_profit, "SG&A": s.sga,
                           "EBITDA": s.ebitda, "D&A": s.depreciation,
                           "EBIT": s.ebit, "Net Income": s.net_income})
        pd.DataFrame(is_data).to_excel(writer, sheet_name="Historical IS", index=False)

        # Sheet 3: Projected IS / DCF
        proj = dcf.projection
        proj_data = []
        for t in proj.years:
            proj_data.append({
                "Year": t, "Revenue": proj.revenue.get(t),
                "EBITDA": proj.ebitda.get(t), "D&A": proj.da.get(t),
                "EBIT": proj.ebit.get(t), "NOPAT": proj.nopat.get(t),
                "CapEx": proj.capex.get(t), "ΔNWC": proj.delta_nwc.get(t),
                "UFCF": proj.ufcf.get(t),
                "Discount Factor": dcf.discount_factors.get(t),
                "PV(UFCF)": dcf.pv_ufcf.get(t),
            })
        pd.DataFrame(proj_data).to_excel(writer, sheet_name="DCF Model", index=False)

        # Sheet 4: Valuation Summary
        val_summary = pd.DataFrame([
            ["Sum PV(UFCF)", dcf.sum_pv_ufcf],
            ["TV (Gordon)", dcf.terminal_value_gordon],
            ["TV (Exit Multiple)", dcf.terminal_value_exit_multiple],
            ["PV TV (Gordon)", dcf.pv_terminal_value_gordon],
            ["PV TV (Exit)", dcf.pv_terminal_value_exit_multiple],
            ["EV (Gordon)", dcf.enterprise_value_gordon],
            ["EV (Exit)", dcf.enterprise_value_exit_multiple],
            ["Net Debt", dcf.net_debt],
            ["Equity (Gordon)", dcf.equity_value_gordon],
            ["Equity (Exit)", dcf.equity_value_exit_multiple],
            ["Implied Price (Gordon)", dcf.implied_price_gordon],
            ["Implied Price (Exit)", dcf.implied_price_exit_multiple],
        ], columns=["Item", "Value ($M)"])
        val_summary.to_excel(writer, sheet_name="Valuation Summary", index=False)

        # Sheet 5: Assumptions
        assn_data = pd.DataFrame([
            ["Scenario", assumptions.scenario.value],
            ["Revenue Growth (Y1-Y5)", str(assumptions.revenue_growth_rates)],
            ["EBITDA Margin", str(assumptions.ebitda_margin)],
            ["CapEx/Sales", f"{assumptions.capex_to_sales:.1%}"],
            ["D&A/Revenue", f"{assumptions.da_to_revenue:.1%}"],
            ["NWC/Revenue", f"{assumptions.nwc_to_revenue:.1%}"],
            ["Tax Rate", f"{assumptions.tax_rate:.1%}"],
            ["TGR", f"{assumptions.terminal_growth_rate:.1%}"],
            ["Exit Multiple", f"{assumptions.exit_multiple}x"],
            ["Mid-Year Convention", str(assumptions.mid_year_convention)],
        ], columns=["Assumption", "Value"])
        assn_data.to_excel(writer, sheet_name="Assumptions", index=False)

        # Sheet 6: Comps (if available)
        if comps and comps.comps:
            comps_data = [{"Ticker": c.ticker, "Name": c.company_name,
                          "Market Cap": c.market_cap, "EV": c.enterprise_value,
                          "EV/EBITDA": c.ev_ebitda, "EV/Rev": c.ev_revenue,
                          "P/E": c.pe_ratio} for c in comps.comps]
            pd.DataFrame(comps_data).to_excel(writer, sheet_name="Comps", index=False)

        # Sheet 7: Audit Trail (if available)
        if audit_df is not None and not audit_df.empty:
            audit_df.to_excel(writer, sheet_name="Audit Trail", index=False)

    logger.info(f"Excel workbook exported to {filepath}")
    return str(path)
