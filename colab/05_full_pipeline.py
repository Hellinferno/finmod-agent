# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 🚀 FMVA — Full Pipeline Demo
#
# Run the complete valuation pipeline in a single call:
# `ingest → normalize → validate → BS check → DCF → export`

# %%
from fmva.pipeline import run_full_pipeline
from fmva.config import FIXTURES_DIR

# %% [markdown]
# ## 1. Run for TechCorp (Base Case)

# %%
result = run_full_pipeline(
    data_path=str(FIXTURES_DIR / "techcorp.json"),
    scenario="base",
    output_dir="outputs",
    export_excel=True,
    export_json_flag=True,
)

print(f"\n🎯 {result.metadata.company_name}")
print(f"   EV (Gordon):    ${result.dcf.enterprise_value_gordon:>12,.0f}M")
print(f"   EV (Exit Mult): ${result.dcf.enterprise_value_exit_multiple:>12,.0f}M")
print(f"   Implied Price:  ${result.dcf.implied_price_gordon:>8,.2f} – ${result.dcf.implied_price_exit_multiple:,.2f}")

# %% [markdown]
# ## 2. Run All Scenarios

# %%
for scenario in ["bear", "base", "bull"]:
    r = run_full_pipeline(
        data_path=str(FIXTURES_DIR / "techcorp.json"),
        scenario=scenario,
        output_dir="outputs",
        export_excel=False,
        export_json_flag=False,
    )
    dcf = r.dcf
    print(f"   {scenario.upper():5s}: EV=${dcf.enterprise_value_gordon:>10,.0f}M  "
          f"Price=${dcf.implied_price_gordon:>7,.2f} – ${dcf.implied_price_exit_multiple:,.2f}")

# %% [markdown]
# ## 3. Run for All Fixtures

# %%
for fixture in ["techcorp.json", "manufactureco.json", "retailchain.json"]:
    try:
        r = run_full_pipeline(
            data_path=str(FIXTURES_DIR / fixture),
            scenario="base",
            output_dir="outputs",
            export_excel=True,
        )
        print(f"   ✅ {r.metadata.company_name}: EV=${r.dcf.enterprise_value_gordon:,.0f}M")
    except Exception as e:
        print(f"   ❌ {fixture}: {e}")

print("\n📁 All outputs saved to ./outputs/")
print("🎉 Pipeline demo complete!")
