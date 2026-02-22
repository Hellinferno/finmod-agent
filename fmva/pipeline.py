"""
Pipeline orchestrator — single entry point for the full FMVA pipeline.

run_full_pipeline(): ingest → normalize → validate → DCF → export
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Optional
from loguru import logger
from fmva.audit.trail import AuditTrail
from fmva.core.ingestion import load_json
from fmva.core.normalization import normalize
from fmva.core.validation import validate
from fmva.core.checker import check_all_balance_sheets
from fmva.core.schemas import AssumptionSet, FinancialStatements, ValuationResult
from fmva.engines.assumptions import get_preset
from fmva.engines.dcf import run_full_dcf
from fmva.engines.wacc import calculate_wacc
from fmva.export.excel_exporter import export_to_excel
from fmva.export.json_exporter import export_to_json
from fmva.exceptions import FMVAError, BalanceSheetError


def run_full_pipeline(
    data_path: str,
    scenario: str = "base",
    assumptions: AssumptionSet = None,
    output_dir: str = "outputs",
    export_excel: bool = True,
    export_json_flag: bool = True,
    skip_comps: bool = True,
    comp_tickers: list[str] = None,
) -> ValuationResult:
    """
    Execute the complete FMVA pipeline.

    Steps:
    1. Load raw data (JSON)
    2. Normalize to canonical schema
    3. Validate data integrity
    4. Check balance sheet
    5. Run DCF valuation
    6. (Optional) Run comps
    7. Export results

    Args:
        data_path: Path to input JSON file.
        scenario: Scenario preset name ("bear", "base", "bull").
        assumptions: Custom AssumptionSet (overrides scenario if provided).
        output_dir: Directory for output files.
        export_excel: Whether to export Excel workbook.
        export_json_flag: Whether to export JSON.
        skip_comps: Skip comparable company analysis.
        comp_tickers: List of ticker symbols for comps analysis.

    Returns:
        ValuationResult with all computed outputs.
    """
    logger.info(f"═══ FMVA Pipeline Start ═══ {data_path}")

    # ── Step 1: Load ───────────────────────────────────────────────────────
    logger.info("Step 1/6: Loading raw data...")
    raw_data = load_json(data_path)

    # ── Step 2: Normalize ──────────────────────────────────────────────────
    logger.info("Step 2/6: Normalizing fields...")
    financials = normalize(raw_data)

    # ── Step 3: Validate ───────────────────────────────────────────────────
    logger.info("Step 3/6: Validating data integrity...")
    report = validate(financials)
    if not report.passed:
        for e in report.errors:
            logger.error(f"  ✗ {e}")
        raise FMVAError(f"Validation failed with {len(report.errors)} error(s)")
    for w in report.warnings:
        logger.warning(f"  ⚠ {w}")

    # ── Step 4: Balance Sheet Check ────────────────────────────────────────
    logger.info("Step 4/6: Checking balance sheets...")
    bs_results = check_all_balance_sheets(financials)
    for r in bs_results:
        if not r.balanced:
            raise BalanceSheetError(r.delta, details={"year": r.year, "suggestion": r.plug_suggestion})

    # ── Step 5: DCF ────────────────────────────────────────────────────────
    logger.info("Step 5/6: Running DCF valuation...")
    if assumptions is None:
        assumptions = get_preset(scenario)

    audit = AuditTrail(company_name=financials.metadata.company_name)
    dcf_result = run_full_dcf(financials, assumptions, audit=audit)

    # ── Step 5b: Comps (optional) ──────────────────────────────────────────
    comps_result = None
    if not skip_comps and comp_tickers:
        logger.info("Step 5b: Running comparable analysis...")
        from fmva.engines.comps import fetch_comp_data, calculate_comps_stats, apply_comps_multiples
        comp_data = fetch_comp_data(comp_tickers)
        stats = calculate_comps_stats(comp_data)
        latest_is = financials.latest_income_statement
        if latest_is and latest_is.ebitda and latest_is.revenue:
            comps_result = apply_comps_multiples(stats, latest_is.ebitda, latest_is.revenue, audit)

    # ── Step 6: Export ─────────────────────────────────────────────────────
    logger.info("Step 6/6: Exporting results...")
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    company_slug = financials.metadata.company_name.lower().replace(" ", "_").replace(".", "")

    result = ValuationResult(
        metadata=financials.metadata,
        normalized=financials,
        assumptions=assumptions,
        dcf=dcf_result,
        comps=comps_result,
    )

    if export_excel:
        excel_path = out_dir / f"{company_slug}_valuation.xlsx"
        export_to_excel(str(excel_path), financials, dcf_result, assumptions,
                       comps_result, audit.to_dataframe())

    if export_json_flag:
        json_path = out_dir / f"{company_slug}_valuation.json"
        export_to_json(result, str(json_path))

    # Export audit trail
    audit_path = out_dir / f"{company_slug}_audit.json"
    audit.export_json(str(audit_path))

    logger.info(
        f"═══ Pipeline Complete ═══ "
        f"EV(Gordon)=${dcf_result.enterprise_value_gordon:,.0f}M, "
        f"EV(Exit)=${dcf_result.enterprise_value_exit_multiple:,.0f}M"
    )

    return result
