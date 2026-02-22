# 06 — API Contracts
## Financial Modeling & Valuation Agent (FMVA)
**Version:** 1.0  
**Date:** 2026-02-23  
**Owner:** Engineering  
**Note:** v1.0 APIs are Python function interfaces (not REST). This document specifies the function signatures, inputs, outputs, and contracts for every public module interface. These contracts enable a v2.0 migration to REST/GraphQL without refactoring module logic.

---

## 1. API Design Principles

- **All functions return typed Python objects** (Pydantic models or primitives)
- **All errors are explicit exceptions** — never silent failures
- **All computation functions are pure** — same inputs always produce same outputs (no side effects)
- **Audit trail is always generated** — no computation function bypasses audit recording
- **The LLM is never called for numerical computation** — only for narrative text

---

## 2. Core Module APIs

### 2.1 `fmva.core.ingestion`

```python
def read_financial_data(
    file_path: str,
    format: Literal["csv", "json", "auto"] = "auto",
    encoding: str = "utf-8",
    currency: str = "USD",
    currency_units: Literal["actuals", "thousands", "millions"] = "thousands"
) -> RawFinancialData:
    """
    Reads raw financial data from a file and returns an unprocessed 
    container for normalization.
    
    Args:
        file_path: Absolute path to the input file (Google Drive path)
        format: File format ("csv", "json", or "auto" to detect)
        encoding: File encoding (default: utf-8)
        currency: Reporting currency (default: USD)
        currency_units: Scale of reported numbers
    
    Returns:
        RawFinancialData: Container with raw tables and detected format info
    
    Raises:
        DataIngestionError: If file cannot be read or parsed
        FileNotFoundError: If file_path does not exist
    
    Example:
        data = read_financial_data(
            "/content/drive/MyDrive/FMVA/inputs/acme_financials.csv",
            format="csv"
        )
    """

def read_financial_data_from_dict(
    data: Dict[str, Any],
    currency: str = "USD",
    currency_units: str = "thousands"
) -> RawFinancialData:
    """
    Accepts raw financial data as a Python dict (for programmatic use).
    
    Args:
        data: Dict conforming to FMVA raw input schema
        currency: Reporting currency
        currency_units: Scale of reported numbers
    
    Returns:
        RawFinancialData
    
    Raises:
        DataIngestionError: If dict structure is invalid
    """
```

---

### 2.2 `fmva.core.normalization`

```python
def normalize_financial_data(
    raw_data: RawFinancialData,
    metadata: CompanyMetadata,
    field_map_override: Optional[Dict[str, str]] = None,
    strict_mode: bool = False
) -> FinancialStatements:
    """
    Normalizes raw financial data into the canonical 3-statement format.
    
    Args:
        raw_data: Output from read_financial_data()
        metadata: Company metadata (name, ticker, fiscal year end, etc.)
        field_map_override: Optional custom field label → canonical name mappings
                           Merged with default field_map.json (user mappings take precedence)
        strict_mode: If True, raises error on any unmapped field.
                     If False, flags unmapped fields as REVIEW_REQUIRED.
    
    Returns:
        FinancialStatements: Canonical 3-statement model
    
    Raises:
        NormalizationError: If critical required fields cannot be mapped
        ValidationError: If mapped values fail type/range validation
    
    Contract:
        - total_revenue must always be successfully mapped (critical field)
        - net_income must always be successfully mapped (critical field)
        - All mapped values preserve original numeric precision
        - All unmapped fields appear in FinancialStatements.normalization_warnings
    
    Example:
        statements = normalize_financial_data(
            raw_data=raw_data,
            metadata=CompanyMetadata(company_name="Acme Corp", valuation_date=date.today()),
            field_map_override={"Net Sales": "total_revenue"}
        )
    """

def get_field_map() -> Dict[str, List[str]]:
    """
    Returns the full label mapping registry.
    
    Returns:
        Dict mapping canonical names to lists of known aliases.
        e.g., {"total_revenue": ["Net Sales", "Revenue", "Net Revenue", ...]}
    """

def validate_statements(
    statements: FinancialStatements
) -> List[str]:
    """
    Validates a normalized FinancialStatements object.
    
    Returns:
        List of warning strings (empty list = fully valid)
    
    Raises:
        ValidationError: If any critical field is missing or invalid
    """
```

---

### 2.3 `fmva.engines.assumptions`

```python
def create_assumption_set(
    name: str = "Base Case",
    **overrides
) -> AssumptionSet:
    """
    Creates a new AssumptionSet, starting from defaults and applying overrides.
    
    Args:
        name: Human-readable name for this scenario
        **overrides: Any AssumptionSet field as keyword argument
    
    Returns:
        AssumptionSet: Validated assumption set
    
    Raises:
        ValidationError: If any override violates bounds or constraints
        ValueError: If WACC <= Terminal Growth Rate
    
    Example:
        bull_case = create_assumption_set(
            name="Bull Case",
            revenue_growth_stage1_pct=30.0,
            ebitda_margin_pct=35.0,
            wacc_pct=9.0
        )
    """

def save_assumption_set(
    assumptions: AssumptionSet,
    drive_folder: str = "/content/drive/MyDrive/FMVA/assumptions/"
) -> str:
    """
    Saves assumption set to Google Drive as JSON.
    
    Returns:
        str: Full path to saved file
    
    Raises:
        IOError: If Drive is not mounted or folder doesn't exist
    """

def load_assumption_set(
    name: str,
    drive_folder: str = "/content/drive/MyDrive/FMVA/assumptions/"
) -> AssumptionSet:
    """
    Loads a named assumption set from Google Drive.
    
    Raises:
        FileNotFoundError: If assumption set doesn't exist
        ValidationError: If loaded data fails Pydantic validation
    """

def list_assumption_sets(
    drive_folder: str = "/content/drive/MyDrive/FMVA/assumptions/"
) -> List[str]:
    """Returns list of saved assumption set names."""
```

---

### 2.4 `fmva.engines.projection`

```python
def project_income_statement(
    base_statements: FinancialStatements,
    assumptions: AssumptionSet,
    audit_trail: AuditTrail
) -> List[IncomeStatementPeriod]:
    """
    Projects the income statement for N years based on assumptions.
    
    Args:
        base_statements: Historical statements (normalization output)
        assumptions: Driver assumptions
        audit_trail: Audit trail object — function MUST record every computation
    
    Returns:
        List of IncomeStatementPeriod objects (one per projected year)
    
    Contract:
        - Revenue projection: LTM_Revenue × (1 + growth_stage1)^year for years 1-5
        - Revenue projection: Year5_Revenue × (1 + growth_stage2)^(year-5) for years 6-10
        - EBITDA = Revenue × ebitda_margin_pct
        - D&A = Revenue × da_pct_revenue
        - EBIT = EBITDA - D&A
        - All intermediate computations recorded to audit_trail
    
    Raises:
        ValueError: If base statements don't have at least 1 historical period
    """

def project_balance_sheet(
    base_statements: FinancialStatements,
    projected_is: List[IncomeStatementPeriod],
    assumptions: AssumptionSet,
    audit_trail: AuditTrail
) -> List[BalanceSheetPeriod]:
    """
    Projects the balance sheet for N years.
    
    Contract:
        - Cash is the plug (balancing item)
        - PP&E rolls forward: Prior PP&E + CapEx - D&A
        - Retained Earnings rolls forward: Prior RE + Net Income - Dividends
        - After projection: run integrity check automatically
        - If BS doesn't balance: flag but do not raise (allow user to review)
    """

def project_cash_flow_statement(
    projected_is: List[IncomeStatementPeriod],
    projected_bs: List[BalanceSheetPeriod],
    assumptions: AssumptionSet,
    audit_trail: AuditTrail
) -> List[CashFlowPeriod]:
    """
    Derives the projected cash flow statement from IS and BS changes.
    
    Contract:
        - CFO = Net Income + D&A + ΔNWC
        - CFI = -CapEx (plus any other investing items)
        - CFF = Debt changes + Equity changes - Dividends
        - Ending Cash = Beginning Cash + CFO + CFI + CFF
        - Ending Cash must reconcile to BS Cash (flag if not)
    """

def build_projected_statements(
    base_statements: FinancialStatements,
    assumptions: AssumptionSet
) -> Tuple[ProjectedStatements, AuditTrail]:
    """
    Orchestration function: builds all three projected statements.
    Creates and returns a fresh AuditTrail.
    
    Returns:
        Tuple of (ProjectedStatements, AuditTrail)
    
    This is the primary entry point for the projection module.
    """
```

---

### 2.5 `fmva.engines.dcf`

```python
def calculate_ufcf(
    year: int,
    ebit: float,
    tax_rate_pct: float,
    da: float,
    capex: float,
    delta_nwc: float,
    audit_trail: AuditTrail
) -> UFCFYearData:
    """
    Calculates Unlevered Free Cash Flow for a single year.
    
    Formula: UFCF = NOPAT + D&A - CapEx - ΔNWC
    Where:   NOPAT = EBIT × (1 - tax_rate)
    
    All values in same currency units as input statements.
    
    Contract:
        - Negative UFCF is valid (not clamped to zero)
        - Every intermediate step recorded to audit_trail
        - capex input should be a negative number (cash outflow)
    """

def calculate_terminal_value_gordon_growth(
    ufcf_final_year: float,
    wacc_pct: float,
    tgr_pct: float,
    audit_trail: AuditTrail
) -> float:
    """
    Calculates Terminal Value using Gordon Growth Model.
    
    Formula: TV = UFCF_final × (1 + TGR) / (WACC - TGR)
    
    Raises:
        GordonGrowthError: If WACC <= TGR
    
    Returns:
        float: Terminal Value (undicounted, at end of projection period)
    """

def calculate_terminal_value_exit_multiple(
    ebitda_final_year: float,
    exit_multiple: float,
    audit_trail: AuditTrail
) -> float:
    """
    Calculates Terminal Value using Exit Multiple Method.
    
    Formula: TV = EBITDA_final × Exit_Multiple
    
    Returns:
        float: Terminal Value (undiscounted)
    """

def discount_value(
    future_value: float,
    wacc_pct: float,
    year: int
) -> Tuple[float, float]:
    """
    Discounts a future value to present value.
    
    Returns:
        Tuple of (discount_factor, present_value)
    
    Formula: PV = FV / (1 + WACC)^year
    """

def calculate_enterprise_value(
    pv_ufcfs: List[float],
    pv_terminal_value: float
) -> float:
    """
    Enterprise Value = Sum(PV_UFCFs) + PV_Terminal_Value
    """

def calculate_equity_value(
    enterprise_value: float,
    total_debt: float,
    cash: float,
    minority_interest: float = 0.0,
    preferred_equity: float = 0.0
) -> float:
    """
    Equity Value = EV - Total Debt + Cash - Minority Interest - Preferred Equity
    """

def run_dcf(
    projected_statements: ProjectedStatements,
    assumptions: AssumptionSet,
    metadata: CompanyMetadata,
    audit_trail: AuditTrail
) -> DCFResult:
    """
    Orchestration function: runs complete DCF valuation.
    
    This is the primary entry point for the DCF module.
    
    Contract:
        - Always computes both GG and Exit Multiple TV (unless GG errors)
        - Flags TV_HIGH_WARNING if TV > 80% of EV
        - All computations recorded to audit_trail
        - Never modifies input objects
    
    Returns:
        DCFResult with all EV/equity/price calculations
    """
```

---

### 2.6 `fmva.engines.comps`

```python
def analyze_comps(
    subject_company: CompanyMetadata,
    subject_financials: FinancialStatements,
    comparable_companies: List[CompanyComps],
    audit_trail: AuditTrail,
    outlier_threshold_sigma: float = 2.0,
    exclude_outliers_from_stats: bool = False
) -> CompsResult:
    """
    Runs comparable company (trading comps) analysis.
    
    Args:
        subject_company: The company being valued
        subject_financials: Subject company's normalized statements
        comparable_companies: List of comp company data
        audit_trail: Audit trail to record to
        outlier_threshold_sigma: σ threshold for outlier flagging (default 2.0)
        exclude_outliers_from_stats: Whether to exclude outliers from median/mean
    
    Returns:
        CompsResult with multiples table and implied valuation range
    
    Contract:
        - EV/EBITDA only computed if EBITDA is provided and positive
        - P/E only computed if Net Income is positive
        - Subject company multiples computed but not included in peer statistics
        - Implied value range uses 25th-75th percentile band
    """

def build_comps_from_dict(
    comp_data_list: List[Dict[str, Any]]
) -> List[CompanyComps]:
    """
    Helper to construct CompanyComps objects from raw dict inputs.
    
    Computes all derived multiples if EV and financial data are provided.
    """
```

---

### 2.7 `fmva.engines.sensitivity`

```python
def generate_wacc_tgr_matrix(
    dcf_function: Callable,
    base_dcf_inputs: Dict[str, Any],
    wacc_range: List[float],
    tgr_range: List[float],
    output_metric: Literal["implied_price_gg", "enterprise_value_gg"] = "implied_price_gg"
) -> SensitivityMatrix:
    """
    Generates a WACC vs. Terminal Growth Rate sensitivity matrix.
    
    Args:
        dcf_function: Reference to run_dcf() or equivalent callable
        base_dcf_inputs: Base case inputs dict (WACC and TGR will be overridden)
        wacc_range: List of WACC values (e.g., [8.0, 9.0, 10.0, 11.0, 12.0])
        tgr_range: List of TGR values (e.g., [1.5, 2.0, 2.5, 3.0, 3.5])
        output_metric: Which output metric to populate the matrix with
    
    Returns:
        SensitivityMatrix with len(wacc_range) × len(tgr_range) cells
    
    Contract:
        - If WACC <= TGR for any cell: cell value = None
        - Matrix is always fully computed (no early exits)
        - Base case cell is identified in returned object
    """

def generate_football_field(
    dcf_result: Optional[DCFResult] = None,
    comps_result: Optional[CompsResult] = None,
    transactions_result: Optional[TransactionResult] = None,
    current_share_price: Optional[float] = None
) -> List[FootballFieldBar]:
    """
    Generates football field chart data from all available valuation methodologies.
    
    At least one result object must be non-None.
    
    Returns:
        List of FootballFieldBar objects (one per methodology)
        Sorted by methodology name for consistent ordering
    """
```

---

### 2.8 `fmva.integrity.checker`

```python
def check_balance_sheet(
    balance_sheet_periods: List[BalanceSheetPeriod],
    tolerance: float = 0.01
) -> List[IntegrityCheckResult]:
    """
    Checks that Assets = Liabilities + Equity for each period.
    
    Args:
        balance_sheet_periods: List of projected balance sheet periods
        tolerance: Acceptable rounding tolerance in same units as data
    
    Returns:
        List of IntegrityCheckResult (one per period)
    
    Contract:
        - Check: Total Assets == Total Liabilities + Total Equity (within tolerance)
        - If fail: compute delta = Total Assets - (Total Liabilities + Total Equity)
        - Suggest plug: if delta > 0: "Add to Cash (+{delta})"; if delta < 0: "Reduce Cash (-{abs(delta)})"
        - Does NOT automatically apply plug — only suggests
    
    Raises:
        Nothing — returns results, caller decides whether to block
    """

def check_cfs_reconciliation(
    cfs_periods: List[CashFlowPeriod],
    bs_periods: List[BalanceSheetPeriod],
    tolerance: float = 0.01
) -> List[IntegrityCheckResult]:
    """
    Checks that CFS ending cash reconciles to Balance Sheet cash.
    
    Contract:
        - Check: CFS.ending_cash == BS.cash_and_equivalents for each period
        - If fail: show delta and suggest reviewing: beginning cash, financing items
    """

def run_all_integrity_checks(
    projected_statements: ProjectedStatements,
    tolerance: float = 0.01
) -> Tuple[bool, List[IntegrityCheckResult]]:
    """
    Runs all integrity checks and returns consolidated results.
    
    Returns:
        Tuple of (all_passed: bool, results: List[IntegrityCheckResult])
    
    Contract:
        - all_passed is True ONLY if every individual check passes
        - Caller should block downstream computation if all_passed is False
    """
```

---

### 2.9 `fmva.integrity.audit_trail`

```python
def create_audit_trail(
    valuation_id: str,
    company_name: str
) -> AuditTrail:
    """Creates a fresh, empty AuditTrail object for a new valuation run."""

def record(
    audit_trail: AuditTrail,
    output_field: str,
    formula: str,
    input_values: Dict[str, float],
    result: float,
    input_sources: Optional[Dict[str, str]] = None,
    notes: Optional[str] = None
) -> None:
    """
    Records a computation to the audit trail.
    
    This function is called internally by all computation functions.
    Do NOT skip this call — it is required for audit trail completeness.
    
    Args:
        output_field: Name of the computed field (e.g., "ufcf_year_3")
        formula: Human-readable formula string
        input_values: Dict of input name → value used in computation
        result: The computed result value
        input_sources: Optional dict of input name → source field path
        notes: Optional explanatory note
    """

def finalize_audit_trail(
    audit_trail: AuditTrail,
    integrity_results: List[IntegrityCheckResult]
) -> AuditTrail:
    """
    Finalizes the audit trail: adds integrity check results, computes summary stats.
    Call this once after all computations are complete.
    
    Returns:
        Updated AuditTrail ready for export
    """
```

---

### 2.10 `fmva.export.excel_exporter`

```python
def export_to_excel(
    valuation_summary: ValuationSummary,
    projected_statements: ProjectedStatements,
    dcf_result: Optional[DCFResult] = None,
    comps_result: Optional[CompsResult] = None,
    sensitivity_output: Optional[SensitivityOutput] = None,
    audit_trail: Optional[AuditTrail] = None,
    output_path: str = "/content/drive/MyDrive/FMVA/outputs/",
    filename: Optional[str] = None
) -> str:
    """
    Exports complete valuation model to formatted .xlsx file.
    
    Args:
        valuation_summary: Master summary object
        projected_statements: 3-statement projections
        output_path: Google Drive folder path
        filename: If None, auto-generates as {company}_{date}_valuation.xlsx
    
    Returns:
        str: Full path to generated Excel file
    
    Contract:
        - File opens without errors in Excel 365 and Google Sheets
        - Sheets generated: Cover, 3-Statement, DCF, Comps, Sensitivity, Audit Trail
        - Missing data (e.g., no comps) results in sheet labeled "N/A — Not Provided"
        - Color coding: blue = inputs, black = formulas, green = outputs
        - No VBA macros (openpyxl only)
    
    Raises:
        ExportError: If file cannot be written to Drive
    """
```

---

### 2.11 `fmva.llm.inference`

```python
def load_model(
    model_path: str = "HuggingFace_Repo/fmva-lora-adapter",
    base_model: str = "mistralai/Mistral-7B-Instruct-v0.3",
    load_in_4bit: bool = True,
    device: str = "cuda"
) -> Tuple[Any, Any]:
    """
    Loads the fine-tuned FMVA model using Unsloth.
    
    Returns:
        Tuple of (model, tokenizer) ready for inference
    
    Raises:
        LLMError.OOMError: If GPU memory insufficient
        FileNotFoundError: If model_path doesn't exist
    
    Contract:
        - Always loads in 4-bit unless load_in_4bit=False explicitly
        - Sets model to eval mode (no gradient computation)
    """

def generate_executive_summary(
    model: Any,
    tokenizer: Any,
    valuation_summary: ValuationSummary,
    max_new_tokens: int = 1024,
    temperature: float = 0.3,
    max_retries: int = 3
) -> str:
    """
    Generates the executive summary narrative using the fine-tuned LLM.
    
    Args:
        model: Loaded Unsloth model
        tokenizer: Loaded tokenizer
        valuation_summary: All computed valuation data (fed as context)
        max_retries: Number of attempts if hallucination is detected
    
    Returns:
        str: Professional narrative text
    
    Contract:
        - LLM NEVER computes financial values — all numbers come from valuation_summary
        - Post-generation: validate that all numbers in narrative match source data
        - If hallucinated number detected: retry with stricter anti-hallucination prompt
        - After max_retries: return narrative with WARNING flag and flagged numbers highlighted
        - Temperature: 0.3 (low for factual output)
    
    Raises:
        LLMError.HallucinationError: If hallucination persists after max_retries
    """

def validate_narrative_numbers(
    narrative: str,
    valuation_summary: ValuationSummary,
    tolerance_pct: float = 1.0
) -> Tuple[bool, List[str]]:
    """
    Extracts all numbers from narrative and validates against source data.
    
    Returns:
        Tuple of (is_valid: bool, flagged_discrepancies: List[str])
    
    Contract:
        - Extracts all numeric values from narrative text
        - Checks each against valuation_summary values within tolerance
        - Returns False if any number cannot be traced to a source value
    """
```

---

## 3. Error Code Reference

```python
# All FMVA error codes as constants
ERROR_CODES = {
    # Ingestion
    "E001": "MISSING_REQUIRED_FIELD",
    "E002": "INVALID_FILE_FORMAT",
    "E003": "ENCODING_ERROR",
    
    # Normalization
    "E101": "FIELD_MAPPING_FAILED",
    "E102": "CLASSIFICATION_UNCERTAIN",
    "E103": "CURRENCY_CONVERSION_FAILED",
    
    # Integrity
    "E201": "BS_IMBALANCE_ERROR",
    "E202": "CFS_IMBALANCE_ERROR",
    "E203": "IS_BS_NET_INCOME_MISMATCH",
    
    # Valuation
    "E301": "GORDON_GROWTH_ERROR",       # WACC <= TGR
    "E302": "WACC_OUT_OF_RANGE",
    "E303": "NEGATIVE_EQUITY_VALUE",
    
    # LLM
    "E401": "LLM_OOM_ERROR",
    "E402": "LLM_HALLUCINATION_ERROR",
    "E403": "LLM_TIMEOUT",
    
    # Export
    "E501": "EXCEL_WRITE_FAILED",
    "E502": "DRIVE_NOT_MOUNTED",
    
    # Warnings (non-blocking)
    "W001": "TV_HIGH_WARNING",           # TV > 80% of EV
    "W002": "EBITDA_NEGATIVE",
    "W003": "ASSUMPTION_OUT_OF_BOUNDS",
    "W004": "OUTLIER_DETECTED",
    "W005": "REVIEW_REQUIRED",           # Unmapped field
}
```

---

## 4. Master Pipeline API

```python
def run_full_pipeline(
    input_file: str,
    company_name: str,
    assumptions: Optional[AssumptionSet] = None,
    comparable_companies: Optional[List[CompanyComps]] = None,
    generate_narrative: bool = True,
    export_excel: bool = True,
    export_json: bool = True,
    output_path: str = "/content/drive/MyDrive/FMVA/outputs/"
) -> ValuationSummary:
    """
    End-to-end pipeline orchestration function.
    Runs all stages in sequence: Ingest → Normalize → Project → Value → Audit → Export
    
    Args:
        input_file: Path to raw financial data file
        company_name: Used for metadata and output file naming
        assumptions: AssumptionSet (if None, loads base case defaults)
        comparable_companies: Optional list for comps analysis
        generate_narrative: Whether to run LLM narrative generation
        export_excel: Whether to generate Excel export
        export_json: Whether to generate JSON export
        output_path: Where to save outputs
    
    Returns:
        ValuationSummary: Complete valuation output
    
    Contract:
        - Saves checkpoints to Drive after each major stage
        - If any integrity check fails: stops and returns error report
        - Always generates AuditTrail regardless of other options
        - Console prints progress at each stage
    
    Example:
        summary = run_full_pipeline(
            input_file="/content/drive/MyDrive/FMVA/inputs/acme.csv",
            company_name="Acme Corp",
            assumptions=create_assumption_set("Base Case", wacc_pct=10.5)
        )
        print(f"Implied share price: ${summary.dcf_implied_price_gg:.2f}")
    """
```

---

*Document Owner: Engineering | Last Updated: 2026-02-23*
