# 08 — Computation Engine Specification
## Financial Modeling & Valuation Agent (FMVA)
**Version:** 1.0  
**Date:** 2026-02-23  
**Owner:** Engineering (Quantitative)  
**Purpose:** Defines every financial formula, mathematical procedure, and computation contract used by FMVA's valuation engine.

---

## 1. Guiding Principles

1. **Determinism:** Same inputs → same outputs. No randomness in computation layer.
2. **Precision:** All calculations use Python `float` (64-bit IEEE 754). Currency values rounded to 2 decimal places for display only; internal computations use full precision.
3. **Transparency:** Every formula is documented here. Every computation is recorded in the Audit Trail.
4. **Conservatism:** When ambiguous, use the more conservative (lower value) approach.
5. **No LLM computation:** All numbers come from deterministic Python code. The LLM only generates narrative text.

---

## 2. Financial Notation Reference

| Symbol | Meaning |
|---|---|
| `R_t` | Revenue in period t |
| `g_1` | Stage 1 revenue growth rate |
| `g_2` | Stage 2 revenue growth rate |
| `m_EBITDA` | EBITDA margin (% of revenue) |
| `m_DA` | D&A margin (% of revenue) |
| `m_CapEx` | CapEx margin (% of revenue) |
| `m_NWC` | ΔNWC margin (% of revenue) |
| `τ` | Effective tax rate |
| `WACC` | Weighted Average Cost of Capital |
| `TGR` | Terminal Growth Rate |
| `EM` | EV/EBITDA Exit Multiple |
| `t` | Year index (1-based) |
| `T` | Final year of explicit forecast period |
| `PV(x)` | Present value of x |

---

## 3. Revenue Projection Engine

### 3.1 Two-Stage Revenue Projection

```
Stage 1 (years 1 through N₁):
    R_t = R_0 × (1 + g₁)^t
    where R_0 = LTM (Last Twelve Months) Revenue
    and N₁ = projection_years_stage1 (default: 5)

Stage 2 (years N₁+1 through N₁+N₂):
    R_t = R_{N₁} × (1 + g₂)^(t - N₁)
    where N₂ = projection_years_stage2 (default: 5, set to 0 for 5-year model)
```

**Implementation:**

```python
def project_revenue(
    ltm_revenue: float,
    growth_stage1: float,      # decimal, e.g., 0.10 for 10%
    growth_stage2: float,      # decimal
    n1: int = 5,
    n2: int = 5
) -> List[float]:
    """Returns list of projected revenues for years 1 through n1+n2."""
    revenues = []
    r = ltm_revenue
    
    for t in range(1, n1 + 1):
        r = r * (1 + growth_stage1)
        revenues.append(round(r, 2))
    
    for t in range(1, n2 + 1):
        r = r * (1 + growth_stage2)
        revenues.append(round(r, 2))
    
    return revenues

# Audit trail entry for each year:
# output_field: "revenue_year_{t}"
# formula: "R_{t-1} × (1 + g₁)" or "R_{t-1} × (1 + g₂)"
# input_values: {"R_{t-1}": <value>, "growth_rate": <rate>}
# result: R_t
```

---

## 4. Income Statement Projection Engine

### 4.1 EBITDA

```
EBITDA_t = R_t × m_EBITDA

where m_EBITDA is the user-configured EBITDA margin assumption
```

### 4.2 Depreciation & Amortization (D&A)

```
DA_t = R_t × m_DA

Note: D&A is projected as a % of revenue for simplicity.
Alternative (PP&E roll): DA_t = Prior PP&E × average_useful_life_pct
    → Used only if user provides granular PP&E data
```

### 4.3 EBIT

```
EBIT_t = EBITDA_t - DA_t
```

### 4.4 Net Operating Profit After Tax (NOPAT)

```
NOPAT_t = EBIT_t × (1 - τ)

If EBIT_t < 0 (operating loss):
    NOPAT_t = EBIT_t × (1 - τ)    [still apply tax shield; negative NOPAT is valid]
    Flag: "EBIT_NEGATIVE_YEAR_{t}"

Note: We use NOPAT, not Net Income, because UFCF is pre-financing.
```

### 4.5 Below-EBIT Items (for Net Income only, not UFCF)

```
EBT_t = EBIT_t - Interest_Expense_t + Interest_Income_t
Tax_t = EBT_t × τ   [if EBT > 0; 0 if EBT ≤ 0 in most jurisdictions]
Net_Income_t = EBT_t - Tax_t

For projections, interest expense is computed from the projected debt schedule:
    Interest_Expense_t = LTM_Long_Term_Debt × average_interest_rate
    (Simplified; full debt schedule in v2.0)
```

---

## 5. Unlevered Free Cash Flow (UFCF) Engine

### 5.1 Core UFCF Formula

```
UFCF_t = NOPAT_t + DA_t - CapEx_t - ΔNWC_t

Where:
    CapEx_t  = R_t × m_CapEx                    [positive outflow; SUBTRACT]
    ΔNWC_t   = R_t × m_NWC                      [positive = use of cash; SUBTRACT]

Full expansion:
    UFCF_t = [EBIT_t × (1 - τ)] + DA_t - [R_t × m_CapEx] - [R_t × m_NWC]
```

**Step-by-Step Computation (with Audit Trail entries):**

```
Step 1: Revenue
    R_t = R_{t-1} × (1 + g)
    Audit: {output: "revenue_t", formula: "R_{t-1} × (1 + g)", inputs: {R_{t-1}: val, g: rate}}

Step 2: EBITDA
    EBITDA_t = R_t × m_EBITDA
    Audit: {output: "ebitda_t", formula: "R_t × m_EBITDA", inputs: {R_t: val, m_EBITDA: margin}}

Step 3: D&A
    DA_t = R_t × m_DA
    Audit: {output: "da_t", formula: "R_t × m_DA", inputs: {R_t: val, m_DA: da_pct}}

Step 4: EBIT
    EBIT_t = EBITDA_t - DA_t
    Audit: {output: "ebit_t", formula: "EBITDA_t - DA_t", inputs: {EBITDA_t: val, DA_t: val}}

Step 5: NOPAT
    NOPAT_t = EBIT_t × (1 - τ)
    Audit: {output: "nopat_t", formula: "EBIT_t × (1 - τ)", inputs: {EBIT_t: val, τ: tax_rate}}

Step 6: CapEx
    CapEx_t = R_t × m_CapEx
    Audit: {output: "capex_t", formula: "R_t × m_CapEx", inputs: {R_t: val, m_CapEx: capex_pct}}

Step 7: ΔNWC
    ΔNWC_t = R_t × m_NWC
    Audit: {output: "delta_nwc_t", formula: "R_t × m_NWC", inputs: {R_t: val, m_NWC: nwc_pct}}

Step 8: UFCF
    UFCF_t = NOPAT_t + DA_t - CapEx_t - ΔNWC_t
    Audit: {output: "ufcf_t", formula: "NOPAT_t + DA_t - CapEx_t - ΔNWC_t",
            inputs: {NOPAT_t: val, DA_t: val, CapEx_t: val, ΔNWC_t: val}}
```

---

## 6. Discounting Engine

### 6.1 Discount Factor

```
DF_t = 1 / (1 + WACC)^t

Convention: End-of-year discounting (standard U.S. banking practice)
Alternative: Mid-year convention (multiply by (1 + WACC)^0.5)
    → v1.0 uses end-of-year; mid-year convention flagged as config option for v1.5
```

### 6.2 Present Value of UFCF

```
PV(UFCF_t) = UFCF_t × DF_t
           = UFCF_t / (1 + WACC)^t
```

### 6.3 Sum of PV(UFCFs)

```
PV_UFCFs = Σ [UFCF_t / (1 + WACC)^t] for t = 1 to T
```

---

## 7. Terminal Value Engine

### 7.1 Gordon Growth Model (Perpetuity Growth)

```
TV_GG = UFCF_T × (1 + TGR) / (WACC - TGR)

Pre-conditions (hard check before computation):
    1. WACC > TGR (strictly greater than)
       → If WACC ≤ TGR: raise GordonGrowthError
    2. TGR ≥ 0 (negative TGR is valid for declining businesses, but warn)
    3. TGR < long-run GDP growth rate (warn if TGR > 4%)
       → If TGR > 5%: raise ASSUMPTION_WARNING

Discounting the Terminal Value:
    PV(TV_GG) = TV_GG / (1 + WACC)^T
```

### 7.2 Exit Multiple (EV/EBITDA)

```
TV_EM = EBITDA_T × EM

Where EM = the assumed EV/EBITDA exit multiple

Discounting the Terminal Value:
    PV(TV_EM) = TV_EM / (1 + WACC)^T

Note: Terminal EBITDA (EBITDA_T) is the final year's projected EBITDA.
      It is NOT EBITDA_T × (1 + TGR) — the exit multiple embeds the growth assumption.
```

### 7.3 Terminal Value as % of Enterprise Value

```
TV_pct_gg = PV(TV_GG) / [PV_UFCFs + PV(TV_GG)] × 100
TV_pct_em = PV(TV_EM) / [PV_UFCFs + PV(TV_EM)] × 100

Flags:
    If TV_pct > 80%: add "TV_HIGH_WARNING" flag to output
    If TV_pct > 95%: add "TV_EXTREME_WARNING" flag (model heavily back-loaded)
```

---

## 8. Enterprise Value & Equity Bridge

### 8.1 Enterprise Value

```
EV_GG = PV_UFCFs + PV(TV_GG)
EV_EM = PV_UFCFs + PV(TV_EM)
```

### 8.2 Net Debt Calculation

```
Total_Debt = Short_Term_Debt + Long_Term_Debt + Capital_Lease_Obligations
Net_Debt = Total_Debt - Cash_and_Equivalents - Short_Term_Investments

Note: If Net_Debt < 0 (net cash position), this is a positive adjustment to equity value.
```

### 8.3 Equity Value Bridge

```
Equity_Value = Enterprise_Value
             - Net_Debt                    [subtract positive net debt]
             - Minority_Interest           [subtract]
             - Preferred_Equity            [subtract]
             + Non-operating_Assets        [add, if provided]

Implied_Share_Price = Equity_Value / Diluted_Shares_Outstanding

Where Diluted_Shares_Outstanding = Basic Shares + Options (treasury stock method)
    + Restricted Stock Units (RSUs)
    + Convertible Securities (if in-the-money)
```

### 8.4 Implied Upside / Downside

```
Implied_Upside_pct = (Implied_Share_Price / Current_Share_Price - 1) × 100

If Current_Share_Price is not provided: flag and skip this calculation.
```

---

## 9. Comparable Company Analysis Engine

### 9.1 Multiple Computation

```
EV_to_Revenue  = Enterprise_Value / LTM_Revenue
EV_to_EBITDA   = Enterprise_Value / LTM_EBITDA    [only if EBITDA > 0]
EV_to_EBIT     = Enterprise_Value / LTM_EBIT      [only if EBIT > 0]
P_to_E         = Market_Cap / LTM_Net_Income       [only if Net_Income > 0]
EV_to_FCF      = Enterprise_Value / LTM_FCF        [only if FCF > 0]

Where:
    LTM = Last Twelve Months (trailing)
    Enterprise_Value = Market_Cap + Net_Debt + Preferred + Minority - Associates
```

### 9.2 Peer Set Statistics

```
For each multiple M across n comparable companies:
    Mean_M    = Σ M_i / n
    Median_M  = middle value when sorted (or average of two middle values)
    P25_M     = 25th percentile (lower quartile)
    P75_M     = 75th percentile (upper quartile)

Outlier Detection:
    σ_M = standard deviation of M across all comps
    Outlier: |M_i - Mean_M| > threshold_sigma × σ_M
    Default threshold_sigma = 2.0

If exclude_outliers_from_stats=True:
    Remove outliers and recompute statistics on clean set
    Always report n_companies and n_excluded_outliers
```

### 9.3 Implied Valuation Range

```
Implied_EV_low    = Subject_LTM_Metric × P25_Multiple
Implied_EV_median = Subject_LTM_Metric × Median_Multiple
Implied_EV_high   = Subject_LTM_Metric × P75_Multiple

Primary multiple for comps-based valuation:
    Preferred: EV/EBITDA (if EBITDA positive)
    Fallback 1: EV/Revenue (for pre-profitability)
    Fallback 2: EV/FCF (for FCF-generative mature businesses)

Equity_Value = EV - Net_Debt
Implied_Price = Equity_Value / Shares_Outstanding
```

---

## 10. Sensitivity Analysis Engine

### 10.1 WACC vs. TGR Sensitivity Matrix

```
For each (WACC_i, TGR_j) combination in the sensitivity ranges:
    
    If WACC_i > TGR_j:
        Run DCF with WACC = WACC_i, TGR = TGR_j (all other inputs held constant)
        Record Implied_Share_Price (or EV) in matrix[WACC_i][TGR_j]
    
    If WACC_i ≤ TGR_j:
        Record None in matrix[WACC_i][TGR_j]
        Label as "N/A"

Implementation principle: The sensitivity function receives a callable DCF function.
It does NOT duplicate DCF logic — it calls run_dcf() with overridden WACC/TGR.
```

### 10.2 WACC vs. Exit Multiple Sensitivity Matrix

```
For each (WACC_i, EM_j) combination:
    Run DCF with WACC = WACC_i, Exit_Multiple = EM_j
    Record Implied_Share_Price in matrix[WACC_i][EM_j]
    
Note: No WACC/EM constraint — all combinations are valid.
```

### 10.3 Color Coding Logic

```
Base case value = matrix[base_wacc][base_tgr]

For each cell value V:
    If V > base_case_value:  color = GREEN
    If V < base_case_value:  color = RED
    If V == base_case_value: color = YELLOW / NEUTRAL

Color intensity: scale intensity proportional to % deviation from base case
    |V - base| / base × 100 → map to opacity (light = small deviation, dark = large)
```

---

## 11. Balance Sheet Integrity Engine

### 11.1 Balance Sheet Check

```
For each projected period t:
    
    CHECK: Total_Assets_t == Total_Liabilities_t + Total_Equity_t
    
    Delta_t = Total_Assets_t - (Total_Liabilities_t + Total_Equity_t)
    
    If |Delta_t| ≤ tolerance (default: 0.01, i.e., $10k for $M statements):
        Result: PASS
    
    Else:
        Result: FAIL
        
        Plug suggestion:
            If Delta_t > 0: "Assets exceed L+E by ${Delta_t}M. Suggest: Add ${Delta_t}M to Cash or reduce Goodwill."
            If Delta_t < 0: "L+E exceed Assets by ${abs(Delta_t)}M. Suggest: Reduce Cash by ${abs(Delta_t)}M or check Retained Earnings roll."
        
        Blocking: FAIL blocks all downstream computation (hard block)
```

### 11.2 Cash Flow Reconciliation Check

```
For each projected period t:
    
    CHECK: CFS_Ending_Cash_t == BS_Cash_t
    
    CFS_Ending_Cash_t = CFS_Beginning_Cash_t + CFO_t + CFI_t + CFF_t
    
    Delta_t = CFS_Ending_Cash_t - BS_Cash_t
    
    If |Delta_t| ≤ tolerance:
        Result: PASS
    
    Else:
        Result: FAIL
        Suggest: "Review beginning cash balance or other financing activities."
        Blocking: FAIL blocks all downstream computation
```

### 11.3 Net Income Link Check

```
For each projected period t:

    CHECK: IS_Net_Income_t ≈ BS_Retained_Earnings_t - BS_Retained_Earnings_{t-1} + Dividends_t

    This ensures Net Income flows correctly from IS to BS (Retained Earnings roll).
    
    Tolerance: ±0.01 (same as above)
    If FAIL: Flag as "IS_BS_NET_INCOME_MISMATCH_YEAR_{t}" — warning, not block
```

---

## 12. WACC Computation (Reference Only)

The FMVA v1.0 accepts WACC as a user-supplied input. The following formula documents how WACC should be computed externally for reference:

```
WACC = (E/V) × Ke + (D/V) × Kd × (1 - τ)

Where:
    E = Equity market capitalization
    D = Total debt (book value or market value)
    V = E + D
    Ke = Cost of equity [via CAPM: Ke = Rf + β × (Rm - Rf) + size_premium]
    Kd = Pre-tax cost of debt [average interest rate on outstanding debt]
    τ  = Effective tax rate
    Rf = Risk-free rate (typically 10-year US Treasury yield)
    β  = Equity Beta (from Bloomberg or computed from regression)
    Rm - Rf = Equity Risk Premium (typically 4.5–6% for US)

FMVA v2.0: Compute WACC automatically from market data feed.
FMVA v1.0: User inputs WACC directly. System validates bounds (5–25%).
```

---

## 13. Numerical Precision Rules

| Operation | Precision Rule |
|---|---|
| All intermediate computations | Full float64 precision (no rounding) |
| Display values | 2 decimal places for currency, 1 for percentages |
| % of revenue margins | 4 decimal places internally (e.g., 0.2000 = 20.00%) |
| Share price output | 2 decimal places (e.g., $57.14) |
| EV / Equity Value | Display in $M or $B with 1 decimal place |
| Sensitivity matrix cells | 2 decimal places (share price) or $M (EV) |
| Discount factors | 8 decimal places internally |
| Excel export values | Full precision stored in cell; format applied for display |

---

## 14. Edge Cases & Guard Rails

| Scenario | Handling |
|---|---|
| Revenue = 0 (first year startup) | Allow; flag as "ZERO_REVENUE_BASE" |
| EBITDA < 0 (loss-making company) | Allow; flag EBITDA_NEGATIVE; skip EV/EBITDA comps multiple |
| UFCF < 0 in multiple years | Allow; discount as-is; add flag for each negative year |
| CapEx > Revenue (impossible) | Warn: ASSUMPTION_WARNING; allow if confirmed |
| Shares outstanding = 0 | Error: MISSING_SHARES_OUTSTANDING; skip per-share outputs |
| Net Debt negative (net cash) | Allow; adds to equity value |
| Comp with no EBITDA | Skip EV/EBITDA for that comp; include in other multiples |
| Comp with negative EBITDA | Exclude from EV/EBITDA calculation; include in revenue multiples |
| Division by zero anywhere | Wrap all divisions in safe_divide(); return None on /0 |

```python
def safe_divide(numerator: float, denominator: float, fallback: Optional[float] = None) -> Optional[float]:
    """Safe division that returns fallback (default None) on zero denominator."""
    if denominator == 0 or denominator is None:
        return fallback
    return numerator / denominator
```

---

## 15. Audit Trail Formula Strings

All audit trail `formula` strings use this notation standard:

```python
FORMULA_STRINGS = {
    "revenue_stage1": "R_{t} = R_{t-1} × (1 + g₁)",
    "revenue_stage2": "R_{t} = R_{t-1} × (1 + g₂)",
    "ebitda": "EBITDA = R × m_EBITDA",
    "da": "D&A = R × m_DA",
    "ebit": "EBIT = EBITDA - D&A",
    "nopat": "NOPAT = EBIT × (1 - τ)",
    "capex": "CapEx = R × m_CapEx",
    "delta_nwc": "ΔNWC = R × m_NWC",
    "ufcf": "UFCF = NOPAT + D&A - CapEx - ΔNWC",
    "discount_factor": "DF = 1 / (1 + WACC)^t",
    "pv_ufcf": "PV(UFCF) = UFCF × DF",
    "tv_gg": "TV_GG = UFCF_T × (1 + TGR) / (WACC - TGR)",
    "tv_em": "TV_EM = EBITDA_T × Exit_Multiple",
    "pv_tv": "PV(TV) = TV / (1 + WACC)^T",
    "ev": "EV = Σ PV(UFCF) + PV(TV)",
    "net_debt": "Net Debt = Total Debt - Cash",
    "equity_value": "Equity Value = EV - Net Debt - Minority Interest - Preferred",
    "implied_price": "Price = Equity Value / Diluted Shares Outstanding",
}
```

---

*Document Owner: Engineering (Quantitative) | Last Updated: 2026-02-23*
