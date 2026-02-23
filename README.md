# 🏦 FMVA — Financial Modeling & Valuation Agent

> **AI-augmented institutional-grade company valuations.**
> Automated DCF, Comparable Company Analysis, Sensitivity Matrices, and LLM-generated narratives — all in one Python package.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-40%2F40%20Passing-brightgreen?logo=pytest)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What It Does

FMVA takes raw financial data and produces a **complete institutional-grade valuation** — the same analysis that investment banks charge $50K–$500K to produce manually.

```
📊 Raw Financials (JSON) → 🔄 Normalize → ✅ Validate → 📈 DCF + Comps → 📑 Excel Report
```

### Core Capabilities

| Module | Description | Status |
|--------|-------------|--------|
| **Data Ingestion** | Load & normalize financial statements from JSON | ✅ Production |
| **Balance Sheet Checker** | Detects imbalances, suggests plugs | ✅ Production |
| **DCF Engine** | Full Discounted Cash Flow with Gordon Growth & Exit Multiple | ✅ Production |
| **WACC Calculator** | CAPM-based with live beta from yfinance | ✅ Production |
| **Comparable Companies** | Real-time peer multiples via yfinance | ✅ Production |
| **Sensitivity Analysis** | WACC vs TGR matrices with monotonicity checks | ✅ Production |
| **Scenario Engine** | Bear / Base / Bull presets + custom assumptions | ✅ Production |
| **Audit Trail** | Immutable step-by-step calculation log | ✅ Production |
| **Excel Export** | Multi-sheet workbook (financials, DCF, comps, audit) | ✅ Production |
| **JSON Export** | Structured valuation output for API consumption | ✅ Production |
| **LLM Narratives** | AI-generated investment memos & risk analysis | 🟡 Scaffolded |
| **PDF Reports** | Professional PDF generation | 🟡 Scaffolded |

---

## 🚀 Quickstart

### 1. Clone & Setup

```bash
git clone https://github.com/Hellinferno/finmod-agent.git
cd finmod-agent

# Create virtual environment (Python 3.10–3.12 recommended)
py -3.11 -m venv .venv
.venv\Scripts\Activate       # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -e ".[dev]"
```

### 2. Run a Full Valuation

```python
from fmva.pipeline import run_full_pipeline

result = run_full_pipeline("data/fixtures/techcorp.json", scenario="base")

print(f"Company:  {result.metadata.company_name}")
print(f"EV (Gordon Growth):  ${result.dcf.enterprise_value_gordon:,.0f}M")
print(f"EV (Exit Multiple):  ${result.dcf.enterprise_value_exit_multiple:,.0f}M")
```

### 3. Run Tests

```bash
pytest -v
# ========================= 40 passed in 9.22s =========================
```

---

## 🏗️ Architecture

```
fmva/
├── core/               ← Data ingestion, normalization, validation
│   ├── ingestion.py        Load raw JSON financial data
│   ├── normalization.py    Map to canonical schema (500+ field aliases)
│   ├── validation.py       Integrity checks & error reporting
│   ├── checker.py          Balance sheet checker with plug suggestions
│   └── schemas.py          Pydantic data models
│
├── engines/            ← Financial computation engines
│   ├── assumptions.py      Bear/Base/Bull scenario presets
│   ├── projection.py       Revenue & EBITDA projection
│   ├── dcf.py              Full DCF (UFCF → Terminal Value → EV)
│   ├── wacc.py             WACC via CAPM + live beta
│   ├── comps.py            Comparable company analysis (yfinance)
│   ├── sensitivity.py      2D sensitivity matrices
│   └── transactions.py     Precedent transaction analysis
│
├── audit/              ← Audit trail & compliance
│   └── trail.py            Immutable calculation log
│
├── export/             ← Output generation
│   ├── excel_exporter.py   Multi-sheet Excel workbook
│   ├── json_exporter.py    Structured JSON export
│   └── pdf_generator.py    PDF report (scaffolded)
│
├── llm/                ← LLM narrative generation
│   ├── prompts.py          Jinja2 prompt templates
│   ├── inference.py        Model inference engine
│   └── loader.py           Model loader (Unsloth-compatible)
│
├── pipeline.py         ← One-command full pipeline orchestrator
├── config.py           ← Global configuration & defaults
└── exceptions.py       ← Custom exception hierarchy
```

---

## 📊 Sample Data

Three fully modeled fixture companies are included:

| Company | Sector | Profile |
|---------|--------|---------|
| **TechCorp Inc** | SaaS / Technology | High growth, high margins |
| **ManufactureCo Ltd** | Industrial / Manufacturing | Stable, capital-intensive |
| **RetailChain Corp** | Retail / Consumer | Mature, lower margins |

---

## 🧪 Test Suite

**40 tests across 5 test modules** — all passing ✅

| Test Module | Tests | What It Validates |
|-------------|-------|-------------------|
| `test_audit.py` | 6 | Audit trail logging, immutability, export |
| `test_comps_sensitivity.py` | 9 | Comps stats, multiples, sensitivity matrices |
| `test_dcf.py` | 10 | Revenue projection, WACC, terminal value, full DCF |
| `test_ingestion.py` | 11 | JSON loading, normalization, validation, balance sheet check |
| `test_integration.py` | 4 | End-to-end pipeline for all fixture companies |

```bash
# Run all tests with coverage
pytest --cov=fmva --cov-report=term-missing

# Run specific module
pytest tests/test_dcf.py -v

# Skip integration tests (faster)
pytest -m "not integration"
```

---

## 📓 Interactive Notebooks

Six Colab-ready notebooks in `colab/` for step-by-step exploration:

| Notebook | Purpose |
|----------|---------|
| `00_setup` | Environment configuration |
| `01_data_ingestion` | Load, normalize & validate financial data |
| `02_dcf_model` | Build and run a DCF valuation |
| `03_comps_analysis` | Comparable company analysis |
| `04_sensitivity` | Sensitivity matrices |
| `05_full_pipeline` | End-to-end pipeline execution |

---

## 🗺️ Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Environment & Foundations | ✅ Complete |
| Phase 1 | Data Ingestion & Normalization | ✅ Complete |
| Phase 2 | Assumption Engine & DCF Core | ✅ Complete |
| Phase 3 | Comps, Transactions & Sensitivity | 🟡 90% (football field chart pending) |
| Phase 4 | LLM Narrative Engine | 🟡 Scaffolded |
| Phase 5 | Audit Trail & Output Engine | 🟡 90% (PDF pending) |
| Phase 6 | Integration & E2E Testing | ✅ Complete (40/40 tests) |
| Phase 7 | MVP Hardening & Documentation | 🔲 In Progress |

See [`10-development-phases.md`](10-development-phases.md) for detailed phase specifications.

---

## 📚 Documentation

This project includes **12 comprehensive specification documents**:

| Doc | Title |
|-----|-------|
| [01](01-product-requirements.md) | Product Requirements |
| [02](02-user-stories-and-acceptance-criteria.md) | User Stories & Acceptance Criteria |
| [03](03-information-architecture.md) | Information Architecture |
| [04](04-system-architecture.md) | System Architecture |
| [05](05-database-schema.md) | Database Schema |
| [06](06-api-contracts.md) | API Contracts |
| [07](07-monorepo-structure.md) | Monorepo Structure |
| [08](08-computation-engine-spec.md) | Computation Engine Spec |
| [09](09-engineering-scope-definition.md) | Engineering Scope Definition |
| [10](10-development-phases.md) | Development Phases & Roadmap |
| [11](11-environment-and-devops.md) | Environment & DevOps |
| [12](12-testing-strategy.md) | Testing Strategy |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Data Models | Pydantic v2 |
| Computation | NumPy, SciPy, Pandas |
| Market Data | yfinance |
| Export | openpyxl (Excel), ReportLab (PDF) |
| Visualization | Matplotlib, Seaborn, Plotly |
| LLM (optional) | Unsloth, Transformers, PEFT |
| Testing | pytest, pytest-cov |
| Logging | Loguru |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Built with ❤️ by the FMVA Team</b><br>
  <i>Democratizing institutional-grade financial analysis</i>
</p>
