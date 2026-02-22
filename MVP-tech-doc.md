# MVP Technical Document
## Financial Modeling & Valuation Agent
### Version 1.0 | Google Colab + Unsloth Stack

---

## 1. Executive Technical Summary

The **Financial Modeling & Valuation Agent** is an AI-augmented notebook application that automates the production of institutional-grade company valuations. The MVP delivers a fully functional, end-to-end pipeline from raw financial data ingestion to a written valuation report — running entirely within Google Colab Pro+ with no server infrastructure required.

**The core technical bet**: By combining Unsloth's 4-bit quantized LLM inference (for narrative generation) with deterministic Python financial computation (for modeling), we can produce a valuation report that matches what a junior IB analyst would produce in 3–5 days — in under 5 minutes.

---

## 2. MVP Scope

The MVP answers one question: **"What is this company worth?"**

It does so via three valuation methods:
1. **DCF Analysis** — Discounted Cash Flow using Unlevered Free Cash Flow
2. **Public Comparable Companies** — Trading multiple benchmarking
3. **Precedent Transactions** — M&A deal multiple benchmarking

And produces three output artifacts:
1. **Structured Excel Workbook** — 10-sheet model
2. **JSON Export** — API-ready data structure
3. **Written Report Narrative** — LLM-generated, fact-grounded

---

## 3. Technical Stack

### 3.1 Complete Stack Map

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│           ipywidgets (Colab notebook cells)              │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                  ORCHESTRATION LAYER                     │
│         Python Notebooks (.ipynb) — 7 notebooks          │
└──────┬──────────┬──────────┬──────────┬─────────────────┘
       │          │          │          │
┌──────▼──┐ ┌────▼────┐ ┌───▼───┐ ┌────▼────┐
│Ingestion│ │ DCF     │ │ Comps │ │ LLM     │
│Module   │ │ Engine  │ │+Trans │ │Narrative│
│(pandas) │ │(numpy)  │ │(yfinance)│(Unsloth)│
└──────┬──┘ └────┬────┘ └───┬───┘ └────┬────┘
       │          │          │          │
┌──────▼──────────▼──────────▼──────────▼─────┐
│              AUDIT TRAIL ENGINE              │
│    Every computation logged with formula     │
└──────────────────────────┬──────────────────┘
                           │
┌──────────────────────────▼──────────────────┐
│              OUTPUT ENGINE                  │
│     Excel (openpyxl) │ JSON │ PDF           │
└──────────────────────────┬──────────────────┘
                           │
┌──────────────────────────▼──────────────────┐
│          PERSISTENCE (Google Drive)         │
│  /outputs/ │ /logs/ │ /data/ │ /models/     │
└─────────────────────────────────────────────┘
```

### 3.2 Technology Decisions

| Component | Technology | Why This Choice |
|-----------|-----------|----------------|
| Runtime | Google Colab Pro+ | Zero infrastructure; GPU on demand; free for prototyping |
| Language | Python 3.10 | Universal in data science/finance; rich ecosystem |
| Data manipulation | pandas + numpy | Industry standard; battle-tested; float64 precision |
| Financial data | yfinance | Free; covers S&P 500 comps; no API key |
| LLM inference | Unsloth (Mistral-7B 4-bit) | 2× faster than HuggingFace; fits T4 VRAM; free |
| UI | ipywidgets | Native Colab support; no frontend build needed |
| Excel export | openpyxl | Pure Python; no LibreOffice dependency |
| Persistence | Google Drive | Universal access; survives Colab resets |
| Templating | Jinja2 | Separates prompts from code; version-controllable |
| Testing | pytest | Standard; lightweight; runs in Colab |

---

## 4. MVP Feature List

### 4.1 Must Have (MVP Blocker)

| # | Feature | Module | Effort |
|---|---------|--------|--------|
| M1 | JSON/CSV/Excel financial data input | Ingestion | 3 days |
| M2 | 3-Statement normalization | Ingestion | 3 days |
| M3 | Balance sheet integrity check | Ingestion | 1 day |
| M4 | Assumption engine with ipywidgets | Assumptions | 2 days |
| M5 | Bear/Base/Bull scenario presets | Assumptions | 1 day |
| M6 | UFCF projection (5-year) | DCF | 3 days |
| M7 | WACC calculation | DCF | 2 days |
| M8 | Terminal Value (Gordon Growth + Exit Multiple) | DCF | 2 days |
| M9 | Enterprise Value & Equity Value bridge | DCF | 1 day |
| M10 | Public Comps (EV/EBITDA, EV/Revenue, P/E) | Comps | 3 days |
| M11 | Precedent Transactions table | Transactions | 2 days |
| M12 | WACC×TGR Sensitivity Matrix | Sensitivity | 2 days |
| M13 | Football Field chart | Sensitivity | 1 day |
| M14 | Full Audit Trail with formula logging | Audit | 2 days |
| M15 | Executive Summary narrative (Unsloth) | LLM | 3 days |
| M16 | Excel export (10 sheets) | Export | 3 days |
| M17 | JSON export | Export | 1 day |

**Total Estimated Effort**: ~35 engineer-days (~7 weeks for 1 engineer)

### 4.2 Should Have (Target for MVP)

| # | Feature | Effort |
|---|---------|--------|
| S1 | 10-year projection toggle | 0.5 days |
| S2 | Mid-year convention toggle | 0.5 days |
| S3 | Risk factors narrative section | 1 day |
| S4 | PDF report export | 2 days |
| S5 | Drive auto-save for all outputs | 0.5 days |
| S6 | yfinance response caching | 1 day |

### 4.3 Won't Have (Explicitly Excluded from MVP)

- Real-time Bloomberg/Refinitiv data
- PDF annual report parsing (OCR)
- SEC EDGAR automated filing ingestion
- Portfolio-level multi-company analysis
- Monte Carlo simulation
- Production web server / API
- User authentication

---

## 5. Data Flow Architecture

```
INPUT
  User provides raw financial data (JSON / CSV / Excel)
  ↓
INGESTION
  loader.py reads file → dict
  normalizer.py maps fields to canonical schema → FinancialStatements
  validator.py checks internal consistency → ValidationReport
  balance_sheet_checker.py verifies A = L + E → BalanceCheckResult
  ↓
ASSUMPTION ENGINE
  User adjusts sliders (or accepts defaults) → AssumptionSet
  Scenario selected (Bear / Base / Bull) → AssumptionSet
  ↓
DCF ENGINE
  project_income_statement() → ProjectionTable
  calculate_ufcf() → [UFCF_1, ..., UFCF_n]
  calculate_wacc() → WACCResult
  calculate_terminal_value() → float
  calculate_equity_value() → ValuationResult
  ↓
COMPS ENGINE
  fetch_comp_data(tickers) → [CompData]  [yfinance]
  calculate_comps_stats() → CompsStats
  apply_comps_multiples() → CompsValuation
  ↓
TRANSACTIONS ENGINE
  parse_transaction_table() → [Transaction]
  calculate_transaction_stats() → TransactionStats
  apply_transaction_multiples() → TransactionValuation
  ↓
SENSITIVITY ENGINE
  sensitivity_matrix(WACC × TGR) → DataFrame
  plot_football_field(all ranges) → Figure
  ↓
AUDIT TRAIL
  AuditTrail.log() called at every step above
  AuditTrail.export_json() → audit_trail.json
  ↓
LLM NARRATIVE (Unsloth)
  build_context(ValuationResult + Comps + Transactions) → dict
  generate_narrative("executive_summary", context) → str
  generate_narrative("dcf_commentary", context) → str
  generate_narrative("risk_factors", context) → str
  check_factual_grounding(narrative, facts) → flags
  ↓
OUTPUT ENGINE
  export_to_excel(result, normalized, path) → .xlsx (10 sheets)
  export_to_json(result, path) → .json
  generate_pdf(result, path) → .pdf
  Save all to Google Drive /outputs/
```

---

## 6. Key Technical Decisions & Rationale

### 6.1 Why Unsloth Over Raw HuggingFace Transformers?

Unsloth provides 2× faster inference on the same hardware through:
- Triton-based custom CUDA kernels
- Optimized attention computation (RoPE, GQA)
- 4-bit quantization (NF4/BnB) that maintains quality

For a T4 GPU (15 GB VRAM), Mistral-7B in 4-bit consumes ~4.5 GB leaving 10+ GB headroom for the KV cache and intermediate activations. Raw HuggingFace with float16 would require ~14 GB — leaving almost no headroom.

### 6.2 Why Deterministic Python for Financials (Not LLM)?

Financial calculations must be:
- **Reproducible**: Same inputs must always produce same outputs
- **Auditable**: Every formula must be traceable
- **Precise**: float64, not the lossy approximations of LLM arithmetic

LLMs are provably unreliable for multi-step arithmetic. We use the LLM only for what it excels at: transforming structured numbers into professional prose.

### 6.3 Why Not Use a Real Database?

In V1, all state is serialized to JSON/pickle on Google Drive. Reasons:
- Zero setup time (no PostgreSQL install in Colab)
- Single user: no concurrent access conflict
- Financial models are run once, not queried repeatedly
- Drive provides sufficient persistence and sharing

### 6.4 Why yfinance Over a Paid Data Provider?

MVP constraint: zero licensing cost. yfinance covers the most common use case (US-listed public comps) for free. The architecture is provider-agnostic — replacing yfinance with a Bloomberg/Capital IQ connector in V2 requires only modifying `comps/fetcher.py`.

---

## 7. LLM Prompt Architecture

### 7.1 The "Financial Analyst Persona" System Prompt

```
You are a senior investment banking analyst with 10 years of experience at 
Goldman Sachs and Morgan Stanley. You are writing a section of an internal 
valuation report for a client. Your writing style is:
- Direct, factual, and quantitative
- Free of hyperbole and marketing language
- Grounded only in the financial data provided
- Structured with clear topic sentences
- Professional but accessible to a CFO-level reader

CRITICAL: You must ONLY cite numbers that appear in the structured data 
provided below. If a number is not in the data, do not include it.
```

### 7.2 Temperature Strategy

| Section | Temperature | Rationale |
|---------|------------|-----------|
| Executive Summary | 0.3 | High factual accuracy required |
| DCF Commentary | 0.2 | Very precise, formula-driven |
| Risk Factors | 0.5 | Moderate creativity for diverse risks |
| Investment Thesis | 0.4 | Narrative but grounded |
| Comps Commentary | 0.25 | Multiple-driven, precise |

---

## 8. Error Handling Hierarchy

```
Level 1 — Input Validation (blocks computation):
  IngestionError: Invalid file format, missing required sections
  BalanceSheetError: Imbalance > $0.01M with no auto-correction

Level 2 — Computation Warnings (continues with flag):
  NegativeEBITDA: Flagged in output, DCF continues
  MissingBeta: Default 1.0 used, warning displayed
  NegativeUFCF: Flagged in sensitivity notes

Level 3 — Output Warnings (report generated, noted):
  NegativeEquityValue: Flagged in report, share price shown as N/A
  HallucinationFlag: Narrative number doesn't match model output

Level 4 — Fatal Errors (session must restart):
  OOMError: GPU out of memory → Switch to A100 runtime
  DriveNotMounted: All outputs fail → Remount Drive
```

---

## 9. Performance Benchmarks (Target)

| Operation | Target Time | Runtime |
|-----------|------------|---------|
| File ingestion + normalization | < 5 seconds | CPU |
| Full DCF (5-year, 3 scenarios) | < 10 seconds | CPU |
| Comps fetch (10 tickers) | < 30 seconds | CPU + network |
| Sensitivity matrix (5×5) | < 5 seconds | CPU |
| Football field chart render | < 3 seconds | CPU |
| LLM model load | < 90 seconds | T4 GPU |
| Executive summary generation | < 45 seconds | T4 GPU |
| Full narrative (5 sections) | < 4 minutes | T4 GPU |
| Excel export (10 sheets) | < 15 seconds | CPU |
| **Total pipeline (with LLM)** | **< 6 minutes** | T4 GPU |
| **Total pipeline (without LLM)** | **< 60 seconds** | CPU |

---

## 10. MVP Success Criteria

The MVP is considered complete when ALL of the following are true:

| Criterion | Verification Method |
|-----------|-------------------|
| DCF output matches manual Excel model within ±0.1% | Cross-validation test |
| All 3 fixture companies process without error | Integration test suite |
| Balance sheet checker catches all planted imbalances | Unit test |
| Executive summary cites correct valuation figures | Hallucination guard check |
| Excel export has 10 correctly formatted sheets | openpyxl validation |
| Full pipeline runs < 6 minutes on Colab T4 | Timed integration test |
| Financial Domain Expert approves methodology | Expert sign-off |
| A junior analyst can run the pipeline without engineering help | User acceptance test |

---

*Version: 1.0 | Status: Draft | Owner: Tech Lead + PM*
