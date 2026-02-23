# 10 — Development Phases & Roadmap
### Financial Modeling & Valuation Agent | Colab + Unsloth Stack

---

## 1. Document Purpose

This document defines the **complete build sequence** for the Financial Modeling & Valuation Agent — from environment setup through production-ready MVP. Each phase has defined deliverables, acceptance gates, estimated effort, and dependencies. Engineers must not begin a phase until all gates from the prior phase are passed.

> **Methodology**: Iterative, notebook-first development. Each phase ends with a working, runnable Colab notebook that a non-engineer (e.g., a financial analyst) can execute end-to-end.

---

## 2. Master Timeline Overview

```
Phase 0 │ Environment & Foundations         │ Week 1       │ 1 Engineer
Phase 1 │ Data Ingestion & Normalization    │ Week 2–3     │ 1–2 Engineers
Phase 2 │ Assumption Engine & DCF Core      │ Week 3–5     │ 2 Engineers
Phase 3 │ Comps, Transactions & Sensitivity │ Week 5–7     │ 2 Engineers
Phase 4 │ LLM Narrative Engine (Unsloth)    │ Week 6–9     │ 1–2 Engineers
Phase 5 │ Audit Trail & Output Engine       │ Week 8–10    │ 1 Engineer
Phase 6 │ Integration & End-to-End Testing  │ Week 10–11   │ Full Team
Phase 7 │ MVP Hardening & Documentation     │ Week 11–12   │ Full Team
```

**Total Estimated Duration**: 12 weeks  
**Team Size**: 2–3 Engineers + 1 PM + 1 Financial Domain Expert (part-time)

---

## 3. Phase 0: Environment & Foundations

**Duration**: Week 1 (5 days)  
**Owner**: Tech Lead  
**Goal**: A fully configured, reproducible Colab environment where every engineer can run a "Hello World" model within 30 minutes of cloning.

### 3.1 Deliverables

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 0.1 | `00_setup.ipynb` — master setup notebook | Runs cell-by-cell on fresh Colab T4 with zero errors |
| 0.2 | `requirements.txt` — all pinned dependencies | `pip install -r requirements.txt` completes < 5 min |
| 0.3 | Google Drive folder structure initialized | `/content/drive/MyDrive/valuation_agent/` exists with all subdirs |
| 0.4 | Unsloth installed and base model loaded | `from unsloth import FastLanguageModel` imports without error |
| 0.5 | Sample financial data fixtures (3 companies) | JSON files in `/data/fixtures/` with valid schema |
| 0.6 | `config.py` with all global constants | WACC defaults, growth defaults, tax rates |
| 0.7 | Logging framework initialized | Every module logs to `/logs/session_{timestamp}.log` on Drive |

### 3.2 Technical Tasks

```
TASK-0.1: Create Google Drive folder structure
  /content/drive/MyDrive/valuation_agent/
    ├── /data/
    │     ├── /raw/          ← user uploads
    │     ├── /normalized/   ← post-ingestion
    │     └── /fixtures/     ← test data
    ├── /models/             ← Unsloth model weights
    ├── /outputs/            ← Excel, JSON, PDF exports
    ├── /logs/               ← session logs
    └── /notebooks/          ← all .ipynb files

TASK-0.2: Pin all dependencies
  Core: pandas==2.1.4, numpy==1.26.3, openpyxl==3.1.2
  Finance: yfinance==0.2.36, scipy==1.12.0
  LLM: unsloth==2024.x, transformers==4.40.0, peft==0.10.0, trl==0.8.6
  UI: ipywidgets==8.1.2, matplotlib==3.8.2, seaborn==0.13.2
  Export: reportlab==4.1.0, nbconvert==7.14.0
  Utils: jinja2==3.1.3, python-dotenv==1.0.1

TASK-0.3: Validate GPU access
  assert torch.cuda.is_available(), "GPU required"
  print(torch.cuda.get_device_name(0))

TASK-0.4: Load Unsloth base model (dry run)
  model, tokenizer = FastLanguageModel.from_pretrained(
      model_name="unsloth/mistral-7b-v0.3-bnb-4bit",
      max_seq_length=4096,
      load_in_4bit=True,
  )

TASK-0.5: Create 3 fixture companies
  - TechCorp Inc (SaaS, high growth)
  - ManufactureCo Ltd (industrial, stable)
  - RetailChain Corp (retail, declining)
```

### 3.3 Phase Gate Criteria

- [x] `00_setup.ipynb` runs clean on fresh runtime
- [x] All 3 fixture datasets load and print without error
- [ ] Unsloth model loads in < 90 seconds on T4
- [x] Drive mount and folder structure verified
- [x] `config.py` reviewed and approved by Financial Domain Expert

---

## 4. Phase 1: Data Ingestion & Normalization

**Duration**: Week 2–3 (10 days)  
**Owner**: Engineer 1  
**Goal**: Any raw financial data (JSON, CSV, Excel) goes in; a validated, normalized 3-Statement model comes out.

### 4.1 Deliverables

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 1.1 | `ingestion/loader.py` | Loads JSON, CSV, XLSX without error |
| 1.2 | `ingestion/normalizer.py` | Maps raw fields to canonical schema |
| 1.3 | `ingestion/validator.py` | Runs all integrity checks, returns structured error list |
| 1.4 | `ingestion/balance_sheet_checker.py` | Detects imbalance, identifies plug, flags to user |
| 1.5 | `01_data_ingestion.ipynb` | End-to-end demo with all 3 fixture companies |
| 1.6 | Unit tests: `tests/test_ingestion.py` | ≥ 80% coverage, all edge cases tested |

### 4.2 Technical Tasks & Sequence

```
SPRINT 1A (Days 1–4): Loaders

  TASK-1.1: JSON Loader
    def load_json(filepath: str) -> dict:
        """Load and validate raw JSON financial data."""
    Handles: nested keys, missing fields, wrong types
    Error: raises IngestionError with field-level details

  TASK-1.2: CSV Loader
    def load_csv(filepath: str) -> pd.DataFrame:
        """Auto-detect header row, parse numeric columns."""
    Handles: comma/semicolon delimiters, empty rows, % formatting
    Colab: uses files.upload() widget for interactive upload

  TASK-1.3: Excel Loader
    def load_excel(filepath: str, sheet_name: str = None) -> dict:
        """Parse multi-sheet Excel; auto-detect IS, BS, CF sheets."""
    Uses: openpyxl
    Auto-detect: sheets named 'Income', 'Balance', 'Cash', 'P&L', etc.

SPRINT 1B (Days 5–8): Normalizer

  TASK-1.4: Field Mapper
    CANONICAL_MAP = {
        "revenue": ["total revenue", "net sales", "net revenue", "turnover"],
        "cogs": ["cost of goods sold", "cost of sales", "cost of revenue"],
        "gross_profit": ["gross profit", "gross income"],
        "ebitda": ["ebitda", "earnings before interest tax depreciation"],
        "ebit": ["ebit", "operating income", "operating profit"],
        "interest_expense": ["interest expense", "finance costs"],
        "tax_expense": ["income tax", "tax expense", "provision for taxes"],
        "net_income": ["net income", "net profit", "profit after tax"],
        "total_assets": ["total assets"],
        "total_liabilities": ["total liabilities"],
        "shareholders_equity": ["shareholders equity", "stockholders equity", "total equity"],
        "cash": ["cash", "cash and equivalents", "cash and cash equivalents"],
        "capex": ["capital expenditure", "capex", "purchase of ppe"],
        "depreciation": ["depreciation", "d&a", "depreciation and amortization"],
        "change_in_wc": ["change in working capital", "delta nwc"],
        "operating_cash_flow": ["operating cash flow", "cash from operations"],
    }

  TASK-1.5: Normalizer Function
    def normalize(raw_data: dict) -> FinancialStatements:
        """Map raw input fields to canonical schema using CANONICAL_MAP."""
    Output: FinancialStatements dataclass (see DB Schema doc)
    Handles: case-insensitive matching, fuzzy match fallback (difflib)

  TASK-1.6: Multi-Year Parser
    def parse_historical(data: dict, years: list[int]) -> HistoricalModel:
        """Parse multi-year data into time-series format."""
    Minimum: 3 years historical; warns if < 3 years

SPRINT 1C (Days 9–10): Validator & Balance Sheet Check

  TASK-1.7: Integrity Validator
    Checks:
      - No negative Revenue
      - EBITDA = EBIT + D&A (within rounding tolerance ±0.5%)
      - Net Income derivable from EBIT – Interest – Tax
      - Operating CF reasonably close to Net Income + D&A ± ΔWC (±10%)
    Output: ValidationReport(errors=[], warnings=[], passed=bool)

  TASK-1.8: Balance Sheet Checker
    def check_balance_sheet(bs: BalanceSheet) -> BalanceCheckResult:
        delta = bs.total_assets - (bs.total_liabilities + bs.shareholders_equity)
        if abs(delta) > TOLERANCE:
            # Identify which line item is most likely wrong
            # Suggest plug: "Consider adding/subtracting {delta} to Retained Earnings"
            return BalanceCheckResult(balanced=False, delta=delta, plug_suggestion=...)
```

### 4.3 Edge Cases to Handle

- Missing line items (graceful degradation + warning, not crash)
- Negative EBITDA companies (valid; flag for user awareness)
- Single-year data (warn; DCF requires at minimum 1 base year)
- Non-USD currencies (flag; no conversion in V1)
- Restated financials (accept as-is; note in audit trail)

### 4.4 Phase Gate Criteria

- [x] All 3 fixture companies normalize without error
- [x] Balance sheet checker correctly identifies planted imbalance in test fixture
- [x] `test_ingestion.py` passes 100% with ≥ 80% coverage
- [x] Financial Domain Expert validates canonical field mappings

---

## 5. Phase 2: Assumption Engine & DCF Core

**Duration**: Week 3–5 (14 days)  
**Owner**: Engineer 1 + Engineer 2  
**Goal**: Interactive assumption toggles and a fully working DCF that produces Enterprise Value and implied share price with complete audit trail.

### 5.1 Deliverables

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 2.1 | `assumptions/engine.py` | Returns AssumptionSet for Bear/Base/Bull |
| 2.2 | `assumptions/widgets.py` | All sliders render in Colab without error |
| 2.3 | `valuation/dcf.py` | Full DCF from UFCF to Equity Value |
| 2.4 | `valuation/wacc.py` | WACC calculation with yfinance beta pull |
| 2.5 | `audit/trail.py` | Every DCF step logged with formula and values |
| 2.6 | `02_dcf_model.ipynb` | Interactive DCF demo notebook |
| 2.7 | Unit tests: `tests/test_dcf.py` | Cross-validated against manual Excel model |

### 5.2 Technical Tasks & Sequence

```
SPRINT 2A (Days 1–5): Assumption Engine

  TASK-2.1: AssumptionSet Dataclass
    @dataclass
    class AssumptionSet:
        scenario: str                    # "bear" | "base" | "bull"
        revenue_growth_rates: list[float]  # [0.10, 0.12, ...] per year
        ebitda_margin: float | list[float] # flat or per-year
        capex_to_sales: float             # e.g., 0.05
        da_to_revenue: float              # D&A as % of revenue
        nwc_to_revenue: float             # NWC as % of revenue
        tax_rate: float                   # e.g., 0.21
        terminal_growth_rate: float       # e.g., 0.025
        exit_multiple: float              # EV/EBITDA for TV

  TASK-2.2: Default Scenario Presets
    BEAR  = AssumptionSet(scenario="bear",  revenue_growth_rates=[0.03]*5, ...)
    BASE  = AssumptionSet(scenario="base",  revenue_growth_rates=[0.08]*5, ...)
    BULL  = AssumptionSet(scenario="bull",  revenue_growth_rates=[0.15]*5, ...)

  TASK-2.3: ipywidgets UI
    Widgets:
      - Revenue Growth (per year): FloatSlider(-20% to +50%)
      - EBITDA Margin: FloatSlider(0% to 60%)
      - CapEx/Sales: FloatSlider(0% to 30%)
      - D&A/Revenue: FloatSlider(0% to 20%)
      - Tax Rate: FloatSlider(0% to 45%)
      - Terminal Growth Rate: FloatSlider(0% to 5%)
      - Exit Multiple: FloatSlider(3x to 25x)
      - Projection Years: IntSlider(5 or 10)
      - Scenario Selector: Dropdown(Bear/Base/Bull/Custom)
    
    On change: auto-recalculate and display updated summary

SPRINT 2B (Days 6–9): WACC Module

  TASK-2.4: WACC Calculator
    def calculate_wacc(
        ticker: str,
        risk_free_rate: float,
        equity_risk_premium: float,
        debt_rate: float,
        tax_rate: float,
        target_d_to_e: float,
    ) -> WACCResult:
        beta = fetch_beta_yfinance(ticker)
        ke = risk_free_rate + beta * equity_risk_premium  # CAPM
        kd_after_tax = debt_rate * (1 - tax_rate)
        weight_e = 1 / (1 + target_d_to_e)
        weight_d = target_d_to_e / (1 + target_d_to_e)
        wacc = ke * weight_e + kd_after_tax * weight_d
        return WACCResult(wacc=wacc, ke=ke, kd=kd_after_tax, beta=beta, ...)

  TASK-2.5: Beta Fetcher
    def fetch_beta_yfinance(ticker: str) -> float:
        stock = yf.Ticker(ticker)
        beta = stock.info.get("beta", 1.0)  # default 1.0 if unavailable
        return beta

SPRINT 2C (Days 10–14): DCF Engine

  TASK-2.6: Revenue & EBITDA Projection
    def project_income_statement(
        base_revenue: float,
        assumptions: AssumptionSet,
        n_years: int,
    ) -> ProjectionTable:
        for year in range(1, n_years+1):
            revenue[year] = revenue[year-1] * (1 + growth[year])
            ebitda[year] = revenue[year] * ebitda_margin[year]
            da[year] = revenue[year] * da_to_rev
            ebit[year] = ebitda[year] - da[year]
            nopat[year] = ebit[year] * (1 - tax_rate)

  TASK-2.7: UFCF Calculation
    def calculate_ufcf(projection: ProjectionTable, assumptions: AssumptionSet) -> list[float]:
        for year:
            capex = revenue[year] * assumptions.capex_to_sales
            delta_nwc = (revenue[year] - revenue[year-1]) * assumptions.nwc_to_revenue
            ufcf[year] = nopat[year] + da[year] - capex - delta_nwc
        return ufcf

  TASK-2.8: Terminal Value
    def calculate_terminal_value(
        ufcf_final: float,
        ebitda_final: float,
        wacc: float,
        terminal_growth: float,
        exit_multiple: float,
        method: str = "gordon",  # or "exit_multiple"
    ) -> float:
        if method == "gordon":
            tv = ufcf_final * (1 + terminal_growth) / (wacc - terminal_growth)
        elif method == "exit_multiple":
            tv = ebitda_final * exit_multiple
        return tv

  TASK-2.9: Enterprise Value & Equity Bridge
    def calculate_equity_value(
        ufcf_series: list[float],
        terminal_value: float,
        wacc: float,
        net_debt: float,
        diluted_shares: float,
        mid_year: bool = True,
    ) -> ValuationResult:
        pv_ufcf = sum(ufcf / (1+wacc)**(t + 0.5 if mid_year else t)
                      for t, ufcf in enumerate(ufcf_series, 1))
        pv_tv = terminal_value / (1+wacc)**(n + 0.5 if mid_year else n)
        enterprise_value = pv_ufcf + pv_tv
        equity_value = enterprise_value - net_debt
        implied_price = equity_value / diluted_shares
        return ValuationResult(...)

  TASK-2.10: Audit Trail Integration
    Every calculation step must call:
      audit.log(
          step="UFCF Year 3",
          formula="NOPAT + D&A - CapEx - ΔNWC",
          inputs={"NOPAT": 45.2, "DA": 12.1, "CapEx": 8.3, "ΔNWC": 3.1},
          output=45.9,
          unit="$M"
      )
```

### 5.3 Validation Requirements

- DCF output must be cross-validated against a manually built Excel model using the same inputs. Tolerance: ±0.1% on EV.
- Financial Domain Expert must sign off on UFCF formula correctness.

### 5.4 Phase Gate Criteria

- [x] DCF matches manual Excel model within ±0.1% tolerance
- [x] All 3 scenarios (Bear/Base/Bull) produce distinct, reasonable valuations
- [ ] Widgets render and update DCF in real-time in Colab
- [x] Audit trail captures every formula, input, and output
- [x] `test_dcf.py` passes 100%

---

## 6. Phase 3: Comps, Precedent Transactions & Sensitivity

**Duration**: Week 5–7 (14 days)  
**Owner**: Engineer 2  
**Goal**: Full comparable company and precedent transaction analysis, plus WACC/TGR sensitivity matrix and football field chart.

### 6.1 Deliverables

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 3.1 | `valuation/comps.py` | Pulls and calculates public trading multiples |
| 3.2 | `valuation/transactions.py` | Processes precedent transaction table |
| 3.3 | `valuation/sensitivity.py` | 2D sensitivity matrices + football field |
| 3.4 | `03_comps_analysis.ipynb` | Demo with 5+ real comps |
| 3.5 | `04_sensitivity_analysis.ipynb` | Interactive sensitivity demo |
| 3.6 | Unit tests: `tests/test_comps.py`, `tests/test_sensitivity.py` | 80%+ coverage |

### 6.2 Technical Tasks

```
SPRINT 3A (Days 1–5): Public Comps

  TASK-3.1: yfinance Data Puller
    def fetch_comp_data(tickers: list[str]) -> list[CompData]:
        for ticker in tickers:
            info = yf.Ticker(ticker).info
            financials = yf.Ticker(ticker).financials
            comp = CompData(
                ticker=ticker,
                market_cap=info["marketCap"],
                enterprise_value=info["enterpriseValue"],
                revenue_ltm=financials.loc["Total Revenue"].iloc[0],
                ebitda_ltm=info.get("ebitda"),
                net_income_ltm=financials.loc["Net Income"].iloc[0],
                pe_ratio=info.get("trailingPE"),
                ev_ebitda=info.get("enterpriseToEbitda"),
                ev_revenue=info.get("enterpriseToRevenue"),
            )

  TASK-3.2: Comps Statistics
    def calculate_comps_stats(comps: list[CompData]) -> CompsStats:
        for metric in ["pe_ratio", "ev_ebitda", "ev_revenue"]:
            values = [getattr(c, metric) for c in comps if getattr(c, metric)]
            stats[metric] = {
                "min": np.min(values),
                "25th": np.percentile(values, 25),
                "median": np.median(values),
                "75th": np.percentile(values, 75),
                "max": np.max(values),
                "mean": np.mean(values),
            }

  TASK-3.3: Implied Valuation from Comps
    def apply_comps_multiples(subject: FinancialStatements, stats: CompsStats) -> CompsValuation:
        implied_ev_ebitda_median = subject.ebitda_ltm * stats["ev_ebitda"]["median"]
        implied_ev_revenue_median = subject.revenue_ltm * stats["ev_revenue"]["median"]
        implied_pe_median = subject.net_income_ltm * stats["pe_ratio"]["median"]
        ...

SPRINT 3B (Days 6–8): Precedent Transactions

  TASK-3.4: Transaction Table Parser
    Expected input format (JSON or CSV):
    {
        "transactions": [
            {
                "target": "Company A",
                "acquirer": "BigCorp",
                "date": "2022-03-15",
                "enterprise_value": 450.0,  # $M
                "target_revenue": 120.0,
                "target_ebitda": 35.0,
                "premium_to_52w_high": 0.22
            }, ...
        ]
    }

  TASK-3.5: Transaction Multiple Calculation
    ev_ebitda = enterprise_value / target_ebitda
    ev_revenue = enterprise_value / target_revenue
    Compute: min, 25th, median, 75th, max across all transactions
    Control premium: mean/median premium to unaffected share price

SPRINT 3C (Days 9–14): Sensitivity Analysis

  TASK-3.6: 2D Sensitivity Matrix Generator
    def sensitivity_matrix(
        base_wacc: float,
        base_tgr: float,
        wacc_range: list[float],  # e.g., [0.08, 0.09, 0.10, 0.11, 0.12]
        tgr_range: list[float],   # e.g., [0.015, 0.020, 0.025, 0.030, 0.035]
        dcf_function: callable,
    ) -> pd.DataFrame:
        matrix = pd.DataFrame(index=wacc_range, columns=tgr_range)
        for wacc in wacc_range:
            for tgr in tgr_range:
                matrix.loc[wacc, tgr] = dcf_function(wacc=wacc, tgr=tgr)
        return matrix

  TASK-3.7: Color-Coded Heatmap
    Apply background_gradient styling to Pandas DataFrame:
    matrix.style.background_gradient(cmap="RdYlGn", axis=None)
    Highlight base case cell with border

  TASK-3.8: Football Field Chart
    def plot_football_field(valuation_ranges: dict) -> plt.Figure:
        # valuation_ranges = {
        #   "DCF (Bear)": (low, high),
        #   "DCF (Base)": (low, high),
        #   "DCF (Bull)": (low, high),
        #   "EV/EBITDA Comps": (low, high),
        #   "EV/Revenue Comps": (low, high),
        #   "Precedent Transactions": (low, high),
        # }
        # Render as horizontal bar chart (broken bars)
        # Current trading price marked as vertical line
```

### 6.3 Phase Gate Criteria

- [x] Comps module pulls live data for 5+ real tickers without error
- [x] Graceful handling of missing yfinance data (no crash, warn user)
- [x] Sensitivity matrix renders with correct gradient styling
- [ ] Football field chart displays all 6 valuation ranges
- [x] Financial Domain Expert validates multiple calculations

---

## 7. Phase 4: LLM Narrative Engine

**Duration**: Week 6–9 (overlaps with Phase 3; 14 days)  
**Owner**: Engineer 1 (AI specialist)  
**Goal**: Unsloth-powered model generates professional, IB-quality narrative sections from structured valuation outputs.

### 7.1 Deliverables

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 4.1 | `llm/model_loader.py` | Loads Unsloth model reliably in < 90s |
| 4.2 | `llm/prompt_templates/` | Jinja2 templates for all 5 narrative sections |
| 4.3 | `llm/narrative_generator.py` | Generates all sections from structured inputs |
| 4.4 | `05_narrative_engine.ipynb` | Demo: full report narrative from DCF outputs |
| 4.5 | `llm/evaluator.py` | Scores narrative quality on 5 dimensions |

### 7.2 Technical Tasks

```
SPRINT 4A (Days 1–5): Model Loading & Prompt Engineering

  TASK-4.1: Robust Model Loader
    def load_model(
        model_name: str = "unsloth/mistral-7b-v0.3-bnb-4bit",
        max_seq_length: int = 4096,
    ) -> tuple[FastLanguageModel, AutoTokenizer]:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_length,
            dtype=None,  # Auto-detect
            load_in_4bit=True,
        )
        FastLanguageModel.for_inference(model)
        return model, tokenizer

  TASK-4.2: Prompt Templates (Jinja2)
    templates/executive_summary.j2:
      "You are a senior investment banking analyst...
       Company: {{ company_name }}
       Sector: {{ sector }}
       DCF Implied Value: ${{ dcf_value }}M ({{ dcf_low }}M – {{ dcf_high }}M range)
       Comps Implied Value: ${{ comps_value }}M
       Key Driver: {{ key_driver }}
       
       Write a 3-paragraph executive summary explaining the valuation..."

    templates/dcf_commentary.j2 — explains UFCF drivers
    templates/comps_commentary.j2 — explains trading multiple spread
    templates/risk_factors.j2 — 5 key risks with mitigation
    templates/investment_thesis.j2 — bull/bear/base case framing

  TASK-4.3: Template Renderer
    def render_prompt(template_name: str, context: dict) -> str:
        env = Environment(loader=FileSystemLoader("templates/"))
        template = env.get_template(f"{template_name}.j2")
        return template.render(**context)

SPRINT 4B (Days 6–10): Generation Pipeline

  TASK-4.4: Narrative Generator
    def generate_narrative(
        section: str,
        context: dict,
        max_new_tokens: int = 512,
        temperature: float = 0.3,  # Low temp for factual financial text
    ) -> str:
        prompt = render_prompt(section, context)
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                repetition_penalty=1.1,
                streamer=TextStreamer(tokenizer),  # Real-time output
            )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

  TASK-4.5: Full Report Narrative Orchestrator
    def generate_full_report(valuation_result: ValuationResult) -> ReportNarrative:
        context = build_context(valuation_result)
        return ReportNarrative(
            executive_summary=generate_narrative("executive_summary", context),
            dcf_commentary=generate_narrative("dcf_commentary", context),
            comps_commentary=generate_narrative("comps_commentary", context),
            risk_factors=generate_narrative("risk_factors", context),
            investment_thesis=generate_narrative("investment_thesis", context),
        )

SPRINT 4C (Days 11–14): Quality Control

  TASK-4.6: Narrative Evaluator
    Score each narrative on:
    1. Factual Grounding (0–10): Does every number cited match the model output?
    2. Professional Tone (0–10): Analyst-grade language?
    3. Completeness (0–10): All required elements present?
    4. Consistency (0–10): No contradictions across sections?
    5. Length Compliance (0–10): Within 200–400 words per section?

  TASK-4.7: Hallucination Guard
    def check_factual_grounding(narrative: str, facts: dict) -> list[str]:
        """Extract all numbers from narrative, verify each against facts dict."""
        cited_numbers = extract_numbers(narrative)
        for num in cited_numbers:
            if not is_close_to_any(num, facts.values(), tolerance=0.05):
                flag_hallucination(num, narrative)
```

### 7.3 Phase Gate Criteria

- [ ] Model loads and generates text on Colab T4 without OOM
- [ ] Executive Summary correctly cites DCF implied value within ±2% of computed value
- [ ] Hallucination guard catches > 80% of planted false numbers in test cases
- [ ] Narrative generation time < 60 seconds per section

---

## 8. Phase 5: Audit Trail & Output Engine

**Duration**: Week 8–10 (7 days)  
**Owner**: Engineer 1  
**Goal**: Every computation is logged immutably; all outputs export cleanly to Excel, JSON, and PDF.

### 8.1 Deliverables

| # | Deliverable | Acceptance Criteria |
|---|-------------|-------------------|
| 5.1 | `audit/trail.py` | Logs every step; exports to JSON |
| 5.2 | `export/excel_exporter.py` | Multi-sheet Excel with formatting |
| 5.3 | `export/json_exporter.py` | Structured JSON for API consumption |
| 5.4 | `export/pdf_generator.py` | PDF report from notebook |
| 5.5 | `06_outputs.ipynb` | Demo all export formats |

### 8.2 Excel Sheet Structure

```
Sheet 1: Cover Page          — Company name, date, analyst
Sheet 2: 3-Statement Model   — Historical IS, BS, CF (raw normalized)
Sheet 3: DCF Model           — Projections, UFCF, TV, EV bridge
Sheet 4: Comps Table         — All comp tickers, multiples, stats
Sheet 5: Transaction Comps   — Precedent transactions table
Sheet 6: Sensitivity WACC    — WACC vs TGR matrix (conditional formatting)
Sheet 7: Sensitivity Ops     — Revenue Growth vs EBITDA Margin
Sheet 8: Football Field      — Chart embedded in sheet
Sheet 9: Audit Trail         — Full step-by-step calculation log
Sheet 10: Assumptions        — All driver inputs with scenario toggle
```

### 8.3 Phase Gate Criteria

- [x] Excel exports all 10 sheets without corruption
- [x] Audit trail JSON includes every DCF step with formula string
- [ ] PDF generates and downloads to Drive successfully
- [x] All numeric values in Excel match in-notebook computed values exactly

---

## 9. Phase 6: Integration & End-to-End Testing

**Duration**: Week 10–11 (7 days)  
**Owner**: Full Team  
**Goal**: Run complete end-to-end pipeline for all 3 fixture companies. No manual intervention required.

### 9.1 Integration Test Matrix

| Test | Input | Expected Output |
|------|-------|----------------|
| INT-01 | TechCorp JSON → full DCF | EV within 5% of manual model |
| INT-02 | ManufactureCo CSV → full DCF | EV within 5% of manual model |
| INT-03 | RetailChain XLSX → full DCF | Negative UFCF handled gracefully |
| INT-04 | Imbalanced BS | Checker flags + plug suggested |
| INT-05 | Missing EBITDA field | Warning raised, not crash |
| INT-06 | 5 real tickers → comps | Multiples table generated |
| INT-07 | Full pipeline → Excel export | All 10 sheets valid |
| INT-08 | Full pipeline → narrative | 5 sections generated, no hallucinations |
| INT-09 | Sensitivity matrix (5×5) | Correct EV at base case cell |
| INT-10 | Football field chart | 6 bars displayed correctly |

---

## 10. Phase 7: MVP Hardening & Documentation

**Duration**: Week 11–12 (7 days)  
**Owner**: Full Team  

| Task | Owner | Effort |
|------|-------|--------|
| Write `README.md` with quickstart guide | Tech Lead | 1 day |
| Record 10-minute demo video | PM | 0.5 days |
| Write financial methodology documentation | Domain Expert | 2 days |
| Performance profiling and memory optimization | Engineer 1 | 1 day |
| Final QA pass on all notebooks | Full Team | 1 day |
| Stakeholder demo and sign-off | PM | 0.5 days |

---

## 11. Phase Gate Sign-off Table

| Phase | Gate Owner | Status |
|-------|-----------|--------|
| Phase 0 | Tech Lead | ✅ Complete |
| Phase 1 | Engineer 1 + Domain Expert | ✅ Complete |
| Phase 2 | Engineer 1/2 + Domain Expert | ✅ Complete |
| Phase 3 | Engineer 2 + Domain Expert | 🟡 Partial (football field pending) |
| Phase 4 | Engineer 1 + PM | 🟡 Scaffolded (LLM prompts + inference ready) |
| Phase 5 | Engineer 1 | 🟡 Partial (PDF pending) |
| Phase 6 | Full Team | ✅ Complete (40/40 tests passing) |
| Phase 7 | PM + Stakeholder | 🔲 In Progress |

---

*Version: 1.1 | Status: Active Development | Last Updated: 2026-02-23 | Owner: Product Manager*
