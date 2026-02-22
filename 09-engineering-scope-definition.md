# 09 — Engineering Scope Definition
### Financial Modeling & Valuation Agent | Colab + Unsloth Stack

---

## 1. Document Purpose

This document establishes the **hard boundary** of what engineers will and will not build in the first release. Every feature, module, and integration is explicitly classified as **IN SCOPE**, **OUT OF SCOPE**, or **FUTURE PHASE**. No code may be written for anything classified as Out of Scope without formal scope-change approval from the Product Manager.

> **Stack Context**: All compute runs on **Google Colab Pro+** with **Unsloth** for fine-tuned LLM inference. There is no persistent server. The primary interface is a **Jupyter Notebook UI** backed by Python modules.

---

## 2. Scope Classification System

| Label | Meaning |
|-------|---------|
| 🟢 IN SCOPE | Must be built and tested before any release |
| 🟡 CONDITIONAL | Built only if a core dependency is completed ahead of schedule |
| 🔴 OUT OF SCOPE | Explicitly excluded from this engagement |
| 🔵 FUTURE PHASE | Planned but deferred to Phase 2+ |

---

## 3. Module-by-Module Scope Declaration

---

### 3.1 Data Ingestion & Normalization Engine

**3-Statement Normalizer**

| Feature | Scope | Notes |
|---------|-------|-------|
| Accept raw JSON financial data (Income Statement, Balance Sheet, Cash Flow) | 🟢 IN SCOPE | Primary input format |
| Accept CSV uploads via Colab file upload widget | 🟢 IN SCOPE | `files.upload()` interface |
| Parse unstructured Excel (.xlsx) with auto-header detection | 🟢 IN SCOPE | `openpyxl` + `pandas` |
| Normalize all inputs to a canonical internal schema (see DB Schema doc) | 🟢 IN SCOPE | Required for all downstream modules |
| Accept direct PDF uploads of annual reports and auto-extract financials | 🔵 FUTURE PHASE | Requires advanced OCR pipeline |
| Live scraping of SEC EDGAR for 10-K / 10-Q filings | 🔵 FUTURE PHASE | API rate limiting complexity |
| Real-time Bloomberg / Refinitiv data feed | 🔴 OUT OF SCOPE | Requires enterprise licensing |
| Multi-currency normalization (auto FX conversion) | 🟡 CONDITIONAL | Only if core normalizer finishes early |
| GAAP vs. IFRS flag detection and adjustment | 🟢 IN SCOPE | Must flag; adjustment logic is Phase 2 |

**Balance Sheet Integrity Check**

| Feature | Scope | Notes |
|---------|-------|-------|
| Auto-verify: Total Assets = Total Liabilities + Shareholders' Equity | 🟢 IN SCOPE | Hard gate; blocks downstream if fails |
| Identify and surface the discrepancy line item | 🟢 IN SCOPE | Must name the specific row |
| Suggest a "Plug" entry to reconcile the balance sheet | 🟢 IN SCOPE | Common practice in IB |
| Auto-correct the balance sheet without user confirmation | 🔴 OUT OF SCOPE | Dangerous; never auto-correct financials |

---

### 3.2 Assumption & Drivers Engine

| Feature | Scope | Notes |
|---------|-------|-------|
| Interactive widget for Revenue Growth Rate (Year 1–10) | 🟢 IN SCOPE | `ipywidgets` sliders |
| Interactive widget for EBITDA Margin assumption | 🟢 IN SCOPE | Per-year or flat |
| Interactive widget for CapEx-to-Sales ratio | 🟢 IN SCOPE | Key for UFCF |
| Interactive widget for D&A as % of Revenue | 🟢 IN SCOPE | Needed for EBITDA → EBIT bridge |
| Interactive widget for Working Capital as % of Revenue | 🟢 IN SCOPE | For UFCF computation |
| Interactive widget for Tax Rate | 🟢 IN SCOPE | NOPAT calculation |
| Scenario Manager (Bear / Base / Bull) presets | 🟢 IN SCOPE | Three named assumption sets |
| Monte Carlo simulation on assumptions | 🔵 FUTURE PHASE | Statistical distribution engine |
| AI-generated assumption benchmarks from industry data | 🟡 CONDITIONAL | If Unsloth fine-tune is complete |
| Save/load assumption profiles from Google Drive | 🟢 IN SCOPE | JSON serialization to Drive |

---

### 3.3 DCF Valuation Module

| Feature | Scope | Notes |
|---------|-------|-------|
| 5-year projection of Revenue, EBITDA, EBIT, NOPAT | 🟢 IN SCOPE | Standard IB model |
| 10-year projection (extended model toggle) | 🟢 IN SCOPE | Toggle in UI |
| Unlevered Free Cash Flow (UFCF) computation | 🟢 IN SCOPE | NOPAT + D&A – CapEx – ΔNWC |
| WACC calculation (Ke, Kd, beta, risk-free rate inputs) | 🟢 IN SCOPE | Manual inputs in V1 |
| Terminal Value — Gordon Growth Model | 🟢 IN SCOPE | TV = UFCF_n × (1+g) / (WACC–g) |
| Terminal Value — Exit EV/EBITDA Multiple | 🟢 IN SCOPE | TV = EBITDA_n × Multiple |
| Enterprise Value and Equity Value bridge | 🟢 IN SCOPE | EV – Net Debt = Equity Value |
| Implied Share Price calculation | 🟢 IN SCOPE | Equity Value / Diluted Shares |
| Discount factors and PV of each year's UFCF (Audit Trail) | 🟢 IN SCOPE | Full table, cell-level trace |
| Mid-year convention toggle | 🟢 IN SCOPE | Common in DCF |
| Auto-WACC from CAPM (pulling beta from yfinance) | 🟢 IN SCOPE | `yfinance` library |
| Real-time risk-free rate from Fed API | 🟡 CONDITIONAL | If API is reliably accessible in Colab |

---

### 3.4 Comparable Companies (Public Comps) Module

| Feature | Scope | Notes |
|---------|-------|-------|
| Accept a list of comparable ticker symbols as input | 🟢 IN SCOPE | User provides list |
| Pull LTM financials (Revenue, EBITDA, Earnings) via yfinance | 🟢 IN SCOPE | `yfinance` in Colab |
| Calculate P/E, EV/EBITDA, EV/Revenue for each comp | 🟢 IN SCOPE | Standard trading multiples |
| Calculate 25th, median, 75th percentile of each multiple | 🟢 IN SCOPE | Comps table summary stats |
| Apply median/mean multiples to subject company metrics | 🟢 IN SCOPE | Implied valuation range |
| Display formatted comps table | 🟢 IN SCOPE | Pandas DataFrame + Excel export |
| Pull EV/Sales, EV/EBIT, Price/Book as secondary multiples | 🟢 IN SCOPE | Supplementary |
| Auto-screen for comparable companies by SIC code | 🔵 FUTURE PHASE | Requires screener API |
| Consensus analyst estimates integration | 🔵 FUTURE PHASE | Requires paid data provider |
| NTM (Next Twelve Months) multiples | 🟡 CONDITIONAL | yfinance forward estimates availability |

---

### 3.5 Precedent Transactions Module

| Feature | Scope | Notes |
|---------|-------|-------|
| Accept manually input transaction table (target, acquirer, date, EV, EBITDA, Revenue) | 🟢 IN SCOPE | Manual JSON/CSV |
| Calculate EV/EBITDA, EV/Revenue for each transaction | 🟢 IN SCOPE | |
| Calculate control premium statistics | 🟢 IN SCOPE | Implied premium over trading price |
| Apply transaction multiples to subject company | 🟢 IN SCOPE | Implied valuation range |
| Auto-pull M&A deals from public databases | 🔴 OUT OF SCOPE | No free reliable API exists |
| Precedent transaction screening by industry | 🔵 FUTURE PHASE | |

---

### 3.6 Sensitivity Analysis Module

| Feature | Scope | Notes |
|---------|-------|-------|
| WACC vs. Terminal Growth Rate sensitivity matrix (2D grid) | 🟢 IN SCOPE | Classic DCF sensitivity |
| Revenue Growth vs. EBITDA Margin sensitivity matrix | 🟢 IN SCOPE | Operating assumption sensitivity |
| Entry Multiple vs. Exit Multiple sensitivity | 🟢 IN SCOPE | For comps-based valuation |
| Render sensitivity matrix as styled Pandas DataFrame | 🟢 IN SCOPE | Color-coded heat map |
| "Football Field" chart (horizontal bar chart of valuation ranges) | 🟢 IN SCOPE | `matplotlib` |
| Export sensitivity tables to Excel with conditional formatting | 🟢 IN SCOPE | `openpyxl` with color scales |
| Interactive 3D sensitivity surface plot | 🔵 FUTURE PHASE | `plotly` 3D |
| Tornado chart (single-variable sensitivity) | 🟡 CONDITIONAL | |

---

### 3.7 LLM / AI Narrative Engine (Unsloth)

| Feature | Scope | Notes |
|---------|-------|-------|
| Load fine-tuned model via Unsloth (4-bit quantization) | 🟢 IN SCOPE | Core tech requirement |
| Generate Executive Summary narrative from financial outputs | 🟢 IN SCOPE | 200–400 word professional narrative |
| Generate Analyst Commentary per valuation section | 🟢 IN SCOPE | DCF, Comps, Transactions sections |
| Generate risk factors and key assumptions disclosure | 🟢 IN SCOPE | Standard report section |
| Prompt template system for reproducible outputs | 🟢 IN SCOPE | Jinja2 templates |
| Fine-tune base model on IB research report corpus | 🔵 FUTURE PHASE | Data curation required |
| RAG over proprietary company documents | 🔵 FUTURE PHASE | Vector DB integration |
| Multi-turn chat interface with the valuation model | 🟡 CONDITIONAL | |
| Real-time streaming output from LLM | 🟢 IN SCOPE | Unsloth streaming tokens |

---

### 3.8 Audit Trail Engine

| Feature | Scope | Notes |
|---------|-------|-------|
| Log every computed value with its source formula and input values | 🟢 IN SCOPE | Immutable calculation log |
| Display audit trail as structured table in notebook | 🟢 IN SCOPE | |
| Link audit trail entries to specific report sections | 🟢 IN SCOPE | Reference IDs |
| Export full audit trail to JSON | 🟢 IN SCOPE | Machine-readable |
| Hash-sign each audit trail entry for tamper detection | 🟡 CONDITIONAL | SHA-256 per row |
| Version history of assumption changes | 🔵 FUTURE PHASE | Git-like state tracking |

---

### 3.9 Output & Export Engine

| Feature | Scope | Notes |
|---------|-------|-------|
| Export full model to structured Excel (.xlsx) with multiple sheets | 🟢 IN SCOPE | `openpyxl` |
| Export all data to JSON | 🟢 IN SCOPE | API-ready structure |
| Generate PDF report from notebook | 🟢 IN SCOPE | `nbconvert` or `reportlab` |
| Auto-download to Google Drive | 🟢 IN SCOPE | `google.colab.drive` |
| Generate PowerPoint presentation | 🔵 FUTURE PHASE | `python-pptx` |
| Interactive HTML report (standalone) | 🟡 CONDITIONAL | `plotly` HTML export |
| Branded Word document (.docx) output | 🔵 FUTURE PHASE | |

---

## 4. Non-Functional Scope

| Requirement | Scope | Target |
|-------------|-------|--------|
| Full model run time (no LLM) | 🟢 IN SCOPE | < 30 seconds on Colab T4 |
| Full model run time (with LLM narrative) | 🟢 IN SCOPE | < 3 minutes on Colab T4 |
| Colab session stability (no OOM crashes) | 🟢 IN SCOPE | Peak RAM < 12 GB |
| Code documentation (inline + docstrings) | 🟢 IN SCOPE | Every public function |
| Unit test coverage | 🟢 IN SCOPE | ≥ 80% on computation modules |
| Production deployment to cloud server | 🔴 OUT OF SCOPE | Colab only in V1 |
| Multi-user concurrent access | 🔴 OUT OF SCOPE | Single-user notebook |
| User authentication system | 🔴 OUT OF SCOPE | Colab handles identity |

---

## 5. Explicit Out-of-Scope Boundaries

The following are **explicitly excluded** and must not be built, prototyped, or scaffolded:

1. **Real-time market data feeds** (Bloomberg, Refinitiv, S&P Capital IQ) — enterprise licensing required
2. **Automated SEC filing ingestion** — out of scope for V1; manual data entry only
3. **Portfolio-level analysis** (multiple companies simultaneously) — single company per session
4. **Options/derivatives pricing** — not a valuation agent feature
5. **Broker-dealer regulatory compliance features** — out of legal scope
6. **Multi-user collaboration** — Colab is single-user
7. **Mobile application** — web/desktop only via Colab
8. **Production API server** — no FastAPI/Flask deployment in V1

---

## 6. Scope Change Process

Any request to bring an Out-of-Scope item into scope requires:

1. Written request to Product Manager with business justification
2. Impact assessment from Tech Lead (time, cost, risk)
3. Product Manager approval
4. Updated scope table version (v1.1, v1.2, etc.)

---

## 7. Engineering Constraints (Given)

| Constraint | Detail |
|-----------|--------|
| Runtime Environment | Google Colab Pro+ only |
| Primary Language | Python 3.10+ |
| LLM Framework | Unsloth (4-bit quantization, QLoRA) |
| Base Model | Mistral-7B or LLaMA-3-8B (TBD by fine-tune eval) |
| GPU Budget | 1× T4 (15 GB VRAM) or 1× A100 (40 GB VRAM) |
| Package Manager | pip (Colab native) |
| Storage | Google Drive (mounted at /content/drive) |
| No external database | All state in-memory or Drive-serialized JSON/pickle |

---

## 8. Scope Sign-off

| Role | Name | Sign-off Required |
|------|------|------------------|
| Product Manager | — | ✅ Before Sprint 1 |
| Tech Lead | — | ✅ Before Sprint 1 |
| Financial Domain Expert | — | ✅ Before Sprint 1 |
| Stakeholder / Client | — | ✅ Before Sprint 1 |

---

*Version: 1.0 | Status: Draft | Owner: Product Manager*
