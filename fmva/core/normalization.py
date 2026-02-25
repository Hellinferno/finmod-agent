"""
Financial data normalization module.

Maps raw field names from various formats to the canonical FMVA schema
using case-insensitive matching and fuzzy fallback (difflib).

The CANONICAL_MAP defines 15+ aliases for each standard financial field.
"""

from __future__ import annotations

import difflib
import re
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

STATEMENT_LABEL_KEYS = (
    "line_item",
    "lineitem",
    "item",
    "label",
    "field",
    "name",
    "metric",
    "account",
    "description",
)
STATEMENT_VALUE_KEYS = (
    "value",
    "amount",
    "val",
    "data",
    "total",
    "raw_value",
    "reported_value",
)
STATEMENT_CONTAINER_KEYS = ("items", "rows", "records", "line_items", "data")
STATEMENT_META_KEYS = {"year", "year_str", "fiscal_year", "period", "statement"}
YEAR_TOKEN_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")


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
    if not isinstance(field_map, dict):
        logger.warning(f"Skipping fuzzy match due to invalid field map type: {type(field_map).__name__}")
        return None

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


def _parse_year_token(value: Any) -> Optional[int]:
    """Extract a 4-digit year from an integer or text token."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = YEAR_TOKEN_PATTERN.search(value)
        if match:
            return int(match.group(0))
    return None


def _unwrap_statement_payload(payload: Any) -> Any:
    """Unwrap nested row containers (items/rows/records/data) if present."""
    if not isinstance(payload, dict):
        return payload
    for key in STATEMENT_CONTAINER_KEYS:
        nested = payload.get(key)
        if isinstance(nested, list):
            return nested
    return payload


def _coerce_row_list_to_mapping(rows: list[Any], year: Optional[int] = None) -> dict[str, Any]:
    """
    Convert row-list payloads into {line_item: value}.

    Supports common row formats such as:
    - {"line_item": "Revenue", "value": 500}
    - {"item": "Revenue", "FY2023": 500}
    - {"Revenue": 500}
    """
    result: dict[str, Any] = {}

    for row in rows:
        if not isinstance(row, dict):
            continue

        label: Optional[str] = None
        for key in STATEMENT_LABEL_KEYS:
            candidate = row.get(key)
            if isinstance(candidate, str) and candidate.strip():
                label = candidate.strip()
                break

        if label is None:
            row_pairs = [
                (k, v)
                for k, v in row.items()
                if str(k).strip().lower() not in STATEMENT_META_KEYS and v not in (None, "")
            ]
            if len(row_pairs) == 1:
                key, value = row_pairs[0]
                result[str(key).strip()] = value
                continue

        if not label:
            continue

        value: Any = None

        if year is not None:
            year_keys: list[Any] = [str(year), year, f"FY{year}", f"fy{year}", f"F{year}", f"f{year}"]
            for y_key in year_keys:
                if y_key in row and row[y_key] not in (None, ""):
                    value = row[y_key]
                    break
            if value is None:
                for key, candidate in row.items():
                    if str(year) in str(key) and candidate not in (None, ""):
                        value = candidate
                        break

        if value is None:
            for key in STATEMENT_VALUE_KEYS:
                candidate = row.get(key)
                if candidate not in (None, ""):
                    value = candidate
                    break

        if value is None:
            for key, candidate in row.items():
                key_lower = str(key).strip().lower()
                if key_lower in STATEMENT_META_KEYS or key_lower in STATEMENT_LABEL_KEYS:
                    continue
                if candidate in (None, ""):
                    continue
                value = candidate
                break

        if value is not None:
            result[label] = value

    return result


def _map_statement_fields(
    raw_data: Any,
    field_map: dict[str, list[str]],
    *,
    year: Optional[int] = None,
) -> dict[str, Any]:
    """Map raw field names to canonical names using the field map."""
    if not isinstance(field_map, dict):
        logger.warning(
            f"Skipping statement mapping due to invalid field map type: {type(field_map).__name__}"
        )
        return {}

    payload = _unwrap_statement_payload(raw_data)
    if isinstance(payload, list):
        payload = _coerce_row_list_to_mapping(payload, year=year)

    if not isinstance(payload, dict):
        logger.warning(
            f"Skipping unsupported statement payload type: {type(raw_data).__name__}"
        )
        return {}

    mapped = {}
    unmapped = []

    for raw_key, value in payload.items():
        raw_key = str(raw_key)
        # Skip metadata/private keys
        if raw_key.startswith("_") or raw_key.lower() in STATEMENT_META_KEYS or raw_key.lower() in STATEMENT_CONTAINER_KEYS:
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
    mapped = _map_statement_fields(data, IS_FIELD_MAP, year=year)
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
    mapped = _map_statement_fields(data, BS_FIELD_MAP, year=year)
    mapped["year"] = year
    return BalanceSheet(**{k: v for k, v in mapped.items() if k in BalanceSheet.model_fields})


def _parse_cash_flow(data: dict, year: int) -> CashFlowStatement:
    """Parse a single year's cash flow data."""
    mapped = _map_statement_fields(data, CF_FIELD_MAP, year=year)
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
    if isinstance(is_data, dict):
        for year_str, year_data in is_data.items():
            year = _parse_year_token(year_str)
            if year is None:
                logger.warning(f"Skipping non-integer year key: {year_str}")
                continue
            income_statements[year] = _parse_income_statement(_unwrap_statement_payload(year_data), year)
    elif isinstance(is_data, list):
        for year_data in is_data:
            if not isinstance(year_data, dict):
                continue
            year = _parse_year_token(year_data.get("year") or year_data.get("year_str"))
            if year:
                income_statements[year] = _parse_income_statement(_unwrap_statement_payload(year_data), year)

    # Parse balance sheets
    balance_sheets: dict[int, BalanceSheet] = {}
    bs_data = raw_data.get("balance_sheet", {})
    if isinstance(bs_data, dict):
        for year_str, year_data in bs_data.items():
            year = _parse_year_token(year_str)
            if year is None:
                continue
            balance_sheets[year] = _parse_balance_sheet(_unwrap_statement_payload(year_data), year)
    elif isinstance(bs_data, list):
        for year_data in bs_data:
            if not isinstance(year_data, dict):
                continue
            year = _parse_year_token(year_data.get("year") or year_data.get("year_str"))
            if year:
                balance_sheets[year] = _parse_balance_sheet(_unwrap_statement_payload(year_data), year)

    # Parse cash flow statements
    cash_flows: dict[int, CashFlowStatement] = {}
    cf_data = raw_data.get("cash_flow_statement", {})
    if isinstance(cf_data, dict):
        for year_str, year_data in cf_data.items():
            year = _parse_year_token(year_str)
            if year is None:
                continue
            cash_flows[year] = _parse_cash_flow(_unwrap_statement_payload(year_data), year)
    elif isinstance(cf_data, list):
        for year_data in cf_data:
            if not isinstance(year_data, dict):
                continue
            year = _parse_year_token(year_data.get("year") or year_data.get("year_str"))
            if year:
                cash_flows[year] = _parse_cash_flow(_unwrap_statement_payload(year_data), year)

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
