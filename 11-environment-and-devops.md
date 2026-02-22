# 11 — Environment & DevOps
### Financial Modeling & Valuation Agent | Colab + Unsloth Stack

---

## 1. Document Purpose

This document is the **definitive configuration reference** for every environment, tool, dependency, and operational procedure used in the Financial Modeling & Valuation Agent project. It covers the Google Colab runtime, Unsloth/GPU configuration, dependency management, Google Drive integration, versioning, and the lightweight CI/CD process appropriate for a notebook-first project.

> **Key principle**: Since the primary runtime is Google Colab (not a traditional server), DevOps practices are adapted for notebook reproducibility, Drive-based persistence, and single-user execution. There is no containerized deployment or CI server in V1.

---

## 2. Runtime Environment

### 2.1 Primary Runtime: Google Colab

| Parameter | Value |
|-----------|-------|
| Platform | Google Colab Pro+ |
| Python Version | 3.10.x (Colab default) |
| GPU (Standard) | NVIDIA T4 (15 GB VRAM) |
| GPU (High-RAM) | NVIDIA A100 (40 GB VRAM) — for LLM fine-tuning only |
| RAM | 12.7 GB (T4 runtime) / 83.5 GB (High-RAM runtime) |
| Disk (ephemeral) | ~107 GB |
| Persistent Storage | Google Drive (mounted) |
| Network | Outbound HTTP allowed; no inbound |
| Session Timeout | 12 hours (Pro+) |

### 2.2 Runtime Selection Guide

| Task | Runtime to Select | Reason |
|------|------------------|--------|
| Data ingestion, normalization | CPU / T4 | No GPU needed |
| DCF, Comps, Sensitivity calculations | CPU / T4 | Numpy/Pandas only |
| LLM Narrative Generation (inference) | T4 GPU | 4-bit quantized Mistral-7B |
| Unsloth fine-tuning (if applicable) | A100 High-RAM | Full QLoRA training |
| Excel/PDF export | CPU / T4 | No GPU needed |

### 2.3 Runtime Environment Variables

Set at the top of every notebook using Colab Secrets (`userdata.get`) or manual assignment:

```python
# --- Environment Configuration (Cell 1 of every notebook) ---
import os
from google.colab import userdata

# Secrets stored in Colab Secrets (left sidebar → 🔑 icon)
HUGGINGFACE_TOKEN = userdata.get("HF_TOKEN")          # Required for gated models
OPENAI_API_KEY = userdata.get("OPENAI_KEY")            # Optional: GPT-4 fallback
YFINANCE_CACHE_DIR = "/content/drive/MyDrive/valuation_agent/cache/yfinance/"

# Paths (always use Drive paths for persistence)
ROOT_DIR = "/content/drive/MyDrive/valuation_agent/"
DATA_DIR = ROOT_DIR + "data/"
MODEL_DIR = ROOT_DIR + "models/"
OUTPUT_DIR = ROOT_DIR + "outputs/"
LOG_DIR = ROOT_DIR + "logs/"
FIXTURES_DIR = DATA_DIR + "fixtures/"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
```

---

## 3. Dependency Management

### 3.1 Master `requirements.txt`

All dependencies must be pinned to exact versions for reproducibility. This file lives in the repo root and in Drive at `ROOT_DIR/config/requirements.txt`.

```
# ============================================================
# Financial Modeling & Valuation Agent — requirements.txt
# Python 3.10+ | Google Colab Pro+
# Last Updated: 2024-Q4
# ============================================================

# --- Core Data & Computation ---
numpy==1.26.3
pandas==2.1.4
scipy==1.12.0

# --- Financial Data ---
yfinance==0.2.36
pandas-datareader==0.10.0

# --- Excel I/O ---
openpyxl==3.1.2
xlsxwriter==3.1.9

# --- Visualization ---
matplotlib==3.8.2
seaborn==0.13.2
plotly==5.18.0

# --- Notebook UI ---
ipywidgets==8.1.2
IPython==8.12.0

# --- LLM / Unsloth ---
# NOTE: Install Unsloth FIRST with its special command (see 3.2)
unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git
transformers==4.40.0
peft==0.10.0
trl==0.8.6
bitsandbytes==0.43.0
accelerate==0.28.0
einops==0.7.0
xformers==0.0.24+cu121  # Colab CUDA 12.1

# --- Templating ---
jinja2==3.1.3

# --- Export ---
reportlab==4.1.0
nbconvert==7.14.0
nbformat==5.9.2

# --- Utilities ---
python-dotenv==1.0.1
pydantic==2.5.3
dataclasses-json==0.6.3
tqdm==4.66.1
loguru==0.7.2
httpx==0.26.0
tenacity==8.2.3           # Retry logic for API calls

# --- Testing ---
pytest==7.4.4
pytest-cov==4.1.0
pytest-mock==3.12.0

# --- Type Checking (dev only) ---
mypy==1.8.0
```

### 3.2 Unsloth Installation (Special Procedure)

Unsloth requires a specific installation order due to CUDA dependencies. This must be the **first cell** in any notebook using the LLM:

```python
# Cell 1 — Unsloth Installation (run once per runtime)
# This cell is idempotent — safe to re-run

import subprocess
import sys

def install_unsloth():
    """Install Unsloth with correct Colab CUDA configuration."""
    # Step 1: Install PyTorch (Colab usually has this; reinstall for version lock)
    # Step 2: Install Unsloth with CUDA 12.1 support
    commands = [
        "pip install --quiet --no-deps packaging ninja einops",
        'pip install --quiet "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"',
        "pip install --quiet --no-deps trl peft accelerate bitsandbytes",
    ]
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"WARNING: {cmd}\n{result.stderr}")
        else:
            print(f"✅ {cmd.split()[2]}")

install_unsloth()

# Verify
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
```

### 3.3 Standard Package Installation Cell

For all other non-Unsloth dependencies:

```python
# Cell 2 — Standard Dependencies
!pip install --quiet -r /content/drive/MyDrive/valuation_agent/config/requirements.txt

# Verify key imports
import numpy as np
import pandas as pd
import yfinance as yf
import openpyxl
import ipywidgets as widgets
print("✅ All standard dependencies loaded")
print(f"Pandas: {pd.__version__} | NumPy: {np.__version__}")
```

### 3.4 Dependency Conflict Resolution

Known conflicts and resolutions:

| Conflict | Symptom | Resolution |
|----------|---------|------------|
| `xformers` vs `transformers` version | Flash Attention errors | Pin to versions in requirements.txt |
| `bitsandbytes` CUDA mismatch | `libcuda.so` not found | Run `!ldconfig` before importing |
| `ipywidgets` not rendering | Widget shows as text | Run `from google.colab import output; output.enable_custom_widget_manager()` |
| `yfinance` rate limiting | `429 Too Many Requests` | Use `tenacity` retry + cache to Drive |

---

## 4. Google Drive Integration

### 4.1 Drive Mount Procedure

```python
# Every notebook must begin with Drive mount
from google.colab import drive
import os

drive.mount("/content/drive", force_remount=False)

# Verify mount
assert os.path.exists("/content/drive/MyDrive"), "Drive mount failed!"
print("✅ Google Drive mounted successfully")

# Initialize folder structure
DIRS = [
    "valuation_agent/data/raw",
    "valuation_agent/data/normalized",
    "valuation_agent/data/fixtures",
    "valuation_agent/models",
    "valuation_agent/outputs/excel",
    "valuation_agent/outputs/json",
    "valuation_agent/outputs/pdf",
    "valuation_agent/logs",
    "valuation_agent/config",
    "valuation_agent/cache/yfinance",
    "valuation_agent/notebooks",
]

for d in DIRS:
    os.makedirs(f"/content/drive/MyDrive/{d}", exist_ok=True)

print("✅ Folder structure initialized")
```

### 4.2 Drive Folder Architecture

```
Google Drive/
└── valuation_agent/
    ├── config/
    │   ├── requirements.txt          ← Pinned dependencies
    │   ├── config.py                 ← Global constants
    │   └── default_assumptions.json ← Default driver values
    │
    ├── data/
    │   ├── raw/                      ← User uploads (never modified)
    │   │   └── {company}_{date}/
    │   ├── normalized/               ← Post-normalization JSON
    │   │   └── {company}_{date}_normalized.json
    │   └── fixtures/                 ← Test data
    │       ├── techcorp.json
    │       ├── manufactureco.json
    │       └── retailchain.json
    │
    ├── models/
    │   ├── mistral-7b-4bit/          ← Cached model weights
    │   └── lora-adapters/            ← Fine-tuned adapter weights
    │
    ├── outputs/
    │   ├── excel/                    ← {company}_{date}_valuation.xlsx
    │   ├── json/                     ← {company}_{date}_valuation.json
    │   └── pdf/                      ← {company}_{date}_report.pdf
    │
    ├── logs/
    │   └── session_{timestamp}.log   ← Loguru logs per session
    │
    ├── cache/
    │   └── yfinance/                 ← Cached API responses
    │       └── {ticker}_{date}.pkl
    │
    └── notebooks/                    ← Colab notebook files (.ipynb)
        ├── 00_setup.ipynb
        ├── 01_data_ingestion.ipynb
        ├── 02_dcf_model.ipynb
        ├── 03_comps_analysis.ipynb
        ├── 04_sensitivity_analysis.ipynb
        ├── 05_narrative_engine.ipynb
        └── 06_outputs.ipynb
```

### 4.3 Session Persistence Strategy

Since Colab sessions reset, all persistent state lives on Drive:

| State Type | Persistence Strategy |
|------------|---------------------|
| Installed packages | Re-install from requirements.txt each session |
| Model weights | Cached on Drive; load from Drive path |
| Normalized financial data | JSON files on Drive |
| Assumption sets | JSON files on Drive |
| Valuation results | JSON + Excel on Drive |
| Session logs | Drive `/logs/` |
| yfinance data | Pickle cache on Drive with TTL of 24 hours |

```python
# yfinance caching example
import pickle
from datetime import datetime, timedelta

def fetch_with_cache(ticker: str, force_refresh: bool = False) -> dict:
    cache_path = f"{YFINANCE_CACHE_DIR}{ticker}_{datetime.now().date()}.pkl"
    
    if os.path.exists(cache_path) and not force_refresh:
        with open(cache_path, "rb") as f:
            return pickle.load(f)
    
    data = yf.Ticker(ticker).info
    with open(cache_path, "wb") as f:
        pickle.dump(data, f)
    return data
```

---

## 5. Logging Configuration

### 5.1 Loguru Setup

Every module uses Loguru for structured logging:

```python
# logging_config.py
from loguru import logger
import sys
from datetime import datetime

def configure_logging(session_name: str = None):
    """Configure Loguru for Colab environment."""
    logger.remove()  # Remove default handler
    
    # Session name
    if not session_name:
        session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    log_path = f"{LOG_DIR}{session_name}.log"
    
    # Console output (colored)
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
        level="INFO",
        colorize=True,
    )
    
    # File output (full detail)
    logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} — {message}",
        level="DEBUG",
        rotation="50 MB",
        retention="7 days",
        compression="zip",
    )
    
    logger.info(f"Logging initialized → {log_path}")
    return logger
```

### 5.2 Log Levels & Usage

| Level | When to Use | Example |
|-------|------------|---------|
| `DEBUG` | Internal calculation steps | `logger.debug(f"UFCF Year 3 = {ufcf:.2f}")` |
| `INFO` | Module-level milestones | `logger.info("Normalization complete")` |
| `WARNING` | Non-fatal issues | `logger.warning(f"Beta unavailable for {ticker}, using 1.0")` |
| `ERROR` | Caught exceptions | `logger.error(f"Balance sheet imbalance: delta={delta}")` |
| `CRITICAL` | Fatal errors that stop execution | `logger.critical("Drive mount failed")` |

---

## 6. Version Control

### 6.1 Git Repository Structure

While Colab notebooks are not ideal for Git, source code files (`.py` modules) are version-controlled:

```
valuation-agent/                  ← Git repository root
├── README.md
├── requirements.txt
├── config.py
├── .gitignore
│
├── ingestion/
│   ├── __init__.py
│   ├── loader.py
│   ├── normalizer.py
│   └── validator.py
│
├── assumptions/
│   ├── __init__.py
│   ├── engine.py
│   └── widgets.py
│
├── valuation/
│   ├── __init__.py
│   ├── dcf.py
│   ├── wacc.py
│   ├── comps.py
│   ├── transactions.py
│   └── sensitivity.py
│
├── llm/
│   ├── __init__.py
│   ├── model_loader.py
│   ├── narrative_generator.py
│   ├── evaluator.py
│   └── templates/
│       ├── executive_summary.j2
│       ├── dcf_commentary.j2
│       ├── comps_commentary.j2
│       ├── risk_factors.j2
│       └── investment_thesis.j2
│
├── audit/
│   ├── __init__.py
│   └── trail.py
│
├── export/
│   ├── __init__.py
│   ├── excel_exporter.py
│   ├── json_exporter.py
│   └── pdf_generator.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_ingestion.py
    ├── test_dcf.py
    ├── test_comps.py
    ├── test_sensitivity.py
    ├── test_audit.py
    └── test_export.py
```

### 6.2 `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.env

# Notebooks (tracked separately via nbstripout)
.ipynb_checkpoints/
*/.ipynb_checkpoints/

# Data (never commit financial data)
data/raw/
data/normalized/
*.pkl
*.xlsx
*.pdf

# Models (too large)
models/
*.bin
*.safetensors

# Logs
logs/
*.log

# Secrets
.env
secrets.json
*_secrets.json
```

### 6.3 Branching Strategy

Given the small team size, use a simple trunk-based workflow:

```
main           ← Always working, tested code
  └── dev      ← Integration branch
        ├── feat/ingestion-normalizer
        ├── feat/dcf-engine
        ├── feat/unsloth-narrative
        └── fix/balance-sheet-checker
```

**Rules**:
- No direct commits to `main`
- Every PR requires at least 1 reviewer
- PR must pass all tests before merge
- Notebooks are committed only after stripping outputs (`nbstripout`)

### 6.4 Commit Message Convention

```
feat(dcf): add mid-year convention toggle
fix(normalizer): handle missing EBITDA field gracefully
test(comps): add yfinance mock for offline testing
docs(audit): document trail schema fields
chore(deps): pin transformers to 4.40.0
```

---

## 7. Notebook Management

### 7.1 Notebook Naming Convention

```
{sequence}_{module_name}.ipynb

Examples:
00_setup.ipynb
01_data_ingestion.ipynb
02_dcf_model.ipynb
03_comps_analysis.ipynb
04_sensitivity_analysis.ipynb
05_narrative_engine.ipynb
06_outputs.ipynb
99_full_pipeline_demo.ipynb
```

### 7.2 Standard Notebook Structure

Every notebook follows this cell structure:

```python
# Cell 1: Title & Metadata (Markdown)
"""
# [Module Name]
**Version**: 1.0 | **Author**: [Name] | **Last Updated**: [Date]
**Purpose**: [One-line description]
**Prerequisites**: [List prior notebooks]
"""

# Cell 2: Drive Mount
from google.colab import drive
drive.mount("/content/drive")

# Cell 3: Package Installation
!pip install --quiet -r /content/drive/MyDrive/valuation_agent/config/requirements.txt

# Cell 4: System Path (to import local modules)
import sys
sys.path.insert(0, "/content/drive/MyDrive/valuation_agent/src/")

# Cell 5: Imports & Logging
import numpy as np
import pandas as pd
# ... all imports
from logging_config import configure_logging
logger = configure_logging()

# Cell 6: Configuration
from config import *  # Load all constants

# Cell 7+: Module-specific content

# Final Cell: Session Summary
logger.info("Session complete")
print("✅ Notebook completed successfully")
print(f"Outputs saved to: {OUTPUT_DIR}")
```

### 7.3 nbstripout (Pre-commit Hook)

Before committing notebooks, strip all outputs to keep the repo clean:

```bash
# Install
pip install nbstripout

# Configure for this repo
nbstripout --install

# Manual strip
nbstripout notebooks/*.ipynb
```

---

## 8. API Management

### 8.1 External APIs Used

| API | Purpose | Auth Method | Rate Limit | Fallback |
|-----|---------|-------------|-----------|---------|
| yfinance | Stock data, beta, multiples | None (no auth) | ~2000 req/hour | Cached pickle on Drive |
| HuggingFace Hub | Model download | HF_TOKEN secret | 1 GB/min download | Local Drive cache |
| Federal Reserve (FRED) | Risk-free rate | API Key | 120 req/min | Manual input |

### 8.2 API Retry Logic

All external API calls use `tenacity` for robust retry:

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, ConnectionError)),
)
def fetch_ticker_data(ticker: str) -> dict:
    """Fetch ticker data with automatic retry."""
    stock = yf.Ticker(ticker)
    info = stock.info
    if not info or "symbol" not in info:
        raise ValueError(f"No data returned for {ticker}")
    return info
```

### 8.3 Secret Management

| Secret | Storage Location | Access Method |
|--------|-----------------|--------------|
| HuggingFace Token | Colab Secrets | `userdata.get("HF_TOKEN")` |
| FRED API Key | Colab Secrets | `userdata.get("FRED_KEY")` |
| OpenAI Key (optional) | Colab Secrets | `userdata.get("OPENAI_KEY")` |

**Never**:
- Hardcode any API key in code
- Commit secrets to Git
- Store secrets in notebook cells

---

## 9. Memory Management

### 9.1 VRAM Budget (T4 — 15 GB)

| Component | VRAM Usage | Notes |
|-----------|-----------|-------|
| Mistral-7B (4-bit) | ~4.5 GB | Unsloth quantization |
| KV Cache (4096 ctx) | ~2.0 GB | Inference only |
| Gradient checkpointing | 0 GB | Disabled at inference |
| PyTorch overhead | ~0.5 GB | |
| **Total at inference** | **~7 GB** | 8 GB headroom |
| LoRA fine-tuning total | ~13 GB | Near T4 limit |

### 9.2 Memory Optimization Patterns

```python
# Pattern 1: Clear GPU cache after LLM inference
import gc
import torch

def clear_gpu_memory():
    gc.collect()
    torch.cuda.empty_cache()
    print(f"GPU memory freed. Allocated: {torch.cuda.memory_allocated()/1e9:.2f} GB")

# Pattern 2: Use float32 only where necessary
# All financial computation uses float64 for precision
# LLM inference uses bfloat16 (Unsloth default)

# Pattern 3: Unload LLM when doing Excel export
def unload_model(model):
    del model
    clear_gpu_memory()

# Pattern 4: Chunked processing for large comp lists
def process_tickers_chunked(tickers: list[str], chunk_size: int = 5) -> list:
    results = []
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i+chunk_size]
        results.extend(fetch_comp_data(chunk))
        time.sleep(1)  # Rate limit courtesy
    return results
```

### 9.3 RAM Monitoring

```python
import psutil

def print_memory_status():
    ram = psutil.virtual_memory()
    print(f"RAM: {ram.used/1e9:.1f} GB used / {ram.total/1e9:.1f} GB total ({ram.percent}%)")
    if torch.cuda.is_available():
        vram_used = torch.cuda.memory_allocated() / 1e9
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"VRAM: {vram_used:.1f} GB used / {vram_total:.1f} GB total")
```

---

## 10. Reproducibility Standards

### 10.1 Random Seed Policy

```python
# Always set at the top of every notebook/script
import random
import numpy as np
import torch

RANDOM_SEED = 42

def set_all_seeds(seed: int = RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_all_seeds()
```

### 10.2 Numerical Precision Policy

| Computation Type | dtype | Reason |
|-----------------|-------|--------|
| All financial calculations | `float64` | Maximum precision for money |
| LLM inference | `bfloat16` | GPU efficiency |
| Matplotlib rendering | `float32` | Sufficient for visualization |

### 10.3 Session Fingerprint

Each session generates a fingerprint saved with outputs for reproducibility:

```python
import hashlib, json, platform
from datetime import datetime

def generate_session_fingerprint(assumptions: dict) -> dict:
    return {
        "session_id": hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:12],
        "timestamp": datetime.now().isoformat(),
        "python_version": platform.python_version(),
        "assumptions_hash": hashlib.sha256(
            json.dumps(assumptions, sort_keys=True).encode()
        ).hexdigest()[:12],
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
    }
```

---

## 11. Lightweight CI Process

Since there is no CI server (Colab is the runtime), CI is manual but gated:

### 11.1 Pre-commit Checklist

Before any commit to `dev` or `main`:

```
□ All tests pass: pytest tests/ --cov=. --cov-report=term-missing
□ Coverage ≥ 80% on computation modules
□ Type check passes: mypy . --ignore-missing-imports
□ No secrets in code: grep -r "sk-" . | grep -v .git
□ Notebooks stripped: nbstripout notebooks/*.ipynb
□ requirements.txt updated if new packages added
□ Docstrings present on all public functions
□ CHANGELOG.md updated
```

### 11.2 Test Execution in Colab

```python
# Run tests from within a notebook (for quick validation)
!cd /content/drive/MyDrive/valuation_agent && \
  pytest tests/ -v --cov=. --cov-report=term-missing --tb=short 2>&1 | tail -50
```

### 11.3 Pre-Release Checklist

Before declaring a phase complete:

```
□ All Phase Gate criteria satisfied (see Phase doc)
□ Financial Domain Expert sign-off on calculations
□ Demo notebook runs clean on fresh Colab runtime (restart → run all)
□ All outputs saved to Drive and verified
□ Session log shows no ERROR or CRITICAL entries
□ README updated with any changed instructions
```

---

## 12. Incident Response

### 12.1 Common Failure Modes

| Failure | Likely Cause | Resolution |
|---------|-------------|-----------|
| OOM (Out of Memory) | LLM too large for T4 | Switch to A100; or reduce max_seq_length |
| Colab session timeout | > 12 hours without interaction | Save state to Drive before long runs |
| yfinance `No data found` | Ticker delisted or API down | Use Drive cache; fallback to manual input |
| Drive mount failure | OAuth expired | Re-authorize Drive in Colab |
| Model download failure | HF network issue | Load from Drive cache |
| Balance sheet not balancing | Incorrect normalization | Check field mapping in normalizer.py |

### 12.2 Graceful Degradation Policy

The system must never crash on bad input data. Every module must:
1. Validate input before processing
2. Log a `WARNING` for soft errors
3. Raise a typed exception for hard errors
4. Provide a user-friendly error message in the notebook cell output

```python
class ValuationAgentError(Exception):
    """Base exception for all agent errors."""
    pass

class IngestionError(ValuationAgentError):
    pass

class BalanceSheetError(ValuationAgentError):
    pass

class DCFError(ValuationAgentError):
    pass

class NarrativeError(ValuationAgentError):
    pass
```

---

*Version: 1.0 | Status: Draft | Owner: Tech Lead*
