"""
Global configuration and default constants for the FMVA system.

All constants are defined here to ensure a single source of truth.
Users may override these at runtime via AssumptionSet or notebook config cells.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────────────────────
# Local development paths (overridden in Colab by Drive mount)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
FIXTURES_DIR = DATA_DIR / "fixtures"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
LOG_DIR = PROJECT_ROOT / "logs"
MODEL_DIR = PROJECT_ROOT / "models"

# Google Drive paths (used when running in Colab)
DRIVE_ROOT = "/content/drive/MyDrive/valuation_agent"
DRIVE_DATA_DIR = f"{DRIVE_ROOT}/data"
DRIVE_OUTPUT_DIR = f"{DRIVE_ROOT}/outputs"
DRIVE_LOG_DIR = f"{DRIVE_ROOT}/logs"
DRIVE_MODEL_DIR = f"{DRIVE_ROOT}/models"
DRIVE_CACHE_DIR = f"{DRIVE_ROOT}/cache/yfinance"

# ── Numerical Precision ────────────────────────────────────────────────────────
BALANCE_SHEET_TOLERANCE = 0.01  # $0.01M tolerance for A = L + E check
EBITDA_CONSISTENCY_TOLERANCE = 0.005  # ±0.5% for EBITDA = EBIT + D&A
CASH_FLOW_REASONABLENESS_TOLERANCE = 0.10  # ±10% for OCF vs NI+D&A±ΔWC
DCF_CROSS_VALIDATION_TOLERANCE = 0.001  # ±0.1% for DCF vs manual Excel
DISPLAY_CURRENCY_DECIMALS = 2
DISPLAY_PERCENT_DECIMALS = 1
INTERNAL_MARGIN_DECIMALS = 4
DISCOUNT_FACTOR_DECIMALS = 8

# ── WACC Bounds ────────────────────────────────────────────────────────────────
WACC_MIN = 0.05  # 5%
WACC_MAX = 0.25  # 25%
DEFAULT_BETA = 1.0  # Used when yfinance beta is unavailable
DEFAULT_RISK_FREE_RATE = 0.045  # 4.5%
DEFAULT_EQUITY_RISK_PREMIUM = 0.055  # 5.5%

# ── Terminal Value ─────────────────────────────────────────────────────────────
TGR_WARNING_THRESHOLD = 0.04  # Warn if TGR > 4%
TGR_ERROR_THRESHOLD = 0.05  # Error if TGR > 5%
TV_HIGH_WARNING_PCT = 80  # Warn if TV > 80% of EV
TV_EXTREME_WARNING_PCT = 95  # Extreme warning if TV > 95% of EV

# ── Comps ──────────────────────────────────────────────────────────────────────
MIN_COMPARABLE_COMPANIES = 3
OUTLIER_SIGMA_THRESHOLD = 2.0
YFINANCE_CACHE_TTL_HOURS = 24

# ── LLM ────────────────────────────────────────────────────────────────────────
DEFAULT_MODEL_NAME = "unsloth/mistral-7b-v0.3-bnb-4bit"
DEFAULT_MAX_SEQ_LENGTH = 4096
DEFAULT_MAX_NEW_TOKENS = 512
HALLUCINATION_TOLERANCE = 0.05  # ±5% for number verification

# ── Temperature Strategy (per narrative section) ───────────────────────────────
LLM_TEMPERATURES = {
    "executive_summary": 0.3,
    "dcf_commentary": 0.2,
    "comps_commentary": 0.25,
    "risk_factors": 0.5,
    "investment_thesis": 0.4,
}

# ── Reproducibility ────────────────────────────────────────────────────────────
RANDOM_SEED = 42

# ── Performance Targets ────────────────────────────────────────────────────────
MAX_PIPELINE_TIME_NO_LLM_SECS = 60
MAX_PIPELINE_TIME_WITH_LLM_SECS = 360
MAX_MODEL_LOAD_TIME_SECS = 90
MAX_NARRATIVE_SECTION_TIME_SECS = 60


@dataclass(frozen=True)
class FMVAConfig:
    """Immutable runtime configuration."""

    balance_sheet_tolerance: float = BALANCE_SHEET_TOLERANCE
    dcf_tolerance: float = DCF_CROSS_VALIDATION_TOLERANCE
    wacc_min: float = WACC_MIN
    wacc_max: float = WACC_MAX
    default_beta: float = DEFAULT_BETA
    default_risk_free_rate: float = DEFAULT_RISK_FREE_RATE
    default_equity_risk_premium: float = DEFAULT_EQUITY_RISK_PREMIUM
    min_comps: int = MIN_COMPARABLE_COMPANIES
    outlier_sigma: float = OUTLIER_SIGMA_THRESHOLD
    random_seed: int = RANDOM_SEED
    model_name: str = DEFAULT_MODEL_NAME
    max_seq_length: int = DEFAULT_MAX_SEQ_LENGTH
    hallucination_tolerance: float = HALLUCINATION_TOLERANCE


# Singleton config instance
DEFAULT_CONFIG = FMVAConfig()
