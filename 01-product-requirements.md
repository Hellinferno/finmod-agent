# 01 — Product Requirements Document (PRD)
## Financial Modeling & Valuation Agent (FMVA)
**Version:** 1.0  
**Date:** 2026-02-23  
**Owner:** Product Management  
**Status:** Draft — Pre-Engineering Review  
**Platform:** Google Colab + Unsloth (LLM fine-tuning backbone)

---

## 1. Executive Summary

The **Financial Modeling & Valuation Agent (FMVA)** is an autonomous, LLM-powered financial analysis system fine-tuned via Unsloth on Google Colab infrastructure. It ingests raw financial statements (Income Statement, Balance Sheet, Cash Flow), normalizes them into a standardized 3-Statement model, runs institutional-grade valuation methodologies (DCF, Comps, Precedent Transactions, Sensitivity Analysis), and outputs audit-trailed, exportable reports in Excel/JSON format with an executive narrative.

The target users are investment banking analysts, equity research professionals, corporate finance teams, and advanced retail investors who need institutional-quality analysis without a full Bloomberg terminal or proprietary modeling team.

---

## 2. Problem Statement

### 2.1 Current Pain Points

| Pain Point | Impact |
|---|---|
| Manual 3-statement modeling takes 4–16 hours per company | Analyst time drain; error-prone |
| No standardized input format across companies/geographies | Data inconsistency; bad models |
| WACC, DCF, and Comps require specialist knowledge | High skill barrier to entry |
| Sensitivity tables are manually built in Excel | Slow, rigid, hard to update |
| No audit trail on calculated outputs | Zero reproducibility; audit risk |
| Balance sheet plug errors are caught late or not at all | Reporting inaccuracies |

### 2.2 Opportunity

A fine-tuned LLM (via Unsloth on Colab) trained on financial modeling patterns can automate 80% of the modeling workflow while providing full transparency via an audit trail. This democratizes institutional-grade financial analysis.

---

## 3. Goals & Non-Goals

### 3.1 Goals
- Automate 3-statement normalization from raw, unstructured financial data
- Support multi-methodology valuation: DCF (2-stage), Trading Comps, Precedent Transactions
- Generate automated sensitivity matrices (WACC vs. TGR) and Football Field charts
- Provide a complete, line-level audit trail for every computed value
- Export results to structured Excel (.xlsx) and JSON formats
- Generate a professional executive summary narrative using the fine-tuned LLM
- Run entirely within Google Colab with Unsloth as the LLM training/inference backbone
- Auto-detect and flag Balance Sheet imbalances with plug suggestions

### 3.2 Non-Goals (v1.0)
- Real-time live data feeds (Bloomberg, Refinitiv) — v2.0
- Portfolio-level aggregation across multiple companies simultaneously
- Automated filing retrieval (SEC EDGAR scraping) — v2.0
- Native mobile application
- Multi-user collaboration / SaaS deployment — v2.0
- IFRS vs GAAP automated reconciliation (manual flag only in v1.0)

---

## 4. Target Users & Personas

### Persona 1: "Alex" — Junior IB Analyst
- **Role:** 1st/2nd year analyst at a boutique investment bank
- **Need:** Build a comp set and DCF for a client pitch in under 2 hours
- **Pain:** Manually building sensitivity tables; getting model checks wrong
- **Success metric:** Produces a full valuation model in < 30 minutes with zero balance sheet errors

### Persona 2: "Priya" — Equity Research Associate
- **Role:** Mid-level ER associate at an asset manager
- **Need:** Quick-turn valuation update on 20+ companies in a sector
- **Pain:** Inconsistent formatting across companies makes comparison hard
- **Success metric:** Standardized comp table output across all 20 companies in one session

### Persona 3: "Marcus" — Corporate Finance Director
- **Role:** Director of FP&A at a mid-market company
- **Need:** Self-service valuation for internal M&A screening
- **Pain:** No access to external research; manual modeling is slow
- **Success metric:** Uploads internal financials, gets a defensible valuation range in < 1 hour

### Persona 4: "Dev" — Quantitative Developer / ML Engineer
- **Role:** Building financial applications using LLMs
- **Need:** Fine-tuneable, modular financial reasoning backbone
- **Pain:** General LLMs hallucinate on financial computations
- **Success metric:** Fine-tuned Unsloth model achieves < 2% numerical error rate on financial benchmarks

---

## 5. Core Features & Functional Requirements

### 5.1 Feature: 3-Statement Normalization Engine (F-001)

**Priority:** P0 — Must Have

**Description:** The system must accept raw financial data in multiple formats (CSV, JSON, plain text, PDF-extracted text) and normalize it into a standardized 3-Statement model: Income Statement, Balance Sheet, and Cash Flow Statement.

**Requirements:**
- FR-001-1: Accept input in CSV, JSON, and plain text formats
- FR-001-2: Auto-detect line item labels across different reporting conventions (e.g., "Revenue" = "Net Sales" = "Total Revenue")
- FR-001-3: Normalize to a canonical schema with standardized field names (see Database Schema doc)
- FR-001-4: Support at minimum 5 historical periods (LTM + 4 prior years)
- FR-001-5: Flag unrecognized line items for manual review
- FR-001-6: Support multi-currency input with USD normalization

**Acceptance Criteria:**
- AC-001-1: Given a raw CSV with non-standard headers, the system correctly maps > 90% of line items to canonical names
- AC-001-2: Given a 5-year historical dataset, output shows all three statements in standardized format
- AC-001-3: Unrecognized items are flagged with a `REVIEW_REQUIRED` tag in output

---

### 5.2 Feature: Assumption / Drivers Engine (F-002)

**Priority:** P0 — Must Have

**Description:** A dedicated module that exposes configurable "Driver" parameters that control the entire projection model. Users must be able to toggle these values via a UI or API call.

**Driver Parameters (v1.0):**

| Driver | Default | Range | Description |
|---|---|---|---|
| Revenue Growth Rate (Year 1-5) | 10% | -50% to +100% | Annual YoY revenue growth |
| Revenue Growth Rate (Year 6-10) | 5% | -50% to +50% | Terminal period growth convergence |
| EBITDA Margin | 20% | 0% to 80% | Projected EBITDA as % of Revenue |
| CapEx-to-Sales Ratio | 5% | 0% to 30% | Capital expenditure as % of Revenue |
| D&A-to-Revenue | 3% | 0% to 20% | Depreciation & Amortization as % of Revenue |
| NWC Change as % of Revenue | 2% | -10% to 20% | Net Working Capital changes |
| Tax Rate | 21% | 0% to 40% | Effective corporate tax rate |
| WACC | 10% | 5% to 25% | Weighted Average Cost of Capital |
| Terminal Growth Rate | 2.5% | 0% to 5% | Gordon Growth model perpetuity rate |
| Exit Multiple (EV/EBITDA) | 10x | 4x to 25x | Exit Multiple for terminal value |

**Requirements:**
- FR-002-1: All drivers must be configurable at runtime without code changes
- FR-002-2: System must validate that inputs are within acceptable bounds and warn on extremes
- FR-002-3: Default values must be sourced from industry benchmarks
- FR-002-4: Driver changes must instantly propagate to all downstream calculations
- FR-002-5: System must support saving and loading named "Assumption Sets"

---

### 5.3 Feature: DCF Valuation Module (F-003)

**Priority:** P0 — Must Have

**Description:** A two-stage Discounted Cash Flow model that calculates Unlevered Free Cash Flow (UFCF) for a 5–10 year explicit forecast period and computes Terminal Value using both Gordon Growth and Exit Multiple methods.

**Requirements:**
- FR-003-1: Calculate UFCF = EBIT × (1 - Tax Rate) + D&A - CapEx - ΔNWC
- FR-003-2: Support configurable projection periods (5 or 10 years)
- FR-003-3: Discount UFCF to present value using WACC
- FR-003-4: Compute Terminal Value via Gordon Growth: TV = UFCF_final × (1 + TGR) / (WACC - TGR)
- FR-003-5: Compute Terminal Value via Exit Multiple: TV = EBITDA_final × Exit Multiple
- FR-003-6: Calculate Enterprise Value = PV(UFCFs) + PV(Terminal Value)
- FR-003-7: Calculate Equity Value = Enterprise Value - Net Debt + Cash
- FR-003-8: Calculate implied share price = Equity Value / Diluted Shares Outstanding
- FR-003-9: Display TV as % of total Enterprise Value (flag if > 80% as a risk indicator)

**Acceptance Criteria:**
- AC-003-1: UFCF calculation matches manual Excel model within 0.01% tolerance
- AC-003-2: Both TV methods (Gordon Growth and Exit Multiple) are always computed and displayed
- AC-003-3: If WACC ≤ TGR, system throws a `GORDON_GROWTH_ERROR` and halts with explanation

---

### 5.4 Feature: Comparable Company Analysis — "Comps" (F-004)

**Priority:** P1 — Should Have

**Description:** Pull or accept a set of comparable public companies and compute a trading multiples table. Apply peer median/mean multiples to the subject company to derive an implied valuation range.

**Supported Multiples:**

| Multiple | Formula |
|---|---|
| EV/Revenue | Enterprise Value ÷ LTM Revenue |
| EV/EBITDA | Enterprise Value ÷ LTM EBITDA |
| EV/EBIT | Enterprise Value ÷ LTM EBIT |
| P/E | Market Cap ÷ LTM Net Income |
| P/Sales | Market Cap ÷ LTM Revenue |
| EV/FCF | Enterprise Value ÷ LTM Free Cash Flow |

**Requirements:**
- FR-004-1: Accept comparable company data via structured JSON input (name, ticker, financial data)
- FR-004-2: Calculate all 6 multiples for each comp and for subject company
- FR-004-3: Compute peer set statistics: Mean, Median, 25th percentile, 75th percentile
- FR-004-4: Apply peer median multiples to subject company financials to derive implied valuation range
- FR-004-5: Flag outlier comps (beyond 2 standard deviations) with a warning
- FR-004-6: Support manual override of any multiple for subjective adjustment

---

### 5.5 Feature: Precedent Transactions Analysis (F-005)

**Priority:** P1 — Should Have

**Description:** Accept a dataset of M&A precedent transactions and analyze acquisition multiples to derive a "control premium" adjusted valuation range.

**Requirements:**
- FR-005-1: Accept transaction data including: Target, Acquirer, Date, Deal Value, Revenue, EBITDA, EV/Revenue, EV/EBITDA
- FR-005-2: Apply transaction multiples to subject company to derive implied value
- FR-005-3: Compute control premium implied by transaction multiples vs. trading comps
- FR-005-4: Filter transactions by: date range, industry, deal size, geography

---

### 5.6 Feature: Sensitivity Analysis (F-006)

**Priority:** P0 — Must Have

**Description:** Generate a 2-dimensional sensitivity matrix (Heat Map / Data Table) showing how implied share price or Enterprise Value changes across combinations of WACC and Terminal Growth Rate (or WACC and Exit Multiple).

**Requirements:**
- FR-006-1: Sensitivity Matrix 1: WACC (rows) vs. Terminal Growth Rate (columns), 5×5 minimum, 7×7 preferred
- FR-006-2: Sensitivity Matrix 2: WACC (rows) vs. Exit Multiple (columns)
- FR-006-3: Color-code output: Green = above base case, Red = below base case
- FR-006-4: Generate Football Field chart data: Horizontal bar chart showing valuation range from each methodology
- FR-006-5: Export sensitivity tables in Excel-ready format

---

### 5.7 Feature: Audit Trail & Self-Correction (F-007)

**Priority:** P0 — Must Have

**Description:** Every computed value must reference its source inputs and formula. The system must provide a machine-readable audit trail JSON alongside every output.

**Requirements:**
- FR-007-1: Every output value links to: (a) formula used, (b) source input values, (c) source line items from original data
- FR-007-2: Balance Sheet check: Auto-verify Assets = Liabilities + Equity for every period
- FR-007-3: If Balance Sheet fails check: Flag with `BS_IMBALANCE_ERROR`, show discrepancy amount, suggest plug (Cash or Goodwill)
- FR-007-4: Numerical cross-checks: Net Income on IS must equal Net Income on BS Retained Earnings delta
- FR-007-5: Cash Flow Statement: Ending Cash on CFS must equal Cash on Balance Sheet
- FR-007-6: Audit trail must be exportable as JSON

---

### 5.8 Feature: Export Engine (F-008)

**Priority:** P0 — Must Have

**Description:** Export all model outputs to structured Excel (.xlsx) with formatted sheets, and to JSON for API consumers.

**Requirements:**
- FR-008-1: Excel export must contain separate sheets: Input Data, 3-Statement Model, DCF Output, Comps Table, Sensitivity Matrix, Audit Trail
- FR-008-2: JSON export must follow the schema defined in the API Contracts document
- FR-008-3: Excel formatting: Color-coded inputs (blue), formulas (black), outputs (green)
- FR-008-4: Include company name, report date, and version header on every sheet

---

### 5.9 Feature: Executive Summary Narrative (F-009)

**Priority:** P1 — Should Have

**Description:** The fine-tuned LLM generates a professional investment banking–style narrative summarizing the valuation, key drivers, risks, and recommendation.

**Requirements:**
- FR-009-1: LLM generates 3-5 paragraph executive summary
- FR-009-2: Narrative must reference specific computed values (e.g., "Our DCF implies an equity value of $X.XXB")
- FR-009-3: Tone must be professional investment banking standard
- FR-009-4: Identify top 3 value drivers and top 3 risk factors
- FR-009-5: Generate one-sentence "headline" valuation (e.g., "We value ACME Corp at $42–$58 per share, implying 23–68% upside")

---

## 6. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Model inference latency | < 60 seconds for full report on Colab T4 GPU |
| Numerical accuracy | < 0.01% deviation from manual Excel model |
| Input format support | CSV, JSON, Plain Text |
| Colab compatibility | Google Colab Pro / Pro+ (T4/A100) |
| Unsloth compatibility | Unsloth 2024.x with 4-bit quantization |
| Export format | .xlsx (openpyxl), .json |
| Audit trail completeness | 100% of output values must have audit trail entry |
| Balance Sheet accuracy | 100% of periods must pass BS check before proceeding |

---

## 7. Constraints

- **Infrastructure:** Google Colab (no persistent server; session-based)
- **LLM Backbone:** Unsloth fine-tuning only (no OpenAI API dependency in v1.0)
- **No real-time data:** All financial data must be user-supplied (no live API in v1.0)
- **Memory:** Colab T4 = 16GB VRAM; model must fit in 4-bit quantization
- **Storage:** Google Drive mount for persistence across sessions
- **Compute cost:** Must complete full run within Colab free tier time limits (< 12 hours/session)

---

## 8. Success Metrics (KPIs)

| Metric | Target (v1.0) |
|---|---|
| Time to full valuation report | < 30 minutes end-to-end |
| Numerical accuracy vs. manual model | > 99.99% |
| Balance Sheet check pass rate | 100% (blocks on failure) |
| Audit trail coverage | 100% of outputs |
| Executive summary quality score | ≥ 4.0 / 5.0 (expert review) |
| LLM hallucination rate on numbers | < 2% |
| Excel export open-without-error rate | 100% |

---

## 9. Dependencies & Assumptions

### Dependencies
- Unsloth library (open source, Apache 2.0)
- Google Colab Pro or Pro+ subscription
- openpyxl for Excel generation
- pandas, numpy for numerical computation
- Google Drive API for persistence
- A fine-tuning dataset of financial modeling examples (to be curated separately)

### Key Assumptions
- Users will provide reasonably clean financial data (OCR quality issues are out of scope for v1.0)
- All inputs are in USD or will be manually converted by the user prior to input
- The fine-tuned model will be hosted on HuggingFace Hub for loading into Colab
- Users have basic familiarity with financial statements

---

## 10. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| LLM hallucinates financial numbers | High | Critical | All numbers computed programmatically; LLM only generates narrative |
| Colab session timeout during long runs | Medium | High | Checkpoint saves to Google Drive every computation step |
| Input data quality too poor to parse | Medium | High | Validation layer + clear error messages |
| WACC ≤ TGR makes DCF undefined | Low | Medium | Hard guard with error message |
| Fine-tuning dataset bias | Medium | Medium | Diverse dataset across industries and geographies |

---

## 11. Version Roadmap

| Version | Key Features | Timeline |
|---|---|---|
| v1.0 (MVP) | 3-Statement normalization, DCF, Sensitivity, Audit Trail, Export | Month 1-3 |
| v1.5 | Comps + Precedent Transactions, Football Field chart | Month 4-5 |
| v2.0 | Live data feeds, SEC EDGAR integration, SaaS deployment | Month 6-9 |
| v3.0 | Portfolio-level analysis, multi-company comparison, API | Month 10-12 |

---

*Document Owner: Product Management | Last Updated: 2026-02-23 | Next Review: Sprint 1 Kickoff*
