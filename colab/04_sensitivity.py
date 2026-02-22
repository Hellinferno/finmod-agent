# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 🔬 FMVA — Sensitivity Analysis & Football Field
#
# Build WACC × TGR sensitivity matrices and generate the valuation football field chart.

# %%
from fmva.core.ingestion import load_json
from fmva.core.normalization import normalize
from fmva.core.schemas import WACCResult
from fmva.engines.assumptions import get_preset
from fmva.engines.dcf import run_full_dcf
from fmva.engines.sensitivity import wacc_tgr_sensitivity, plot_football_field
from fmva.audit.trail import AuditTrail
from fmva.config import FIXTURES_DIR

# Quick DCF run for base data
raw = load_json(str(FIXTURES_DIR / "techcorp.json"))
financials = normalize(raw)
assumptions = get_preset("base")
wacc_r = WACCResult(wacc=0.10, cost_of_equity=0.10, cost_of_debt_after_tax=0.04,
                    beta=1.0, risk_free_rate=0.045, equity_risk_premium=0.055,
                    weight_equity=0.77, weight_debt=0.23)
dcf = run_full_dcf(financials, assumptions, wacc_r)
print(f"📋 Base DCF: EV=${dcf.enterprise_value_gordon:,.0f}M, Price=${dcf.implied_price_gordon:,.2f}")

# %% [markdown]
# ## 1. WACC × TGR Sensitivity Matrix

# %%
import pandas as pd

audit = AuditTrail()
n = assumptions.projection_years
last_ufcf = dcf.projection.ufcf[n]
shares = financials.metadata.diluted_shares_outstanding

matrix = wacc_tgr_sensitivity(
    base_ufcf=last_ufcf,
    base_sum_pv=dcf.sum_pv_ufcf,
    net_debt=dcf.net_debt,
    shares=shares,
    n_years=n,
    mid_year=True,
    wacc_range=[0.08, 0.09, 0.10, 0.11, 0.12],
    tgr_range=[0.015, 0.020, 0.025, 0.030, 0.035],
    audit=audit,
)

# Format as DataFrame
df = pd.DataFrame(
    matrix["data"],
    index=[f"WACC={w:.0%}" for w in matrix["row_values"]],
    columns=[f"TGR={t:.1%}" for t in matrix["col_values"]],
)
df = df.applymap(lambda x: f"${x:,.2f}" if x else "N/A")
print("\n📊 WACC × TGR Sensitivity (Implied Share Price):")
print(df.to_string())

# %% [markdown]
# ## 2. Football Field Chart

# %%
fig = plot_football_field(
    dcf_range=(dcf.implied_price_gordon, dcf.implied_price_exit_multiple),
    current_price=financials.metadata.current_share_price,
    output_path="outputs/football_field.png",
)
print("\n🏈 Football field chart generated → outputs/football_field.png")

# %% [markdown]
# ## Done!
# → Proceed to 05_full_pipeline.py for the complete end-to-end run.
