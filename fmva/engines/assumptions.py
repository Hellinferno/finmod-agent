"""
Assumption engine — manages Bear/Base/Bull scenario presets and custom assumptions.

Handles:
- Default scenario presets with industry-standard values
- Save/load assumption profiles to/from JSON
- Per-year or flat margin configuration
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from loguru import logger

from fmva.core.schemas import AssumptionSet, Scenario


# ── Default Scenario Presets ───────────────────────────────────────────────────

BEAR_PRESET = AssumptionSet(
    scenario=Scenario.BEAR,
    revenue_growth_rates=[0.03, 0.03, 0.02, 0.02, 0.02],
    ebitda_margin=0.18,
    capex_to_sales=0.07,
    da_to_revenue=0.05,
    nwc_to_revenue=0.10,
    tax_rate=0.25,
    terminal_growth_rate=0.015,
    exit_multiple=8.0,
    projection_years=5,
    mid_year_convention=True,
)

BASE_PRESET = AssumptionSet(
    scenario=Scenario.BASE,
    revenue_growth_rates=[0.10, 0.10, 0.09, 0.09, 0.08],
    ebitda_margin=0.25,
    capex_to_sales=0.06,
    da_to_revenue=0.05,
    nwc_to_revenue=0.08,
    tax_rate=0.21,
    terminal_growth_rate=0.025,
    exit_multiple=12.0,
    projection_years=5,
    mid_year_convention=True,
)

BULL_PRESET = AssumptionSet(
    scenario=Scenario.BULL,
    revenue_growth_rates=[0.15, 0.15, 0.13, 0.12, 0.10],
    ebitda_margin=0.30,
    capex_to_sales=0.05,
    da_to_revenue=0.04,
    nwc_to_revenue=0.06,
    tax_rate=0.21,
    terminal_growth_rate=0.03,
    exit_multiple=16.0,
    projection_years=5,
    mid_year_convention=True,
)

PRESETS: dict[str, AssumptionSet] = {
    "bear": BEAR_PRESET,
    "base": BASE_PRESET,
    "bull": BULL_PRESET,
}


def get_preset(scenario: str) -> AssumptionSet:
    """Get a default scenario preset by name."""
    key = scenario.lower().strip()
    if key not in PRESETS:
        raise ValueError(f"Unknown scenario '{scenario}'. Valid: {list(PRESETS.keys())}")
    return PRESETS[key].model_copy()


def save_assumptions(assumptions: AssumptionSet, filepath: str) -> None:
    """Save an assumption set to a JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(assumptions.model_dump(mode="json"), f, indent=2)
    logger.info(f"Assumptions saved to {filepath}")


def load_assumptions(filepath: str) -> AssumptionSet:
    """Load an assumption set from a JSON file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Assumption file not found: {filepath}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assumptions = AssumptionSet(**data)
    logger.info(f"Assumptions loaded from {filepath} (scenario: {assumptions.scenario})")
    return assumptions


def extend_growth_rates(assumptions: AssumptionSet, target_years: int) -> AssumptionSet:
    """
    Extend or truncate growth rates to match the target projection years.

    If fewer growth rates than projection years, repeat the last rate.
    If more, truncate.
    """
    rates = list(assumptions.revenue_growth_rates)
    if len(rates) < target_years:
        last_rate = rates[-1] if rates else 0.05
        rates.extend([last_rate] * (target_years - len(rates)))
    elif len(rates) > target_years:
        rates = rates[:target_years]

    return assumptions.model_copy(update={
        "revenue_growth_rates": rates,
        "projection_years": target_years,
    })


def get_ebitda_margin_for_year(assumptions: AssumptionSet, year_index: int) -> float:
    """
    Get EBITDA margin for a specific projection year.

    Supports both flat (single float) and per-year (list) margin specs.
    """
    if isinstance(assumptions.ebitda_margin, list):
        if year_index < len(assumptions.ebitda_margin):
            return assumptions.ebitda_margin[year_index]
        return assumptions.ebitda_margin[-1]  # Use last value if beyond list
    return assumptions.ebitda_margin
