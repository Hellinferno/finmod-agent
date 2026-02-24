"""Tests for data ingestion, normalization, validation, and balance sheet checking."""

import json
import pytest
from pathlib import Path
from fmva.core.ingestion import load_json, load_pdf
from fmva.core.normalization import normalize
from fmva.core.validation import validate
from fmva.core.checker import check_balance_sheet, check_all_balance_sheets


class TestLoadJson:
    def test_load_techcorp(self, techcorp_path):
        data = load_json(techcorp_path)
        assert "income_statement" in data
        assert "balance_sheet" in data
        assert "cash_flow_statement" in data
        assert data["company_name"] == "TechCorp Inc."

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_json("nonexistent.json")

    def test_load_missing_sections(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text(json.dumps({"foo": "bar"}))
        with pytest.raises(Exception):
            load_json(str(bad))

    def test_load_pdf_basic(self, tmp_path):
        pytest.importorskip("pdfplumber")
        from reportlab.pdfgen import canvas

        pdf_path = tmp_path / "simple_fs.pdf"
        c = canvas.Canvas(str(pdf_path))
        c.setFont("Helvetica", 11)
        c.drawString(72, 800, "TechCorp Inc.")
        c.drawString(72, 780, "Income Statement")
        c.drawString(72, 762, "2023 2022")
        c.drawString(72, 744, "Revenue 500 450")
        c.drawString(72, 726, "EBITDA 125 110")
        c.drawString(72, 700, "Balance Sheet")
        c.drawString(72, 682, "2023 2022")
        c.drawString(72, 664, "Total Assets 750 700")
        c.drawString(72, 646, "Total Liabilities 325 300")
        c.drawString(72, 620, "Cash Flow Statement")
        c.drawString(72, 602, "2023 2022")
        c.drawString(72, 584, "Operating Cash Flow 140 130")
        c.save()

        data = load_pdf(str(pdf_path))
        assert data["company_name"] == "TechCorp Inc."
        assert "2023" in data["income_statement"]
        assert "2023" in data["balance_sheet"]
        assert "2023" in data["cash_flow_statement"]
        assert data["income_statement"]["2023"]["Revenue"] == 500.0


class TestNormalization:
    def test_normalize_techcorp(self, techcorp_raw):
        fs = normalize(techcorp_raw)
        assert fs.metadata.company_name == "TechCorp Inc."
        assert 2023 in fs.income_statements
        assert fs.income_statements[2023].revenue == 500.0
        assert fs.income_statements[2023].ebitda == 185.0
        assert fs.income_statements[2023].net_income == 118.5

    def test_normalize_manufactureco(self, manufactureco_path):
        """ManufactureCo uses alternate field names — tests fuzzy matching."""
        raw = json.loads(Path(manufactureco_path).read_text())
        fs = normalize(raw)
        assert fs.income_statements[2023].revenue == 1200.0  # "net sales" → revenue
        assert fs.income_statements[2023].ebit == 240.0  # "operating income" → ebit

    def test_normalize_retailchain(self, retailchain_path):
        """RetailChain uses 'turnover', 'cost of sales', 'finance costs'."""
        raw = json.loads(Path(retailchain_path).read_text())
        fs = normalize(raw)
        assert fs.income_statements[2023].revenue == 800.0  # "turnover" → revenue
        assert fs.income_statements[2023].net_income == 48.2  # "net profit" → net_income

    def test_balance_sheet_fields(self, techcorp_raw):
        fs = normalize(techcorp_raw)
        bs = fs.balance_sheets[2023]
        assert bs.total_assets == 750.0
        assert bs.total_liabilities == 325.0
        assert bs.shareholders_equity == 425.0

    def test_historical_years(self, techcorp_raw):
        fs = normalize(techcorp_raw)
        assert fs.historical_years == [2021, 2022, 2023]
        assert fs.latest_year == 2023


class TestValidation:
    def test_techcorp_passes(self, techcorp_normalized):
        report = validate(techcorp_normalized)
        assert report.passed is True
        assert len(report.errors) == 0


class TestBalanceSheetChecker:
    def test_techcorp_balanced(self, techcorp_normalized):
        bs = techcorp_normalized.balance_sheets[2023]
        result = check_balance_sheet(bs)
        assert result.balanced is True
        assert abs(result.delta) <= 0.01

    def test_imbalanced_detected(self, imbalanced_bs_path):
        raw = json.loads(Path(imbalanced_bs_path).read_text())
        fs = normalize(raw)
        bs = fs.balance_sheets[2023]
        result = check_balance_sheet(bs)
        assert result.balanced is False
        assert result.delta == 100.0  # $450M - ($140M + $210M) = $100M
        assert result.plug_suggestion is not None
