"""
Balance sheet integrity checker.

Verifies that Total Assets = Total Liabilities + Shareholders' Equity
within the configured tolerance ($0.01M).

If imbalanced:
- Reports the delta
- Identifies likely off-balance direction
- Suggests a specific plug entry
"""

from __future__ import annotations

from loguru import logger

from fmva.config import BALANCE_SHEET_TOLERANCE
from fmva.core.schemas import BalanceSheet, BalanceCheckResult, FinancialStatements


def check_balance_sheet(
    bs: BalanceSheet,
    tolerance: float = BALANCE_SHEET_TOLERANCE,
) -> BalanceCheckResult:
    """
    Verify that a balance sheet balances: Assets = Liabilities + Equity.

    Args:
        bs: BalanceSheet to check.
        tolerance: Maximum acceptable imbalance in $M (default: $0.01M).

    Returns:
        BalanceCheckResult with balanced flag, delta, and plug suggestion.
    """
    delta = bs.total_assets - (bs.total_liabilities + bs.shareholders_equity)

    if abs(delta) <= tolerance:
        logger.debug(f"Year {bs.year}: Balance sheet balanced (delta=${delta:.4f}M)")
        return BalanceCheckResult(
            balanced=True,
            delta=round(delta, 4),
            plug_suggestion=None,
            year=bs.year,
        )

    # ── Imbalanced - build plug suggestion ─────────────────────────────────
    if delta > 0:
        # Assets exceed L+E
        suggestion = (
            f"Assets exceed Liabilities + Equity by ${delta:,.2f}M. "
            f"Suggestion: Add ${delta:,.2f}M to Retained Earnings, "
            f"or check for missing liability line items."
        )
    else:
        # L+E exceed Assets
        suggestion = (
            f"Liabilities + Equity exceed Assets by ${abs(delta):,.2f}M. "
            f"Suggestion: Reduce Retained Earnings by ${abs(delta):,.2f}M, "
            f"or check for missing asset line items (e.g., Goodwill, Intangibles)."
        )

    logger.error(
        f"Year {bs.year}: Balance sheet IMBALANCED - "
        f"Assets=${bs.total_assets:,.1f}M, L+E=${bs.total_liabilities + bs.shareholders_equity:,.1f}M, "
        f"Delta=${delta:,.2f}M"
    )

    return BalanceCheckResult(
        balanced=False,
        delta=round(delta, 4),
        plug_suggestion=suggestion,
        year=bs.year,
    )


def check_all_balance_sheets(
    fs: FinancialStatements,
    tolerance: float = BALANCE_SHEET_TOLERANCE,
) -> list[BalanceCheckResult]:
    """
    Check balance sheets for all historical years.

    Args:
        fs: FinancialStatements containing one or more years.
        tolerance: Maximum acceptable imbalance.

    Returns:
        List of BalanceCheckResult, one per year.
    """
    results = []
    for year in sorted(fs.balance_sheets.keys()):
        bs = fs.balance_sheets[year]
        result = check_balance_sheet(bs, tolerance)
        results.append(result)

    balanced_count = sum(1 for r in results if r.balanced)
    total = len(results)
    logger.info(f"Balance sheet check: {balanced_count}/{total} years balanced")

    return results
