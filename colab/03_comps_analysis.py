# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 📊 FMVA — Comparable Company Analysis
#
# Fetch peer company data, compute valuation multiples, and derive implied EV ranges.

# %%
from fmva.core.ingestion import load_json
from fmva.core.normalization import normalize
from fmva.engines.comps import fetch_comp_data, calculate_comps_stats, apply_comps_multiples
from fmva.audit.trail import AuditTrail
from fmva.config import FIXTURES_DIR

# Load target company
raw = load_json(str(FIXTURES_DIR / "techcorp.json"))
financials = normalize(raw)
latest_is = financials.latest_income_statement

print(f"📋 Target: {financials.metadata.company_name}")
print(f"   LTM Revenue: ${latest_is.revenue:,.0f}M")
print(f"   LTM EBITDA: ${latest_is.ebitda:,.0f}M")

# %% [markdown]
# ## 1. Fetch Comparable Companies

# %%
# Define peer group (edit these tickers for your analysis)
PEER_TICKERS = ["MSFT", "GOOGL", "ORCL", "CRM", "ADBE"]

print(f"\n🔍 Fetching data for {len(PEER_TICKERS)} peers...")
comps = fetch_comp_data(PEER_TICKERS)

import pandas as pd
comp_table = [{
    "Ticker": c.ticker, "Name": c.company_name,
    "Market Cap ($M)": f"{c.market_cap:,.0f}" if c.market_cap else "N/A",
    "EV/EBITDA": f"{c.ev_ebitda:.1f}x" if c.ev_ebitda else "N/A",
    "EV/Revenue": f"{c.ev_revenue:.1f}x" if c.ev_revenue else "N/A",
    "P/E": f"{c.pe_ratio:.1f}x" if c.pe_ratio else "N/A",
} for c in comps]
print(pd.DataFrame(comp_table).to_string(index=False))

# %% [markdown]
# ## 2. Calculate Statistics

# %%
stats = calculate_comps_stats(comps)

print(f"\n📊 Multiple Statistics ({stats.n_companies} companies, {stats.n_excluded_outliers} outliers removed):")
for mult_name, vals in stats.multiples.items():
    if vals["median"] is not None:
        print(f"   {mult_name:12s}: "
              f"Min={vals['min']:.1f}x  P25={vals['p25']:.1f}x  "
              f"Median={vals['median']:.1f}x  P75={vals['p75']:.1f}x  Max={vals['max']:.1f}x")

# %% [markdown]
# ## 3. Apply Multiples to Target

# %%
audit = AuditTrail(company_name=financials.metadata.company_name)
result = apply_comps_multiples(stats, latest_is.ebitda, latest_is.revenue, audit)

print(f"\n🎯 Implied Enterprise Value Range:")
print(f"   EV/EBITDA: ${result.implied_ev_ebitda_low:,.0f}M – ${result.implied_ev_ebitda_high:,.0f}M (median: ${result.implied_ev_ebitda_median:,.0f}M)")
print(f"   EV/Revenue: ${result.implied_ev_revenue_low:,.0f}M – ${result.implied_ev_revenue_high:,.0f}M (median: ${result.implied_ev_revenue_median:,.0f}M)")

print("\n→ Proceed to 04_sensitivity.py")
