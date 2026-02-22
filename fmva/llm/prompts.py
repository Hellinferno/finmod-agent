"""
Jinja2 prompt template rendering for LLM narrative sections.
"""

from __future__ import annotations
from typing import Any
from jinja2 import Environment, BaseLoader
from loguru import logger

# ── Built-in prompt templates ──────────────────────────────────────────────────

TEMPLATES = {
    "executive_summary": """You are a senior equity research analyst. Write an executive summary for {{ company_name }}.

Key financials:
- LTM Revenue: ${{ "%.1f"|format(revenue) }}M, EBITDA: ${{ "%.1f"|format(ebitda) }}M
- DCF Equity Value (Gordon): ${{ "%.0f"|format(dcf_eq_gordon) }}M → Implied price: ${{ "%.2f"|format(implied_gordon) }}
- DCF Equity Value (Exit Multiple): ${{ "%.0f"|format(dcf_eq_exit) }}M → Implied price: ${{ "%.2f"|format(implied_exit) }}
{% if current_price %}- Current share price: ${{ "%.2f"|format(current_price) }}{% endif %}
{% if comps_median %}- Comps implied EV (median EV/EBITDA): ${{ "%.0f"|format(comps_median) }}M{% endif %}

Provide a 3-4 paragraph summary covering: valuation conclusion, key drivers, and primary risks. Use precise numbers. Do NOT hallucinate any data not provided above.""",

    "dcf_commentary": """You are a financial analyst. Write a 2-paragraph DCF methodology commentary for {{ company_name }}.

Assumptions: WACC={{ "%.1f"|format(wacc*100) }}%, TGR={{ "%.1f"|format(tgr*100) }}%, Exit Multiple={{ exit_multiple }}x
Projection: {{ n_years }}-year forecast, Revenue CAGR {{ "%.1f"|format(rev_cagr*100) }}%
Key output: EV(Gordon)=${{ "%.0f"|format(ev_gordon) }}M, EV(Exit)=${{ "%.0f"|format(ev_exit) }}M
TV as % of EV: {{ "%.0f"|format(tv_pct) }}%

Cover: methodology rationale, key assumptions, and sensitivity to WACC/TGR. Be analytical. Do NOT invent numbers.""",

    "comps_commentary": """You are a financial analyst. Write a 2-paragraph comparable companies commentary for {{ company_name }}.

Peer group: {{ peers|join(', ') }}
Median EV/EBITDA: {{ "%.1f"|format(med_ev_ebitda) }}x, Median EV/Revenue: {{ "%.1f"|format(med_ev_rev) }}x
Implied EV range: ${{ "%.0f"|format(implied_low) }}M – ${{ "%.0f"|format(implied_high) }}M

Cover: peer selection rationale, multiple comparison, and implied range interpretation. Be precise.""",

    "risk_factors": """You are a financial analyst. List 4-6 key risk factors for {{ company_name }} ({{ industry }} sector).

Current financials: Revenue ${{ "%.0f"|format(revenue) }}M, EBITDA margin {{ "%.1f"|format(ebitda_margin*100) }}%
Debt/Equity: {{ "%.1f"|format(de_ratio*100) }}%, Revenue growth: {{ "%.1f"|format(rev_growth*100) }}%

Provide concise risk factors covering: market, operational, financial, and execution risks. Format as numbered list.""",

    "investment_thesis": """You are a senior equity analyst. Write a 2-paragraph investment thesis for {{ company_name }}.

Valuation range: ${{ "%.2f"|format(price_low) }} – ${{ "%.2f"|format(price_high) }} per share
{% if current_price %}Current price: ${{ "%.2f"|format(current_price) }} ({{ "%.0f"|format(upside) }}% potential upside/downside){% endif %}
Key metrics: Revenue growth {{ "%.1f"|format(rev_growth*100) }}%, EBITDA margin {{ "%.1f"|format(ebitda_margin*100) }}%

Write a balanced thesis covering bull and bear cases. Reference specific numbers. Do NOT hallucinate.""",
}


def render_prompt(template_name: str, context: dict[str, Any]) -> str:
    """Render a prompt template with the given context."""
    if template_name not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}. Available: {list(TEMPLATES.keys())}")
    env = Environment(loader=BaseLoader())
    tmpl = env.from_string(TEMPLATES[template_name])
    result = tmpl.render(**context)
    logger.debug(f"Rendered prompt '{template_name}' ({len(result)} chars)")
    return result


def build_dcf_context(dcf_result, financials, assumptions) -> dict[str, Any]:
    """Build template context from DCF results."""
    latest_is = financials.latest_income_statement
    n = assumptions.projection_years
    rev_y1 = dcf_result.projection.revenue.get(1, 0)
    rev_yn = dcf_result.projection.revenue.get(n, 0)
    rev_cagr = (rev_yn / latest_is.revenue) ** (1 / n) - 1 if latest_is.revenue else 0

    return {
        "company_name": financials.metadata.company_name,
        "revenue": latest_is.revenue or 0,
        "ebitda": latest_is.ebitda or 0,
        "dcf_eq_gordon": dcf_result.equity_value_gordon or 0,
        "dcf_eq_exit": dcf_result.equity_value_exit_multiple or 0,
        "implied_gordon": dcf_result.implied_price_gordon or 0,
        "implied_exit": dcf_result.implied_price_exit_multiple or 0,
        "current_price": financials.metadata.current_share_price,
        "wacc": dcf_result.wacc_result.wacc if dcf_result.wacc_result else 0.10,
        "tgr": assumptions.terminal_growth_rate,
        "exit_multiple": assumptions.exit_multiple,
        "n_years": n,
        "rev_cagr": rev_cagr,
        "ev_gordon": dcf_result.enterprise_value_gordon or 0,
        "ev_exit": dcf_result.enterprise_value_exit_multiple or 0,
        "tv_pct": dcf_result.tv_pct_of_ev_gordon or 0,
    }
