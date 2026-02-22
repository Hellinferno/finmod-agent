# 03 — Information Architecture (IA)
## Financial Modeling & Valuation Agent (FMVA)
**Version:** 1.0  
**Date:** 2026-02-23  
**Owner:** Product Management / UX  

---

## 1. Overview

The Information Architecture defines how data is structured, organized, labeled, and flows through the FMVA system. This document covers the conceptual data model, user mental models, navigation hierarchy (for the Colab notebook interface), content taxonomy, and information flows between modules.

---

## 2. User Mental Model

The FMVA mirrors the mental model of an investment banking analyst building a model in Excel, but automates every computation. The user thinks in these sequential stages:

```
Stage 1: DATA IN          → Upload raw financial statements
Stage 2: NORMALIZE        → Review standardized 3-statement model
Stage 3: CONFIGURE        → Set assumptions / drivers
Stage 4: COMPUTE          → Run valuation methodologies
Stage 5: REVIEW           → Check audit trail, fix errors
Stage 6: EXPORT           → Download Excel + narrative report
```

Every section of the Colab notebook, every API endpoint, and every output file maps directly to one of these 6 stages.

---

## 3. Top-Level Information Hierarchy

```
FMVA System
│
├── 01. INPUT LAYER
│   ├── Raw Financial Data
│   │   ├── Income Statement (raw)
│   │   ├── Balance Sheet (raw)
│   │   └── Cash Flow Statement (raw)
│   ├── Comparable Company Data
│   ├── Precedent Transaction Data
│   └── Configuration / Assumptions
│
├── 02. PROCESSING LAYER
│   ├── Normalization Engine
│   │   ├── Field Mapping Registry
│   │   └── Canonical Schema Store
│   ├── Assumption / Drivers Engine
│   ├── 3-Statement Model Builder
│   └── Financial Integrity Checker
│
├── 03. VALUATION LAYER
│   ├── DCF Module
│   │   ├── UFCF Calculator
│   │   ├── Terminal Value Calculator
│   │   └── EV / Equity Bridge
│   ├── Comps Module
│   │   ├── Trading Multiples Table
│   │   └── Implied Value Range
│   ├── Precedent Transactions Module
│   └── Sensitivity Analysis Module
│       ├── WACC vs. TGR Matrix
│       ├── WACC vs. Exit Multiple Matrix
│       └── Football Field Data
│
├── 04. INTEGRITY LAYER
│   ├── Audit Trail Generator
│   ├── Balance Sheet Checker
│   ├── CFS ↔ Balance Sheet Reconciler
│   └── Cross-Statement Validator
│
├── 05. OUTPUT LAYER
│   ├── Excel Export Engine
│   │   ├── Sheet: Cover
│   │   ├── Sheet: 3-Statement Model
│   │   ├── Sheet: DCF
│   │   ├── Sheet: Trading Comps
│   │   ├── Sheet: Sensitivity
│   │   └── Sheet: Audit Trail
│   ├── JSON Export Engine
│   ├── Executive Summary (LLM)
│   └── Football Field Chart Data
│
└── 06. LLM LAYER (Unsloth/Colab)
    ├── Fine-tuning Pipeline
    │   ├── Training Dataset (JSONL)
    │   └── Model Checkpoints (Google Drive)
    ├── Inference Engine
    └── Narrative Generator
```

---

## 4. Data Taxonomy

### 4.1 Canonical Income Statement Schema

All income statement data, regardless of source format, is normalized to the following canonical taxonomy:

```
INCOME STATEMENT
│
├── REVENUE
│   ├── total_revenue                    [Primary]
│   ├── product_revenue                  [Optional]
│   ├── service_revenue                  [Optional]
│   └── other_revenue                    [Optional]
│
├── COST OF GOODS SOLD (COGS)
│   ├── total_cogs                       [Primary]
│   ├── product_cogs                     [Optional]
│   └── service_cogs                     [Optional]
│
├── GROSS PROFIT
│   └── gross_profit                     [Derived: Revenue - COGS]
│
├── OPERATING EXPENSES
│   ├── research_and_development         [Optional]
│   ├── sales_and_marketing              [Optional]
│   ├── general_and_administrative       [Optional]
│   └── total_opex                       [Optional/Derived]
│
├── EBITDA
│   └── ebitda                           [Derived: Gross Profit - OpEx + D&A]
│
├── DEPRECIATION_AND_AMORTIZATION
│   └── da                               [Primary/Optional]
│
├── EBIT
│   └── ebit                             [Derived: EBITDA - D&A]
│
├── NON-OPERATING
│   ├── interest_expense                 [Primary]
│   ├── interest_income                  [Optional]
│   └── other_non_operating              [Optional]
│
├── EBT (Earnings Before Tax)
│   └── ebt                              [Derived]
│
├── TAXES
│   └── income_tax_expense               [Primary]
│
└── NET INCOME
    └── net_income                       [Primary/Derived]
```

### 4.2 Canonical Balance Sheet Schema

```
BALANCE SHEET
│
├── ASSETS
│   ├── CURRENT ASSETS
│   │   ├── cash_and_equivalents         [Primary]
│   │   ├── short_term_investments       [Optional]
│   │   ├── accounts_receivable          [Primary]
│   │   ├── inventory                    [Optional]
│   │   ├── prepaid_expenses             [Optional]
│   │   └── total_current_assets         [Derived/Primary]
│   │
│   ├── NON-CURRENT ASSETS
│   │   ├── property_plant_equipment     [Primary]
│   │   ├── accumulated_depreciation     [Primary]
│   │   ├── net_ppe                      [Derived]
│   │   ├── goodwill                     [Optional]
│   │   ├── intangible_assets            [Optional]
│   │   ├── long_term_investments        [Optional]
│   │   └── total_non_current_assets     [Derived/Primary]
│   │
│   └── TOTAL ASSETS                     [Derived: Current + Non-Current]
│
├── LIABILITIES
│   ├── CURRENT LIABILITIES
│   │   ├── accounts_payable             [Primary]
│   │   ├── accrued_liabilities          [Optional]
│   │   ├── short_term_debt              [Optional]
│   │   ├── deferred_revenue_current     [Optional]
│   │   └── total_current_liabilities    [Derived/Primary]
│   │
│   ├── NON-CURRENT LIABILITIES
│   │   ├── long_term_debt               [Primary]
│   │   ├── deferred_tax_liabilities     [Optional]
│   │   ├── deferred_revenue_lt          [Optional]
│   │   └── total_non_current_liabilities [Derived/Primary]
│   │
│   └── TOTAL LIABILITIES                [Derived]
│
└── EQUITY
    ├── common_stock                     [Optional]
    ├── additional_paid_in_capital       [Optional]
    ├── retained_earnings                [Primary]
    ├── accumulated_other_comprehensive  [Optional]
    ├── treasury_stock                   [Optional]
    └── TOTAL_EQUITY                     [Primary/Derived]
```

### 4.3 Canonical Cash Flow Statement Schema

```
CASH FLOW STATEMENT
│
├── OPERATING ACTIVITIES
│   ├── net_income                       [Link to IS]
│   ├── add_back_da                      [Link to IS]
│   ├── change_in_accounts_receivable    [Derived from BS]
│   ├── change_in_inventory              [Derived from BS]
│   ├── change_in_accounts_payable       [Derived from BS]
│   ├── other_operating_activities       [Optional]
│   └── cfo                              [Derived/Primary]
│
├── INVESTING ACTIVITIES
│   ├── capex                            [Primary]
│   ├── acquisitions                     [Optional]
│   ├── asset_sales                      [Optional]
│   └── cfi                              [Derived/Primary]
│
├── FINANCING ACTIVITIES
│   ├── debt_issuance                    [Optional]
│   ├── debt_repayment                   [Optional]
│   ├── equity_issuance                  [Optional]
│   ├── dividends_paid                   [Optional]
│   ├── share_repurchases                [Optional]
│   └── cff                              [Derived/Primary]
│
└── CASH RECONCILIATION
    ├── beginning_cash                   [Link to prior BS]
    ├── net_change_in_cash               [Derived: CFO + CFI + CFF]
    └── ending_cash                      [Derived; must = BS cash]
```

### 4.4 Valuation Output Taxonomy

```
VALUATION OUTPUTS
│
├── DCF OUTPUT
│   ├── Per-Year Projections
│   │   ├── revenue
│   │   ├── ebitda
│   │   ├── ebit
│   │   ├── nopat
│   │   ├── da
│   │   ├── capex
│   │   ├── delta_nwc
│   │   ├── ufcf
│   │   └── pv_ufcf
│   │
│   ├── Terminal Value
│   │   ├── tv_gordon_growth
│   │   ├── tv_exit_multiple
│   │   ├── pv_tv_gordon_growth
│   │   └── pv_tv_exit_multiple
│   │
│   └── Summary
│       ├── enterprise_value_gg
│       ├── enterprise_value_em
│       ├── equity_value_gg
│       ├── equity_value_em
│       ├── implied_price_gg
│       ├── implied_price_em
│       └── tv_pct_of_ev
│
├── COMPS OUTPUT
│   ├── Comp Table (per company)
│   │   ├── ev_to_revenue
│   │   ├── ev_to_ebitda
│   │   ├── ev_to_ebit
│   │   ├── pe_ratio
│   │   └── ev_to_fcf
│   ├── Peer Statistics
│   │   ├── mean, median, p25, p75
│   └── Subject Company Implied Value Range
│
├── SENSITIVITY OUTPUT
│   ├── Matrix 1: WACC vs. TGR (5×5 or 7×7 grid)
│   ├── Matrix 2: WACC vs. Exit Multiple
│   └── Football Field
│       ├── dcf_gg_range [low, high]
│       ├── dcf_em_range [low, high]
│       ├── comps_range [low, high]
│       ├── transactions_range [low, high]
│       └── current_price [reference]
│
└── AUDIT TRAIL
    ├── Per-calculation records
    │   ├── output_field
    │   ├── formula
    │   ├── input_values (dict)
    │   ├── result
    │   └── timestamp
    └── Integrity Checks
        ├── bs_check [PASS/FAIL, per period]
        ├── cfs_check [PASS/FAIL, per period]
        └── is_check [PASS/FAIL, per period]
```

---

## 5. Field Label Mapping Registry

This registry defines how non-standard financial labels map to canonical names. The normalization engine uses fuzzy matching + this registry.

| Canonical Name | Common Aliases |
|---|---|
| `total_revenue` | Net Sales, Revenue, Total Revenue, Revenues, Sales, Turnover, Net Revenue |
| `cogs` | Cost of Revenue, Cost of Goods Sold, Cost of Sales, Direct Costs |
| `gross_profit` | Gross Income, Gross Margin (absolute) |
| `ebitda` | EBITDA, Adjusted EBITDA, Operating EBITDA |
| `da` | D&A, Depreciation & Amortization, Dep. and Amort. |
| `ebit` | Operating Income, Operating Profit, EBIT |
| `interest_expense` | Interest Expense, Finance Costs, Interest Charges |
| `net_income` | Net Profit, Net Earnings, Bottom Line, Profit After Tax |
| `cash_and_equivalents` | Cash, Cash & Equivalents, Cash and Short-term Investments |
| `accounts_receivable` | AR, Receivables, Trade Receivables |
| `total_assets` | Total Assets, Assets |
| `total_liabilities` | Total Liabilities, Liabilities |
| `long_term_debt` | LT Debt, Long-term Borrowings, Senior Notes |
| `retained_earnings` | Retained Earnings, Accumulated Deficit, R/E |
| `capex` | Capital Expenditures, CapEx, PP&E Purchases, Purchases of Fixed Assets |
| `cfo` | Cash from Operations, Operating Cash Flow, Net Cash from Operating Activities |

---

## 6. Colab Notebook Navigation Structure

The Colab notebook is organized as follows (serves as the UI for analysts):

```
FMVA_Main.ipynb
│
├── Section 0: Setup & Imports
│   ├── 0.1 Install dependencies
│   ├── 0.2 Mount Google Drive
│   └── 0.3 Load fine-tuned model (Unsloth)
│
├── Section 1: Data Ingestion
│   ├── 1.1 Upload financial data (file picker)
│   ├── 1.2 Preview raw data
│   └── 1.3 Run normalization → preview canonical output
│
├── Section 2: Assumption Configuration
│   ├── 2.1 Set revenue growth (Stage 1 & 2)
│   ├── 2.2 Set EBITDA margin
│   ├── 2.3 Set CapEx, D&A, NWC, Tax Rate
│   ├── 2.4 Set WACC and Terminal Value assumptions
│   └── 2.5 (Optional) Load saved assumption set
│
├── Section 3: 3-Statement Model
│   ├── 3.1 Build projected Income Statement
│   ├── 3.2 Build projected Balance Sheet
│   ├── 3.3 Build projected Cash Flow Statement
│   └── 3.4 Run integrity checks → review results
│
├── Section 4: Valuation
│   ├── 4.1 DCF — UFCF projection
│   ├── 4.2 DCF — Terminal Value (both methods)
│   ├── 4.3 DCF — Enterprise Value & Equity Bridge
│   ├── 4.4 (Optional) Trading Comps
│   └── 4.5 (Optional) Precedent Transactions
│
├── Section 5: Sensitivity Analysis
│   ├── 5.1 Generate WACC vs. TGR matrix
│   ├── 5.2 Generate WACC vs. Exit Multiple matrix
│   └── 5.3 Generate Football Field data
│
├── Section 6: Output & Export
│   ├── 6.1 Generate Audit Trail
│   ├── 6.2 Generate Executive Summary (LLM)
│   ├── 6.3 Export to Excel (.xlsx) → Google Drive
│   └── 6.4 Export to JSON
│
└── Section 7: (Dev Only) Fine-tuning Pipeline
    ├── 7.1 Load training dataset
    ├── 7.2 Configure Unsloth training params
    ├── 7.3 Run fine-tuning
    └── 7.4 Evaluate model on test set
```

---

## 7. File System Architecture (Google Drive)

```
Google Drive/
└── FMVA/
    ├── inputs/
    │   ├── {company_name}_{date}_raw.csv
    │   └── {company_name}_{date}_comps.json
    ├── assumptions/
    │   ├── base_case.json
    │   ├── bull_case.json
    │   └── bear_case.json
    ├── outputs/
    │   ├── {company_name}_{date}_valuation.xlsx
    │   ├── {company_name}_{date}_valuation.json
    │   └── {company_name}_{date}_audit_trail.json
    ├── models/
    │   ├── fmva_lora_adapter/           ← Unsloth LoRA weights
    │   └── checkpoints/
    │       ├── checkpoint_100/
    │       └── checkpoint_200/
    └── training_data/
        ├── financial_narratives_train.jsonl
        └── financial_narratives_eval.jsonl
```

---

## 8. Information Flow Diagram

```
USER INPUT
    │
    ▼
[Raw Financial Data CSV/JSON]
    │
    ▼
[NORMALIZATION ENGINE]
    │  → Field Mapping Registry
    │  → Validation Layer
    │
    ▼
[CANONICAL 3-STATEMENT MODEL]
    │
    ├──────────────────────────────────────┐
    ▼                                      ▼
[ASSUMPTION ENGINE]              [INTEGRITY CHECKER]
    │                                      │
    ├── Revenue Growth                     ├── BS Check (Assets = L+E)
    ├── EBITDA Margin                      ├── CFS ↔ BS Reconciliation
    ├── CapEx / D&A / NWC                  └── IS → BS Link (Net Income)
    └── WACC / TGR / Exit Multiple
    │
    ▼
[PROJECTION ENGINE]
    │  → 5-10 Year P&L, BS, CFS Projections
    │
    ▼
[VALUATION MODULES]
    │
    ├── [DCF MODULE]
    │   ├── UFCF Calculation
    │   ├── Terminal Value (GG + EM)
    │   └── EV / Equity Value Bridge
    │
    ├── [COMPS MODULE]
    │   └── Trading Multiples Table
    │
    ├── [TRANSACTIONS MODULE]
    │   └── Precedent Transaction Multiples
    │
    └── [SENSITIVITY MODULE]
        ├── WACC vs. TGR Matrix
        ├── WACC vs. Exit Multiple Matrix
        └── Football Field Data
    │
    ▼
[AUDIT TRAIL GENERATOR]
    │  → Attaches source trace to every output value
    │
    ▼
[OUTPUT LAYER]
    │
    ├── [EXCEL EXPORT ENGINE] → .xlsx (Google Drive)
    ├── [JSON EXPORT ENGINE] → .json (Google Drive)
    └── [LLM NARRATIVE ENGINE]
        │  → Fine-tuned model via Unsloth
        └── → Executive Summary Text
```

---

## 9. Error States & System Responses

| Error Code | Trigger Condition | System Response | Blocks Processing? |
|---|---|---|---|
| `MISSING_REQUIRED_FIELD` | Required schema field absent | Flag missing field, specify impact | Partial block |
| `CLASSIFICATION_UNCERTAIN` | Line item can't be auto-classified | Flag for manual review | No |
| `BS_IMBALANCE_ERROR` | Assets ≠ L+E | Flag, show delta, suggest plug | Yes |
| `CFS_IMBALANCE_ERROR` | Ending cash ≠ BS cash | Flag, show delta | Yes |
| `GORDON_GROWTH_ERROR` | WACC ≤ TGR | Show error, use Exit Multiple only | Partial |
| `TV_HIGH_WARNING` | TV > 80% of EV | Warning flag, continue | No |
| `EBITDA_NEGATIVE` | Projected EBITDA < 0 | Warning flag, continue | No |
| `ASSUMPTION_WARNING` | Driver outside typical bounds | Confirmation prompt | Pauses |
| `OUTLIER_DETECTED` | Comp is 2σ+ from peer mean | Flag, ask include/exclude | No |
| `OOM_ERROR` | GPU OOM during inference | Prompt: reduce batch / use 4-bit | Yes |

---

*Document Owner: Product Management / UX | Last Updated: 2026-02-23*
