"""
Data ingestion module — loads financial data from JSON, CSV, and Excel files.

Handles:
- JSON files with nested financial statement data
- CSV files with automatic delimiter detection
- Excel files with automatic sheet detection (IS, BS, CF)
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from fmva.exceptions import IngestionError, FileFormatError


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

    logger.info(f"Loaded JSON from {filepath} — {len(data)} top-level keys")
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

                logger.info(f"Loaded CSV from {filepath} — {df.shape[0]} rows × {df.shape[1]} cols (sep='{sep}')")
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
