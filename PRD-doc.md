# Product Requirements Document (PRD)
## Financial Modeling & Valuation Agent
### Version 1.0 | Authored by: Product Manager

---

## 1. Product Vision

**Vision Statement**:  
To democratize institutional-grade financial valuation — making the analytical power of a Goldman Sachs associate available to any financial professional who can run a Google Colab notebook.

**The Problem**:  
A junior investment banking associate spends 3–5 days building a DCF model from scratch for each company. This time is consumed by manual data entry, formula construction, sensitivity analysis, and writing the narrative. Senior professionals are bottlenecked reviewing work that is 80% templated. Smaller funds, corporate development teams, and independent advisors lack the resources to do this work at all.

**The Solution**:  
An AI agent that accepts raw financial statements and produces a complete, audit-ready valuation report — including DCF, comparable company analysis, precedent transactions, sensitivity matrices, and a written executive summary — in under 6 minutes.

**Target Users**:  
- Junior investment banking analysts (primary)
- Corporate development / M&A teams (primary)
- Private equity associates (secondary)
- Independent financial advisors (secondary)
- Finance students and educators (tertiary)

---

## 2. Goals & Success Metrics

### 2.1 Business Goals

| Goal | Metric | Target |
|------|--------|--------|
| Reduce time-to-valuation | Time from data upload to full report | < 6 minutes (vs 3–5 days manual) |
| Match institutional quality | Financial Domain Expert score | ≥ 4.0/5.0 on methodology correctness |
| High adoption | % of beta users who run ≥ 3 valuations | ≥ 60% |
| Trust through transparency | % of users who review audit trail | ≥ 40% |
| Narrative quality | Human evaluator score (finance professional) | ≥ 3.5/5.0 |

### 2.2 Anti-Goals (What We Are Not Trying to Do)

- We are NOT trying to replace the judgment of a senior banker
- We are NOT building a trading or investment advice tool
- We are NOT trying to compete with Bloomberg Terminal in data richness
- We are NOT building a collaborative multi-user platform in V1

---

## 3. User Personas

### Persona 1: Alex — The Junior IB Analyst
- **Role**: 1st year analyst at a mid-market investment bank
- **Pain**: Spends 80% of time on mechanical modeling, 20% on actual analysis
- **Goal**: Build a credible first-draft model to show the VP within 24 hours
- **Technical comfort**: High with Excel; comfortable with Python notebooks
- **Use case**: Builds a DCF for a client pitch; uses the agent to get the first draft, then reviews and adjusts

### Persona 2: Priya — The Corporate Development Associate
- **Role**: Corp Dev team at a $500M revenue SaaS company
- **Pain**: Needs to evaluate 5–10 acquisition targets per quarter; no dedicated modeling staff
- **Goal**: Quick, defensible valuation for Go/No-Go decision
- **Technical comfort**: Moderate; can run a notebook with instructions
- **Use case**: Uploads target company's 10-K data; wants a one-page valuation summary to bring to the CFO

### Persona 3: Jordan — The Finance Student
- **Role**: MBA student, finance concentration
- **Pain**: Learning DCF by reading textbooks — no hands-on tool
- **Goal**: See a live, institutional-quality model and understand why each number is what it is
- **Technical comfort**: High; comfortable with Python
- **Use case**: Runs the agent on a company they know, then traces the audit trail to understand each formula

---

## 4. Feature Requirements

---

### FR-1: Data Ingestion

**FR-1.1** The system MUST accept financial data in JSON format matching the canonical schema.

**FR-1.2** The system MUST accept financial data in CSV format with automatic delimiter detection.

**FR-1.3** The system MUST accept financial data in Excel (.xlsx) format with automatic sheet and header detection.

**FR-1.4** The system MUST normalize all accepted formats into the canonical 3-Statement schema (Income Statement, Balance Sheet, Cash Flow Statement).

**FR-1.5** The system MUST support at minimum 3 years of historical financial data.

**FR-1.6** The system MUST warn the user (but not block) if fewer than 3 years of historical data are provided.

**FR-1.7** The system MUST map at least 15 common field-name aliases for each canonical field (e.g., "Total Revenue", "Net Sales", "Net Revenue", "Turnover" all map to `revenue`).

**FR-1.8** The system MUST flag GAAP vs. IFRS accounting standard if detectable.

**FR-1.9** The system MUST validate that Total Assets = Total Liabilities + Shareholders' Equity within a $0.01M tolerance.

**FR-1.10** If the balance sheet does not balance, the system MUST identify the discrepancy amount, attempt to identify the likely off-balance line item, and suggest a specific "Plug" value to reconcile it.

**FR-1.11** The system MUST NOT auto-correct financial data without explicit user confirmation.

---

### FR-2: Assumption Engine

**FR-2.1** The system MUST provide a user-facing interface to configure the following drivers:
- Revenue Growth Rate (per year, years 1–5 minimum)
- EBITDA Margin (flat or per-year)
- D&A as % of Revenue
- CapEx as % of Revenue
- Net Working Capital as % of Revenue
- Tax Rate
- Terminal Growth Rate
- Exit EV/EBITDA Multiple

**FR-2.2** The system MUST provide pre-configured Bear, Base, and Bull scenario presets.

**FR-2.3** When a scenario preset is selected, all relevant sliders MUST update to reflect the preset values.

**FR-2.4** The system MUST allow users to modify individual assumptions within a preset (creating a Custom scenario).

**FR-2.5** The system MUST save the current assumption set to Google Drive upon user request.

**FR-2.6** The system MUST allow loading of a previously saved assumption set from Google Drive.

**FR-2.7** The system MUST display a summary of the current assumption set at all times in the notebook.

---

### FR-3: DCF Valuation

**FR-3.1** The system MUST project Revenue, EBITDA, D&A, EBIT, NOPAT for at least 5 years.

**FR-3.2** The system MUST support a 10-year projection period (toggled by the user).

**FR-3.3** The system MUST calculate Unlevered Free Cash Flow (UFCF) for each projection year using the formula: `UFCF = NOPAT + D&A − CapEx − ΔNWC`.

**FR-3.4** The system MUST calculate WACC using the CAPM formula: `WACC = Ke×We + Kd(1−t)×Wd`.

**FR-3.5** The system MUST automatically fetch beta from yfinance if a ticker symbol is provided.

**FR-3.6** If beta cannot be fetched, the system MUST default to beta = 1.0 and warn the user.

**FR-3.7** The system MUST calculate Terminal Value using the Gordon Growth Model: `TV = UFCF_n × (1+g) / (WACC − g)`.

**FR-3.8** The system MUST calculate Terminal Value using the Exit Multiple method: `TV = EBITDA_n × exit_multiple`.

**FR-3.9** The system MUST allow the user to select which Terminal Value method to use.

**FR-3.10** The system MUST support a Mid-Year Convention toggle (discount UFCFs at 0.5, 1.5, etc.).

**FR-3.11** The system MUST compute Enterprise Value as the sum of discounted UFCFs and the discounted Terminal Value.

**FR-3.12** The system MUST compute Equity Value as `Enterprise Value − Net Debt`.

**FR-3.13** The system MUST compute Implied Share Price as `Equity Value / Diluted Shares Outstanding`.

**FR-3.14** The system MUST raise an error (not crash) if WACC ≤ Terminal Growth Rate (mathematically invalid Gordon Growth).

**FR-3.15** The system MUST display a warning (not block) if Equity Value is negative.

---

### FR-4: Comparable Companies Analysis

**FR-4.1** The system MUST accept a list of comparable company ticker symbols as input.

**FR-4.2** The system MUST retrieve LTM (Last Twelve Months) financial data for each ticker using yfinance.

**FR-4.3** The system MUST calculate EV/EBITDA, EV/Revenue, and P/E for each comparable company.

**FR-4.4** The system MUST calculate and display minimum, 25th percentile, median, 75th percentile, and maximum for each multiple across the comp set.

**FR-4.5** The system MUST apply the median and 25th/75th percentile multiples to the subject company's financial metrics to produce an implied EV range.

**FR-4.6** The system MUST handle missing or unavailable data for individual comps gracefully (skip ticker with warning, do not crash).

**FR-4.7** The system MUST require a minimum of 3 comparable companies for statistical validity.

**FR-4.8** The system MUST cache yfinance responses locally for 24 hours to avoid redundant API calls.

---

### FR-5: Precedent Transactions Analysis

**FR-5.1** The system MUST accept a manually provided table of precedent transactions in JSON or CSV format.

**FR-5.2** Required fields per transaction: Target Name, Acquirer Name, Transaction Date, Enterprise Value, Target Revenue, Target EBITDA.

**FR-5.3** The system MUST calculate EV/EBITDA and EV/Revenue for each transaction.

**FR-5.4** The system MUST calculate transaction multiple statistics (min, median, max, 25th, 75th).

**FR-5.5** The system MUST apply median transaction multiples to the subject company to produce an implied EV range.

**FR-5.6** The system MUST calculate control premium statistics if an unaffected share price is provided.

---

### FR-6: Sensitivity Analysis

**FR-6.1** The system MUST generate a WACC vs. Terminal Growth Rate sensitivity matrix (minimum 5×5).

**FR-6.2** The system MUST generate a Revenue Growth vs. EBITDA Margin sensitivity matrix (minimum 5×5).

**FR-6.3** The system MUST render sensitivity matrices with color-coded gradient (green = higher value, red = lower value).

**FR-6.4** The base case cell in every sensitivity matrix MUST be visually distinguished (e.g., bold border).

**FR-6.5** The system MUST generate a "Football Field" chart displaying all valuation ranges side by side.

**FR-6.6** The Football Field chart MUST include ranges from: DCF Bear/Base/Bull, EV/EBITDA Comps (25th–75th), EV/Revenue Comps (25th–75th), and Precedent Transactions (25th–75th).

**FR-6.7** If the current trading price of the subject company is available, the Football Field chart MUST display it as a reference line.

---

### FR-7: Audit Trail

**FR-7.1** The system MUST log every numerical computation with: step name, formula string, all input values, output value, and unit of measure.

**FR-7.2** The audit trail MUST be viewable as a formatted table within the notebook.

**FR-7.3** The audit trail MUST be exportable to JSON format.

**FR-7.4** The audit trail MUST be included as a dedicated sheet in the Excel export.

**FR-7.5** Audit trail entries MUST be immutable once logged (append-only).

**FR-7.6** Each audit trail session MUST include: session ID, timestamp, company name, and assumption set identifier.

---

### FR-8: LLM Narrative Engine

**FR-8.1** The system MUST generate an Executive Summary narrative of 200–400 words explaining the valuation conclusion.

**FR-8.2** The Executive Summary MUST cite the DCF-implied Enterprise Value, Equity Value, and implied share price.

**FR-8.3** The system MUST generate a DCF Commentary section explaining the key UFCF drivers.

**FR-8.4** The system MUST generate a Risk Factors section listing at least 5 key risks.

**FR-8.5** The LLM narrative MUST only cite numbers that appear in the computed output (anti-hallucination constraint).

**FR-8.6** The system MUST include a hallucination guard that flags any number in the narrative that does not match the model output within ±5%.

**FR-8.7** If the LLM fails to generate (OOM, timeout), the system MUST continue with all quantitative outputs and insert a placeholder in the narrative section.

**FR-8.8** Narrative generation MUST use Unsloth with a 4-bit quantized language model.

---

### FR-9: Output & Export

**FR-9.1** The system MUST export all valuation outputs to a structured Excel workbook (.xlsx) with 10 defined sheets.

**FR-9.2** The system MUST export all valuation outputs to a structured JSON file.

**FR-9.3** Both Excel and JSON exports MUST be automatically saved to Google Drive.

**FR-9.4** The Excel workbook MUST include the Football Field chart as an embedded image.

**FR-9.5** The Excel workbook MUST include conditional color formatting on all sensitivity matrices.

**FR-9.6** All exported numerical values MUST exactly match the in-session computed values (no rounding discrepancy > $0.001M).

**FR-9.7** The JSON export MUST include: all raw inputs, all normalized financial data, all assumptions, all computed valuation outputs, and the full audit trail.

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Requirement | Target |
|-------------|--------|
| Full pipeline time (without LLM) | ≤ 60 seconds on Colab T4 |
| Full pipeline time (with LLM narrative) | ≤ 6 minutes on Colab T4 |
| LLM model load time | ≤ 90 seconds |
| Excel export time | ≤ 30 seconds |
| Peak memory usage (CPU RAM) | ≤ 8 GB |
| Peak VRAM usage (with LLM) | ≤ 12 GB |

### 5.2 Reliability

| Requirement | Target |
|-------------|--------|
| Crash rate on valid input | 0% (no crashes, only typed errors) |
| Correct handling of missing optional fields | 100% (warn and continue) |
| DCF accuracy vs. manual model | ≤ 0.1% tolerance |
| Balance sheet check false negative rate | 0% (must detect all imbalances > $0.01M) |

### 5.3 Usability

| Requirement | Target |
|-------------|--------|
| Time for a new user to run first valuation | ≤ 15 minutes (with documentation) |
| Comprehensibility of error messages | All error messages must suggest corrective action |
| Widget responsiveness | Assumption change → updated summary in ≤ 2 seconds |

### 5.4 Data Integrity

| Requirement | Target |
|-------------|--------|
| Float precision for all financial calculations | float64 (no float32) |
| Rounding policy | Round only at display layer, not intermediate calculations |
| Audit trail completeness | 100% of numerical outputs must appear in audit trail |

---

## 6. Constraints

| Constraint | Detail |
|------------|--------|
| Runtime | Google Colab Pro+ only |
| No production server | V1 is notebook-only |
| No external data licensing | yfinance only (free) |
| LLM must fit T4 VRAM | 4-bit quantization required |
| Single-user session | No multi-user concurrent access |
| Colab Python version | Python 3.10 |

---

## 7. User Journey (Primary Flow)

```
Step 1: PREPARE DATA
  User collects financial statements from any source
  Formats as JSON, CSV, or Excel
  ↓
Step 2: OPEN NOTEBOOK
  User opens 01_data_ingestion.ipynb in Colab
  Runs setup cells (installs dependencies, mounts Drive)
  ↓
Step 3: UPLOAD DATA
  User clicks "Upload" button (Colab file picker)
  Or specifies a Drive path
  ↓
Step 4: REVIEW NORMALIZATION
  System shows formatted 3-Statement table
  Flags any warnings (missing fields, GAAP/IFRS, etc.)
  If balance sheet imbalanced: shows delta and plug suggestion
  ↓
Step 5: SET ASSUMPTIONS
  User opens 02_dcf_model.ipynb
  Selects scenario (Bear/Base/Bull) or customizes
  Reviews WACC inputs (auto-fetches beta if ticker provided)
  ↓
Step 6: RUN DCF
  Clicks "Run DCF" button
  System projects 5-year model and computes EV in < 10 seconds
  ↓
Step 7: REVIEW COMPS
  Opens 03_comps_analysis.ipynb
  Enters comparable ticker list
  System fetches data and shows comps table with stats
  ↓
Step 8: REVIEW SENSITIVITY
  Opens 04_sensitivity_analysis.ipynb
  Views WACC×TGR matrix and Football Field chart
  ↓
Step 9: GENERATE NARRATIVE
  Opens 05_narrative_engine.ipynb
  Clicks "Generate Report"
  LLM writes executive summary and commentary (~2 minutes)
  ↓
Step 10: EXPORT
  Opens 06_outputs.ipynb
  Clicks "Export All"
  Excel, JSON, PDF saved to Drive
  User downloads or shares from Drive
```

---

## 8. Acceptance Criteria Summary

| Feature Area | Primary AC |
|-------------|-----------|
| Data Ingestion | All 3 fixture companies normalize without error |
| Balance Sheet Check | Correctly identifies planted $50M imbalance and suggests plug |
| DCF | Implied EV within ±0.1% of manually computed Excel model |
| WACC | Matches manual calculation using same inputs |
| Comps | Median EV/EBITDA from 5 tickers calculated correctly |
| Sensitivity Matrix | Base case cell matches standalone DCF within ±0.1% |
| Football Field | All 6 valuation ranges displayed with correct scaling |
| Audit Trail | Every DCF step traceable from inputs to output |
| Narrative | No hallucinated numbers; all figures cite computed values |
| Excel Export | 10 sheets present, all values match in-session computations |
| Performance | Full pipeline (with LLM) < 6 minutes on T4 |

---

## 9. Release Criteria

The MVP is approved for release when ALL of the following are true:

- [ ] All 17 Must-Have features implemented and tested
- [ ] All 10 integration tests in `test_integration.py` pass
- [ ] Financial Domain Expert signs off on methodology
- [ ] A non-engineer (finance analyst) successfully runs end-to-end without engineering help
- [ ] No P0 or P1 bugs open
- [ ] Documentation complete (README + financial methodology guide)
- [ ] PM demo to stakeholders completed

---

*Version: 1.0 | Status: Draft | Owner: Product Manager*
