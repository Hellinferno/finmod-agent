"""
Pydantic data models for all FMVA data structures.

These schemas define the canonical representation of financial data throughout
the system. All modules consume and produce these types.

Design:
- Immutable models (frozen=True) for data integrity
- Optional fields with sensible defaults for graceful degradation
- Validators for business logic constraints
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


# ── Enums ──────────────────────────────────────────────────────────────────────


class AccountingStandard(str, Enum):
    GAAP = "GAAP"
    IFRS = "IFRS"
    UNKNOWN = "UNKNOWN"


class Scenario(str, Enum):
    BEAR = "bear"
    BASE = "base"
    BULL = "bull"
    CUSTOM = "custom"


class TVMethod(str, Enum):
    GORDON = "gordon"
    EXIT_MULTIPLE = "exit_multiple"


# ── Company Metadata ───────────────────────────────────────────────────────────


class CompanyMetadata(BaseModel):
    """Basic company identification data."""

    model_config = {"frozen": True}

    company_name: str
    ticker: Optional[str] = None
    currency: str = "USD"
    units: str = "millions"  # "millions" | "thousands" | "billions"
    accounting_standard: AccountingStandard = AccountingStandard.UNKNOWN
    fiscal_year_end: str = "December"
    diluted_shares_outstanding: Optional[float] = None
    current_share_price: Optional[float] = None


# ── Income Statement ──────────────────────────────────────────────────────────


class IncomeStatement(BaseModel):
    """Canonical income statement for a single fiscal year."""

    model_config = {"frozen": True}

    year: int
    revenue: float
    cogs: Optional[float] = None
    gross_profit: Optional[float] = None
    sga: Optional[float] = None
    rd_expense: Optional[float] = None
    depreciation: Optional[float] = None
    ebitda: Optional[float] = None
    ebit: Optional[float] = None
    interest_expense: Optional[float] = None
    other_income: Optional[float] = None
    ebt: Optional[float] = None
    tax_expense: Optional[float] = None
    net_income: Optional[float] = None


# ── Balance Sheet ──────────────────────────────────────────────────────────────


class BalanceSheet(BaseModel):
    """Canonical balance sheet for a single fiscal year."""

    model_config = {"frozen": True}

    year: int
    # Assets
    cash: Optional[float] = None
    short_term_investments: Optional[float] = None
    accounts_receivable: Optional[float] = None
    inventory: Optional[float] = None
    other_current_assets: Optional[float] = None
    total_current_assets: Optional[float] = None
    ppe: Optional[float] = None
    goodwill: Optional[float] = None
    intangible_assets: Optional[float] = None
    other_non_current_assets: Optional[float] = None
    total_assets: float

    # Liabilities
    accounts_payable: Optional[float] = None
    short_term_debt: Optional[float] = None
    accrued_liabilities: Optional[float] = None
    other_current_liabilities: Optional[float] = None
    total_current_liabilities: Optional[float] = None
    long_term_debt: Optional[float] = None
    other_non_current_liabilities: Optional[float] = None
    total_liabilities: float

    # Equity
    common_stock: Optional[float] = None
    retained_earnings: Optional[float] = None
    additional_paid_in_capital: Optional[float] = None
    shareholders_equity: float

    @property
    def net_debt(self) -> float:
        """Net Debt = Short Term Debt + Long Term Debt - Cash - Short Term Investments."""
        st_debt = self.short_term_debt or 0.0
        lt_debt = self.long_term_debt or 0.0
        cash = self.cash or 0.0
        st_inv = self.short_term_investments or 0.0
        return st_debt + lt_debt - cash - st_inv


# ── Cash Flow Statement ───────────────────────────────────────────────────────


class CashFlowStatement(BaseModel):
    """Canonical cash flow statement for a single fiscal year."""

    model_config = {"frozen": True}

    year: int
    # Operating
    net_income: Optional[float] = None
    depreciation: Optional[float] = None
    change_in_working_capital: Optional[float] = None
    other_operating: Optional[float] = None
    operating_cash_flow: Optional[float] = None

    # Investing
    capex: Optional[float] = None
    acquisitions: Optional[float] = None
    other_investing: Optional[float] = None
    investing_cash_flow: Optional[float] = None

    # Financing
    debt_issuance: Optional[float] = None
    debt_repayment: Optional[float] = None
    dividends_paid: Optional[float] = None
    share_buybacks: Optional[float] = None
    other_financing: Optional[float] = None
    financing_cash_flow: Optional[float] = None

    # Net
    net_change_in_cash: Optional[float] = None
    beginning_cash: Optional[float] = None
    ending_cash: Optional[float] = None

    @property
    def free_cash_flow(self) -> Optional[float]:
        """FCF = Operating Cash Flow + CapEx (CapEx is negative)."""
        if self.operating_cash_flow is not None and self.capex is not None:
            return self.operating_cash_flow + self.capex
        return None


# ── Container ──────────────────────────────────────────────────────────────────


class FinancialStatements(BaseModel):
    """Complete normalized financial data for a single company across multiple years."""

    metadata: CompanyMetadata
    income_statements: dict[int, IncomeStatement] = Field(default_factory=dict)
    balance_sheets: dict[int, BalanceSheet] = Field(default_factory=dict)
    cash_flows: dict[int, CashFlowStatement] = Field(default_factory=dict)
    warnings: dict[str, Any] = Field(default_factory=dict)

    @property
    def historical_years(self) -> list[int]:
        """All years present in any statement, sorted."""
        years = set()
        years.update(self.income_statements.keys())
        years.update(self.balance_sheets.keys())
        years.update(self.cash_flows.keys())
        return sorted(years)

    @property
    def latest_year(self) -> int:
        """The most recent fiscal year in the data."""
        return max(self.historical_years)

    @property
    def latest_income_statement(self) -> Optional[IncomeStatement]:
        return self.income_statements.get(self.latest_year)

    @property
    def latest_balance_sheet(self) -> Optional[BalanceSheet]:
        return self.balance_sheets.get(self.latest_year)


# ── Validation & Check Results ─────────────────────────────────────────────────


class ValidationReport(BaseModel):
    """Result of data integrity validation."""

    passed: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BalanceCheckResult(BaseModel):
    """Result of balance sheet integrity check."""

    balanced: bool
    delta: float = 0.0
    plug_suggestion: Optional[str] = None
    year: Optional[int] = None


# ── Assumption Set ─────────────────────────────────────────────────────────────


class AssumptionSet(BaseModel):
    """Complete set of modeling assumptions for a valuation."""

    scenario: Scenario = Scenario.BASE
    revenue_growth_rates: list[float] = Field(
        default_factory=lambda: [0.08] * 5,
        description="Growth rates per projection year (decimal)"
    )
    ebitda_margin: float | list[float] = Field(
        default=0.25, description="EBITDA margin (flat or per-year)"
    )
    capex_to_sales: float = Field(default=0.06, description="CapEx as % of revenue")
    da_to_revenue: float = Field(default=0.05, description="D&A as % of revenue")
    nwc_to_revenue: float = Field(default=0.08, description="ΔWC as % of Δrevenue")
    tax_rate: float = Field(default=0.21, description="Effective tax rate")
    terminal_growth_rate: float = Field(default=0.025, description="Terminal growth rate")
    exit_multiple: float = Field(default=12.0, description="EV/EBITDA exit multiple")
    projection_years: int = Field(default=5, description="Number of projection years (5 or 10)")
    wacc: Optional[float] = Field(default=None, description="Override WACC (if pre-computed)")
    mid_year_convention: bool = Field(default=True, description="Use mid-year discounting")


# ── Projection Output ─────────────────────────────────────────────────────────


class ProjectionTable(BaseModel):
    """Projected income statement and UFCF for all forecast years."""

    years: list[int] = Field(default_factory=list)
    revenue: dict[int, float] = Field(default_factory=dict)
    ebitda: dict[int, float] = Field(default_factory=dict)
    da: dict[int, float] = Field(default_factory=dict)
    ebit: dict[int, float] = Field(default_factory=dict)
    nopat: dict[int, float] = Field(default_factory=dict)
    capex: dict[int, float] = Field(default_factory=dict)
    delta_nwc: dict[int, float] = Field(default_factory=dict)
    ufcf: dict[int, float] = Field(default_factory=dict)


# ── WACC Result ────────────────────────────────────────────────────────────────


class WACCResult(BaseModel):
    """Result of WACC calculation."""

    wacc: float
    cost_of_equity: float
    cost_of_debt_after_tax: float
    beta: float
    risk_free_rate: float
    equity_risk_premium: float
    weight_equity: float
    weight_debt: float


# ── DCF / Valuation Result ─────────────────────────────────────────────────────


class DCFResult(BaseModel):
    """Complete DCF valuation result."""

    projection: ProjectionTable = Field(default_factory=ProjectionTable)
    discount_factors: dict[int, float] = Field(default_factory=dict)
    pv_ufcf: dict[int, float] = Field(default_factory=dict)
    sum_pv_ufcf: float = 0.0
    terminal_value_gordon: Optional[float] = None
    terminal_value_exit_multiple: Optional[float] = None
    pv_terminal_value_gordon: Optional[float] = None
    pv_terminal_value_exit_multiple: Optional[float] = None
    enterprise_value_gordon: Optional[float] = None
    enterprise_value_exit_multiple: Optional[float] = None
    net_debt: float = 0.0
    equity_value_gordon: Optional[float] = None
    equity_value_exit_multiple: Optional[float] = None
    implied_price_gordon: Optional[float] = None
    implied_price_exit_multiple: Optional[float] = None
    tv_pct_of_ev_gordon: Optional[float] = None
    tv_pct_of_ev_exit_multiple: Optional[float] = None
    wacc_result: Optional[WACCResult] = None
    assumptions: Optional[AssumptionSet] = None
    warnings: dict[str, Any] = Field(default_factory=dict)


# ── Comps Result ───────────────────────────────────────────────────────────────


class CompData(BaseModel):
    """Financial data for a single comparable company."""

    ticker: str
    company_name: Optional[str] = None
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    revenue_ltm: Optional[float] = None
    ebitda_ltm: Optional[float] = None
    net_income_ltm: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_revenue: Optional[float] = None
    pe_ratio: Optional[float] = None
    ev_ebit: Optional[float] = None
    ev_fcf: Optional[float] = None


class CompsStats(BaseModel):
    """Statistical summary of comparable company multiples."""

    multiples: dict[str, dict[str, Optional[float]]] = Field(default_factory=dict)
    n_companies: int = 0
    n_excluded_outliers: int = 0


class CompsResult(BaseModel):
    """Full comparable company analysis result."""

    comps: list[CompData] = Field(default_factory=list)
    stats: Optional[CompsStats] = None
    implied_ev_ebitda_low: Optional[float] = None
    implied_ev_ebitda_median: Optional[float] = None
    implied_ev_ebitda_high: Optional[float] = None
    implied_ev_revenue_low: Optional[float] = None
    implied_ev_revenue_median: Optional[float] = None
    implied_ev_revenue_high: Optional[float] = None


# ── Transaction Result ─────────────────────────────────────────────────────────


class Transaction(BaseModel):
    """Single precedent transaction."""

    target: str
    acquirer: Optional[str] = None
    date: Optional[str] = None
    enterprise_value: float
    target_revenue: Optional[float] = None
    target_ebitda: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_revenue: Optional[float] = None
    premium_to_unaffected: Optional[float] = None


class TransactionResult(BaseModel):
    """Precedent transaction analysis result."""

    transactions: list[Transaction] = Field(default_factory=list)
    stats: dict[str, dict[str, Optional[float]]] = Field(default_factory=dict)
    implied_ev_ebitda_median: Optional[float] = None
    implied_ev_revenue_median: Optional[float] = None


# ── Sensitivity Output ─────────────────────────────────────────────────────────


class SensitivityOutput(BaseModel):
    """Sensitivity analysis output."""

    wacc_tgr_matrix: Optional[dict] = None
    wacc_em_matrix: Optional[dict] = None
    rev_growth_margin_matrix: Optional[dict] = None
    base_case_value: Optional[float] = None


# ── Full Valuation Result ──────────────────────────────────────────────────────


class ValuationResult(BaseModel):
    """Master result object containing all valuation outputs."""

    metadata: Optional[CompanyMetadata] = None
    normalized: Optional[FinancialStatements] = None
    assumptions: Optional[AssumptionSet] = None
    dcf: Optional[DCFResult] = None
    comps: Optional[CompsResult] = None
    transactions: Optional[TransactionResult] = None
    sensitivity: Optional[SensitivityOutput] = None
    narrative: Optional[dict[str, str]] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
