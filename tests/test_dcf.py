"""Tests for DCF engine — projection, WACC, terminal value, equity bridge."""

import pytest
from fmva.audit.trail import AuditTrail
from fmva.engines.projection import project_income_statement
from fmva.engines.dcf import (
    calculate_discount_factors,
    calculate_terminal_value_gordon,
    calculate_terminal_value_exit_multiple,
    run_full_dcf,
)
from fmva.engines.wacc import calculate_wacc
from fmva.exceptions import GordonGrowthError, WACCBoundsError


class TestProjection:
    def test_revenue_projection(self, base_assumptions):
        audit = AuditTrail()
        proj = project_income_statement(500.0, base_assumptions, 5, audit)
        # Year 1: 500 * 1.10 = 550
        assert abs(proj.revenue[1] - 550.0) < 0.01
        # Year 2: 550 * 1.10 = 605
        assert abs(proj.revenue[2] - 605.0) < 0.01
        # All years populated
        assert len(proj.years) == 5
        assert all(t in proj.ufcf for t in proj.years)

    def test_ufcf_positive(self, base_assumptions):
        audit = AuditTrail()
        proj = project_income_statement(500.0, base_assumptions, 5, audit)
        for t in proj.years:
            assert proj.ufcf[t] > 0, f"UFCF should be positive in Year {t}"

    def test_ebitda_margin_applied(self, base_assumptions):
        audit = AuditTrail()
        proj = project_income_statement(500.0, base_assumptions, 5, audit)
        # EBITDA margin = 25%
        assert abs(proj.ebitda[1] / proj.revenue[1] - 0.25) < 0.001


class TestWACC:
    def test_wacc_in_bounds(self):
        result = calculate_wacc(beta=1.2, debt_rate=0.05, tax_rate=0.21, target_d_to_e=0.3)
        assert 0.05 <= result.wacc <= 0.25

    def test_wacc_components(self):
        result = calculate_wacc(
            risk_free_rate=0.04, equity_risk_premium=0.06,
            beta=1.0, debt_rate=0.05, tax_rate=0.21, target_d_to_e=0.25,
        )
        # Ke = 0.04 + 1.0 * 0.06 = 0.10
        assert abs(result.cost_of_equity - 0.10) < 0.001
        # Kd_at = 0.05 * (1 - 0.21) = 0.0395
        assert abs(result.cost_of_debt_after_tax - 0.0395) < 0.001


class TestTerminalValue:
    def test_gordon_growth(self):
        audit = AuditTrail()
        tv = calculate_terminal_value_gordon(100.0, 0.10, 0.025, audit)
        # TV = 100 * 1.025 / (0.10 - 0.025) = 102.5 / 0.075 = 1366.67
        assert abs(tv - 1366.67) < 0.1

    def test_gordon_invalid_raises(self):
        with pytest.raises(GordonGrowthError):
            calculate_terminal_value_gordon(100.0, 0.025, 0.10)  # WACC < TGR

    def test_exit_multiple(self):
        audit = AuditTrail()
        tv = calculate_terminal_value_exit_multiple(200.0, 12.0, audit)
        assert tv == 2400.0


class TestFullDCF:
    def test_dcf_produces_result(self, techcorp_normalized, base_assumptions):
        from fmva.core.schemas import WACCResult
        wacc_r = WACCResult(wacc=0.10, cost_of_equity=0.10, cost_of_debt_after_tax=0.04,
                           beta=1.0, risk_free_rate=0.045, equity_risk_premium=0.055,
                           weight_equity=0.77, weight_debt=0.23)
        result = run_full_dcf(techcorp_normalized, base_assumptions, wacc_r)
        assert result.enterprise_value_gordon > 0
        assert result.enterprise_value_exit_multiple > 0
        assert result.equity_value_gordon > 0
        assert result.implied_price_gordon > 0
        assert result.implied_price_exit_multiple > 0

    def test_dcf_ev_exit_gt_zero(self, techcorp_normalized, base_assumptions):
        from fmva.core.schemas import WACCResult
        wacc_r = WACCResult(wacc=0.10, cost_of_equity=0.10, cost_of_debt_after_tax=0.04,
                           beta=1.0, risk_free_rate=0.045, equity_risk_premium=0.055,
                           weight_equity=0.77, weight_debt=0.23)
        result = run_full_dcf(techcorp_normalized, base_assumptions, wacc_r)
        assert result.enterprise_value_exit_multiple > result.sum_pv_ufcf  # TV adds value
