# 05 — Database Schema
## Financial Modeling & Valuation Agent (FMVA)
**Version:** 1.0  
**Date:** 2026-02-23  
**Owner:** Engineering  
**Note:** v1.0 uses JSON/file-based storage on Google Drive (no relational DB). This document defines the data schemas in both Pydantic (runtime) and JSON Schema (storage/API) formats.

---

## 1. Schema Overview

All data in FMVA is modeled as structured Python objects (Pydantic) that serialize to JSON for Google Drive persistence. The schemas form a directed acyclic graph:

```
CompanyMetadata
      │
      ▼
FinancialStatements (3 historical periods min)
      │
      ▼
AssumptionSet
      │
      ▼
ProjectedStatements (N years)
      │
      ├── DCFResult
      ├── CompsResult
      ├── TransactionResult
      ├── SensitivityOutput
      └── ValuationSummary
              │
              ├── AuditTrail
              └── ExecutiveSummary
```

---

## 2. Core Data Schemas

### 2.1 CompanyMetadata

```python
class CompanyMetadata(BaseModel):
    """Identifies the subject company for the valuation."""
    
    company_name: str
    ticker: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    fiscal_year_end: Optional[str] = None          # e.g., "December", "June"
    reporting_currency: str = "USD"
    currency_units: str = "thousands"              # "thousands", "millions", "actuals"
    shares_outstanding: Optional[float] = None     # Diluted shares (in thousands)
    current_share_price: Optional[float] = None    # For Football Field reference
    valuation_date: date
    prepared_by: Optional[str] = None
    version: str = "1.0"
```

**JSON Storage Example:**
```json
{
  "company_name": "Acme Corp",
  "ticker": "ACME",
  "industry": "SaaS / Enterprise Software",
  "sector": "Technology",
  "fiscal_year_end": "December",
  "reporting_currency": "USD",
  "currency_units": "millions",
  "shares_outstanding": 100.5,
  "current_share_price": 42.50,
  "valuation_date": "2026-02-23",
  "prepared_by": "Alex Chen",
  "version": "1.0"
}
```

---

### 2.2 IncomeStatement

```python
class IncomeStatementPeriod(BaseModel):
    """One period (year/quarter) of income statement data."""
    
    period_label: str                              # "FY2023", "LTM", "FY2024E"
    period_type: Literal["historical", "projected"]
    
    # Revenue
    total_revenue: float
    product_revenue: Optional[float] = None
    service_revenue: Optional[float] = None
    other_revenue: Optional[float] = None
    
    # Costs
    total_cogs: Optional[float] = None
    gross_profit: Optional[float] = None           # Derived if COGS provided
    gross_margin_pct: Optional[float] = None       # Derived
    
    # Operating Expenses
    research_and_development: Optional[float] = None
    sales_and_marketing: Optional[float] = None
    general_and_administrative: Optional[float] = None
    total_opex: Optional[float] = None
    
    # EBITDA
    ebitda: Optional[float] = None
    ebitda_margin_pct: Optional[float] = None      # Derived
    
    # D&A
    depreciation_and_amortization: Optional[float] = None
    
    # EBIT
    ebit: Optional[float] = None
    ebit_margin_pct: Optional[float] = None        # Derived
    
    # Below EBIT
    interest_expense: Optional[float] = None
    interest_income: Optional[float] = None
    other_non_operating: Optional[float] = None
    
    # EBT and Taxes
    ebt: Optional[float] = None
    income_tax_expense: Optional[float] = None
    effective_tax_rate_pct: Optional[float] = None # Derived
    
    # Bottom Line
    net_income: float
    net_income_margin_pct: Optional[float] = None  # Derived
    
    # Quality flags
    flags: List[str] = []                          # e.g., ["EBITDA_NEGATIVE"]
    
    class Config:
        validate_assignment = True
```

---

### 2.3 BalanceSheet

```python
class BalanceSheetPeriod(BaseModel):
    """One period of balance sheet data."""
    
    period_label: str
    period_type: Literal["historical", "projected"]
    
    # Current Assets
    cash_and_equivalents: float
    short_term_investments: Optional[float] = None
    accounts_receivable: Optional[float] = None
    inventory: Optional[float] = None
    prepaid_expenses: Optional[float] = None
    other_current_assets: Optional[float] = None
    total_current_assets: float                    # Required (summed or provided)
    
    # Non-Current Assets
    property_plant_equipment_gross: Optional[float] = None
    accumulated_depreciation: Optional[float] = None
    net_ppe: Optional[float] = None               # Derived if gross+accum provided
    goodwill: Optional[float] = None
    intangible_assets: Optional[float] = None
    long_term_investments: Optional[float] = None
    other_non_current_assets: Optional[float] = None
    total_non_current_assets: Optional[float] = None
    
    total_assets: float                            # Required
    
    # Current Liabilities
    accounts_payable: Optional[float] = None
    accrued_liabilities: Optional[float] = None
    short_term_debt: Optional[float] = None
    deferred_revenue_current: Optional[float] = None
    other_current_liabilities: Optional[float] = None
    total_current_liabilities: Optional[float] = None
    
    # Non-Current Liabilities
    long_term_debt: float                          # Required for net debt calc
    deferred_tax_liabilities: Optional[float] = None
    deferred_revenue_long_term: Optional[float] = None
    other_non_current_liabilities: Optional[float] = None
    total_non_current_liabilities: Optional[float] = None
    
    total_liabilities: Optional[float] = None
    
    # Equity
    common_stock: Optional[float] = None
    additional_paid_in_capital: Optional[float] = None
    retained_earnings: float                       # Required
    accumulated_other_comprehensive_income: Optional[float] = None
    treasury_stock: Optional[float] = None
    total_equity: float                            # Required
    
    total_liabilities_and_equity: Optional[float] = None  # Derived
    
    # Derived: Net Debt
    net_debt: Optional[float] = None              # Derived: Total Debt - Cash
    
    # Integrity
    balance_check_pass: Optional[bool] = None
    balance_check_delta: Optional[float] = None   # Assets - (L+E)
    flags: List[str] = []
```

---

### 2.4 CashFlowStatement

```python
class CashFlowPeriod(BaseModel):
    """One period of cash flow statement data."""
    
    period_label: str
    period_type: Literal["historical", "projected"]
    
    # Operating Activities
    net_income: float                              # Links to IS
    add_back_da: Optional[float] = None
    change_in_accounts_receivable: Optional[float] = None
    change_in_inventory: Optional[float] = None
    change_in_accounts_payable: Optional[float] = None
    change_in_other_working_capital: Optional[float] = None
    other_operating_activities: Optional[float] = None
    cash_from_operations: float                    # CFO
    
    # Investing Activities
    capital_expenditures: float                    # CapEx (negative value)
    acquisitions: Optional[float] = None
    asset_sales: Optional[float] = None
    other_investing_activities: Optional[float] = None
    cash_from_investing: float                     # CFI
    
    # Financing Activities
    debt_issuance: Optional[float] = None
    debt_repayment: Optional[float] = None
    equity_issuance: Optional[float] = None
    dividends_paid: Optional[float] = None
    share_repurchases: Optional[float] = None
    other_financing_activities: Optional[float] = None
    cash_from_financing: float                     # CFF
    
    # Reconciliation
    beginning_cash: Optional[float] = None
    net_change_in_cash: Optional[float] = None    # Derived: CFO + CFI + CFF
    ending_cash: Optional[float] = None           # Derived; must = BS cash
    
    # Integrity
    cfs_balance_check_pass: Optional[bool] = None
    cfs_balance_check_delta: Optional[float] = None
    flags: List[str] = []
```

---

### 2.5 FinancialStatements (Container)

```python
class FinancialStatements(BaseModel):
    """Container for all three financial statements across all periods."""
    
    metadata: CompanyMetadata
    income_statements: List[IncomeStatementPeriod]   # Sorted chronologically
    balance_sheets: List[BalanceSheetPeriod]
    cash_flow_statements: List[CashFlowPeriod]
    
    # Field-level audit: tracks which fields were auto-mapped vs. provided
    field_provenance: Dict[str, Literal["provided", "derived", "estimated", "missing"]] = {}
    normalization_warnings: List[str] = []
    
    @property
    def periods(self) -> List[str]:
        return [is_.period_label for is_ in self.income_statements]
    
    @property
    def latest_period(self) -> str:
        return self.income_statements[-1].period_label
```

---

### 2.6 AssumptionSet

```python
class AssumptionSet(BaseModel):
    """All driver assumptions for the projection model."""
    
    name: str = "Base Case"
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Revenue Projections
    revenue_growth_stage1_pct: float = 10.0        # Years 1-5 (%)
    revenue_growth_stage2_pct: float = 5.0         # Years 6-10 (%)
    projection_years_stage1: int = 5
    projection_years_stage2: int = 5               # 0 to skip stage 2
    
    # Margin Assumptions
    ebitda_margin_pct: float = 20.0                # % of Revenue
    da_pct_revenue: float = 3.0                    # D&A as % of Revenue
    
    # Capital & Working Capital
    capex_pct_revenue: float = 5.0                 # CapEx as % of Revenue
    nwc_change_pct_revenue: float = 2.0            # ΔNWC as % of Revenue
    
    # Tax
    effective_tax_rate_pct: float = 21.0
    
    # DCF Parameters
    wacc_pct: float = 10.0                         # Weighted Average Cost of Capital
    terminal_growth_rate_pct: float = 2.5          # Gordon Growth
    exit_multiple_ev_ebitda: float = 10.0          # Exit Multiple TV
    terminal_value_method: Literal["both", "gordon_growth", "exit_multiple"] = "both"
    
    # Sensitivity Ranges
    wacc_sensitivity_range: List[float] = [8.0, 9.0, 10.0, 11.0, 12.0]
    tgr_sensitivity_range: List[float] = [1.5, 2.0, 2.5, 3.0, 3.5]
    exit_multiple_sensitivity_range: List[float] = [7.0, 9.0, 10.0, 12.0, 14.0]
    
    class Config:
        validate_assignment = True
    
    @validator('wacc_pct', 'terminal_growth_rate_pct')
    def validate_wacc_gt_tgr(cls, v, values):
        if 'terminal_growth_rate_pct' in values and 'wacc_pct' in values:
            if values.get('wacc_pct', 100) <= values.get('terminal_growth_rate_pct', 0):
                raise ValueError("WACC must be greater than Terminal Growth Rate")
        return v
```

---

### 2.7 UFCFProjection

```python
class UFCFYearData(BaseModel):
    """UFCF computation for a single projected year."""
    
    year: int                                       # 1-10
    period_label: str                               # "Year 1", "FY2027E"
    
    # Inputs
    revenue: float
    ebitda: float
    ebitda_margin_pct: float
    da: float
    ebit: float
    nopat: float                                    # EBIT × (1 - Tax Rate)
    capex: float                                    # Negative value
    delta_nwc: float                                # Positive = use of cash
    
    # Output
    ufcf: float                                     # NOPAT + D&A - CapEx - ΔNWC
    
    # Discounting
    discount_factor: float                          # 1 / (1 + WACC)^year
    pv_ufcf: float                                  # UFCF × Discount Factor
    
    # Audit trace
    formula: str = "UFCF = NOPAT + D&A - CapEx - ΔNWC"
    audit_entries: List[AuditEntry] = []
```

---

### 2.8 DCFResult

```python
class TerminalValueResult(BaseModel):
    tv_gordon_growth: Optional[float] = None
    tv_exit_multiple: Optional[float] = None
    pv_tv_gordon_growth: Optional[float] = None
    pv_tv_exit_multiple: Optional[float] = None
    tv_as_pct_ev_gg: Optional[float] = None
    tv_as_pct_ev_em: Optional[float] = None
    tv_high_warning: bool = False                   # True if TV > 80% of EV

class DCFResult(BaseModel):
    """Full DCF valuation output."""
    
    # UFCF Projections
    ufcf_by_year: List[UFCFYearData]
    sum_pv_ufcf: float
    
    # Terminal Value
    terminal_value: TerminalValueResult
    
    # Enterprise Value Bridge
    enterprise_value_gg: Optional[float] = None    # EV using GG terminal value
    enterprise_value_em: Optional[float] = None    # EV using EM terminal value
    
    # Equity Value Bridge
    total_debt: float
    cash_and_equivalents: float
    net_debt: float                                 # Total Debt - Cash
    minority_interest: float = 0.0
    preferred_equity: float = 0.0
    
    equity_value_gg: Optional[float] = None
    equity_value_em: Optional[float] = None
    
    # Per Share
    diluted_shares_outstanding: float
    implied_price_gg: Optional[float] = None
    implied_price_em: Optional[float] = None
    
    # Assumptions used (snapshot for audit)
    wacc_used: float
    tgr_used: float
    exit_multiple_used: float
    tax_rate_used: float
    projection_years: int
    
    # Errors
    gordon_growth_error: Optional[str] = None
    flags: List[str] = []
```

---

### 2.9 CompsResult

```python
class CompanyComps(BaseModel):
    """Single comparable company data."""
    
    company_name: str
    ticker: Optional[str] = None
    
    # Market Data
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    
    # LTM Financials
    ltm_revenue: float
    ltm_ebitda: Optional[float] = None
    ltm_ebit: Optional[float] = None
    ltm_net_income: Optional[float] = None
    ltm_fcf: Optional[float] = None
    
    # Computed Multiples
    ev_to_revenue: Optional[float] = None          # Derived
    ev_to_ebitda: Optional[float] = None           # Derived
    ev_to_ebit: Optional[float] = None             # Derived
    pe_ratio: Optional[float] = None               # Derived
    ev_to_fcf: Optional[float] = None              # Derived
    
    is_outlier: bool = False
    outlier_reason: Optional[str] = None

class PeerSetStatistics(BaseModel):
    """Statistical summary of the peer set multiples."""
    
    metric: str
    mean: float
    median: float
    p25: float
    p75: float
    min: float
    max: float
    n_companies: int
    n_excluded_outliers: int = 0

class CompsResult(BaseModel):
    """Full comps analysis output."""
    
    companies: List[CompanyComps]
    peer_statistics: List[PeerSetStatistics]
    
    # Implied Valuation Range for Subject Company
    implied_ev_range_low: float                    # Based on 25th pct multiples
    implied_ev_range_high: float                   # Based on 75th pct multiples
    implied_ev_median: float
    
    implied_equity_value_range_low: float
    implied_equity_value_range_high: float
    implied_equity_value_median: float
    
    implied_price_range_low: Optional[float] = None
    implied_price_range_high: Optional[float] = None
    implied_price_median: Optional[float] = None
```

---

### 2.10 SensitivityOutput

```python
class SensitivityMatrix(BaseModel):
    """2D sensitivity matrix output."""
    
    row_variable: str                              # e.g., "WACC"
    col_variable: str                              # e.g., "Terminal Growth Rate"
    row_values: List[float]
    col_values: List[float]
    output_metric: str                             # "Implied Price Per Share", "Enterprise Value"
    
    # Matrix data: dict of {row_value: {col_value: output_value}}
    # None values indicate invalid combinations (e.g., WACC <= TGR)
    matrix: Dict[str, Dict[str, Optional[float]]]
    
    base_case_row: float                           # Highlighted cell
    base_case_col: float

class FootballFieldBar(BaseModel):
    """Single bar in a football field chart."""
    
    methodology: str                               # "DCF (Gordon Growth)", "Trading Comps"
    low: float                                     # Low end of range
    high: float                                    # High end of range
    base_case: Optional[float] = None

class SensitivityOutput(BaseModel):
    """Full sensitivity analysis output."""
    
    wacc_vs_tgr_matrix: SensitivityMatrix
    wacc_vs_exit_multiple_matrix: SensitivityMatrix
    
    football_field: List[FootballFieldBar]
    current_price: Optional[float] = None         # Reference point
```

---

### 2.11 AuditEntry & AuditTrail

```python
class AuditEntry(BaseModel):
    """A single auditable computation record."""
    
    entry_id: str                                  # UUID
    timestamp: datetime
    
    output_field: str                              # e.g., "ufcf_year_3"
    formula: str                                   # e.g., "NOPAT + D&A - CapEx - ΔNWC"
    
    # Source values with labels
    input_values: Dict[str, float]                 # e.g., {"NOPAT": 11.85, "D&A": 5.0}
    input_sources: Dict[str, str]                  # e.g., {"NOPAT": "dcf.year3.nopat"}
    
    result: float
    
    # For derived fields: what formula step this is
    computation_step: Optional[str] = None
    notes: Optional[str] = None

class IntegrityCheckResult(BaseModel):
    """Result of a single integrity check."""
    
    check_name: str                                # "BS_CHECK", "CFS_CHECK"
    period_label: str
    passed: bool
    delta: Optional[float] = None                  # Discrepancy amount
    suggested_plug: Optional[str] = None
    details: Optional[str] = None

class AuditTrail(BaseModel):
    """Complete audit trail for the entire valuation."""
    
    valuation_id: str                              # UUID for this run
    company_name: str
    generated_at: datetime
    
    # Computation audit entries
    entries: List[AuditEntry]
    
    # Integrity check results
    integrity_checks: List[IntegrityCheckResult]
    
    # Summary stats
    total_computations: int
    total_integrity_checks: int
    all_integrity_checks_passed: bool
    
    # Warning and error log
    warnings: List[str]
    errors: List[str]
    
    @property
    def coverage_pct(self) -> float:
        """% of output fields with audit trail entries."""
        return 100.0  # Must always be 100%
```

---

### 2.12 ValuationSummary

```python
class ValuationSummary(BaseModel):
    """Master valuation output — feeds both export engines and LLM narrative."""
    
    # Identity
    valuation_id: str
    company_name: str
    valuation_date: date
    
    # DCF Summary
    dcf_implied_price_gg: Optional[float] = None
    dcf_implied_price_em: Optional[float] = None
    dcf_ev_gg: Optional[float] = None
    dcf_ev_em: Optional[float] = None
    
    # Comps Summary
    comps_implied_price_low: Optional[float] = None
    comps_implied_price_high: Optional[float] = None
    
    # Transaction Summary
    transactions_implied_price_low: Optional[float] = None
    transactions_implied_price_high: Optional[float] = None
    
    # Blended Range (Football Field min/max)
    overall_value_range_low: float
    overall_value_range_high: float
    current_share_price: Optional[float] = None
    
    # Implied upside/downside
    implied_upside_pct_low: Optional[float] = None
    implied_upside_pct_high: Optional[float] = None
    
    # Key metrics for narrative
    revenue_cagr_projected: float
    ebitda_margin_final_year: float
    wacc_used: float
    tgr_used: float
    
    # Narrative
    executive_summary: Optional[str] = None        # LLM-generated
    headline: Optional[str] = None                 # One-sentence summary
    
    # References to full result objects
    dcf_result: Optional[DCFResult] = None
    comps_result: Optional[CompsResult] = None
    sensitivity_output: Optional[SensitivityOutput] = None
    audit_trail: Optional[AuditTrail] = None
```

---

## 3. Training Data Schema (Unsloth Fine-tuning)

### 3.1 Instruction-Tuning Format (Alpaca)

All fine-tuning examples follow the Alpaca instruction format stored as JSONL:

```json
{
  "instruction": "Generate a professional investment banking executive summary for the following company valuation. Write in the style of a top-tier investment bank pitch book narrative.",
  "input": "Company: Acme Corp (SaaS)\nValuation Date: 2026-02-23\nDCF Implied Share Price (Gordon Growth): $57.00\nDCF Implied Share Price (Exit Multiple): $61.50\nTrading Comps Range: $48.00 - $65.00\nCurrent Share Price: $42.50\nImplied Upside: 23% - 53%\nRevenue CAGR (5-year): 18.5%\nEBITDA Margin (Year 5): 28%\nWACC: 10%\nTerminal Growth Rate: 2.5%\nKey Risk: High customer concentration (top 5 = 40% of revenue)\nKey Driver: Expanding margins from SaaS operating leverage",
  "output": "Acme Corp represents a compelling investment opportunity at current trading levels, with our multi-methodology valuation analysis yielding an implied equity value range of $48–$65 per share, representing 13–53% upside to the current price of $42.50.\n\nOur DCF analysis, underpinned by a 10% WACC and 2.5% terminal growth rate, implies an intrinsic value of $57.00–$61.50 per share using Gordon Growth and Exit Multiple approaches respectively. The valuation is primarily driven by the company's robust top-line trajectory — an 18.5% revenue CAGR over our five-year forecast period — combined with significant EBITDA margin expansion from current levels to an estimated 28% in Year 5, as SaaS operating leverage accrues from the fixed-cost structure of the business.\n\nOur trading comps analysis, anchored against a peer set of comparable high-growth enterprise software companies, corroborates this range at $48–$65 per share on median EV/NTM Revenue and EV/NTM EBITDA multiples.\n\nThe primary risk to our thesis is customer concentration: the top five customers represent approximately 40% of annual recurring revenue, creating meaningful churn sensitivity. Additionally, our valuation is predicated on sustained above-market growth, which may prove challenging if macroeconomic conditions deteriorate or competitive dynamics intensify.\n\nWe value Acme Corp at $48–$65 per share, implying 13–53% upside, and recommend further due diligence to validate the customer expansion pipeline."
}
```

### 3.2 Training Data Quality Criteria

Each training example must meet:
- `instruction` field: Clear, specific task definition
- `input` field: Structured valuation data (all numbers must be explicitly provided — no ambiguity)
- `output` field: Professional narrative; all numbers in output must appear verbatim from input (no hallucination)
- Length: Output between 250–600 words
- Diversity: Cover Technology, Healthcare, Consumer, Industrials, Energy sectors
- Coverage: Include bull/bear/base cases; pre-profitability and mature companies

---

## 4. File Storage Schema

### 4.1 Output JSON Schema

The final `{company}_{date}_valuation.json` follows this top-level structure:

```json
{
  "schema_version": "1.0",
  "valuation_id": "uuid-here",
  "generated_at": "2026-02-23T14:30:00Z",
  "metadata": { ... },
  "financial_statements": {
    "historical": { ... },
    "projected": { ... }
  },
  "assumptions": { ... },
  "valuation": {
    "dcf": { ... },
    "comps": { ... },
    "transactions": { ... },
    "sensitivity": { ... },
    "summary": { ... }
  },
  "audit_trail": { ... }
}
```

---

*Document Owner: Engineering | Last Updated: 2026-02-23*
