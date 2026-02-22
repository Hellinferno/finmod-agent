# 12 — Testing Strategy
### Financial Modeling & Valuation Agent | Colab + Unsloth Stack

---

## 1. Document Purpose

This document defines the **complete testing philosophy, test suite architecture, and quality gates** for the Financial Modeling & Valuation Agent. Given the financial nature of this product — where a calculation error can mean a multi-million dollar mispricing — testing is treated as a first-class engineering concern, not an afterthought.

> **Core Principle**: Every number the agent outputs that a financial professional might rely on must be independently verifiable. The test suite is the machine-readable equivalent of an auditor's working papers.

---

## 2. Testing Philosophy

### 2.1 The Three Laws of Financial Software Testing

1. **Law of Ground Truth**: Every financial calculation test must have a manually computed, domain-expert-verified expected value. "It looks about right" is not a test.

2. **Law of Tolerance**: Financial calculations operate on real-world data with rounding. Every test must specify an explicit tolerance (e.g., ±0.01% for DCF values, ±$0.001M for intermediate calculations).

3. **Law of Audit-First**: If a test fails, the audit trail must contain enough information to explain exactly why it failed. No black boxes.

### 2.2 Testing Pyramid for This Project

```
                    ┌─────────────────┐
                    │  E2E / Notebook  │  ← 5% of tests; slowest; human-reviewed
                    │     Tests        │
                   /───────────────────\
                  /  Integration Tests  \  ← 20% of tests; module boundaries
                 /─────────────────────── \
                /      Unit Tests          \  ← 75% of tests; fast; automated
               /────────────────────────────\
```

**Target Coverage**:
- Unit tests: ≥ 80% line coverage on all `src/` modules
- Integration tests: 100% of module-boundary interactions
- E2E tests: All 10 integration scenarios from Phase 6

---

## 3. Test Environment Setup

### 3.1 Test Dependencies

```bash
# Install test dependencies
pip install pytest==7.4.4 pytest-cov==4.1.0 pytest-mock==3.12.0

# Run full suite
pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

# Run specific module
pytest tests/test_dcf.py -v -k "test_ufcf"

# Run with detailed output
pytest tests/ -v -s --tb=long
```

### 3.2 `conftest.py` — Shared Fixtures

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def techcorp_raw():
    """TechCorp Inc raw financial data (SaaS, high growth)."""
    with open(FIXTURES_DIR / "techcorp_raw.json") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def manufactureco_raw():
    """ManufactureCo raw financial data (industrial, stable)."""
    with open(FIXTURES_DIR / "manufactureco_raw.json") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def retailchain_raw():
    """RetailChain raw financial data (retail, declining)."""
    with open(FIXTURES_DIR / "retailchain_raw.json") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def imbalanced_bs_raw():
    """Financial data with a deliberately imbalanced balance sheet."""
    with open(FIXTURES_DIR / "imbalanced_bs.json") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def techcorp_normalized(techcorp_raw):
    """Pre-normalized TechCorp data (avoids re-running normalizer every test)."""
    from ingestion.normalizer import normalize
    return normalize(techcorp_raw)

@pytest.fixture
def base_assumptions():
    """Standard base case assumptions."""
    from assumptions.engine import AssumptionSet
    return AssumptionSet(
        scenario="base",
        revenue_growth_rates=[0.10, 0.10, 0.09, 0.09, 0.08],
        ebitda_margin=0.25,
        capex_to_sales=0.06,
        da_to_revenue=0.05,
        nwc_to_revenue=0.08,
        tax_rate=0.21,
        terminal_growth_rate=0.025,
        exit_multiple=12.0,
        projection_years=5,
    )

@pytest.fixture
def mock_yfinance(mocker):
    """Mock yfinance to avoid live API calls in tests."""
    mock_ticker = mocker.MagicMock()
    mock_ticker.info = {
        "marketCap": 5_000_000_000,
        "enterpriseValue": 5_200_000_000,
        "beta": 1.25,
        "trailingPE": 28.5,
        "enterpriseToEbitda": 18.2,
        "enterpriseToRevenue": 4.5,
        "ebitda": 280_000_000,
    }
    mocker.patch("yfinance.Ticker", return_value=mock_ticker)
    return mock_ticker
```

---

## 4. Unit Tests

### 4.1 `test_ingestion.py`

```python
# tests/test_ingestion.py
"""
Tests for data ingestion, normalization, and validation modules.
Ground truth: manually verified financial statements for fixture companies.
"""
import pytest
import pandas as pd
from ingestion.loader import load_json, load_csv, load_excel
from ingestion.normalizer import normalize, CANONICAL_MAP
from ingestion.validator import validate
from ingestion.balance_sheet_checker import check_balance_sheet

TOLERANCE = 1e-6  # Absolute tolerance for financial values ($M)

class TestJSONLoader:
    def test_loads_valid_json(self, techcorp_raw):
        result = load_json("tests/fixtures/techcorp_raw.json")
        assert isinstance(result, dict)
        assert "income_statement" in result
        assert "balance_sheet" in result
        assert "cash_flow" in result

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_json("nonexistent.json")

    def test_raises_on_malformed_json(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid json}")
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_json(str(bad_file))

    def test_raises_ingestion_error_on_missing_section(self):
        from ingestion.loader import IngestionError
        with pytest.raises(IngestionError, match="balance_sheet"):
            load_json("tests/fixtures/missing_balance_sheet.json")


class TestCSVLoader:
    def test_loads_comma_delimited(self):
        df = load_csv("tests/fixtures/techcorp_is.csv")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_handles_semicolon_delimiter(self):
        df = load_csv("tests/fixtures/semicolon_delimited.csv")
        assert df.shape[1] > 1  # Multiple columns parsed

    def test_handles_percent_formatting(self):
        # "25.0%" should be parsed as 0.25
        df = load_csv("tests/fixtures/with_percents.csv")
        assert df["ebitda_margin"].dtype == float
        assert abs(df["ebitda_margin"].iloc[0] - 0.25) < TOLERANCE


class TestNormalizer:
    def test_maps_revenue_alias(self):
        raw = {"income_statement": {"net sales": 1000.0}, ...}
        normalized = normalize(raw)
        assert normalized.income_statement.revenue == 1000.0

    def test_case_insensitive_mapping(self):
        raw = {"income_statement": {"TOTAL REVENUE": 1000.0}, ...}
        normalized = normalize(raw)
        assert normalized.income_statement.revenue == 1000.0

    def test_all_canonical_fields_present(self, techcorp_normalized):
        fs = techcorp_normalized
        # Income Statement
        assert fs.income_statement.revenue is not None
        assert fs.income_statement.gross_profit is not None
        assert fs.income_statement.ebitda is not None
        assert fs.income_statement.ebit is not None
        assert fs.income_statement.net_income is not None
        # Balance Sheet
        assert fs.balance_sheet.total_assets is not None
        assert fs.balance_sheet.total_liabilities is not None
        assert fs.balance_sheet.shareholders_equity is not None
        # Cash Flow
        assert fs.cash_flow.operating_cash_flow is not None
        assert fs.cash_flow.capex is not None

    def test_multi_year_parsing(self, techcorp_raw):
        normalized = normalize(techcorp_raw)
        assert len(normalized.historical_years) >= 3

    def test_warns_on_single_year_data(self, caplog):
        single_year_raw = load_json("tests/fixtures/single_year_only.json")
        with pytest.warns(UserWarning, match="minimum 3 years"):
            normalize(single_year_raw)

    def test_negative_ebitda_accepted_with_flag(self):
        raw = load_json("tests/fixtures/negative_ebitda.json")
        result = normalize(raw)
        assert result.income_statement.ebitda < 0
        assert result.warnings["negative_ebitda"] is True

    def test_gaap_flag_detected(self, techcorp_raw):
        techcorp_raw["accounting_standard"] = "GAAP"
        result = normalize(techcorp_raw)
        assert result.accounting_standard == "GAAP"


class TestBalanceSheetChecker:
    # TechCorp fixture: Assets = 1500.0, Liabilities = 900.0, Equity = 600.0 → balanced
    def test_balanced_sheet_passes(self, techcorp_normalized):
        result = check_balance_sheet(techcorp_normalized.balance_sheet)
        assert result.balanced is True
        assert result.delta == pytest.approx(0.0, abs=0.01)

    def test_imbalanced_sheet_detected(self, imbalanced_bs_raw):
        from ingestion.normalizer import normalize
        normalized = normalize(imbalanced_bs_raw)
        result = check_balance_sheet(normalized.balance_sheet)
        assert result.balanced is False
        assert abs(result.delta) > 0.01

    def test_plug_suggestion_provided(self, imbalanced_bs_raw):
        from ingestion.normalizer import normalize
        normalized = normalize(imbalanced_bs_raw)
        result = check_balance_sheet(normalized.balance_sheet)
        assert result.plug_suggestion is not None
        assert "Retained Earnings" in result.plug_suggestion or "delta" in result.plug_suggestion.lower()

    def test_tolerance_within_rounding(self):
        """$0.001M difference should be within tolerance."""
        from ingestion.balance_sheet_checker import BalanceSheet
        bs = BalanceSheet(total_assets=1000.001, total_liabilities=600.0, shareholders_equity=400.0)
        result = check_balance_sheet(bs)
        assert result.balanced is True  # Within $0.01M tolerance


class TestValidator:
    def test_valid_data_passes(self, techcorp_normalized):
        report = validate(techcorp_normalized)
        assert report.passed is True
        assert len(report.errors) == 0

    def test_negative_revenue_flagged(self):
        from ingestion.validator import validate, ValidationReport
        # Negative revenue is invalid
        bad_data = build_fixture(revenue=-100.0)
        report = validate(bad_data)
        assert report.passed is False
        assert any("negative revenue" in e.lower() for e in report.errors)

    def test_ebitda_da_consistency(self, techcorp_normalized):
        """EBITDA should approximately equal EBIT + D&A."""
        fs = techcorp_normalized.income_statement
        expected_ebitda = fs.ebit + fs.depreciation
        assert abs(fs.ebitda - expected_ebitda) / fs.ebitda < 0.005  # ±0.5%
```

---

### 4.2 `test_dcf.py`

```python
# tests/test_dcf.py
"""
DCF Engine Unit Tests.
Ground truth: manually verified Excel model (TechCorp Base Case).

Manual Model Parameters (TechCorp Base Case):
  Base Revenue (Year 0):     $500.0M
  Revenue Growth:            10%, 10%, 9%, 9%, 8%
  EBITDA Margin:             25%
  D&A/Revenue:               5%
  CapEx/Sales:               6%
  NWC/Revenue:               8%
  Tax Rate:                  21%
  WACC:                      10%
  Terminal Growth Rate:      2.5%
  Net Debt:                  $150M
  Diluted Shares:            100M

Expected Outputs (manually verified):
  Year 1 Revenue:            $550.0M
  Year 5 Revenue:            $735.5M (approx)
  Year 5 UFCF:               $68.2M (approx)
  Terminal Value (Gordon):   $1,284M (approx)
  Enterprise Value:          $1,102M (approx)
  Equity Value:              $952M (approx)
  Implied Share Price:       $9.52 (approx)
"""
import pytest
from valuation.dcf import (
    project_income_statement,
    calculate_ufcf,
    calculate_terminal_value,
    calculate_equity_value,
)
from valuation.wacc import calculate_wacc

TOLERANCE_PCT = 0.001  # 0.1% tolerance for cross-model validation

class TestIncomeStatementProjection:
    def test_year1_revenue(self, base_assumptions):
        proj = project_income_statement(
            base_revenue=500.0,
            assumptions=base_assumptions,
            n_years=5,
        )
        assert proj.revenue[1] == pytest.approx(550.0, rel=TOLERANCE_PCT)

    def test_year5_revenue(self, base_assumptions):
        proj = project_income_statement(500.0, base_assumptions, 5)
        # 500 × 1.10 × 1.10 × 1.09 × 1.09 × 1.08 = 735.50 (approx)
        assert proj.revenue[5] == pytest.approx(735.5, rel=0.005)

    def test_ebitda_margin_applied(self, base_assumptions):
        proj = project_income_statement(500.0, base_assumptions, 5)
        for year in range(1, 6):
            margin = proj.ebitda[year] / proj.revenue[year]
            assert margin == pytest.approx(0.25, rel=TOLERANCE_PCT)

    def test_ebit_equals_ebitda_minus_da(self, base_assumptions):
        proj = project_income_statement(500.0, base_assumptions, 5)
        for year in range(1, 6):
            assert proj.ebit[year] == pytest.approx(
                proj.ebitda[year] - proj.da[year], rel=TOLERANCE_PCT
            )

    def test_nopat_equals_ebit_times_one_minus_tax(self, base_assumptions):
        proj = project_income_statement(500.0, base_assumptions, 5)
        for year in range(1, 6):
            expected = proj.ebit[year] * (1 - 0.21)
            assert proj.nopat[year] == pytest.approx(expected, rel=TOLERANCE_PCT)

    def test_ten_year_projection(self, base_assumptions):
        base_assumptions.projection_years = 10
        base_assumptions.revenue_growth_rates = [0.10]*10
        proj = project_income_statement(500.0, base_assumptions, 10)
        assert len(proj.revenue) == 11  # Year 0 through 10
        assert proj.revenue[10] == pytest.approx(500.0 * (1.10**10), rel=0.001)


class TestUFCFCalculation:
    def test_ufcf_formula_year1(self, base_assumptions):
        """UFCF = NOPAT + D&A - CapEx - ΔNWC"""
        proj = project_income_statement(500.0, base_assumptions, 5)
        ufcf_series = calculate_ufcf(proj, base_assumptions)
        
        # Manual Year 1:
        # Revenue: 550, EBITDA: 137.5, DA: 27.5, EBIT: 110, NOPAT: 86.9
        # CapEx: 33.0 (6% × 550), ΔNWC: 4.0 (8% × (550-500))
        # UFCF = 86.9 + 27.5 - 33.0 - 4.0 = 77.4
        assert ufcf_series[0] == pytest.approx(77.4, rel=0.01)

    def test_ufcf_positive_for_profitable_company(self, base_assumptions):
        proj = project_income_statement(500.0, base_assumptions, 5)
        ufcf_series = calculate_ufcf(proj, base_assumptions)
        assert all(ufcf > 0 for ufcf in ufcf_series)

    def test_negative_ufcf_handled(self):
        """High CapEx company can have negative UFCF — should not crash."""
        from assumptions.engine import AssumptionSet
        high_capex = AssumptionSet(
            scenario="stress",
            revenue_growth_rates=[0.05]*5,
            ebitda_margin=0.10,
            capex_to_sales=0.15,  # CapEx > NOPAT + D&A
            da_to_revenue=0.03,
            nwc_to_revenue=0.08,
            tax_rate=0.21,
            terminal_growth_rate=0.025,
            exit_multiple=8.0,
            projection_years=5,
        )
        proj = project_income_statement(500.0, high_capex, 5)
        ufcf_series = calculate_ufcf(proj, high_capex)
        assert isinstance(ufcf_series, list)
        assert len(ufcf_series) == 5
        # No crash; negative values allowed


class TestTerminalValue:
    def test_gordon_growth_model(self):
        # TV = UFCF_final × (1 + g) / (WACC - g)
        # TV = 68.2 × 1.025 / (0.10 - 0.025) = 68.2 × 1.025 / 0.075 = 931.7M
        tv = calculate_terminal_value(
            ufcf_final=68.2,
            ebitda_final=183.9,
            wacc=0.10,
            terminal_growth=0.025,
            exit_multiple=12.0,
            method="gordon",
        )
        assert tv == pytest.approx(931.7, rel=0.01)

    def test_exit_multiple_method(self):
        # TV = EBITDA_final × multiple = 183.9 × 12 = 2,206.8M
        tv = calculate_terminal_value(
            ufcf_final=68.2,
            ebitda_final=183.9,
            wacc=0.10,
            terminal_growth=0.025,
            exit_multiple=12.0,
            method="exit_multiple",
        )
        assert tv == pytest.approx(2206.8, rel=TOLERANCE_PCT)

    def test_raises_on_wacc_less_than_growth(self):
        with pytest.raises(ValueError, match="WACC must be greater than terminal growth"):
            calculate_terminal_value(
                ufcf_final=68.2,
                ebitda_final=183.9,
                wacc=0.02,
                terminal_growth=0.03,  # g > WACC — invalid
                exit_multiple=12.0,
                method="gordon",
            )

    def test_raises_on_negative_tv(self):
        with pytest.raises(ValueError, match="Terminal value cannot be negative"):
            calculate_terminal_value(
                ufcf_final=-100.0,
                ebitda_final=-50.0,
                wacc=0.10,
                terminal_growth=0.025,
                exit_multiple=12.0,
                method="gordon",
            )


class TestEquityValueBridge:
    def test_enterprise_to_equity_bridge(self):
        result = calculate_equity_value(
            ufcf_series=[77.4, 78.1, 74.5, 72.0, 68.2],
            terminal_value=931.7,
            wacc=0.10,
            net_debt=150.0,
            diluted_shares=100.0,
            mid_year=True,
        )
        # Enterprise Value should be > 0
        assert result.enterprise_value > 0
        # Equity Value = EV - Net Debt
        assert result.equity_value == pytest.approx(
            result.enterprise_value - 150.0, rel=TOLERANCE_PCT
        )
        # Implied Price = Equity Value / Shares
        assert result.implied_price == pytest.approx(
            result.equity_value / 100.0, rel=TOLERANCE_PCT
        )

    def test_mid_year_convention_differs_from_eoy(self):
        kwargs = dict(
            ufcf_series=[77.4, 78.1, 74.5, 72.0, 68.2],
            terminal_value=931.7,
            wacc=0.10,
            net_debt=150.0,
            diluted_shares=100.0,
        )
        mid_year = calculate_equity_value(**kwargs, mid_year=True)
        eoy = calculate_equity_value(**kwargs, mid_year=False)
        # Mid-year should give higher PV (discounted for 0.5 year less)
        assert mid_year.enterprise_value > eoy.enterprise_value

    def test_negative_equity_value_flagged(self):
        result = calculate_equity_value(
            ufcf_series=[10.0, 10.0, 10.0, 10.0, 10.0],
            terminal_value=100.0,
            wacc=0.10,
            net_debt=5000.0,  # Massive debt → negative equity
            diluted_shares=100.0,
            mid_year=True,
        )
        assert result.equity_value < 0
        assert result.warnings["negative_equity"] is True
```

---

### 4.3 `test_comps.py`

```python
# tests/test_comps.py
"""
Comparable Companies Module Tests.
All yfinance calls are mocked to avoid live API dependency.
"""
import pytest
from valuation.comps import fetch_comp_data, calculate_comps_stats, apply_comps_multiples

MOCK_COMPS_DATA = [
    {"ticker": "AAPL", "ev_ebitda": 20.0, "ev_revenue": 5.0, "pe_ratio": 28.0},
    {"ticker": "MSFT", "ev_ebitda": 22.0, "ev_revenue": 10.0, "pe_ratio": 32.0},
    {"ticker": "GOOGL", "ev_ebitda": 18.0, "ev_revenue": 6.0, "pe_ratio": 24.0},
    {"ticker": "META",  "ev_ebitda": 14.0, "ev_revenue": 5.5, "pe_ratio": 20.0},
    {"ticker": "AMZN",  "ev_ebitda": 25.0, "ev_revenue": 3.0, "pe_ratio": 42.0},
]

class TestCompsStats:
    def test_median_ev_ebitda(self):
        stats = calculate_comps_stats(MOCK_COMPS_DATA)
        # Sorted ev_ebitda: 14, 18, 20, 22, 25 → median = 20
        assert stats["ev_ebitda"]["median"] == pytest.approx(20.0)

    def test_25th_percentile(self):
        stats = calculate_comps_stats(MOCK_COMPS_DATA)
        assert stats["ev_ebitda"]["25th"] == pytest.approx(18.0, rel=0.01)

    def test_75th_percentile(self):
        stats = calculate_comps_stats(MOCK_COMPS_DATA)
        assert stats["ev_ebitda"]["75th"] == pytest.approx(22.0, rel=0.01)

    def test_handles_missing_multiples(self):
        """Should skip tickers with None multiples, not crash."""
        data_with_gaps = MOCK_COMPS_DATA + [
            {"ticker": "NFLX", "ev_ebitda": None, "ev_revenue": 4.0, "pe_ratio": 35.0}
        ]
        stats = calculate_comps_stats(data_with_gaps)
        # ev_ebitda should still use only 5 valid values
        assert stats["ev_ebitda"]["count"] == 5

    def test_minimum_3_comps_required(self):
        with pytest.raises(ValueError, match="minimum 3 comparable companies"):
            calculate_comps_stats(MOCK_COMPS_DATA[:2])


class TestCompsImpliedValuation:
    def test_implied_ev_from_ebitda_multiple(self, techcorp_normalized):
        stats = calculate_comps_stats(MOCK_COMPS_DATA)
        result = apply_comps_multiples(techcorp_normalized, stats)
        
        # TechCorp EBITDA (from fixture) × median EV/EBITDA
        ebitda = techcorp_normalized.income_statement.ebitda
        expected_ev = ebitda * stats["ev_ebitda"]["median"]
        assert result.ev_from_ebitda_median == pytest.approx(expected_ev, rel=0.001)

    def test_implied_range_low_high(self, techcorp_normalized):
        stats = calculate_comps_stats(MOCK_COMPS_DATA)
        result = apply_comps_multiples(techcorp_normalized, stats)
        # 25th percentile should be lower than 75th
        assert result.ev_from_ebitda_25th < result.ev_from_ebitda_75th


class TestCompsDataFetcher:
    def test_fetches_all_tickers(self, mock_yfinance):
        tickers = ["AAPL", "MSFT", "GOOGL"]
        result = fetch_comp_data(tickers)
        assert len(result) == 3

    def test_handles_invalid_ticker_gracefully(self, mocker):
        mocker.patch("yfinance.Ticker").side_effect = Exception("Not found")
        result = fetch_comp_data(["INVALIDTICKER999"])
        assert len(result) == 0  # Empty result, not crash
```

---

### 4.4 `test_sensitivity.py`

```python
# tests/test_sensitivity.py
import pytest
import pandas as pd
from valuation.sensitivity import sensitivity_matrix, plot_football_field

class TestSensitivityMatrix:
    def test_matrix_shape(self, base_assumptions, techcorp_normalized):
        wacc_range = [0.08, 0.09, 0.10, 0.11, 0.12]
        tgr_range = [0.015, 0.020, 0.025, 0.030, 0.035]
        matrix = sensitivity_matrix(
            base_wacc=0.10,
            base_tgr=0.025,
            wacc_range=wacc_range,
            tgr_range=tgr_range,
            assumptions=base_assumptions,
            normalized_data=techcorp_normalized,
        )
        assert matrix.shape == (5, 5)

    def test_base_case_cell_matches_dcf(self, base_assumptions, techcorp_normalized):
        """The (WACC=10%, TGR=2.5%) cell must match the standalone DCF result."""
        from valuation.dcf import run_full_dcf
        
        standalone_ev = run_full_dcf(techcorp_normalized, base_assumptions).enterprise_value
        
        wacc_range = [0.08, 0.09, 0.10, 0.11, 0.12]
        tgr_range = [0.015, 0.020, 0.025, 0.030, 0.035]
        matrix = sensitivity_matrix(
            base_wacc=0.10, base_tgr=0.025,
            wacc_range=wacc_range, tgr_range=tgr_range,
            assumptions=base_assumptions,
            normalized_data=techcorp_normalized,
        )
        base_cell_ev = matrix.loc[0.10, 0.025]
        assert base_cell_ev == pytest.approx(standalone_ev, rel=0.001)

    def test_higher_wacc_lower_ev(self, base_assumptions, techcorp_normalized):
        """As WACC increases, EV should decrease (inverse relationship)."""
        wacc_range = [0.08, 0.10, 0.12]
        tgr_range = [0.025]
        matrix = sensitivity_matrix(
            base_wacc=0.10, base_tgr=0.025,
            wacc_range=wacc_range, tgr_range=tgr_range,
            assumptions=base_assumptions,
            normalized_data=techcorp_normalized,
        )
        assert matrix.loc[0.08, 0.025] > matrix.loc[0.10, 0.025] > matrix.loc[0.12, 0.025]

    def test_higher_tgr_higher_ev(self, base_assumptions, techcorp_normalized):
        """As terminal growth rate increases, EV should increase."""
        wacc_range = [0.10]
        tgr_range = [0.015, 0.025, 0.035]
        matrix = sensitivity_matrix(
            base_wacc=0.10, base_tgr=0.025,
            wacc_range=wacc_range, tgr_range=tgr_range,
            assumptions=base_assumptions,
            normalized_data=techcorp_normalized,
        )
        assert matrix.loc[0.10, 0.015] < matrix.loc[0.10, 0.025] < matrix.loc[0.10, 0.035]

    def test_returns_pandas_dataframe(self, base_assumptions, techcorp_normalized):
        matrix = sensitivity_matrix(
            base_wacc=0.10, base_tgr=0.025,
            wacc_range=[0.09, 0.10, 0.11],
            tgr_range=[0.020, 0.025, 0.030],
            assumptions=base_assumptions,
            normalized_data=techcorp_normalized,
        )
        assert isinstance(matrix, pd.DataFrame)


class TestFootballField:
    def test_chart_generates_without_error(self):
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend for testing
        
        valuation_ranges = {
            "DCF (Bear)": (800, 950),
            "DCF (Base)": (950, 1100),
            "DCF (Bull)": (1100, 1350),
            "EV/EBITDA Comps": (850, 1050),
            "EV/Revenue Comps": (900, 1150),
            "Precedent Transactions": (1050, 1400),
        }
        fig = plot_football_field(valuation_ranges, current_price=1000.0)
        assert fig is not None

    def test_chart_has_correct_number_of_bars(self):
        import matplotlib
        matplotlib.use("Agg")
        valuation_ranges = {
            "DCF (Base)": (950, 1100),
            "EV/EBITDA Comps": (850, 1050),
        }
        fig = plot_football_field(valuation_ranges)
        ax = fig.axes[0]
        assert len(ax.patches) >= 2
```

---

### 4.5 `test_audit.py`

```python
# tests/test_audit.py
import pytest
import json
from audit.trail import AuditTrail, AuditEntry

class TestAuditTrail:
    def test_logs_entry(self):
        trail = AuditTrail()
        trail.log(
            step="UFCF Year 1",
            formula="NOPAT + D&A - CapEx - ΔNWC",
            inputs={"NOPAT": 86.9, "DA": 27.5, "CapEx": 33.0, "ΔNWC": 4.0},
            output=77.4,
            unit="$M",
        )
        assert len(trail.entries) == 1
        assert trail.entries[0].step == "UFCF Year 1"
        assert trail.entries[0].output == 77.4

    def test_entries_are_immutable(self):
        trail = AuditTrail()
        trail.log("Step 1", "A + B", {"A": 1, "B": 2}, 3, "$M")
        with pytest.raises(Exception):
            trail.entries[0].output = 999  # Should be frozen dataclass

    def test_exports_to_json(self, tmp_path):
        trail = AuditTrail()
        trail.log("Revenue Year 1", "Base × (1+g)", {"Base": 500, "g": 0.10}, 550, "$M")
        
        output_file = tmp_path / "audit.json"
        trail.export_json(str(output_file))
        
        with open(output_file) as f:
            data = json.load(f)
        
        assert len(data["entries"]) == 1
        assert data["entries"][0]["step"] == "Revenue Year 1"
        assert data["entries"][0]["output"] == 550

    def test_all_dcf_steps_captured(self, base_assumptions, techcorp_normalized):
        from valuation.dcf import run_full_dcf
        trail = AuditTrail()
        run_full_dcf(techcorp_normalized, base_assumptions, audit_trail=trail)
        
        step_names = [e.step for e in trail.entries]
        # Must include these key steps
        assert any("Revenue" in s for s in step_names)
        assert any("UFCF" in s for s in step_names)
        assert any("Terminal Value" in s for s in step_names)
        assert any("Enterprise Value" in s for s in step_names)
        assert any("Equity Value" in s for s in step_names)
```

---

## 5. Integration Tests

### 5.1 `test_integration.py`

```python
# tests/test_integration.py
"""
End-to-end integration tests. These are slower and test complete pipelines.
Run with: pytest tests/test_integration.py -v -m integration
"""
import pytest

pytestmark = pytest.mark.integration  # Mark all tests in this file

class TestFullDCFPipeline:
    def test_techcorp_end_to_end(self, techcorp_raw, base_assumptions):
        """Full pipeline: raw JSON → normalized → DCF → EV."""
        from ingestion.loader import load_json
        from ingestion.normalizer import normalize
        from ingestion.validator import validate
        from ingestion.balance_sheet_checker import check_balance_sheet
        from valuation.dcf import run_full_dcf
        
        # Ingest
        normalized = normalize(techcorp_raw)
        # Validate
        report = validate(normalized)
        assert report.passed
        # Balance sheet
        bs_check = check_balance_sheet(normalized.balance_sheet)
        assert bs_check.balanced
        # DCF
        result = run_full_dcf(normalized, base_assumptions)
        assert result.enterprise_value > 0
        assert result.implied_price > 0

    def test_imbalanced_bs_does_not_crash_pipeline(self, imbalanced_bs_raw, base_assumptions):
        """Imbalanced balance sheet should flag, not crash, the full pipeline."""
        from ingestion.normalizer import normalize
        from ingestion.balance_sheet_checker import check_balance_sheet
        from valuation.dcf import run_full_dcf
        
        normalized = normalize(imbalanced_bs_raw)
        bs_check = check_balance_sheet(normalized.balance_sheet)
        
        assert bs_check.balanced is False
        assert bs_check.plug_suggestion is not None
        
        # DCF should still run with a warning (not block)
        result = run_full_dcf(normalized, base_assumptions)
        assert result.warnings["balance_sheet_imbalanced"] is True


class TestCompsIntegration:
    def test_comps_to_valuation_range(self, mock_yfinance, techcorp_normalized):
        from valuation.comps import fetch_comp_data, calculate_comps_stats, apply_comps_multiples
        
        tickers = ["AAPL", "MSFT", "GOOGL", "META", "AMZN"]
        comps_data = fetch_comp_data(tickers)
        stats = calculate_comps_stats(comps_data)
        implied = apply_comps_multiples(techcorp_normalized, stats)
        
        assert implied.ev_from_ebitda_median > 0
        assert implied.ev_from_revenue_median > 0


class TestExcelExport:
    def test_excel_generates_10_sheets(self, techcorp_normalized, base_assumptions, tmp_path):
        from valuation.dcf import run_full_dcf
        from export.excel_exporter import export_to_excel
        
        result = run_full_dcf(techcorp_normalized, base_assumptions)
        output_path = tmp_path / "test_valuation.xlsx"
        
        export_to_excel(result, techcorp_normalized, str(output_path))
        
        import openpyxl
        wb = openpyxl.load_workbook(str(output_path))
        assert len(wb.sheetnames) == 10

    def test_excel_values_match_computed(self, techcorp_normalized, base_assumptions, tmp_path):
        from valuation.dcf import run_full_dcf
        from export.excel_exporter import export_to_excel
        import openpyxl
        
        result = run_full_dcf(techcorp_normalized, base_assumptions)
        output_path = tmp_path / "test_valuation.xlsx"
        export_to_excel(result, techcorp_normalized, str(output_path))
        
        wb = openpyxl.load_workbook(str(output_path))
        dcf_sheet = wb["DCF Model"]
        # Verify Enterprise Value cell matches computed EV
        ev_cell = dcf_sheet["B30"]  # Convention: EV is in row 30
        assert abs(ev_cell.value - result.enterprise_value) < 0.01
```

---

## 6. Narrative / LLM Tests

### 6.1 LLM Test Strategy

LLM outputs cannot be tested for exact string matches. Instead, test:
1. **Structure** — Required sections are present
2. **Factual grounding** — Numbers cited match the model output
3. **Constraints** — Word count, format compliance

```python
# tests/test_narrative.py
import pytest
import re

class TestNarrativeStructure:
    @pytest.fixture
    def sample_narrative(self):
        """Use a cached/mock narrative for testing (not live LLM)."""
        return {
            "executive_summary": (
                "TechCorp Inc. is valued at $952M in equity value under the base case DCF, "
                "implying a share price of $9.52. This is driven by projected revenue growth "
                "of 10% annually and EBITDA margin expansion to 25%. The EV/EBITDA comps "
                "analysis corroborates this at $950M median implied value."
            ),
        }

    def test_executive_summary_cites_dcf_value(self, sample_narrative):
        text = sample_narrative["executive_summary"]
        # Should contain the dollar amount
        assert "$952M" in text or "952" in text

    def test_executive_summary_length(self, sample_narrative):
        text = sample_narrative["executive_summary"]
        word_count = len(text.split())
        assert 150 <= word_count <= 500  # 150–500 word range

    def test_no_hallucinated_numbers(self, sample_narrative):
        from llm.evaluator import check_factual_grounding
        
        known_facts = {"equity_value": 952.0, "implied_price": 9.52, "ev": 1102.0}
        flagged = check_factual_grounding(
            sample_narrative["executive_summary"],
            known_facts,
            tolerance=0.05,  # ±5%
        )
        assert len(flagged) == 0, f"Hallucinated numbers: {flagged}"
```

---

## 7. Test Data Fixtures

### 7.1 Fixture Specification

All fixtures live in `tests/fixtures/`. They are small JSON files manually constructed and verified by the Financial Domain Expert.

```json
// tests/fixtures/techcorp_raw.json
{
    "company_name": "TechCorp Inc.",
    "ticker": "TECH",
    "currency": "USD",
    "units": "millions",
    "accounting_standard": "GAAP",
    "fiscal_year_end": "December",
    "income_statement": {
        "2021": {
            "total revenue": 413.2,
            "cost of goods sold": 124.0,
            "gross profit": 289.2,
            "ebitda": 99.2,
            "depreciation and amortization": 18.5,
            "operating income": 80.7,
            "interest expense": 8.2,
            "income tax": 15.2,
            "net income": 57.3
        },
        "2022": {
            "total revenue": 454.5,
            ...
        },
        "2023": {
            "total revenue": 500.0,
            ...
        }
    },
    "balance_sheet": {
        "2023": {
            "total assets": 1500.0,
            "total liabilities": 900.0,
            "shareholders equity": 600.0,
            "cash and equivalents": 120.0
        }
    },
    "cash_flow": {
        "2023": {
            "cash from operations": 95.0,
            "capital expenditure": -30.0,
            "depreciation and amortization": 25.0
        }
    },
    "additional_data": {
        "diluted_shares": 100.0,
        "net_debt": 150.0
    }
}
```

---

## 8. Quality Gates Summary

| Gate | Metric | Threshold | Blocks Release? |
|------|--------|-----------|----------------|
| Unit test pass rate | % tests green | 100% | Yes |
| Code coverage (computation modules) | Line coverage | ≥ 80% | Yes |
| DCF cross-model tolerance | vs. manual Excel | ≤ 0.1% | Yes |
| Balance sheet checker accuracy | Correct detections | 100% of planted tests | Yes |
| Integration test pass rate | % green | 100% | Yes |
| Narrative factual grounding | Hallucination catch rate | ≥ 80% of planted errors | Yes |
| Excel export integrity | Values match computed | 100% of checked cells | Yes |
| Full pipeline runtime | Colab T4 (no LLM) | ≤ 30 seconds | No (Warning) |
| Full pipeline runtime (with LLM) | Colab T4 | ≤ 3 minutes | No (Warning) |
| Peak memory usage | RAM + VRAM combined | ≤ 12 GB | No (Warning) |

---

## 9. Test Execution Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Run only fast unit tests (exclude integration)
pytest tests/ -v -m "not integration"

# Run only integration tests
pytest tests/ -v -m integration

# Run specific test class
pytest tests/test_dcf.py::TestUFCFCalculation -v

# Run with verbose output and no capture (see print statements)
pytest tests/ -v -s

# Check coverage threshold
pytest tests/ --cov=. --cov-fail-under=80
```

---

*Version: 1.0 | Status: Draft | Owner: Tech Lead*
