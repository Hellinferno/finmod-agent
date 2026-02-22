"""Integration tests — full pipeline from raw JSON to DCF result."""

import json
import pytest
from pathlib import Path
from fmva.core.ingestion import load_json
from fmva.core.normalization import normalize
from fmva.core.validation import validate
from fmva.core.checker import check_all_balance_sheets
from fmva.core.schemas import WACCResult
from fmva.engines.assumptions import get_preset
from fmva.engines.dcf import run_full_dcf
from fmva.exceptions import BalanceSheetError


@pytest.mark.integration
class TestFullPipeline:
    def _run_pipeline(self, fixture_path):
        raw = load_json(fixture_path)
        fs = normalize(raw)
        report = validate(fs)
        bs_results = check_all_balance_sheets(fs)
        assumptions = get_preset("base")
        wacc_r = WACCResult(wacc=0.10, cost_of_equity=0.10, cost_of_debt_after_tax=0.04,
                           beta=1.0, risk_free_rate=0.045, equity_risk_premium=0.055,
                           weight_equity=0.77, weight_debt=0.23)
        dcf = run_full_dcf(fs, assumptions, wacc_r)
        return fs, report, bs_results, dcf

    def test_techcorp_full_pipeline(self, techcorp_path):
        fs, report, bs, dcf = self._run_pipeline(techcorp_path)
        assert report.passed
        assert all(r.balanced for r in bs)
        assert dcf.enterprise_value_gordon > 0
        assert dcf.implied_price_gordon > 0

    def test_manufactureco_pipeline(self, manufactureco_path):
        fs, report, bs, dcf = self._run_pipeline(manufactureco_path)
        assert report.passed
        assert all(r.balanced for r in bs)
        assert dcf.enterprise_value_gordon > 0

    def test_retailchain_pipeline(self, retailchain_path):
        fs, report, bs, dcf = self._run_pipeline(retailchain_path)
        assert report.passed
        assert all(r.balanced for r in bs)
        assert dcf.enterprise_value_gordon > 0

    def test_imbalanced_bs_raises(self, imbalanced_bs_path):
        raw = load_json(imbalanced_bs_path)
        fs = normalize(raw)
        bs_results = check_all_balance_sheets(fs)
        assert any(not r.balanced for r in bs_results)
