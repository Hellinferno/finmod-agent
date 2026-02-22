# System Design Document
## Financial Modeling & Valuation Agent
### Version 1.0 | Google Colab + Unsloth Stack

---

## 1. System Overview

The Financial Modeling & Valuation Agent is a **sequential, single-user computation pipeline** implemented as a collection of modular Python packages orchestrated by Jupyter notebooks on Google Colab. The system processes raw financial data and produces institutional-grade valuation outputs.

The design philosophy is **modular monolith**: all code runs in the same Python process in a single Colab session, but is organized into clearly separated modules with well-defined interfaces, so any module can be replaced independently (e.g., swapping yfinance for Bloomberg API without touching the DCF engine).

---

## 2. High-Level System Design

### 2.1 Component Diagram

```
╔══════════════════════════════════════════════════════════════════╗
║                    GOOGLE COLAB RUNTIME                          ║
║  ┌──────────────────────────────────────────────────────────┐   ║
║  │                JUPYTER NOTEBOOK UI                        │   ║
║  │  ┌─────────────────────────────────────────────────────┐ │   ║
║  │  │  ipywidgets: Sliders, Dropdowns, Buttons, Tables    │ │   ║
║  │  └───────────────────────┬─────────────────────────────┘ │   ║
║  └──────────────────────────│─────────────────────────────── ┘   ║
║                             │ calls                              ║
║  ┌──────────────────────────▼─────────────────────────────────┐ ║
║  │                   ORCHESTRATOR LAYER                        │ ║
║  │              (notebook cells / main.py)                     │ ║
║  └──┬──────────┬──────────┬──────────┬──────────┬─────────────┘ ║
║     │          │          │          │          │                ║
║  ┌──▼──┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐          ║
║  │ IN  │  │ ASSU  │  │  DCF  │  │ COMPS │  │  LLM  │          ║
║  │GEST │  │MPTION │  │ENGINE │  │+TRANS │  │NARRAT │          ║
║  │ION  │  │ENGINE │  │       │  │ENGINE │  │ IVE   │          ║
║  └──┬──┘  └───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘          ║
║     └─────────┴──────────┴──────────┴──────────┘│              ║
║                           │                      │              ║
║  ┌────────────────────────▼──────────────────────▼───────────┐ ║
║  │                    AUDIT TRAIL ENGINE                      │ ║
║  └────────────────────────────────────────────────────────────┘ ║
║                           │                                      ║
║  ┌────────────────────────▼───────────────────────────────────┐ ║
║  │              SENSITIVITY & VISUALIZATION ENGINE             │ ║
║  └────────────────────────┬───────────────────────────────────┘ ║
║                           │                                      ║
║  ┌────────────────────────▼───────────────────────────────────┐ ║
║  │                    OUTPUT ENGINE                            │ ║
║  │          Excel │ JSON │ PDF │ Auto-Drive-Save               │ ║
║  └────────────────────────────────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════╝
           │                              │
           ▼                              ▼
  ┌─────────────────┐          ┌────────────────────┐
  │  Google Drive   │          │  External APIs     │
  │  (Persistence)  │          │  yfinance │ HF Hub │
  └─────────────────┘          └────────────────────┘
```

---

## 3. Module Design

### 3.1 Ingestion Module

**Responsibility**: Accept raw financial data in any supported format, validate it, and normalize it into the canonical `FinancialStatements` schema.

**Interface**:
```python
from ingestion.loader import load_json, load_csv, load_excel
from ingestion.normalizer import normalize
from ingestion.validator import validate
from ingestion.balance_sheet_checker import check_balance_sheet

# Usage pattern (always in this order)
raw_data = load_json(filepath)
normalized = normalize(raw_data)
validation = validate(normalized)
bs_check = check_balance_sheet(normalized.balance_sheet)
```

**Internal Design**:
```
loader.py
  ├── load_json(filepath) → dict
  ├── load_csv(filepath) → dict  [auto-detect delimiter]
  └── load_excel(filepath) → dict [auto-detect sheets]

normalizer.py
  ├── CANONICAL_MAP: dict[str, list[str]]  [field alias registry]
  ├── normalize(raw: dict) → FinancialStatements
  ├── _map_field(raw_key: str) → str  [fuzzy match with difflib]
  └── _parse_multi_year(data: dict, years: list) → HistoricalModel

validator.py
  ├── validate(fs: FinancialStatements) → ValidationReport
  ├── _check_revenue_positive(fs) → list[str]
  ├── _check_ebitda_consistency(fs) → list[str]
  └── _check_cash_flow_reasonableness(fs) → list[str]

balance_sheet_checker.py
  ├── check_balance_sheet(bs: BalanceSheet) → BalanceCheckResult
  ├── TOLERANCE = 0.01  # $0.01M
  └── _suggest_plug(delta: float, bs: BalanceSheet) → str
```

**Data Contract — `FinancialStatements`**:
```python
@dataclass(frozen=True)
class IncomeStatement:
    revenue: float
    cogs: float
    gross_profit: float
    ebitda: float
    depreciation: float
    ebit: float
    interest_expense: float
    tax_expense: float
    net_income: float
    year: int

@dataclass(frozen=True)
class BalanceSheet:
    total_assets: float
    total_liabilities: float
    shareholders_equity: float
    cash: float
    net_debt: float
    year: int

@dataclass(frozen=True)
class CashFlow:
    operating_cash_flow: float
    capex: float
    depreciation: float
    free_cash_flow: float
    year: int

@dataclass
class FinancialStatements:
    company_name: str
    ticker: Optional[str]
    currency: str
    units: str  # "millions" | "thousands" | "billions"
    accounting_standard: str  # "GAAP" | "IFRS"
    historical_years: list[int]
    income_statements: dict[int, IncomeStatement]
    balance_sheets: dict[int, BalanceSheet]
    cash_flows: dict[int, CashFlow]
    diluted_shares: float
    warnings: dict[str, Any]
```

---

### 3.2 Assumption Engine

**Responsibility**: Provide a user-facing interface to configure all modeling drivers; serialize/deserialize assumption sets; supply default scenario presets.

**Interface**:
```python
from assumptions.engine import AssumptionSet, PRESETS
from assumptions.widgets import render_assumption_widgets

# Load preset
assumptions = PRESETS["base"]

# Or render interactive UI
assumptions = render_assumption_widgets()  # Returns AssumptionSet via callback

# Save/load
assumptions.save("/content/drive/MyDrive/valuation_agent/data/my_assumptions.json")
assumptions = AssumptionSet.load("path.json")
```

**Widget Layout**:
```
┌────────────────────────────────────────────────────────────┐
│  SCENARIO: [Bear ▼] [Base ▼] [Bull ▼] [Custom]           │
├──────────────────────────┬─────────────────────────────────┤
│  REVENUE DRIVERS         │  COST DRIVERS                   │
│  Revenue Growth (Y1–Y5)  │  EBITDA Margin: [====|25%]      │
│  Y1: [====|10%]          │  D&A / Revenue: [==|5%]         │
│  Y2: [====|10%]          │  Tax Rate:      [====|21%]      │
│  Y3: [===|9%]            │                                 │
│  Y4: [===|9%]            │  CAPITAL DRIVERS                │
│  Y5: [==|8%]             │  CapEx / Sales: [===|6%]        │
│                          │  NWC / Revenue: [===|8%]        │
├──────────────────────────┴─────────────────────────────────┤
│  TERMINAL VALUE                                            │
│  Method: [Gordon Growth ▼] [Exit Multiple ▼]               │
│  Terminal Growth Rate:  [==|2.5%]                          │
│  Exit EV/EBITDA Multiple: [========|12.0x]                 │
├────────────────────────────────────────────────────────────┤
│  WACC INPUTS                                               │
│  Risk-Free Rate: [=|4.5%]   Equity Risk Premium: [=|5.5%] │
│  Beta: [auto from yfinance]  Debt Rate: [=|6%]            │
│  D/E Ratio: [===|0.30]                                     │
└────────────────────────────────────────────────────────────┘
```

---

### 3.3 DCF Engine

**Responsibility**: Execute all DCF computations from income statement projection through to Enterprise Value and implied share price. Every computation must register with the Audit Trail.

**Computation Graph**:
```
Base Revenue (Year 0)
    │
    ├── × (1 + growth_rate_y1) → Revenue_Y1
    │       × ebitda_margin    → EBITDA_Y1
    │       − da_to_rev        → DA_Y1
    │       EBITDA − DA        → EBIT_Y1
    │       × (1 − tax_rate)   → NOPAT_Y1
    │
    ├── NOPAT_Y1 + DA_Y1       → Cash_NOPAT_DA_Y1
    │   − (rev_Y1 × capex_pct) → minus_CapEx_Y1
    │   − (ΔREV × nwc_pct)     → minus_ΔNWC_Y1
    │                            = UFCF_Y1
    │
    ├── [repeat for Y2–Y5]
    │
    ├── UFCF_Yn × (1+g) / (WACC-g) → Terminal_Value_Gordon
    │   OR EBITDA_Yn × exit_mult   → Terminal_Value_Exit
    │
    ├── Σ UFCF_i / (1+WACC)^(i±0.5) → PV_of_UFCFs
    ├── TV / (1+WACC)^(n±0.5)       → PV_of_TV
    ├── PV_UFCFs + PV_TV             → Enterprise_Value
    ├── EV − Net_Debt                → Equity_Value
    └── Equity_Value / Shares        → Implied_Price
```

**Key Function Signatures**:
```python
def project_income_statement(
    base_revenue: float,
    assumptions: AssumptionSet,
    n_years: int,
    audit: AuditTrail,
) -> ProjectionTable:
    ...

def calculate_ufcf(
    projection: ProjectionTable,
    assumptions: AssumptionSet,
    audit: AuditTrail,
) -> list[float]:
    ...

def calculate_terminal_value(
    ufcf_final: float,
    ebitda_final: float,
    wacc: float,
    terminal_growth: float,
    exit_multiple: float,
    method: Literal["gordon", "exit_multiple"],
    audit: AuditTrail,
) -> float:
    ...

def calculate_equity_value(
    ufcf_series: list[float],
    terminal_value: float,
    wacc: float,
    net_debt: float,
    diluted_shares: float,
    mid_year: bool,
    audit: AuditTrail,
) -> ValuationResult:
    ...

def run_full_dcf(
    normalized: FinancialStatements,
    assumptions: AssumptionSet,
    audit_trail: AuditTrail,
) -> ValuationResult:
    """Top-level orchestrator — calls all DCF functions in sequence."""
    ...
```

---

### 3.4 Comps & Transactions Engine

**Responsibility**: Retrieve or accept comparable company and transaction data; compute relevant multiples; produce implied valuation ranges.

**Data Source Strategy**:
```
Public Comps:
  Primary: yfinance (free, US stocks)
  Fallback: Manual input JSON
  Cache: Drive pickle, 24-hour TTL

Precedent Transactions:
  V1: Manual input only (JSON or CSV)
  V2: M&A database API (scope TBD)
```

**Comps Table Design**:
```
┌────────┬─────────┬───────────┬────────────┬─────────────┐
│ Ticker │  Mkt Cap│   EV/EBITDA│  EV/Revenue│    P/E      │
├────────┼─────────┼───────────┼────────────┼─────────────┤
│ MSFT   │  $2.5T  │    22.1x  │    10.2x   │   32.1x     │
│ AAPL   │  $2.8T  │    20.4x  │     7.5x   │   28.5x     │
│ GOOGL  │  $1.9T  │    18.3x  │     5.8x   │   24.2x     │
│ ...    │   ...   │    ...    │    ...     │    ...      │
├────────┼─────────┼───────────┼────────────┼─────────────┤
│ Min    │         │    14.0x  │     3.0x   │   20.0x     │
│ 25th   │         │    18.0x  │     5.0x   │   24.0x     │
│ Median │         │    20.4x  │     6.5x   │   28.5x     │
│ 75th   │         │    22.1x  │     8.5x   │   32.1x     │
│ Max    │         │    25.0x  │    12.0x   │   42.0x     │
└────────┴─────────┴───────────┴────────────┴─────────────┘
Implied EV (Median):   $X,XXX M      $X,XXX M
```

---

### 3.5 LLM Narrative Engine

**Responsibility**: Transform structured valuation outputs into professional written narratives using Unsloth-powered Mistral-7B.

**Design Pattern — RAG-lite**:
Rather than full RAG with a vector database, we use structured context injection: a complete JSON object of all relevant facts is injected into every prompt. The LLM's instruction to "only cite numbers from the provided data" combined with the post-generation hallucination guard provides sufficient factual grounding.

**Generation Pipeline**:
```
ValuationResult
    │
    ├── build_context(result) → dict
    │     {
    │       "company_name": "TechCorp Inc.",
    │       "dcf_ev": 1102.4,
    │       "dcf_equity_value": 952.4,
    │       "implied_price": 9.52,
    │       "revenue_cagr_5yr": 0.092,
    │       "ebitda_margin_year5": 0.25,
    │       "wacc": 0.10,
    │       "tgr": 0.025,
    │       "comps_ev_ebitda_median": 20.4,
    │       "comps_implied_ev_median": 989.0,
    │       ...
    │     }
    │
    ├── render_prompt("executive_summary", context) → str
    │     [Jinja2 template fills all {{ variables }}]
    │
    ├── generate_narrative(prompt, model, tokenizer) → str
    │     [Unsloth inference with temp=0.3, max_new_tokens=512]
    │
    └── check_factual_grounding(narrative, context) → flags
          [Extract numbers from text, verify against context dict]
```

**Fallback Strategy**: If GPU runs out of memory or Unsloth fails to load:
1. Log error with full traceback
2. Insert placeholder text: "[AI NARRATIVE UNAVAILABLE — Manual review required]"
3. Continue with all quantitative outputs
4. Never crash the full pipeline due to LLM failure

---

### 3.6 Audit Trail Engine

**Responsibility**: Provide an immutable, append-only log of every computation performed, with enough detail to fully reconstruct any result from scratch.

**Design**:
```python
@dataclass(frozen=True)
class AuditEntry:
    entry_id: str           # UUID
    timestamp: str          # ISO 8601
    step: str               # Human-readable step name
    module: str             # "dcf" | "comps" | "sensitivity"
    formula: str            # Formula as string: "NOPAT + D&A - CapEx - ΔNWC"
    inputs: dict[str, float] # {"NOPAT": 86.9, "DA": 27.5, ...}
    output: float           # 77.4
    unit: str               # "$M" | "%" | "x"
    assumption_set_hash: str # Hash of AssumptionSet used

class AuditTrail:
    def __init__(self):
        self._entries: list[AuditEntry] = []
    
    def log(self, step, module, formula, inputs, output, unit) -> AuditEntry:
        entry = AuditEntry(
            entry_id=str(uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            step=step,
            module=module,
            formula=formula,
            inputs=inputs,
            output=output,
            unit=unit,
        )
        self._entries.append(entry)
        return entry
    
    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        return tuple(self._entries)  # Immutable view
    
    def export_json(self, path: str) -> None: ...
    def to_dataframe(self) -> pd.DataFrame: ...
    def export_to_excel_sheet(self, workbook: openpyxl.Workbook) -> None: ...
```

**Audit Trail Output Format (JSON)**:
```json
{
    "session_id": "a3f8b2c1d9e4",
    "company": "TechCorp Inc.",
    "generated_at": "2024-11-15T14:32:01Z",
    "assumption_set": "base",
    "entries": [
        {
            "entry_id": "uuid-001",
            "timestamp": "2024-11-15T14:32:03Z",
            "step": "Revenue Year 1",
            "module": "dcf",
            "formula": "Base_Revenue × (1 + growth_rate_Y1)",
            "inputs": {"Base_Revenue": 500.0, "growth_rate_Y1": 0.10},
            "output": 550.0,
            "unit": "$M"
        },
        ...
    ]
}
```

---

### 3.7 Sensitivity Engine

**Responsibility**: Generate all sensitivity analyses — the WACC×TGR matrix, the Revenue Growth×EBITDA Margin matrix, and the Football Field chart.

**Computation Design — Sensitivity Matrix**:
```python
def sensitivity_matrix(
    param1_range: list[float],   # e.g., WACC range
    param2_range: list[float],   # e.g., TGR range
    base_assumptions: AssumptionSet,
    normalized_data: FinancialStatements,
    output_metric: Literal["ev", "equity_value", "implied_price"] = "ev",
) -> pd.DataFrame:
    """
    Generates a 2D sensitivity matrix by running the full DCF n×m times.
    Computation cost: O(n×m) DCF runs.
    For a 5×5 matrix: 25 DCF runs. At ~0.4s each: ~10 seconds total.
    """
    results = {}
    for p1 in param1_range:
        for p2 in param2_range:
            modified = assumptions.copy(wacc_override=p1, tgr_override=p2)
            result = run_full_dcf(normalized_data, modified, audit=NullAudit())
            results[(p1, p2)] = getattr(result, output_metric)
    
    return pd.DataFrame(
        data=[[results[(p1, p2)] for p2 in param2_range] for p1 in param1_range],
        index=param1_range,
        columns=param2_range,
    )
```

**Football Field Chart Design**:
```
Enterprise Value ($M)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DCF (Bear)          ████████████░░░░░░░░░░
DCF (Base)                    ████████████████░░░░░░
DCF (Bull)                              ████████████████████
EV/EBITDA Comps          ████████████████░░░░
EV/Revenue Comps              ████████████░░░░░░
Precedent Trans.                    ████████████████████
                  │                │                │
                 $800M          $1,100M          $1,400M
                             ▲
                     Current Trading: $950M
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 3.8 Output Engine

**Responsibility**: Transform all in-memory computation results into downloadable artifacts.

**Excel Workbook Architecture**:
```
Sheet 1: Cover Page
  - Company name, logo placeholder, date, analyst name
  - Valuation summary table (3 methods, 3 scenarios)
  - Key statistics (revenue, EBITDA, EV, implied price)

Sheet 2: 3-Statement Model
  - Historical IS, BS, CF side by side (3 years)
  - Color coding: actuals blue, projections green
  - Integrity check result displayed

Sheet 3: DCF Model
  - Rows: Revenue, EBITDA, D&A, EBIT, NOPAT, CapEx, ΔNWC, UFCF
  - Columns: Historical Y-2, Y-1, Y0 | Projected Y1–Y5(10)
  - PV calculations, TV, EV, Equity Value bridge
  - WACC derivation table (side panel)

Sheet 4: Public Comps
  - Full comps table with all multiples
  - Statistics row (min, 25th, median, 75th, max)
  - Implied EV summary

Sheet 5: Precedent Transactions
  - Full transaction table
  - Multiple statistics
  - Implied EV summary

Sheet 6: WACC×TGR Sensitivity
  - 5×5 EV matrix with conditional formatting (green=high, red=low)
  - Base case cell highlighted with border

Sheet 7: RevGrowth×EBITDA Sensitivity
  - 5×5 EV matrix

Sheet 8: Football Field Chart
  - Embedded matplotlib chart (saved as image, inserted)

Sheet 9: Audit Trail
  - Full tabular log of every calculation
  - Columns: Step, Formula, Inputs, Output, Unit, Timestamp

Sheet 10: Assumptions
  - All driver inputs displayed
  - Bear / Base / Bull comparison table
```

---

## 4. Data Persistence Design

### 4.1 State Lifecycle

```
Session Start
    │
    ├── Drive Mount → verify /content/drive/MyDrive/valuation_agent/
    ├── Load config → /config/config.py
    ├── Load model weights → /models/ (if LLM needed)
    │
    ├── User uploads raw data → /data/raw/{company}_{date}/
    ├── Normalized data saved → /data/normalized/{company}_{date}_norm.json
    ├── Assumptions saved → /data/{company}_{date}_assumptions.json
    │
    ├── Valuation computed (in-memory)
    ├── Audit trail saved → /outputs/json/{company}_{date}_audit.json
    ├── Excel saved → /outputs/excel/{company}_{date}_valuation.xlsx
    ├── JSON saved → /outputs/json/{company}_{date}_valuation.json
    ├── PDF saved → /outputs/pdf/{company}_{date}_report.pdf
    │
    └── Session log → /logs/session_{timestamp}.log
```

### 4.2 File Naming Convention

```
{company_slug}_{YYYYMMDD}_{type}.{ext}

Examples:
  techcorp_20241115_raw.json
  techcorp_20241115_normalized.json
  techcorp_20241115_assumptions_base.json
  techcorp_20241115_valuation.xlsx
  techcorp_20241115_valuation.json
  techcorp_20241115_report.pdf
  techcorp_20241115_audit.json
```

---

## 5. Inter-Module Communication

All modules communicate via **typed Python dataclasses** — no global mutable state, no magic strings. The `AuditTrail` object is passed as a dependency into every computation function.

```
FinancialStatements ────→ DCF Engine ─────→ ValuationResult
     │                                           │
AssumptionSet ──────────→ DCF Engine            │
                                                 ↓
CompData + CompsStats ──────────────→ FullReport
                                                 │
TransactionData ─────────────────────→ FullReport
                                                 │
AuditTrail ─────────────────────────────────────┘
                                                 │
                                    OutputEngine.export(FullReport)
```

---

## 6. Security & Privacy

Since V1 runs entirely within the user's own Google Colab and Drive account:
- **No data leaves the user's GCP project** unless they explicitly share their Drive
- **No API keys are stored in code** — Colab Secrets used for all credentials
- **Financial data never transmitted to third parties** in V1 (yfinance pulls public market data only)
- **LLM inference is local** (Unsloth on Colab GPU — no data sent to external LLM API)

---

## 7. Scalability Considerations (Phase 2+)

The V1 system is designed to be extractable into a production service with minimal refactoring:

| V1 Design | V2 Migration Path |
|-----------|------------------|
| Colab notebook orchestration | FastAPI service with same Python modules |
| JSON serialization | PostgreSQL with SQLAlchemy ORM |
| Drive persistence | S3 / GCS blob storage |
| yfinance data | Bloomberg API / Capital IQ connector |
| Single-user | Multi-tenant with auth |
| ipywidgets UI | React/Next.js frontend |
| Colab LLM | Dedicated GPU instance / vLLM server |

---

*Version: 1.0 | Status: Draft | Owner: Tech Lead*
