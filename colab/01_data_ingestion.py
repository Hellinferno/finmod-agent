# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 📊 FMVA — Data Ingestion & Normalization
#
# Load raw financial data, normalize field names, validate integrity,
# and check balance sheet consistency.

# %% [markdown]
# ## 1. Load Raw Data

# %%
from fmva.core.ingestion import load_json
from fmva.config import FIXTURES_DIR

# Load the TechCorp fixture (or replace with your own data path)
DATA_PATH = str(FIXTURES_DIR / "techcorp.json")
raw_data = load_json(DATA_PATH)

print(f"Company: {raw_data['company_name']}")
print(f"Years: {list(raw_data['income_statement'].keys())}")
print(f"Sections: {[k for k in raw_data.keys() if not k.startswith('_')]}")

# %% [markdown]
# ## 2. Normalize to Canonical Schema

# %%
from fmva.core.normalization import normalize

financials = normalize(raw_data)

print(f"\n📋 {financials.metadata.company_name}")
print(f"   Ticker: {financials.metadata.ticker}")
print(f"   Years: {financials.historical_years}")
print(f"   Latest revenue: ${financials.latest_income_statement.revenue:,.1f}M")
print(f"   Latest EBITDA: ${financials.latest_income_statement.ebitda:,.1f}M")

# %% [markdown]
# ## 3. Validate Data Integrity

# %%
from fmva.core.validation import validate

report = validate(financials)
print(f"\n✅ Validation: {'PASSED' if report.passed else '❌ FAILED'}")
for e in report.errors:
    print(f"   ✗ {e}")
for w in report.warnings:
    print(f"   ⚠ {w}")

# %% [markdown]
# ## 4. Check Balance Sheet

# %%
from fmva.core.checker import check_all_balance_sheets

bs_results = check_all_balance_sheets(financials)
for r in bs_results:
    status = "✅ Balanced" if r.balanced else f"❌ Imbalanced (Δ=${r.delta:,.2f}M)"
    print(f"   Year {r.year}: {status}")

# %% [markdown]
# ## 5. Display Historical Summary

# %%
import pandas as pd

rows = []
for year in financials.historical_years:
    is_stmt = financials.income_statements[year]
    rows.append({
        "Year": year,
        "Revenue ($M)": f"{is_stmt.revenue:,.1f}",
        "EBITDA ($M)": f"{is_stmt.ebitda:,.1f}" if is_stmt.ebitda else "N/A",
        "EBITDA Margin": f"{is_stmt.ebitda / is_stmt.revenue:.1%}" if is_stmt.ebitda and is_stmt.revenue else "N/A",
        "Net Income ($M)": f"{is_stmt.net_income:,.1f}" if is_stmt.net_income else "N/A",
    })

df = pd.DataFrame(rows)
print("\n📈 Historical Income Statement Summary:")
print(df.to_string(index=False))
print("\n→ Proceed to 02_dcf_model.py")
