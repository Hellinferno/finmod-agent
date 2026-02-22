# 04 — System Architecture
## Financial Modeling & Valuation Agent (FMVA)
**Version:** 1.0  
**Date:** 2026-02-23  
**Owner:** Engineering Lead  
**Platform:** Google Colab + Unsloth + Google Drive

---

## 1. Architecture Overview

The FMVA is built as a **modular, single-environment pipeline** designed to run entirely within Google Colab. It follows a layered architecture that separates: data ingestion and normalization, computation engines, LLM inference, and output generation. Because Colab is session-based (not persistent), all state is checkpointed to Google Drive after each major computation stage.

### Architecture Style
- **Monolithic Notebook** (v1.0): Single Colab `.ipynb` orchestrates all modules via Python function calls
- **Modular Python Package**: Each major subsystem is a standalone Python module importable as `fmva.<module>`
- **LLM Layer**: Decoupled — the fine-tuned LLM (Unsloth) is loaded on-demand for narrative generation only; all numerical computations are performed by deterministic Python code
- **Storage Layer**: Google Drive acts as the persistence layer (inputs, outputs, model weights, checkpoints)

---

## 2. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GOOGLE COLAB RUNTIME                         │
│                         (T4 / A100 GPU)                             │
│                                                                     │
│  ┌─────────────┐   ┌──────────────┐   ┌───────────────────────┐   │
│  │  NOTEBOOK   │   │  FMVA PYTHON │   │    UNSLOTH LLM        │   │
│  │ ORCHESTRATOR│──▶│   PACKAGE    │   │   INFERENCE ENGINE    │   │
│  │(FMVA_Main   │   │              │   │                       │   │
│  │ .ipynb)     │   │ ┌──────────┐ │   │ ┌───────────────────┐ │   │
│  └─────────────┘   │ │Ingest &  │ │   │ │ Fine-tuned LoRA   │ │   │
│                    │ │Normalize │ │   │ │ (4-bit quant.)    │ │   │
│                    │ └──────────┘ │   │ └───────────────────┘ │   │
│                    │ ┌──────────┐ │   │           │           │   │
│                    │ │Assumption│ │   │    Narrative Output    │   │
│                    │ │Engine    │ │   └───────────────────────┘   │
│                    │ └──────────┘ │              ▲                 │
│                    │ ┌──────────┐ │              │                 │
│                    │ │Projection│ │    Valuation summary JSON      │
│                    │ │Engine    │─┼──────────────┘                 │
│                    │ └──────────┘ │                                │
│                    │ ┌──────────┐ │                                │
│                    │ │Valuation │ │                                │
│                    │ │Modules   │ │                                │
│                    │ └──────────┘ │                                │
│                    │ ┌──────────┐ │                                │
│                    │ │Audit &   │ │                                │
│                    │ │Integrity │ │                                │
│                    │ └──────────┘ │                                │
│                    │ ┌──────────┐ │                                │
│                    │ │Export    │ │                                │
│                    │ │Engine    │ │                                │
│                    │ └──────────┘ │                                │
│                    └──────────────┘                                │
│                           │                                        │
└───────────────────────────┼────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │     GOOGLE DRIVE        │
              │  (Persistence Layer)    │
              │                        │
              │  /FMVA/                 │
              │  ├── inputs/            │
              │  ├── outputs/           │
              │  ├── assumptions/       │
              │  ├── models/            │
              │  └── training_data/     │
              └─────────────────────────┘
```

---

## 3. Module Architecture

### 3.1 Module Dependency Map

```
fmva/
│
├── core/
│   ├── ingestion.py          ← Reads CSV/JSON/text input
│   ├── normalization.py      ← Maps raw → canonical schema
│   ├── schema.py             ← Pydantic models for all data types
│   └── validation.py         ← Input validation + error generation
│
├── engines/
│   ├── assumptions.py        ← Driver configuration & management
│   ├── projection.py         ← 3-statement projection (5-10 years)
│   ├── dcf.py                ← UFCF, Terminal Value, EV/Equity bridge
│   ├── comps.py              ← Trading comps analysis
│   ├── transactions.py       ← Precedent transaction analysis
│   └── sensitivity.py        ← Sensitivity matrices + Football Field
│
├── integrity/
│   ├── checker.py            ← BS/CFS/IS integrity checks
│   ├── audit_trail.py        ← Audit trace generation
│   └── error_codes.py        ← All error codes and messages
│
├── export/
│   ├── excel_exporter.py     ← openpyxl-based Excel generation
│   └── json_exporter.py      ← JSON schema export
│
├── llm/
│   ├── loader.py             ← Unsloth model loading
│   ├── inference.py          ← LLM inference wrapper
│   ├── prompts.py            ← Prompt templates for narrative gen
│   └── finetune.py           ← Fine-tuning pipeline (training only)
│
├── utils/
│   ├── drive.py              ← Google Drive I/O utilities
│   ├── math_utils.py         ← Financial math helpers
│   └── formatting.py         ← Number formatting utilities
│
└── config/
    ├── defaults.json         ← Default assumption values
    └── field_map.json        ← Label mapping registry
```

### 3.2 Module Dependency Rules

```
core/        → No upstream dependencies within fmva
engines/     → Depends on: core/, config/
integrity/   → Depends on: core/, engines/
export/      → Depends on: core/, engines/, integrity/
llm/         → Depends on: engines/ (for input values), config/
utils/       → No dependencies within fmva
```

**Critical constraint:** The `llm/` module has NO dependency on the numerical computation path. Numbers flow IN to the LLM as context; the LLM never computes financial values.

---

## 4. Computation Architecture

### 4.1 Data Flow Through Computation Pipeline

```
Raw Input (CSV/JSON)
        │
        ▼
[ingestion.py]
  - read_csv() / read_json()
  - detect_encoding()
  - standardize_null_values()
        │
        ▼
[normalization.py]
  - map_field_labels()          ← uses field_map.json
  - detect_statement_type()
  - validate_required_fields()
  - normalize_currency()
        │
        ▼
[schema.py — Canonical 3-Statement Object]
  FinancialStatements {
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    cash_flow_statement: CashFlowStatement
    metadata: CompanyMetadata
  }
        │
        ▼
[validation.py]
  - check_required_fields()
  - check_value_types()
  - check_date_consistency()
        │
        ▼
[assumptions.py — AssumptionSet Object]
  - load_defaults() or load_saved()
  - apply_user_overrides()
  - validate_bounds()
        │
        ▼
[projection.py — ProjectedStatements Object]
  - project_income_statement(base, assumptions, n_years)
  - project_balance_sheet(base, assumptions, projected_IS)
  - project_cash_flow_statement(projected_IS, projected_BS)
        │
        ▼
[checker.py — IntegrityReport Object]
  - check_balance_sheet(projected_BS)    → PASS/FAIL per year
  - check_cfs_balance(projected_CFS, projected_BS)
  - cross_check_net_income(projected_IS, projected_BS)
  [BLOCK if any FAIL]
        │
        ▼
[dcf.py — DCFResult Object]
  - calculate_ufcf(projected_IS, projected_CFS, assumptions)
  - discount_cash_flows(ufcfs, wacc)
  - calculate_tv_gordon_growth(ufcf_final, wacc, tgr)
  - calculate_tv_exit_multiple(ebitda_final, exit_multiple)
  - calculate_enterprise_value()
  - calculate_equity_value(ev, net_debt, cash)
  - calculate_implied_price(equity_value, shares_outstanding)
        │
        ▼
[sensitivity.py — SensitivityOutput Object]
  - generate_wacc_tgr_matrix(dcf_fn, wacc_range, tgr_range)
  - generate_wacc_em_matrix(dcf_fn, wacc_range, em_range)
  - generate_football_field(dcf_result, comps_result, tx_result)
        │
        ▼
[audit_trail.py — AuditTrail Object]
  - record_calculation(field, formula, inputs, result)
  - generate_report()
        │
        ▼
[export/ + llm/]
  - export_excel(all_results, audit_trail)
  - export_json(all_results, audit_trail)
  - generate_narrative(llm_model, valuation_summary)
```

---

## 5. LLM Architecture (Unsloth + Colab)

### 5.1 Model Selection

| Component | Selection | Rationale |
|---|---|---|
| Base Model | Mistral-7B-Instruct-v0.3 or LLaMA-3-8B-Instruct | Strong instruction following; fits in 4-bit on T4 |
| Fine-tuning Method | LoRA (Low-Rank Adaptation) via Unsloth | Memory efficient; fast convergence; preserves base reasoning |
| Quantization | 4-bit (NF4) | Required for T4 (16GB VRAM); Unsloth 2x speedup |
| Training Data | Custom JSONL: financial narrative instruction pairs | Domain-specific financial language |
| Adapter Storage | HuggingFace Hub + Google Drive backup | Portable; reloadable across sessions |

### 5.2 Fine-tuning Architecture

```
Training Data (JSONL)
    │
    ▼
[Dataset Loader]
  - Load from Google Drive /training_data/
  - Format: {"instruction": "...", "input": "...", "output": "..."}
  - Split: 90% train / 10% eval
    │
    ▼
[Unsloth FastLanguageModel]
  - load_model(model_name, max_seq_length=2048, dtype=None, load_in_4bit=True)
  - get_peft_model(model, lora params)
    │
    ▼
[LoRA Configuration]
  - r = 16                    ← rank
  - lora_alpha = 32
  - target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"]
  - lora_dropout = 0.05
    │
    ▼
[SFTTrainer (TRL)]
  - per_device_train_batch_size = 2
  - gradient_accumulation_steps = 4
  - max_steps = 1000
  - learning_rate = 2e-4
  - fp16 = True (T4) / bf16 = True (A100)
  - logging_steps = 10
  - save_steps = 100           ← Checkpoint to Drive every 100 steps
  - eval_steps = 100
    │
    ▼
[Checkpoint Saver]
  - Save to: /FMVA/models/checkpoints/checkpoint_{step}/
  - Save final: /FMVA/models/fmva_lora_adapter/
```

### 5.3 Inference Architecture

```
[Unsloth Model Loader]
  - Load base model (4-bit)
  - Load LoRA adapter from /FMVA/models/fmva_lora_adapter/
  - Enable inference mode (no gradient computation)
    │
    ▼
[Prompt Constructor — prompts.py]
  - Template: Alpaca format
  - Input: Valuation summary JSON → formatted as plain text context
  - Instruction: "Generate an institutional-grade investment banking 
                 executive summary based on the following valuation data:"
    │
    ▼
[Generation Config]
  - max_new_tokens = 1024
  - temperature = 0.3          ← Low temperature for factual output
  - top_p = 0.9
  - repetition_penalty = 1.1
    │
    ▼
[Post-processor]
  - Extract narrative text from model output
  - Validate that all numeric references match source data
  - If hallucinated number detected → retry with stricter prompt
```

---

## 6. Data Persistence Architecture (Google Drive)

Since Colab sessions are ephemeral, all data must be persisted to Google Drive at key checkpoints.

### 6.1 Checkpoint Strategy

| Checkpoint | Trigger | Saved To |
|---|---|---|
| Raw input saved | User uploads file | `/FMVA/inputs/` |
| Normalized data saved | After normalization completes | `/FMVA/inputs/normalized_` prefix |
| Assumption set saved | User calls save_assumptions() | `/FMVA/assumptions/` |
| Projection checkpoint | After 3-statement projection | `/FMVA/outputs/projections_checkpoint.json` |
| DCF checkpoint | After DCF computation | `/FMVA/outputs/dcf_checkpoint.json` |
| Training checkpoint | Every 100 fine-tuning steps | `/FMVA/models/checkpoints/` |
| Final Excel output | End of pipeline | `/FMVA/outputs/{company}_{date}.xlsx` |
| Final JSON output | End of pipeline | `/FMVA/outputs/{company}_{date}.json` |
| Audit trail | End of pipeline | `/FMVA/outputs/{company}_{date}_audit.json` |

### 6.2 Session Recovery

```python
def resume_session():
    """
    Called at notebook startup to check for existing checkpoints
    and offer to resume from last saved state.
    """
    checkpoints = drive.list_checkpoints()
    if checkpoints:
        print(f"Found checkpoint from {checkpoints[-1]['timestamp']}")
        print(f"Completed stages: {checkpoints[-1]['completed_stages']}")
        resume = input("Resume from checkpoint? [y/n]: ")
        if resume == 'y':
            return drive.load_checkpoint(checkpoints[-1])
    return None
```

---

## 7. Error Handling Architecture

### 7.1 Error Hierarchy

```python
class FMVAError(Exception):
    """Base exception for all FMVA errors"""
    
class DataIngestionError(FMVAError):
    """Raised when raw data cannot be parsed"""

class NormalizationError(FMVAError):
    """Raised when field mapping fails critically"""

class IntegrityError(FMVAError):
    """Raised when financial statements fail integrity checks"""
    class BalanceSheetError(IntegrityError): pass
    class CashFlowError(IntegrityError): pass

class ValuationError(FMVAError):
    """Raised when valuation computation fails"""
    class GordonGrowthError(ValuationError): pass
    class WACCError(ValuationError): pass

class LLMError(FMVAError):
    """Raised when LLM inference fails or hallucinates"""
    class HallucinationError(LLMError): pass
    class OOMError(LLMError): pass

class ExportError(FMVAError):
    """Raised when export generation fails"""
```

### 7.2 Error Handling Strategy

```
CRITICAL ERRORS (block all downstream processing):
  - BalanceSheetError → User must fix input or accept plug
  - GordonGrowthError → Remove GG TV; proceed with Exit Multiple only
  - DataIngestionError → Cannot proceed; user must fix input

WARNING ERRORS (flag but continue processing):
  - NormalizationError (partial) → Flag unrecognized fields
  - LLM HallucinationError → Retry with stricter prompt; 3 attempts
  - ASSUMPTION_WARNING → Confirm prompt; do not block

RECOVERY STRATEGY:
  - All computations wrapped in try/except blocks
  - On error: save current state to Drive checkpoint
  - Generate detailed error report with fix suggestions
  - Never silently ignore errors
```

---

## 8. Performance Architecture

### 8.1 Computational Performance Targets

| Operation | Target Time | Notes |
|---|---|---|
| CSV/JSON ingestion | < 2 seconds | Pure Python/pandas |
| Normalization | < 5 seconds | Field mapping + validation |
| 3-Statement projection (10 yr) | < 1 second | Vectorized numpy |
| DCF computation (incl. both TV) | < 1 second | Vectorized |
| Sensitivity matrix (7×7 = 49 scenarios) | < 10 seconds | Vectorized |
| Audit trail generation | < 3 seconds | Dict operations |
| Excel export | < 15 seconds | openpyxl write |
| LLM narrative generation | < 60 seconds | T4 GPU inference |
| Total pipeline (excluding LLM training) | < 2 minutes | |
| Unsloth fine-tuning (1000 steps) | 1-3 hours | A100 recommended |

### 8.2 Memory Management

```
Colab T4 VRAM: 16GB
├── Base LLM (4-bit quantized): ~4-5GB
├── LoRA Adapter: ~200MB
├── Activations + KV Cache: ~2GB
└── Available headroom: ~8GB (sufficient)

Colab RAM: 12.7GB (free) / 25.5GB (Pro)
├── pandas DataFrames: ~100MB (for typical 5-year dataset)
├── numpy arrays (projections): ~50MB
└── openpyxl workbook: ~200MB
└── Available headroom: Very comfortable
```

---

## 9. Security Architecture

Since FMVA v1.0 runs in Colab (single-user environment):

- **No network API calls** to external financial data services (all data is user-supplied)
- **No authentication layer** needed (Colab handles Google account auth)
- **Sensitive data** (financial statements) stored only in user's own Google Drive
- **Model weights** stored on HuggingFace Hub under user's own account
- **No data leaves the user's environment** — no telemetry, no server calls in v1.0
- **HuggingFace token** stored as Colab secret (not hardcoded)

---

## 10. Scalability Notes (v2.0 Considerations)

v1.0 is intentionally single-user, session-based. For v2.0 SaaS deployment, the architecture would evolve:

- Colab → FastAPI backend on Cloud Run / GKE
- Google Drive → PostgreSQL + S3/GCS for file storage
- Synchronous Colab notebook → Async task queue (Celery + Redis)
- Single-user → Multi-tenant with row-level security
- Unsloth on Colab → vLLM inference server on GPU instances
- Notebook UI → React/Next.js frontend + REST API

These are not requirements for v1.0 but should be considered in module design (avoid tight Colab coupling in core computation logic).

---

*Document Owner: Engineering Lead | Last Updated: 2026-02-23*
