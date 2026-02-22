"""
Financial Modeling & Valuation Agent (FMVA)
==========================================
AI-augmented institutional-grade company valuations.

Produces DCF, Comparable Company, and Precedent Transaction analyses
with full audit trail and LLM-generated narratives.

Version: 1.0.0
Stack: Google Colab + Unsloth + Python 3.10
"""

__version__ = "1.0.0"
__author__ = "FMVA Team"

from fmva.config import DEFAULT_CONFIG
from fmva.exceptions import FMVAError
