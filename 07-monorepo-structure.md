# 07 — Monorepo Structure
## Financial Modeling & Valuation Agent (FMVA)
**Version:** 1.0  
**Date:** 2026-02-23  
**Owner:** Engineering  

---

## 1. Repository Overview

The FMVA project lives in a single monorepo hosted on GitHub. It is designed to be cloned and run directly in Google Colab via `!git clone` or mounted via Google Drive. The structure separates the Python package (`fmva/`), notebooks (`notebooks/`), training data (`data/`), tests (`tests/`), and documentation (`docs/`).

---

## 2. Full Repository Tree

```
fmva/                                          ← Root of monorepo
│
├── README.md                                  ← Quick start guide
├── LICENSE                                    ← MIT License
├── CHANGELOG.md                               ← Version history
├── .gitignore                                 ← Excludes: .env, *.csv inputs, model weights
├── pyproject.toml                             ← Project metadata + dependencies (PEP 517)
├── requirements.txt                           ← Pinned dependency versions for Colab
├── requirements-dev.txt                       ← Dev-only deps (pytest, black, mypy)
├── setup.py                                   ← For pip install -e . in Colab
│
├── notebooks/                                 ← Colab notebooks (primary user interface)
│   ├── FMVA_Main.ipynb                        ← End-to-end pipeline notebook (for analysts)
│   ├── FMVA_Finetune.ipynb                    ← Unsloth fine-tuning notebook (for ML engineers)
│   ├── FMVA_Dev_Playground.ipynb              ← Module testing / exploration
│   └── FMVA_Quickstart.ipynb                  ← 10-minute demo with sample data
│
├── fmva/                                      ← Main Python package
│   ├── __init__.py                            ← Package exports + version
│   │
│   ├── core/                                  ← Data ingestion & normalization
│   │   ├── __init__.py
│   │   ├── ingestion.py                       ← read_financial_data(), read_financial_data_from_dict()
│   │   ├── normalization.py                   ← normalize_financial_data(), get_field_map()
│   │   ├── schema.py                          ← All Pydantic models
│   │   └── validation.py                      ← validate_statements()
│   │
│   ├── engines/                               ← Computation engines
│   │   ├── __init__.py
│   │   ├── assumptions.py                     ← AssumptionSet CRUD
│   │   ├── projection.py                      ← 3-statement projection
│   │   ├── dcf.py                             ← Full DCF engine
│   │   ├── comps.py                           ← Trading comps analysis
│   │   ├── transactions.py                    ← Precedent transactions analysis
│   │   └── sensitivity.py                     ← Sensitivity matrices + football field
│   │
│   ├── integrity/                             ← Audit & integrity checking
│   │   ├── __init__.py
│   │   ├── checker.py                         ← check_balance_sheet(), check_cfs_reconciliation()
│   │   ├── audit_trail.py                     ← AuditTrail management
│   │   └── error_codes.py                     ← All error code constants + messages
│   │
│   ├── export/                                ← Output generation
│   │   ├── __init__.py
│   │   ├── excel_exporter.py                  ← openpyxl-based Excel generation
│   │   └── json_exporter.py                   ← JSON schema export
│   │
│   ├── llm/                                   ← LLM integration (Unsloth)
│   │   ├── __init__.py
│   │   ├── loader.py                          ← load_model() via Unsloth
│   │   ├── inference.py                       ← generate_executive_summary()
│   │   ├── prompts.py                         ← Prompt templates
│   │   └── finetune.py                        ← Fine-tuning pipeline (training mode only)
│   │
│   ├── utils/                                 ← Shared utilities
│   │   ├── __init__.py
│   │   ├── drive.py                           ← Google Drive mount, read, write, checkpoint
│   │   ├── math_utils.py                      ← discount_value(), cagr(), safe_divide()
│   │   └── formatting.py                      ← format_currency(), format_pct(), format_multiple()
│   │
│   ├── config/                                ← Static configuration
│   │   ├── defaults.json                      ← Default assumption values
│   │   └── field_map.json                     ← Label mapping registry (500+ aliases)
│   │
│   └── pipeline.py                            ← run_full_pipeline() orchestrator
│
├── data/                                      ← Training and sample data
│   ├── sample_inputs/                         ← Sample financial data for demos
│   │   ├── acme_corp_sample.csv               ← Sample IS + BS + CFS (tech company)
│   │   ├── acme_corp_comps.json               ← Sample comps data
│   │   └── acme_corp_expected_output.json     ← Expected output for testing
│   │
│   ├── training/                              ← LLM fine-tuning data
│   │   ├── financial_narratives_train.jsonl   ← Training examples (Alpaca format)
│   │   ├── financial_narratives_eval.jsonl    ← Evaluation examples
│   │   └── data_curation_guide.md             ← How to add new training examples
│   │
│   └── field_map_extensions/                  ← Community-contributed label mappings
│       └── uk_gaap_extensions.json
│
├── tests/                                     ← Test suite
│   ├── __init__.py
│   ├── conftest.py                            ← pytest fixtures (sample data, mock objects)
│   │
│   ├── unit/                                  ← Unit tests (per module)
│   │   ├── test_ingestion.py
│   │   ├── test_normalization.py
│   │   ├── test_projection.py
│   │   ├── test_dcf.py
│   │   ├── test_comps.py
│   │   ├── test_sensitivity.py
│   │   ├── test_integrity_checker.py
│   │   ├── test_audit_trail.py
│   │   ├── test_excel_exporter.py
│   │   └── test_math_utils.py
│   │
│   ├── integration/                           ← End-to-end pipeline tests
│   │   ├── test_full_pipeline.py              ← Runs complete pipeline with sample data
│   │   ├── test_pipeline_error_cases.py       ← Tests all error scenarios
│   │   └── test_excel_output_validation.py    ← Validates generated Excel files
│   │
│   ├── numerical/                             ← Numerical accuracy tests
│   │   ├── test_dcf_accuracy.py               ← Compares vs. known-good Excel model
│   │   ├── test_sensitivity_accuracy.py
│   │   └── reference_model/
│   │       └── acme_corp_reference.xlsx       ← Hand-built reference model for comparison
│   │
│   └── llm/                                   ← LLM output tests (lightweight, no GPU needed)
│       ├── test_prompt_construction.py
│       └── test_narrative_number_validation.py
│
├── docs/                                      ← Pre-engineering documentation
│   ├── 01-product-requirements.md
│   ├── 02-user-stories-and-acceptance-criteria.md
│   ├── 03-information-architecture.md
│   ├── 04-system-architecture.md
│   ├── 05-database-schema.md
│   ├── 06-api-contracts.md
│   ├── 07-monorepo-structure.md
│   ├── 08-computation-engine-spec.md
│   ├── 09-engineering-scope-definition.md
│   ├── 10-development-phases.md
│   ├── 11-environment-and-devops.md
│   └── 12-testing-strategy.md
│
├── scripts/                                   ← Utility scripts
│   ├── install_colab.sh                       ← One-shot Colab environment setup
│   ├── validate_training_data.py              ← Validates JSONL training data quality
│   ├── generate_field_map.py                  ← Regenerates field_map.json from sources
│   └── benchmark_dcf_accuracy.py             ← Numerical accuracy benchmarking vs. Excel
│
└── .github/                                   ← GitHub configuration
    ├── workflows/
    │   ├── tests.yml                           ← Run pytest on push/PR
    │   ├── lint.yml                            ← Run black + mypy on push/PR
    │   └── release.yml                         ← Tag-based release workflow
    └── PULL_REQUEST_TEMPLATE.md
```

---

## 3. Key File Details

### 3.1 `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "fmva"
version = "1.0.0"
description = "Financial Modeling & Valuation Agent — Institutional-grade autonomous valuation"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"

dependencies = [
    "pydantic>=2.5.0",
    "pandas>=2.1.0",
    "numpy>=1.26.0",
    "openpyxl>=3.1.0",
    "python-dateutil>=2.8.0",
    "tqdm>=4.66.0",
    "colorama>=0.4.6",       # Colored console output
]

[project.optional-dependencies]
llm = [
    "unsloth>=2024.1",
    "torch>=2.1.0",
    "transformers>=4.36.0",
    "trl>=0.7.4",
    "peft>=0.7.0",
    "accelerate>=0.25.0",
    "bitsandbytes>=0.41.0",
]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.11.0",
    "mypy>=1.7.0",
    "isort>=5.12.0",
    "openpyxl-stubs>=0.1.25",
]

[tool.black]
line-length = 100
target-version = ["py310", "py311"]

[tool.mypy]
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=fmva --cov-report=term-missing --cov-fail-under=80"
```

### 3.2 `requirements.txt` (Colab-compatible, pinned)

```
# Core computation
pydantic==2.5.3
pandas==2.1.4
numpy==1.26.3
openpyxl==3.1.2
python-dateutil==2.8.2
tqdm==4.66.1
colorama==0.4.6

# LLM stack (Colab install via install_colab.sh)
# unsloth — installed separately due to CUDA build requirements
# torch, transformers, trl, peft, accelerate, bitsandbytes
```

### 3.3 `scripts/install_colab.sh`

```bash
#!/bin/bash
# One-shot environment setup for Google Colab
# Run: !bash scripts/install_colab.sh

echo "=== FMVA Colab Setup ==="

# 1. Install base package
pip install -e . --quiet

# 2. Install Unsloth (GPU-optimized install)
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" --quiet

# 3. Install xformers (memory-efficient attention)
pip install xformers --quiet

# 4. Verify GPU
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')"

echo "=== Setup Complete ==="
```

---

## 4. Module Import Structure

```python
# Public API (importable from top-level fmva package)

from fmva import (
    # Pipeline orchestrator
    run_full_pipeline,
    
    # Core
    read_financial_data,
    normalize_financial_data,
    
    # Assumptions
    create_assumption_set,
    save_assumption_set,
    load_assumption_set,
    
    # Engines
    build_projected_statements,
    run_dcf,
    analyze_comps,
    generate_wacc_tgr_matrix,
    generate_football_field,
    
    # Integrity
    run_all_integrity_checks,
    create_audit_trail,
    
    # Export
    export_to_excel,
    
    # LLM
    load_model,
    generate_executive_summary,
    
    # Schema (for type hints)
    CompanyMetadata,
    AssumptionSet,
    ValuationSummary,
)
```

---

## 5. Naming Conventions

| Convention | Applies To | Rule |
|---|---|---|
| `snake_case` | All Python files, functions, variables | Strict PEP 8 |
| `PascalCase` | All Pydantic model class names | `IncomeStatementPeriod`, `DCFResult` |
| `UPPER_SNAKE_CASE` | Constants and error codes | `BS_IMBALANCE_ERROR`, `TV_HIGH_WARNING` |
| `{company}_{date}_{type}.{ext}` | All output files | `acme_corp_20260223_valuation.xlsx` |
| `{scenario}_case.json` | Assumption set files | `base_case.json`, `bull_case.json` |
| `test_{module}.py` | All test files | Mirrors source module name |
| `FMVA_{Purpose}.ipynb` | All notebooks | `FMVA_Main.ipynb`, `FMVA_Finetune.ipynb` |

---

## 6. Git Branch Strategy

```
main            ← Production-ready; always passing tests
    │
    ├── develop ← Integration branch; PR target for features
    │       │
    │       ├── feature/US-007-ufcf-calculator
    │       ├── feature/US-013-balance-sheet-check
    │       ├── feature/US-015-excel-export
    │       └── feature/US-017-unsloth-finetune
    │
    ├── hotfix/ ← Emergency fixes directly from main
    └── release/v1.0 ← Release preparation branch
```

**PR Rules:**
- All PRs must target `develop` (not `main` directly)
- PRs require: 1 approval + all tests passing + > 80% coverage on changed files
- `main` is updated only from `develop` (via PR) or `hotfix/` branches
- Every merge to `main` triggers a GitHub Actions test run

---

## 7. .gitignore Key Entries

```gitignore
# Input financial data (potentially confidential)
data/inputs/**/*.csv
data/inputs/**/*.json
!data/sample_inputs/        # Sample data is committed

# Model weights (too large for Git)
models/
*.bin
*.safetensors
*.gguf

# Environment
.env
.env.local
secrets.json

# Colab artifacts
__pycache__/
*.pyc
.ipynb_checkpoints/
*.ipynb_checkpoint

# Output files
outputs/
*.xlsx
!tests/numerical/reference_model/*.xlsx    # Reference model committed for testing

# Coverage
.coverage
htmlcov/

# Type checking
.mypy_cache/
```

---

*Document Owner: Engineering | Last Updated: 2026-02-23*
