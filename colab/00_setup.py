# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # 🚀 FMVA — Setup & Environment Configuration
#
# This notebook sets up the Financial Modeling & Valuation Agent environment.
# Run this **once** at the start of every Colab session.

# %% [markdown]
# ## 1. Install Dependencies

# %%
# Install FMVA package and dependencies
import subprocess, sys

# In Colab, install from the mounted Drive:
# !pip install -e /content/drive/MyDrive/valuation_agent/finmod-agent

# For local development:
subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", ".", "-q"])

# %% [markdown]
# ## 2. Mount Google Drive (Colab Only)

# %%
import os

if "COLAB_GPU" in os.environ:
    from google.colab import drive
    drive.mount("/content/drive")
    print("✅ Google Drive mounted")
else:
    print("ℹ️ Not running in Colab — using local filesystem")

# %% [markdown]
# ## 3. Configure Logging

# %%
from fmva.logging_config import configure_logging

logger = configure_logging(session_name="fmva_setup")
logger.info("FMVA environment configured")

# %% [markdown]
# ## 4. Verify Installation

# %%
import fmva
print(f"✅ FMVA v{fmva.__version__} loaded")

from fmva.core.schemas import FinancialStatements, AssumptionSet, DCFResult
from fmva.engines.assumptions import get_preset
from fmva.config import DEFAULT_CONFIG

print(f"   Config: WACC bounds [{DEFAULT_CONFIG.wacc_min:.0%} – {DEFAULT_CONFIG.wacc_max:.0%}]")
print(f"   Default model: {DEFAULT_CONFIG.model_name}")
print(f"   Bear/Base/Bull presets ready")

# %% [markdown]
# ## 5. Check GPU (for LLM narrative)

# %%
try:
    import torch
    if torch.cuda.is_available():
        gpu = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_mem / 1e9
        print(f"✅ GPU: {gpu} ({vram:.1f} GB VRAM)")
    else:
        print("⚠️ No GPU detected — LLM narrative will be slow or unavailable")
except ImportError:
    print("⚠️ PyTorch not installed — LLM features unavailable")

print("\n🎉 Setup complete! Proceed to 01_data_ingestion.py")
