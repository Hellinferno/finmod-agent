# 02 — User Stories & Acceptance Criteria
## Financial Modeling & Valuation Agent (FMVA)
**Version:** 1.0  
**Date:** 2026-02-23  
**Owner:** Product Management  
**Format:** Epic → User Story → Acceptance Criteria (BDD: Given / When / Then)

---

## Story Map Overview

```
EPIC-01: Data Ingestion & Normalization
EPIC-02: Assumption & Driver Configuration
EPIC-03: DCF Valuation
EPIC-04: Comparable Company Analysis (Comps)
EPIC-05: Precedent Transactions
EPIC-06: Sensitivity Analysis
EPIC-07: Audit Trail & Integrity Checks
EPIC-08: Export & Reporting
EPIC-09: LLM Narrative Generation
EPIC-10: Developer / ML Engineer Workflow (Colab + Unsloth)
```

---

## EPIC-01: Data Ingestion & Normalization

> **As a** financial analyst,  
> **I want** to upload raw financial data in any common format,  
> **So that** I don't have to manually reformat data before modeling.

---

### US-001: Upload Raw Financial Data

**As an** investment banking analyst,  
**I want** to upload a CSV file containing income statement, balance sheet, and cash flow data,  
**So that** the system automatically ingests and parses it without manual formatting.

**Priority:** P0  
**Story Points:** 5

**Acceptance Criteria:**

```gherkin
Scenario 1: Successful CSV upload with standard headers
  Given I have a CSV file with headers: "Year", "Revenue", "COGS", "Gross Profit", "EBITDA", "Net Income"
  When I upload the file to the FMVA input endpoint
  Then the system parses and maps all 6 fields to canonical schema names within 5 seconds
  And the system returns a confirmation with a parsed preview of the first 3 rows
  And no data is lost

Scenario 2: CSV with non-standard headers
  Given I have a CSV with headers: "FY", "Net Sales", "Cost of Revenues", "Operating Income"
  When I upload the file
  Then the system maps "Net Sales" → "Revenue", "Cost of Revenues" → "COGS"
  And the system flags any unmapped columns with status "REVIEW_REQUIRED"
  And processing continues for all successfully mapped fields

Scenario 3: Missing required fields
  Given I upload a CSV that is missing "Net Income"
  When the system processes the file
  Then it returns an error: "MISSING_REQUIRED_FIELD: Net Income"
  And it specifies which downstream calculations will be blocked
  And it does NOT proceed to modeling

Scenario 4: Multi-year data (5 periods)
  Given I upload a CSV with 5 fiscal years (FY2020–FY2024) of income statement data
  When the system processes it
  Then all 5 periods appear in the normalized output
  And years are sorted chronologically (oldest to newest)
```

---

### US-002: Upload JSON Financial Data

**As a** developer integrating FMVA into my pipeline,  
**I want** to POST raw financial data as a JSON payload,  
**So that** I can programmatically feed data from other systems.

**Priority:** P0  
**Story Points:** 3

**Acceptance Criteria:**

```gherkin
Scenario 1: Valid JSON input
  Given I POST a JSON payload conforming to the FMVA input schema
  When the API processes it
  Then it returns HTTP 200 with a normalized 3-statement JSON response
  And all monetary values are in USD thousands

Scenario 2: Invalid JSON structure
  Given I POST a malformed JSON (missing "balance_sheet" key)
  When the API processes it
  Then it returns HTTP 400 with error: "INVALID_SCHEMA: Missing 'balance_sheet'"
  And no partial processing occurs

Scenario 3: Multi-currency input
  Given I POST data with "currency": "EUR" and "fx_rate_to_usd": 1.08
  When the system processes it
  Then all values are converted to USD using the provided FX rate
  And the audit trail records: "Converted EUR → USD at rate 1.08"
```

---

### US-003: Auto-detect Financial Statement Type

**As a** user who uploads a combined financial data file,  
**I want** the system to automatically identify which rows belong to Income Statement, Balance Sheet, or Cash Flow Statement,  
**So that** I don't need to pre-split the data myself.

**Priority:** P1  
**Story Points:** 8

**Acceptance Criteria:**

```gherkin
Scenario 1: Combined file with section headers
  Given I upload a CSV with section labels: "INCOME STATEMENT", "BALANCE SHEET", "CASH FLOW"
  When the system parses it
  Then it correctly routes each row to its respective statement
  And the 3-statement output is fully populated

Scenario 2: No section headers present
  Given I upload a flat CSV with no section markers
  When the system processes it
  Then it attempts auto-classification using line item name matching
  And it flags any ambiguous items with "CLASSIFICATION_UNCERTAIN"
  And it asks the user to confirm classification before proceeding
```

---

## EPIC-02: Assumption & Driver Configuration

> **As a** financial analyst,  
> **I want** to configure all key modeling assumptions in one place,  
> **So that** my model reflects my investment thesis.

---

### US-004: Set Revenue Growth Assumptions

**As a** buy-side analyst,  
**I want** to set different revenue growth rates for the Stage 1 (years 1–5) and Stage 2 (years 6–10) projection periods,  
**So that** my model reflects an accelerating-then-decelerating growth path typical of growth companies.

**Priority:** P0  
**Story Points:** 3

**Acceptance Criteria:**

```gherkin
Scenario 1: Set stage-specific growth rates
  Given I set Stage 1 growth = 25% and Stage 2 growth = 8%
  When the model projects revenue
  Then years 1-5 revenue each grow at 25% YoY from the base year
  And years 6-10 revenue each grow at 8% YoY from year 5
  And the audit trail shows: "Year 3 Revenue = Year 2 Revenue × 1.25"

Scenario 2: Growth rate out of bounds
  Given I set Stage 1 growth = 150%
  When I submit the assumptions
  Then the system shows warning: "ASSUMPTION_WARNING: Revenue Growth 150% exceeds typical bounds (100%). Confirm?"
  And processing is paused until I confirm or adjust

Scenario 3: Zero growth rate
  Given I set both growth rates to 0%
  When the model projects revenue
  Then all projected years equal the base year revenue
  And no error is thrown
```

---

### US-005: Set EBITDA Margin

**As an** analyst,  
**I want** to set a target EBITDA margin for the projection period,  
**So that** I can model margin expansion or compression scenarios.

**Priority:** P0  
**Story Points:** 2

**Acceptance Criteria:**

```gherkin
Scenario 1: Margin expansion scenario
  Given historical EBITDA margin is 15% and I set target margin to 28%
  When the model computes projected EBITDA
  Then EBITDA for each projected year = Projected Revenue × 28%
  And the audit trail notes: "EBITDA Margin: 28% (user input; historical: 15%)"

Scenario 2: Margin below zero
  Given I set EBITDA margin to -5%
  When I submit
  Then the system allows it (negative EBITDA is valid for pre-profitability companies)
  And it adds a flag: "EBITDA_NEGATIVE: Company projected as pre-profitability"
```

---

### US-006: Save and Load Assumption Sets

**As an** analyst running multiple scenarios,  
**I want** to save named assumption sets (e.g., "Base Case", "Bull Case", "Bear Case"),  
**So that** I can switch between scenarios instantly and compare outputs.

**Priority:** P1  
**Story Points:** 5

**Acceptance Criteria:**

```gherkin
Scenario 1: Save assumption set
  Given I have configured all drivers
  When I call save_assumptions(name="Bull Case")
  Then the system saves all driver values to a JSON file on Google Drive
  And confirms: "Assumption set 'Bull Case' saved successfully"

Scenario 2: Load assumption set
  Given "Bull Case" assumption set exists on Drive
  When I call load_assumptions(name="Bull Case")
  Then all driver values are restored to their saved state
  And the model immediately recomputes all outputs
```

---

## EPIC-03: DCF Valuation

> **As an** analyst,  
> **I want** a rigorous two-stage DCF model computed automatically,  
> **So that** I can derive an intrinsic value without building Excel models.

---

### US-007: Calculate Unlevered Free Cash Flow (UFCF)

**As an** investment banking analyst,  
**I want** the system to calculate UFCF for each projected year,  
**So that** I can see the cash generation profile of the business before capital structure effects.

**Priority:** P0  
**Story Points:** 5

**Acceptance Criteria:**

```gherkin
Scenario 1: Standard UFCF calculation
  Given Revenue = $100M, EBITDA Margin = 20%, D&A = $5M, CapEx = $8M, ΔNWC = $2M, Tax Rate = 21%
  When the system computes UFCF
  Then EBIT = $20M - $5M = $15M
  And NOPAT = $15M × (1 - 0.21) = $11.85M
  And UFCF = $11.85M + $5M - $8M - $2M = $6.85M
  And the audit trail shows every intermediate step

Scenario 2: Negative UFCF in early years
  Given CapEx is very high in years 1-2 leading to negative UFCF
  When the system discounts cash flows
  Then negative values are correctly discounted (not set to zero)
  And a warning flag: "UFCF_NEGATIVE in Year 1, Year 2" is added to output
```

---

### US-008: Compute Terminal Value — Both Methods

**As an** analyst,  
**I want** terminal value computed via both Gordon Growth and Exit Multiple,  
**So that** I can triangulate and present both to clients.

**Priority:** P0  
**Story Points:** 5

**Acceptance Criteria:**

```gherkin
Scenario 1: Gordon Growth terminal value
  Given WACC = 10%, TGR = 2.5%, Final Year UFCF = $50M
  When TV(Gordon Growth) is computed
  Then TV = $50M × 1.025 / (0.10 - 0.025) = $683.33M
  And PV(TV) = $683.33M / (1.10)^10 = $263.47M (for 10-year model)

Scenario 2: Exit Multiple terminal value
  Given Final Year EBITDA = $80M, EV/EBITDA Multiple = 12x
  When TV(Exit Multiple) is computed
  Then TV = $80M × 12 = $960M

Scenario 3: WACC equals TGR — error case
  Given WACC = 5% and TGR = 5%
  When the system attempts Gordon Growth computation
  Then it throws error: "GORDON_GROWTH_ERROR: WACC (5%) must exceed TGR (5%). Division by zero."
  And it still computes Exit Multiple TV
  And it halts DCF computation until the user adjusts inputs
```

---

### US-009: Compute Enterprise Value and Equity Value

**As an** analyst,  
**I want** the final Enterprise Value and implied equity value per share,  
**So that** I can present a clear investment conclusion.

**Priority:** P0  
**Story Points:** 3

**Acceptance Criteria:**

```gherkin
Scenario 1: Full DCF bridge
  Given PV of UFCFs = $200M, PV of TV(Gordon Growth) = $400M
  And Net Debt = $50M, Cash = $20M, Shares Outstanding = 10M
  When Enterprise Value is computed
  Then EV = $200M + $400M = $600M
  And Equity Value = $600M - $50M + $20M = $570M
  And Implied Price Per Share = $570M / 10M = $57.00
  And TV as % of EV = $400M / $600M = 66.7%

Scenario 2: TV% exceeds 80%
  Given PV(TV) represents 85% of total EV
  When output is generated
  Then a warning is added: "TV_HIGH_WARNING: Terminal Value represents 85% of Enterprise Value. Model is highly sensitive to terminal assumptions."
```

---

## EPIC-04: Comparable Company Analysis

---

### US-010: Input and Analyze Comp Set

**As an** analyst,  
**I want** to input a set of comparable companies and see a formatted trading multiples table,  
**So that** I can contextualize the subject company's valuation.

**Priority:** P1  
**Story Points:** 8

**Acceptance Criteria:**

```gherkin
Scenario 1: Valid comp set input
  Given I provide 5 comparable companies with their EV, Revenue, EBITDA, and market cap data
  When the system processes them
  Then it displays a table with: Company, EV/Rev, EV/EBITDA, EV/EBIT, P/E, P/Sales
  And it shows Mean, Median, 25th pct, 75th pct for each multiple
  And it applies median multiples to subject company to show implied valuation range

Scenario 2: Outlier detection
  Given one comp has EV/EBITDA of 45x while peers range 8x-15x
  When the system processes the comp set
  Then the outlier is flagged: "OUTLIER_DETECTED: [Company] EV/EBITDA 45x is 2.3σ above peer mean"
  And the user is asked whether to include or exclude from median calculation
```

---

## EPIC-05: Sensitivity Analysis

---

### US-011: Generate WACC vs. TGR Sensitivity Matrix

**As an** analyst preparing a pitch book,  
**I want** a sensitivity matrix showing implied share price across a range of WACC and TGR combinations,  
**So that** I can show clients how robust or sensitive the valuation is.

**Priority:** P0  
**Story Points:** 8

**Acceptance Criteria:**

```gherkin
Scenario 1: Standard 5x5 sensitivity matrix
  Given Base WACC = 10%, range ±2% in 1% steps (8%, 9%, 10%, 11%, 12%)
  And Base TGR = 2.5%, range ±1% in 0.5% steps (1.5%, 2.0%, 2.5%, 3.0%, 3.5%)
  When the sensitivity matrix is generated
  Then a 5×5 matrix of implied share prices is returned
  And the base case cell (10% WACC / 2.5% TGR) is highlighted
  And values above base case are colored green, below are colored red

Scenario 2: WACC-TGR conflict in sensitivity
  Given one cell has WACC = 8% and TGR = 8%
  When that cell is computed
  Then that cell shows "N/A — WACC ≤ TGR" instead of a numeric value
  And all other cells compute normally
```

---

### US-012: Generate Football Field Chart Data

**As an** analyst,  
**I want** a football field chart showing the valuation range from each methodology,  
**So that** I can present a holistic valuation summary.

**Priority:** P1  
**Story Points:** 5

**Acceptance Criteria:**

```gherkin
Scenario 1: Full football field
  Given DCF (Gordon Growth) range, DCF (Exit Multiple) range, Trading Comps range, Precedent Transactions range are all computed
  When football field data is generated
  Then it returns a structured dataset with: methodology name, low value, high value, base case value
  And data is formatted for horizontal bar chart rendering
  And all ranges include the current trading price as a reference point (if provided)
```

---

## EPIC-07: Audit Trail & Integrity Checks

---

### US-013: Balance Sheet Auto-Check

**As an** analyst building a model,  
**I want** the system to automatically verify that Assets = Liabilities + Equity for every period,  
**So that** I catch modeling errors before presenting to a client.

**Priority:** P0  
**Story Points:** 5

**Acceptance Criteria:**

```gherkin
Scenario 1: Balanced balance sheet
  Given Total Assets = $500M and Total Liabilities + Equity = $500M for each of 5 years
  When the balance sheet check runs
  Then it returns "BS_CHECK: PASS" for all periods
  And modeling proceeds

Scenario 2: Imbalanced balance sheet
  Given Total Assets = $502M and Total Liabilities + Equity = $500M in Year 3
  When the balance sheet check runs
  Then it returns "BS_IMBALANCE_ERROR: Year 3 — Discrepancy of $2M"
  And it suggests: "Check: Plug to Cash (+$2M) OR review Retained Earnings"
  And it BLOCKS all downstream valuation computations
  And it generates a diff report showing which line items changed between years

Scenario 3: Multiple periods fail
  Given Years 2 and 4 both fail the balance sheet check
  When the check runs
  Then errors are reported for both years individually
  And the system identifies which specific line items are most likely causing each discrepancy
```

---

### US-014: Cash Flow Statement Integrity Check

**As an** analyst,  
**I want** the system to verify that the ending cash balance on the Cash Flow Statement matches Cash on the Balance Sheet,  
**So that** I can confirm the three statements are fully linked.

**Priority:** P0  
**Story Points:** 3

**Acceptance Criteria:**

```gherkin
Scenario 1: CFS ties to Balance Sheet
  Given Ending Cash on CFS = $45M and Cash on Balance Sheet = $45M for all years
  When the cross-check runs
  Then "CFS_CHECK: PASS" is returned for all years

Scenario 2: Mismatch detected
  Given Ending Cash on CFS = $45M and Cash on Balance Sheet = $47M in Year 2
  When the cross-check runs
  Then "CFS_IMBALANCE_ERROR: Year 2 — CFS Ending Cash $45M ≠ BS Cash $47M (Δ $2M)"
  And it suggests: "Review: Other financing activities or beginning cash balance"
```

---

## EPIC-08: Export & Reporting

---

### US-015: Export to Excel (.xlsx)

**As an** analyst,  
**I want** to export the full model to a formatted Excel file,  
**So that** I can share it with clients and colleagues who don't use the FMVA tool.

**Priority:** P0  
**Story Points:** 8

**Acceptance Criteria:**

```gherkin
Scenario 1: Successful Excel export
  Given a fully computed model (3-statement, DCF, Comps, Sensitivity)
  When I call export_excel()
  Then an .xlsx file is generated and saved to Google Drive
  And it contains sheets: "Cover", "3-Statement", "DCF", "Comps", "Sensitivity", "Audit Trail"
  And the file opens without errors in Microsoft Excel 365 and Google Sheets

Scenario 2: Color coding
  Given the Excel file is generated
  When I open the "DCF" sheet
  Then all hard-coded input cells are blue
  And all formula-driven cells are black with no fill
  And all output summary cells are green

Scenario 3: Partial model export
  Given Comps analysis was not run (no comp data provided)
  When I export to Excel
  Then the "Comps" sheet is generated but marked "N/A — No Comp Data Provided"
  And all other sheets are fully populated
```

---

## EPIC-09: LLM Narrative Generation

---

### US-016: Generate Executive Summary Narrative

**As an** analyst preparing client materials,  
**I want** the LLM to generate a professional investment banking narrative summarizing the valuation,  
**So that** I have a strong starting point for my investment memo.

**Priority:** P1  
**Story Points:** 13 (includes LLM fine-tuning component)

**Acceptance Criteria:**

```gherkin
Scenario 1: Full narrative generation
  Given a complete valuation model output
  When generate_executive_summary() is called
  Then the LLM returns a 3-5 paragraph narrative in under 60 seconds
  And it references specific computed values (EV, equity value, implied share price)
  And it identifies the top 3 value drivers
  And it identifies the top 3 key risks
  And it includes a one-sentence headline with valuation range

Scenario 2: Narrative does not hallucinate numbers
  Given the DCF implies equity value of $570M and share price of $57.00
  When the narrative is generated
  Then the narrative states "$570M equity value" and "$57.00 per share" (not any other numbers)
  And all numbers in the narrative can be traced back to computed output values

Scenario 3: Pre-profitability company narrative
  Given the subject company has negative EBITDA
  When narrative is generated
  Then the tone adjusts appropriately: revenue growth, runway, path to profitability are highlighted
  And traditional P/E and EV/EBITDA multiples are de-emphasized in favor of EV/Revenue
```

---

## EPIC-10: Developer / ML Engineer Workflow (Colab + Unsloth)

---

### US-017: Fine-tune LLM on Colab with Unsloth

**As a** ML engineer,  
**I want** to fine-tune a base LLM (e.g., Mistral-7B or LLaMA-3) on financial modeling data using Unsloth on Google Colab,  
**So that** the model learns to generate accurate financial narratives and assist with computation.

**Priority:** P0  
**Story Points:** 21

**Acceptance Criteria:**

```gherkin
Scenario 1: Unsloth fine-tuning runs successfully
  Given a Colab Pro+ instance with A100 GPU
  And the training dataset contains ≥ 1,000 financial modeling examples in instruction-tuning format
  When the fine-tuning script is run
  Then training completes without OOM errors using 4-bit quantization
  And the fine-tuned adapter weights are saved to Google Drive at checkpoints every 100 steps
  And training loss decreases monotonically over the first 500 steps

Scenario 2: Inference on Colab T4
  Given the fine-tuned model is loaded with Unsloth in 4-bit mode on a T4 GPU
  When I run inference with a financial data prompt
  Then the model responds in < 30 seconds
  And GPU memory usage is < 14GB

Scenario 3: Model checkpoint recovery
  Given a Colab session times out at step 400
  When I restart the session and resume training
  Then training resumes from the last checkpoint (step 400)
  And no training data is lost
```

---

### US-018: Run Full Pipeline in Single Colab Notebook

**As an** analyst using FMVA,  
**I want** to run the entire workflow (ingest → normalize → model → value → export) from a single Colab notebook,  
**So that** I don't need to manage multiple scripts or environments.

**Priority:** P0  
**Story Points:** 8

**Acceptance Criteria:**

```gherkin
Scenario 1: End-to-end notebook run
  Given I open the FMVA_Main.ipynb notebook in Google Colab
  And I mount my Google Drive
  And I upload my financial data file
  When I click "Run All"
  Then all cells execute in order without errors
  And the final output cell displays: valuation summary, audit trail status, export file path
  And total execution time is < 30 minutes on a T4 GPU

Scenario 2: Modular cell execution
  Given I only want to run the DCF module (not Comps)
  When I run only the DCF section cells
  Then only the DCF outputs are generated
  And no errors are thrown for unexecuted modules
```

---

## Story Prioritization Summary

| Story ID | Title | Priority | Points | MVP? |
|---|---|---|---|---|
| US-001 | Upload raw CSV data | P0 | 5 | ✅ Yes |
| US-002 | Upload JSON data | P0 | 3 | ✅ Yes |
| US-003 | Auto-detect statement type | P1 | 8 | ❌ No |
| US-004 | Set revenue growth | P0 | 3 | ✅ Yes |
| US-005 | Set EBITDA margin | P0 | 2 | ✅ Yes |
| US-006 | Save/load assumption sets | P1 | 5 | ❌ No |
| US-007 | Calculate UFCF | P0 | 5 | ✅ Yes |
| US-008 | Compute terminal value | P0 | 5 | ✅ Yes |
| US-009 | Compute EV and equity value | P0 | 3 | ✅ Yes |
| US-010 | Comps analysis | P1 | 8 | ❌ No |
| US-011 | WACC vs. TGR sensitivity matrix | P0 | 8 | ✅ Yes |
| US-012 | Football field chart data | P1 | 5 | ❌ No |
| US-013 | Balance sheet auto-check | P0 | 5 | ✅ Yes |
| US-014 | CFS integrity check | P0 | 3 | ✅ Yes |
| US-015 | Excel export | P0 | 8 | ✅ Yes |
| US-016 | Executive summary narrative | P1 | 13 | ❌ No |
| US-017 | Unsloth fine-tuning | P0 | 21 | ✅ Yes |
| US-018 | Single Colab notebook pipeline | P0 | 8 | ✅ Yes |

**MVP Total Points:** 70 | **Full v1.0 Points:** 125

---

*Document Owner: Product Management | Last Updated: 2026-02-23*
