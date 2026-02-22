"""Tests for comparable company and sensitivity analysis engines."""

import pytest
import numpy as np
from fmva.core.schemas import CompData, CompsStats
from fmva.engines.comps import calculate_comps_stats, apply_comps_multiples
from fmva.engines.sensitivity import sensitivity_matrix, wacc_tgr_sensitivity
from fmva.audit.trail import AuditTrail


class TestCompsStats:
    def _make_comps(self):
        return [
            CompData(ticker="A", ev_ebitda=10.0, ev_revenue=3.0, pe_ratio=20.0),
            CompData(ticker="B", ev_ebitda=12.0, ev_revenue=3.5, pe_ratio=22.0),
            CompData(ticker="C", ev_ebitda=11.0, ev_revenue=2.8, pe_ratio=18.0),
            CompData(ticker="D", ev_ebitda=13.0, ev_revenue=4.0, pe_ratio=25.0),
            CompData(ticker="E", ev_ebitda=9.5, ev_revenue=2.5, pe_ratio=15.0),
        ]

    def test_stats_median(self):
        stats = calculate_comps_stats(self._make_comps())
        assert stats.n_companies == 5
        ev_ebitda = stats.multiples["ev_ebitda"]
        assert ev_ebitda["median"] == 11.0  # Sorted: 9.5, 10, 11, 12, 13

    def test_stats_percentiles(self):
        stats = calculate_comps_stats(self._make_comps())
        ev_ebitda = stats.multiples["ev_ebitda"]
        assert ev_ebitda["min"] <= ev_ebitda["p25"] <= ev_ebitda["median"]
        assert ev_ebitda["median"] <= ev_ebitda["p75"] <= ev_ebitda["max"]

    def test_apply_multiples(self):
        stats = calculate_comps_stats(self._make_comps())
        audit = AuditTrail()
        result = apply_comps_multiples(stats, target_ebitda=200.0, target_revenue=800.0, audit=audit)
        # Median EV/EBITDA = 11.0 → implied EV = 11.0 × 200 = 2200
        assert result.implied_ev_ebitda_median == pytest.approx(11.0 * 200.0, rel=0.01)

    def test_empty_comps(self):
        stats = calculate_comps_stats([])
        assert stats.n_companies == 0


class TestSensitivityMatrix:
    def test_matrix_shape(self):
        rows = [0.08, 0.09, 0.10, 0.11, 0.12]
        cols = [0.015, 0.020, 0.025, 0.030, 0.035]
        result = sensitivity_matrix(rows, cols, lambda r, c: r + c)
        assert len(result["data"]) == 5
        assert len(result["data"][0]) == 5

    def test_matrix_values(self):
        result = sensitivity_matrix([1, 2], [10, 20], lambda r, c: r * c)
        assert result["data"][0][0] == 10  # 1 × 10
        assert result["data"][1][1] == 40  # 2 × 20

    def test_wacc_tgr_sensitivity_shape(self):
        result = wacc_tgr_sensitivity(
            base_ufcf=100.0, base_sum_pv=400.0, net_debt=50.0,
            shares=100.0, n_years=5, mid_year=True,
        )
        assert len(result["data"]) == 5
        assert len(result["data"][0]) == 5

    def test_wacc_tgr_monotonicity(self):
        """Higher WACC should give lower valuation (for same TGR)."""
        result = wacc_tgr_sensitivity(
            base_ufcf=100.0, base_sum_pv=400.0, net_debt=50.0,
            shares=100.0, n_years=5, mid_year=True,
            wacc_range=[0.08, 0.10, 0.12],
            tgr_range=[0.02, 0.025, 0.03],
        )
        # For TGR=2.5% (col index 1): higher WACC rows → lower values
        col_idx = 1
        vals = [result["data"][r][col_idx] for r in range(3)]
        # Filter out None values
        vals = [v for v in vals if v is not None]
        for i in range(len(vals) - 1):
            assert vals[i] > vals[i + 1], "Higher WACC should yield lower valuation"

    def test_invalid_wacc_tgr_returns_none(self):
        """When WACC ≤ TGR, Gordon Growth is invalid → should return None."""
        result = sensitivity_matrix(
            [0.02], [0.03],  # WACC=2%, TGR=3% → invalid
            lambda wacc, tgr: None if wacc <= tgr else 100.0,
        )
        assert result["data"][0][0] is None
