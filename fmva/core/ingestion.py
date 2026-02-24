"""
Data ingestion module - loads financial data from JSON, CSV, Excel, and PDF files.

Handles:
- JSON files with nested financial statement data
- CSV files with automatic delimiter detection
- Excel files with automatic sheet detection (IS, BS, CF)
- PDF files via table/text extraction heuristics
"""

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from fmva.exceptions import IngestionError, FileFormatError


YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")
NUMBER_PATTERN = re.compile(r"\(?\$?-?\d[\d,]*(?:\.\d+)?\)?")


def load_json(filepath: str) -> dict[str, Any]:
    """
    Load and validate raw JSON financial data.

    Args:
        filepath: Path to the JSON file.

    Returns:
        Parsed dictionary containing financial statements.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        FileFormatError: If the file is not valid JSON.
        IngestionError: If required sections are missing.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if path.suffix.lower() != ".json":
        raise FileFormatError(f"Expected .json file, got: {path.suffix}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {filepath}: {e}") from e

    if not isinstance(data, dict):
        raise IngestionError(f"JSON root must be a dict, got {type(data).__name__}")

    # Validate required sections
    required_sections = ["income_statement", "balance_sheet", "cash_flow_statement"]
    missing = [s for s in required_sections if s not in data]
    if missing:
        # Try alternate key names
        alt_keys = {
            "income_statement": ["income_statement", "is", "profit_and_loss", "p_and_l", "pl"],
            "balance_sheet": ["balance_sheet", "bs"],
            "cash_flow_statement": [
                "cash_flow_statement", "cash_flow", "cfs", "cf",
                "cashflow", "cash_flows"
            ],
        }
        for section in missing.copy():
            for alt in alt_keys.get(section, []):
                if alt in data:
                    data[section] = data.pop(alt)
                    missing.remove(section)
                    break

    if missing:
        raise IngestionError(
            f"Missing required section(s): {', '.join(missing)}. "
            f"Available keys: {list(data.keys())}",
            details={"missing": missing, "available": list(data.keys())},
        )

    logger.info(f"Loaded JSON from {filepath} - {len(data)} top-level keys")
    return data


def load_csv(filepath: str, **kwargs) -> pd.DataFrame:
    """
    Load financial data from CSV with auto-delimiter detection.

    Args:
        filepath: Path to the CSV file.
        **kwargs: Additional arguments passed to pd.read_csv.

    Returns:
        DataFrame with parsed financial data.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        FileFormatError: If the file cannot be parsed.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if path.suffix.lower() not in (".csv", ".tsv", ".txt"):
        raise FileFormatError(f"Expected CSV file, got: {path.suffix}")

    # Try different delimiters
    for sep in [",", ";", "\t", "|"]:
        try:
            df = pd.read_csv(path, sep=sep, **kwargs)
            if df.shape[1] > 1:
                # Handle percentage formatting
                for col in df.columns:
                    if df[col].dtype == object:
                        # Try to convert "25.0%" -> 0.25
                        try:
                            pct_mask = df[col].str.contains("%", na=False)
                            if pct_mask.any():
                                df.loc[pct_mask, col] = (
                                    df.loc[pct_mask, col]
                                    .str.replace("%", "")
                                    .astype(float)
                                    / 100.0
                                )
                                df[col] = pd.to_numeric(df[col], errors="coerce")
                        except (AttributeError, TypeError):
                            pass

                logger.info(f"Loaded CSV from {filepath} - {df.shape[0]} rows x {df.shape[1]} cols (sep='{sep}')")
                return df
        except Exception:
            continue

    raise FileFormatError(f"Could not parse CSV file: {filepath}")


def load_excel(filepath: str, sheet_name: str = None) -> dict[str, Any]:
    """
    Load financial data from Excel with automatic sheet detection.

    Auto-detects sheets named 'Income', 'Balance', 'Cash', 'P&L', etc.

    Args:
        filepath: Path to the .xlsx file.
        sheet_name: Specific sheet to load (optional).

    Returns:
        Dictionary with parsed data from all relevant sheets.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        FileFormatError: If the file cannot be parsed.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if path.suffix.lower() not in (".xlsx", ".xls"):
        raise FileFormatError(f"Expected Excel file, got: {path.suffix}")

    try:
        xl = pd.ExcelFile(path)
    except Exception as e:
        raise FileFormatError(f"Cannot read Excel file {filepath}: {e}") from e

    sheet_names = xl.sheet_names
    logger.info(f"Excel file has sheets: {sheet_names}")

    # Sheet detection patterns
    IS_PATTERNS = ["income", "p&l", "profit", "revenue", "pl", "is"]
    BS_PATTERNS = ["balance", "bs", "position", "assets"]
    CF_PATTERNS = ["cash", "cf", "cfs", "cashflow", "flow"]

    def find_sheet(patterns: list[str]) -> str | None:
        for name in sheet_names:
            lower = name.lower().strip()
            for pat in patterns:
                if pat in lower:
                    return name
        return None

    result = {"_source": str(filepath), "_sheets": sheet_names}

    if sheet_name:
        df = pd.read_excel(xl, sheet_name=sheet_name)
        result["data"] = df.to_dict(orient="records")
    else:
        is_sheet = find_sheet(IS_PATTERNS)
        bs_sheet = find_sheet(BS_PATTERNS)
        cf_sheet = find_sheet(CF_PATTERNS)

        if is_sheet:
            result["income_statement"] = pd.read_excel(xl, sheet_name=is_sheet).to_dict(orient="records")
        if bs_sheet:
            result["balance_sheet"] = pd.read_excel(xl, sheet_name=bs_sheet).to_dict(orient="records")
        if cf_sheet:
            result["cash_flow_statement"] = pd.read_excel(xl, sheet_name=cf_sheet).to_dict(orient="records")

        # If no known sheets found, load all sheets
        if not any(k in result for k in ["income_statement", "balance_sheet", "cash_flow_statement"]):
            for name in sheet_names:
                df = pd.read_excel(xl, sheet_name=name)
                result[name] = df.to_dict(orient="records")

    logger.info(f"Loaded Excel from {filepath}")
    return result


def _clean_cell(value: Any) -> str:
    """Normalize extracted table cell content to plain text."""
    if value is None:
        return ""
    return str(value).replace("\n", " ").strip()


def _parse_numeric(value: str) -> float | None:
    """Parse numeric cell values like '(1,234.5)', '$450', '12.4%'."""
    if not value:
        return None

    cleaned = value.strip()
    if cleaned in {"-", "--", "n/a", "N/A", "na", "NA"}:
        return None

    negative = cleaned.startswith("(") and cleaned.endswith(")")
    cleaned = (
        cleaned.replace(",", "")
        .replace("$", "")
        .replace("%", "")
        .replace("(", "")
        .replace(")", "")
    )

    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None

    parsed = float(match.group(0))
    if negative and parsed > 0:
        parsed *= -1.0
    return parsed


def _classify_statement(table_text: str) -> str | None:
    """Classify a table as income statement, balance sheet, or cash flow."""
    text = table_text.lower()

    score_income = sum(
        token in text for token in ["income statement", "revenue", "gross profit", "ebitda", "net income"]
    )
    score_balance = sum(
        token in text for token in ["balance sheet", "total assets", "total liabilities", "equity", "shareholders"]
    )
    score_cash = sum(
        token in text for token in ["cash flow", "operating activities", "investing activities", "financing activities"]
    )

    scores = {
        "income_statement": score_income,
        "balance_sheet": score_balance,
        "cash_flow_statement": score_cash,
    }
    statement = max(scores, key=scores.get)
    return statement if scores[statement] > 0 else None


def _line_item_hint(line_item: str) -> str | None:
    """Infer statement type from a line-item label when table header is weak."""
    key = line_item.lower()
    if any(token in key for token in ["revenue", "gross", "ebit", "net income", "tax expense"]):
        return "income_statement"
    if any(token in key for token in ["assets", "liabilities", "equity", "receivable", "payable", "debt"]):
        return "balance_sheet"
    if any(token in key for token in ["cash flow", "operating cash", "capex", "financing", "investing"]):
        return "cash_flow_statement"
    return None


def _extract_year_cols(rows: list[list[str]]) -> tuple[dict[int, int], int]:
    """
    Detect year columns from the first few rows.

    Returns:
        (column index -> year, header row index)
    """
    for header_idx in range(min(3, len(rows))):
        year_cols: dict[int, int] = {}
        for col_idx, cell in enumerate(rows[header_idx]):
            match = YEAR_PATTERN.search(cell)
            if match:
                year_cols[col_idx] = int(match.group(0))
        if year_cols:
            return year_cols, header_idx
    return {}, 0


def _extract_rows_from_text(
    text_chunks: list[str],
    extracted: dict[str, Any],
    detected_years: set[int],
) -> int:
    """
    Fallback extraction when table detection is weak.

    This scans plain text lines in section order and maps numeric rows into
    income/balance/cash flow buckets.
    """
    if not text_chunks:
        return 0

    rows_added = 0
    active_statement: str | None = None
    active_years = sorted(detected_years, reverse=True)
    default_year = str(active_years[0]) if active_years else "2023"

    for block in text_chunks:
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            lower = line.lower()
            heading_detected = False
            if "income statement" in lower or "statement of operations" in lower:
                active_statement = "income_statement"
                heading_detected = True
            if "balance sheet" in lower or "statement of financial position" in lower:
                active_statement = "balance_sheet"
                heading_detected = True
            if "cash flow" in lower or "statement of cash flows" in lower:
                active_statement = "cash_flow_statement"
                heading_detected = True

            line_for_values = line
            if heading_detected:
                line_for_values = re.sub(
                    r"(?i)income statement|statement of operations|balance sheet|"
                    r"statement of financial position|cash flow statement|statement of cash flows",
                    "",
                    line_for_values,
                ).strip()
                if not line_for_values:
                    continue

            line_years = [int(y) for y in YEAR_PATTERN.findall(line_for_values)]
            if line_years:
                active_years = sorted(set(line_years), reverse=True)
                continue

            number_tokens = NUMBER_PATTERN.findall(line_for_values)
            if not number_tokens:
                continue

            statement = active_statement or _line_item_hint(line_for_values)
            if not statement:
                continue

            # Remove all numeric tokens to isolate a line-item label.
            label = line_for_values
            for token in number_tokens:
                label = label.replace(token, " ")
            label = re.sub(r"\s+", " ", label).strip(" :-")
            if not label or len(label) < 2:
                continue

            values = [_parse_numeric(token) for token in number_tokens]
            values = [v for v in values if v is not None]
            if not values:
                continue

            if active_years:
                for idx, value in enumerate(values[: len(active_years)]):
                    year_key = str(active_years[idx])
                    bucket = extracted[statement].setdefault(year_key, {})
                    if label not in bucket:
                        bucket[label] = value
                        rows_added += 1
            else:
                bucket = extracted[statement].setdefault(default_year, {})
                if label not in bucket:
                    bucket[label] = values[0]
                    rows_added += 1

    return rows_added


def load_pdf(filepath: str) -> dict[str, Any]:
    """
    Load financial data from PDF statements.

    Notes:
    - Uses pdfplumber table extraction when available.
    - Falls back to line-wise numeric extraction if year columns are not detected.
    - Returns canonical top-level keys expected by normalization.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if path.suffix.lower() != ".pdf":
        raise FileFormatError(f"Expected .pdf file, got: {path.suffix}")

    try:
        import pdfplumber
    except ImportError as exc:
        raise FileFormatError(
            "PDF ingestion requires 'pdfplumber'. Install dependencies and retry."
        ) from exc

    extracted: dict[str, Any] = {
        "company_name": path.stem,
        "income_statement": {},
        "balance_sheet": {},
        "cash_flow_statement": {},
    }
    detected_years: set[int] = set()
    extracted_rows = 0

    with pdfplumber.open(path) as pdf:
        all_text_parts: list[str] = []

        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text:
                all_text_parts.append(page_text)
                detected_years.update(int(y) for y in YEAR_PATTERN.findall(page_text))

            tables = page.extract_tables() or []
            for table in tables:
                rows = [
                    [_clean_cell(cell) for cell in row]
                    for row in table
                    if row and any(_clean_cell(cell) for cell in row)
                ]
                if len(rows) < 2:
                    continue

                joined_preview = " ".join(" ".join(r) for r in rows[:8])
                statement_type = _classify_statement(joined_preview)
                year_cols, header_idx = _extract_year_cols(rows)

                default_year = str(max(detected_years)) if detected_years else "2023"

                for row in rows[header_idx + 1:]:
                    line_item = row[0].strip() if row else ""
                    if not line_item:
                        continue
                    if YEAR_PATTERN.fullmatch(line_item):
                        continue

                    inferred_type = statement_type or _line_item_hint(line_item)
                    if not inferred_type:
                        continue

                    if year_cols:
                        for col_idx, year in year_cols.items():
                            if col_idx >= len(row):
                                continue
                            value = _parse_numeric(row[col_idx])
                            if value is None:
                                continue
                            year_key = str(year)
                            bucket = extracted[inferred_type].setdefault(year_key, {})
                            bucket[line_item] = value
                            extracted_rows += 1
                    else:
                        # Fallback when table has no explicit year headers:
                        # assign first numeric value found to the latest detected year.
                        values = [_parse_numeric(cell) for cell in row[1:]]
                        value = next((v for v in values if v is not None), None)
                        if value is None:
                            continue
                        bucket = extracted[inferred_type].setdefault(default_year, {})
                        bucket[line_item] = value
                        extracted_rows += 1

        if all_text_parts:
            first_non_empty = next(
                (line.strip() for line in all_text_parts[0].splitlines() if line.strip()),
                path.stem,
            )
            if len(first_non_empty) <= 120:
                extracted["company_name"] = first_non_empty

            # Secondary pass over plain text for PDFs where table extraction misses structure.
            extracted_rows += _extract_rows_from_text(all_text_parts, extracted, detected_years)

    if extracted_rows == 0:
        raise IngestionError(
            "Could not extract financial rows from PDF. "
            "If the PDF is scanned/image-only, run OCR first or upload Excel/CSV/JSON."
        )

    logger.info(
        f"Loaded PDF from {filepath} - extracted {extracted_rows} data points across "
        f"{len(extracted['income_statement'])} IS years, "
        f"{len(extracted['balance_sheet'])} BS years, "
        f"{len(extracted['cash_flow_statement'])} CF years"
    )
    return extracted
