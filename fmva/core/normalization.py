"""
Financial data normalization module.

Maps raw field names from various formats to the canonical FMVA schema
using case-insensitive matching and fuzzy fallback (difflib).

The CANONICAL_MAP defines 15+ aliases for each standard financial field.
"""

from __future__ import annotations

import difflib
import warnings
from typing import Any, Optional

from loguru import logger

from fmva.core.schemas import (
    AccountingStandard,
    BalanceSheet,
    CashFlowStatement,
    CompanyMetadata,
    FinancialStatements,
    IncomeStatement,
)
from fmva.exceptions import NormalizationError, FieldMappingError


# ── Canonical Field Mapping ────────────────────────────────────────────────────
# Key = canonical field name, Value = list of accepted aliases (all lowercase)

IS_FIELD_MAP: dict[str, list[str]] = {
    "revenue": [
        "total revenue", "net sales", "net revenue", "turnover", "revenue",
        "sales", "total sales", "net turnover", "total net revenue",
        "total_revenue", "net_sales", "net_revenue",
    ],
    "cogs": [
        "cost of goods sold", "cost of sales", "cost of revenue", "cogs",
        "cost_of_goods_sold", "cost_of_sales", "cost_of_revenue",
    ],
    "gross_profit": [
        "gross profit", "gross income", "gross margin",
        "gross_profit", "gross_income",
    ],
    "sga": [
        "selling general admin", "selling general and administrative",
        "sg&a", "sga", "selling_general_admin", "operating expenses",
    ],
    "rd_expense": [
        "research development", "r&d", "research and development",
        "research_development", "rd_expense", "r&d expense",
    ],
    "depreciation": [
        "depreciation and amortization", "d&a", "depreciation",
        "depreciation_and_amortization", "amortization",
        "deprec", "da",
    ],
    "ebitda": [
        "ebitda", "earnings before interest tax depreciation amortization",
        "earnings before interest tax depreciation",
    ],
    "ebit": [
        "ebit", "operating income", "operating profit",
        "earnings before interest and tax", "operating_income",
        "operating_profit",
    ],
    "interest_expense": [
        "interest expense", "finance costs", "interest_expense",
        "interest costs", "financial expenses",
    ],
    "other_income": [
        "other income", "other_income", "non-operating income",
        "other revenue",
    ],
    "ebt": [
        "earnings before tax", "ebt", "income before tax",
        "profit before tax", "earnings_before_tax", "pre-tax income",
    ],
    "tax_expense": [
        "income tax expense", "tax expense", "provision for taxes",
        "income tax", "income_tax_expense", "tax_expense",
        "provision_for_taxes",
    ],
    "net_income": [
        "net income", "net profit", "profit after tax", "net earnings",
        "net_income", "net_profit", "profit_after_tax",
    ],
}

BS_FIELD_MAP: dict[str, list[str]] = {
    "cash": [
        "cash and equivalents", "cash and cash equivalents", "cash",
        "cash_and_equivalents", "cash_and_cash_equivalents",
    ],
    "short_term_investments": [
        "short term investments", "short_term_investments",
        "marketable securities",
    ],
    "accounts_receivable": [
        "accounts receivable", "accounts_receivable", "trade receivables",
        "receivables",
    ],
    "inventory": ["inventory", "inventories"],
    "other_current_assets": ["other current assets", "other_current_assets"],
    "total_current_assets": ["total current assets", "total_current_assets"],
    "ppe": [
        "property plant equipment", "property_plant_equipment", "ppe",
        "pp&e", "fixed assets", "property plant and equipment",
    ],
    "goodwill": ["goodwill"],
    "intangible_assets": [
        "intangible assets", "intangible_assets", "intangibles",
    ],
    "other_non_current_assets": [
        "other non current assets", "other_non_current_assets",
        "other long term assets",
    ],
    "total_assets": ["total assets", "total_assets"],
    "accounts_payable": [
        "accounts payable", "accounts_payable", "trade payables",
    ],
    "short_term_debt": [
        "short term debt", "short_term_debt", "current portion of debt",
        "current debt",
    ],
    "accrued_liabilities": [
        "accrued liabilities", "accrued_liabilities", "accrued expenses",
    ],
    "other_current_liabilities": [
        "other current liabilities", "other_current_liabilities",
    ],
    "total_current_liabilities": [
        "total current liabilities", "total_current_liabilities",
    ],
    "long_term_debt": [
        "long term debt", "long_term_debt", "non-current debt",
        "long-term borrowings",
    ],
    "other_non_current_liabilities": [
        "other non current liabilities", "other_non_current_liabilities",
    ],
    "total_liabilities": ["total liabilities", "total_liabilities"],
    "common_stock": ["common stock", "common_stock", "share capital"],
    "retained_earnings": ["retained earnings", "retained_earnings"],
    "additional_paid_in_capital": [
        "additional paid in capital", "additional_paid_in_capital",
        "apic", "share premium",
    ],
    "shareholders_equity": [
        "shareholders equity", "stockholders equity", "total equity",
        "total shareholders equity", "total stockholders equity",
        "shareholders_equity", "stockholders_equity", "total_equity",
        "total_shareholders_equity",
    ],
}

CF_FIELD_MAP: dict[str, list[str]] = {
    "net_income": ["net income", "net_income", "net profit", "profit after tax"],
    "depreciation": [
        "depreciation and amortization", "depreciation_and_amortization",
        "d&a", "depreciation", "da",
    ],
    "change_in_working_capital": [
        "change in working capital", "change_in_working_capital",
        "delta nwc", "delta_nwc", "working capital changes",
    ],
    "other_operating": [
        "other operating activities", "other_operating_activities",
        "other_operating",
    ],
    "operating_cash_flow": [
        "operating cash flow", "cash from operations",
        "operating_cash_flow", "cash_from_operations",
        "net cash from operating",
    ],
    "capex": [
        "capital expenditures", "capex", "capital_expenditures",
        "purchase of ppe", "purchase_of_ppe", "purchases of property",
    ],
    "acquisitions": ["acquisitions", "business acquisitions"],
    "other_investing": [
        "other investing activities", "other_investing_activities",
        "other_investing",
    ],
    "investing_cash_flow": [
        "cash from investing", "investing_cash_flow", "cash_from_investing",
    ],
    "debt_issuance": ["debt issuance", "debt_issuance", "proceeds from debt"],
    "debt_repayment": ["debt repayment", "debt_repayment", "repayment of debt"],
    "dividends_paid": ["dividends paid", "dividends_paid", "dividend payments"],
    "share_buybacks": [
        "share buybacks", "share_buybacks", "stock repurchases",
        "repurchase of stock",
    ],
    "other_financing": [
        "other financing activities", "other_financing_activities",
        "other_financing",
    ],
    "financing_cash_flow": [
        "cash from financing", "financing_cash_flow", "cash_from_financing",
    ],
    "net_change_in_cash": [
        "net change in cash", "net_change_in_cash", "change in cash",
    ],
    "beginning_cash": ["beginning cash", "beginning_cash", "opening cash"],
    "ending_cash": ["ending cash", "ending_cash", "closing cash"],
}


def _fuzzy_match(raw_key: str, field_map: dict[str, list[str]], cutoff: float = 0.6) -> Optional[str]:
    """
    Attempt to match a raw field name to a canonical field using fuzzy matching.

    Args:
        raw_key: The raw field name from the input data.
        field_map: Canonical field map to search.
        cutoff: Minimum similarity ratio for a match.

    Returns:
        Canonical field name if matched, None otherwise.
    """
    raw_lower = raw_key.lower().strip().replace("_", " ")

    # Exact match first
    for canonical, aliases in field_map.items():
        if raw_lower in aliases or raw_lower == canonical:
            return canonical

    # Fuzzy match fallback
    all_aliases = {}
    for canonical, aliases in field_map.items():
        for alias in aliases:
            all_aliases[alias] = canonical
        all_aliases[canonical] = canonical

    matches = difflib.get_close_matches(raw_lower, all_aliases.keys(), n=1, cutoff=cutoff)
    if matches:
        return all_aliases[matches[0]]

    return None


def _map_statement_fields(
    raw_data: dict[str, Any],
    field_map: dict[str, list[str]],
) -> dict[str, Any]:
    """Map raw field names to canonical names using the field map."""
    mapped = {}
    unmapped = []

    for raw_key, value in raw_data.items():
        # Skip metadata/private keys
        if raw_key.startswith("_"):
            continue

        canonical = _fuzzy_match(raw_key, field_map)
        if canonical:
            # Convert to float if numeric
            if isinstance(value, (int, float)):
                mapped[canonical] = float(value)
            elif isinstance(value, str):
                try:
                    mapped[canonical] = float(value.replace(",", "").replace("$", "").replace("%", ""))
                except ValueError:
                    mapped[canonical] = value
            else:
                mapped[canonical] = value
        else:
            unmapped.append(raw_key)

    if unmapped:
        logger.debug(f"Unmapped fields: {unmapped}")

    return mapped


def _parse_income_statement(data: dict, year: int) -> IncomeStatement:
    """Parse a single year's income statement data."""
    mapped = _map_statement_fields(data, IS_FIELD_MAP)
    mapped["year"] = year

    # Compute derived fields if missing
    if "gross_profit" not in mapped and "revenue" in mapped and "cogs" in mapped:
        mapped["gross_profit"] = mapped["revenue"] - mapped["cogs"]

    if "ebit" not in mapped and "ebitda" in mapped and "depreciation" in mapped:
        mapped["ebit"] = mapped["ebitda"] - mapped["depreciation"]

    if "ebitda" not in mapped and "ebit" in mapped and "depreciation" in mapped:
        mapped["ebitda"] = mapped["ebit"] + mapped["depreciation"]

    return IncomeStatement(**{k: v for k, v in mapped.items() if k in IncomeStatement.model_fields})


def _parse_balance_sheet(data: dict, year: int) -> BalanceSheet:
    """Parse a single year's balance sheet data."""
    mapped = _map_statement_fields(data, BS_FIELD_MAP)
    mapped["year"] = year
    return BalanceSheet(**{k: v for k, v in mapped.items() if k in BalanceSheet.model_fields})


def _parse_cash_flow(data: dict, year: int) -> CashFlowStatement:
    """Parse a single year's cash flow data."""
    mapped = _map_statement_fields(data, CF_FIELD_MAP)
    mapped["year"] = year
    return CashFlowStatement(**{k: v for k, v in mapped.items() if k in CashFlowStatement.model_fields})


def normalize(raw_data: dict[str, Any]) -> FinancialStatements:
    """
    Normalize raw financial data into the canonical FMVA schema.

    Args:
        raw_data: Dictionary from load_json/load_csv/load_excel.

    Returns:
        FinancialStatements with all years normalized.

    Raises:
        NormalizationError: If critical field mapping fails.
    """
    # Extract metadata
    acct_std = raw_data.get("accounting_standard", "UNKNOWN").upper()
    try:
        accounting = AccountingStandard(acct_std)
    except ValueError:
        accounting = AccountingStandard.UNKNOWN

    metadata = CompanyMetadata(
        company_name=raw_data.get("company_name", "Unknown Company"),
        ticker=raw_data.get("ticker"),
        currency=raw_data.get("currency", "USD"),
        units=raw_data.get("units", "millions"),
        accounting_standard=accounting,
        fiscal_year_end=raw_data.get("fiscal_year_end", "December"),
        diluted_shares_outstanding=raw_data.get("diluted_shares_outstanding"),
        current_share_price=raw_data.get("current_share_price"),
    )

    # Parse income statements
    income_statements: dict[int, IncomeStatement] = {}
    is_data = raw_data.get("income_statement", {})
    for year_str, year_data in is_data.items():
        try:
            year = int(year_str)
        except ValueError:
            logger.warning(f"Skipping non-integer year key: {year_str}")
            continue
        income_statements[year] = _parse_income_statement(year_data, year)

    # Parse balance sheets
    balance_sheets: dict[int, BalanceSheet] = {}
    bs_data = raw_data.get("balance_sheet", {})
    for year_str, year_data in bs_data.items():
        try:
            year = int(year_str)
        except ValueError:
            continue
        balance_sheets[year] = _parse_balance_sheet(year_data, year)

    # Parse cash flow statements
    cash_flows: dict[int, CashFlowStatement] = {}
    cf_data = raw_data.get("cash_flow_statement", {})
    for year_str, year_data in cf_data.items():
        try:
            year = int(year_str)
        except ValueError:
            continue
        cash_flows[year] = _parse_cash_flow(year_data, year)

    # Build warnings
    model_warnings: dict[str, Any] = {}

    # Check for minimum years
    all_years = set(income_statements.keys()) | set(balance_sheets.keys()) | set(cash_flows.keys())
    if len(all_years) < 3:
        msg = f"Only {len(all_years)} year(s) of data provided; minimum 3 years recommended."
        model_warnings["insufficient_years"] = True
        warnings.warn(msg, UserWarning)
        logger.warning(msg)

    # Check for negative EBITDA
    for year, is_stmt in income_statements.items():
        if is_stmt.ebitda is not None and is_stmt.ebitda < 0:
            model_warnings["negative_ebitda"] = True
            logger.warning(f"Negative EBITDA in year {year}: ${is_stmt.ebitda:.1f}M")

    # GAAP/IFRS flag
    if accounting != AccountingStandard.UNKNOWN:
        model_warnings["accounting_standard_detected"] = accounting.value

    result = FinancialStatements(
        metadata=metadata,
        income_statements=income_statements,
        balance_sheets=balance_sheets,
        cash_flows=cash_flows,
        warnings=model_warnings,
    )

    logger.info(
        f"Normalized {metadata.company_name}: "
        f"{len(income_statements)} IS, {len(balance_sheets)} BS, {len(cash_flows)} CF years"
    )

    return result
