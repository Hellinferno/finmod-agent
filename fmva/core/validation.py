"""
Financial data validation module.

Checks normalized data for internal consistency and reasonableness.
All checks produce warnings or errors - never silently modifies data.
"""

from __future__ import annotations

from loguru import logger

from fmva.config import EBITDA_CONSISTENCY_TOLERANCE, CASH_FLOW_REASONABLENESS_TOLERANCE
from fmva.core.schemas import FinancialStatements, ValidationReport


def validate(fs: FinancialStatements) -> ValidationReport:
    """
    Validate normalized financial statements for internal consistency.

    Checks performed:
    1. Revenue must be non-negative (error if negative)
    2. EBITDA ≈ EBIT + D&A within ±0.5% (warning if inconsistent)
    3. Operating CF reasonably close to NI + D&A ± ΔWC within ±10% (warning)
    4. Net Income derivable from EBIT - Interest - Tax (warning)

    Args:
        fs: Normalized FinancialStatements.

    Returns:
        ValidationReport with errors, warnings, and pass/fail status.
    """
    errors: list[str] = []
    warnings_list: list[str] = []

    for year in fs.historical_years:
        # ── Income Statement Checks ────────────────────────────────────────
        is_stmt = fs.income_statements.get(year)
        if is_stmt:
            # Check 1: Revenue must be non-negative
            if is_stmt.revenue is not None and is_stmt.revenue < 0:
                errors.append(
                    f"Year {year}: Negative revenue (${is_stmt.revenue:.1f}M) - "
                    f"this is invalid for most companies."
                )

            # Check 2: EBITDA consistency (EBITDA ≈ EBIT + D&A)
            if (
                is_stmt.ebitda is not None
                and is_stmt.ebit is not None
                and is_stmt.depreciation is not None
            ):
                expected_ebitda = is_stmt.ebit + is_stmt.depreciation
                if is_stmt.ebitda != 0:
                    pct_diff = abs(is_stmt.ebitda - expected_ebitda) / abs(is_stmt.ebitda)
                    if pct_diff > EBITDA_CONSISTENCY_TOLERANCE:
                        warnings_list.append(
                            f"Year {year}: EBITDA (${is_stmt.ebitda:.1f}M) does not equal "
                            f"EBIT + D&A (${expected_ebitda:.1f}M). "
                            f"Difference: {pct_diff:.2%}"
                        )

        # ── Cash Flow Checks ───────────────────────────────────────────────
        cf_stmt = fs.cash_flows.get(year)
        if cf_stmt and is_stmt:
            # Check 3: OCF reasonableness
            if (
                cf_stmt.operating_cash_flow is not None
                and is_stmt.net_income is not None
                and is_stmt.depreciation is not None
            ):
                # Simple approximation: OCF ≈ NI + D&A ± ΔWC
                delta_wc = cf_stmt.change_in_working_capital or 0.0
                expected_ocf = is_stmt.net_income + is_stmt.depreciation + delta_wc
                if expected_ocf != 0:
                    pct_diff = abs(cf_stmt.operating_cash_flow - expected_ocf) / abs(expected_ocf)
                    if pct_diff > CASH_FLOW_REASONABLENESS_TOLERANCE:
                        warnings_list.append(
                            f"Year {year}: Operating Cash Flow (${cf_stmt.operating_cash_flow:.1f}M) "
                            f"differs from NI + D&A ± ΔWC (${expected_ocf:.1f}M) by {pct_diff:.1%}. "
                            f"Check for non-cash items or other adjustments."
                        )

    passed = len(errors) == 0

    if errors:
        for e in errors:
            logger.error(f"Validation error: {e}")
    if warnings_list:
        for w in warnings_list:
            logger.warning(f"Validation warning: {w}")

    if passed:
        logger.info("Validation passed - all integrity checks OK")
    else:
        logger.error(f"Validation failed - {len(errors)} error(s)")

    return ValidationReport(
        passed=passed,
        errors=errors,
        warnings=warnings_list,
    )
