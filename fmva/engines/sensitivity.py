"""
Sensitivity analysis engine - 2D matrices and football field visualization.
"""

from __future__ import annotations
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from loguru import logger
from fmva.audit.trail import AuditTrail


def sensitivity_matrix(
    row_values: list[float], col_values: list[float],
    compute_fn: Callable[[float, float], float],
    row_label: str = "Row", col_label: str = "Col",
    audit: AuditTrail = None,
) -> dict:
    """
    Build a 2D sensitivity matrix by varying two parameters.

    Args:
        row_values: Values for the row axis (e.g., WACC from 8% to 12%).
        col_values: Values for the column axis (e.g., TGR from 1% to 3%).
        compute_fn: Function(row_val, col_val) → output value.
        row_label: Label for the row axis.
        col_label: Label for the column axis.
        audit: AuditTrail (logged once for the full matrix, not per cell).

    Returns:
        Dict with row_values, col_values, data (2D list), row_label, col_label.
    """
    data = []
    for rv in row_values:
        row = []
        for cv in col_values:
            try:
                val = compute_fn(rv, cv)
            except Exception:
                val = None
            row.append(val)
        data.append(row)

    if audit:
        audit.log(
            f"Sensitivity Matrix ({row_label} × {col_label})",
            f"Vary {row_label} and {col_label}",
            {"n_rows": len(row_values), "n_cols": len(col_values)},
            len(row_values) * len(col_values), "cells", "sensitivity",
        )

    return {
        "row_label": row_label, "col_label": col_label,
        "row_values": row_values, "col_values": col_values,
        "data": data,
    }


def wacc_tgr_sensitivity(
    base_ufcf: float, base_sum_pv: float, net_debt: float,
    shares: float, n_years: int, mid_year: bool = True,
    wacc_range: list[float] = None, tgr_range: list[float] = None,
    base_wacc: float | None = None,
    audit: AuditTrail = None,
) -> dict:
    """Build WACC × Terminal Growth Rate sensitivity matrix for implied share price."""
    if wacc_range is None:
        wacc_range = [0.08, 0.09, 0.10, 0.11, 0.12]
    if tgr_range is None:
        tgr_range = [0.015, 0.020, 0.025, 0.030, 0.035]
    if base_wacc is None:
        base_wacc = wacc_range[len(wacc_range) // 2]

    def _discount_sum(wacc: float) -> float:
        return sum(
            1.0 / ((1.0 + wacc) ** (t - 0.5 if mid_year else float(t)))
            for t in range(1, n_years + 1)
        )

    # Infer an annual UFCF proxy from the base case so stage-period PV also responds to WACC.
    base_discount_sum = _discount_sum(base_wacc)
    ufcf_proxy = (base_sum_pv / base_discount_sum) if base_discount_sum else 0.0

    def _compute(wacc, tgr):
        if wacc <= tgr:
            return None
        tv = base_ufcf * (1 + tgr) / (wacc - tgr)
        exp = n_years - 0.5 if mid_year else float(n_years)
        pv_tv = tv / ((1 + wacc) ** exp)
        stage_pv = ufcf_proxy * _discount_sum(wacc)
        ev = stage_pv + pv_tv
        eq = ev - net_debt
        return eq / shares if shares else None

    return sensitivity_matrix(wacc_range, tgr_range, _compute, "WACC", "TGR", audit)


def plot_football_field(
    dcf_range: tuple[float, float],
    comps_range: tuple[float, float] = None,
    txn_range: tuple[float, float] = None,
    current_price: float = None,
    output_path: str = None,
) -> plt.Figure:
    """
    Create a horizontal bar (football field) valuation summary chart.

    Args:
        dcf_range: (low, high) from DCF (Gordon, Exit Multiple).
        comps_range: (low, high) from comparable companies.
        txn_range: (low, high) from precedent transactions.
        current_price: Current market price (vertical line).
        output_path: Path to save the chart (optional).

    Returns:
        matplotlib Figure.
    """
    categories = []
    lows = []
    widths = []
    colors = ["#2196F3", "#4CAF50", "#FF9800"]
    color_idx = 0

    if dcf_range:
        categories.append("DCF")
        lows.append(dcf_range[0])
        widths.append(dcf_range[1] - dcf_range[0])
        color_idx += 1
    if comps_range:
        categories.append("Comps")
        lows.append(comps_range[0])
        widths.append(comps_range[1] - comps_range[0])
        color_idx += 1
    if txn_range:
        categories.append("Transactions")
        lows.append(txn_range[0])
        widths.append(txn_range[1] - txn_range[0])

    fig, ax = plt.subplots(figsize=(12, 5))
    y_pos = range(len(categories))

    bars = ax.barh(y_pos, widths, left=lows, height=0.5,
                   color=colors[:len(categories)], alpha=0.85, edgecolor="white", linewidth=1.5)

    # Add value labels
    for bar, low, width in zip(bars, lows, widths):
        ax.text(low + width / 2, bar.get_y() + bar.get_height() / 2,
                f"${low:,.0f} - ${low + width:,.0f}", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")

    if current_price is not None:
        ax.axvline(x=current_price, color="#E91E63", linestyle="--", linewidth=2,
                   label=f"Current: ${current_price:,.2f}")
        ax.legend(fontsize=10)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=12, fontweight="bold")
    ax.set_xlabel("Implied Share Price ($)", fontsize=12)
    ax.set_title("Valuation Football Field", fontsize=14, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        logger.info(f"Football field chart saved to {output_path}")

    return fig
