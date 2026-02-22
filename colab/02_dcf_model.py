# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 💰 FMVA — DCF Valuation Model
#
# Run a full Discounted Cash Flow valuation with Gordon Growth
# and Exit Multiple terminal value methods.

# %% [markdown]
# ## 1. Load & Normalize Data

# %%
from fmva.core.ingestion import load_json
from fmva.core.normalization import normalize
from fmva.config import FIXTURES_DIR

raw = load_json(str(FIXTURES_DIR / "techcorp.json"))
financials = normalize(raw)
print(f"📋 {financials.metadata.company_name} — LTM Revenue: ${financials.latest_income_statement.revenue:,.0f}M")

# %% [markdown]
# ## 2. Configure Assumptions

# %%
from fmva.engines.assumptions import get_preset

# Choose scenario: "bear", "base", or "bull"
assumptions = get_preset("base")

print(f"\n⚙️ Scenario: {assumptions.scenario.value.upper()}")
print(f"   Revenue growth: {[f'{g:.0%}' for g in assumptions.revenue_growth_rates]}")
print(f"   EBITDA margin: {assumptions.ebitda_margin:.0%}")
print(f"   Tax rate: {assumptions.tax_rate:.0%}")
print(f"   TGR: {assumptions.terminal_growth_rate:.1%}")
print(f"   Exit multiple: {assumptions.exit_multiple}x")

# %% [markdown]
# ## 3. Calculate WACC

# %%
from fmva.engines.wacc import calculate_wacc
from fmva.audit.trail import AuditTrail

audit = AuditTrail(company_name=financials.metadata.company_name)

wacc_result = calculate_wacc(
    beta=1.2,  # Override or use yfinance auto-fetch via ticker=
    debt_rate=0.055,
    tax_rate=assumptions.tax_rate,
    target_d_to_e=0.30,
    audit=audit,
)

print(f"\n📊 WACC: {wacc_result.wacc:.2%}")
print(f"   Cost of equity: {wacc_result.cost_of_equity:.2%}")
print(f"   Cost of debt (AT): {wacc_result.cost_of_debt_after_tax:.2%}")
print(f"   Equity weight: {wacc_result.weight_equity:.1%}")

# %% [markdown]
# ## 4. Run Full DCF

# %%
from fmva.engines.dcf import run_full_dcf

dcf = run_full_dcf(financials, assumptions, wacc_result, audit)

print(f"\n🎯 DCF Results — {financials.metadata.company_name}")
print(f"{'─' * 50}")
print(f"   Sum PV(UFCF):        ${dcf.sum_pv_ufcf:>12,.1f}M")
print(f"   TV (Gordon):         ${dcf.terminal_value_gordon:>12,.1f}M")
print(f"   TV (Exit Multiple):  ${dcf.terminal_value_exit_multiple:>12,.1f}M")
print(f"   PV TV (Gordon):      ${dcf.pv_terminal_value_gordon:>12,.1f}M")
print(f"   PV TV (Exit):        ${dcf.pv_terminal_value_exit_multiple:>12,.1f}M")
print(f"{'─' * 50}")
print(f"   EV (Gordon):         ${dcf.enterprise_value_gordon:>12,.1f}M")
print(f"   EV (Exit Multiple):  ${dcf.enterprise_value_exit_multiple:>12,.1f}M")
print(f"   Net Debt:            ${dcf.net_debt:>12,.1f}M")
print(f"{'─' * 50}")
print(f"   Equity (Gordon):     ${dcf.equity_value_gordon:>12,.1f}M")
print(f"   Equity (Exit):       ${dcf.equity_value_exit_multiple:>12,.1f}M")
if dcf.implied_price_gordon:
    print(f"{'─' * 50}")
    print(f"   Implied Price (G):   ${dcf.implied_price_gordon:>12,.2f}")
    print(f"   Implied Price (EM):  ${dcf.implied_price_exit_multiple:>12,.2f}")
if financials.metadata.current_share_price:
    print(f"   Current Price:       ${financials.metadata.current_share_price:>12,.2f}")

# %% [markdown]
# ## 5. View Projected Financials

# %%
import pandas as pd

proj = dcf.projection
proj_rows = []
for t in proj.years:
    proj_rows.append({
        "Year": t,
        "Revenue": f"${proj.revenue[t]:,.0f}M",
        "EBITDA": f"${proj.ebitda[t]:,.0f}M",
        "NOPAT": f"${proj.nopat[t]:,.0f}M",
        "UFCF": f"${proj.ufcf[t]:,.0f}M",
        "DF": f"{dcf.discount_factors[t]:.4f}",
        "PV(UFCF)": f"${dcf.pv_ufcf[t]:,.1f}M",
    })
print("\n📈 Projected Financials:")
print(pd.DataFrame(proj_rows).to_string(index=False))

# %% [markdown]
# ## 6. Audit Trail

# %%
audit_df = audit.to_dataframe()
print(f"\n📋 Audit Trail: {len(audit)} entries")
print(audit_df[["step", "formula", "output", "unit"]].head(15).to_string(index=False))

print("\n→ Proceed to 03_comps_analysis.py")
