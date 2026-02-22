"""
LLM model loader — Unsloth/HuggingFace model with 4-bit quantization.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Optional, Tuple
from loguru import logger
from fmva.config import DEFAULT_MODEL_NAME, DEFAULT_MAX_SEQ_LENGTH


def load_model(
    model_name: str = DEFAULT_MODEL_NAME,
    max_seq_length: int = DEFAULT_MAX_SEQ_LENGTH,
    cache_dir: Optional[str] = None,
) -> Tuple[Any, Any]:
    """
    Load an Unsloth (or HuggingFace) causal LM with 4-bit quantization.

    Args:
        model_name: HuggingFace model ID.
        max_seq_length: Max context length.
        cache_dir: Local/Drive cache directory for model weights.

    Returns:
        (model, tokenizer) tuple.
    """
    try:
        from unsloth import FastLanguageModel
        logger.info(f"Loading Unsloth model: {model_name} (seq_len={max_seq_length})")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_length,
            dtype=None,
            load_in_4bit=True,
            cache_dir=cache_dir,
        )
        FastLanguageModel.for_inference(model)
        logger.info("Unsloth model loaded successfully")
        return model, tokenizer
    except ImportError:
        logger.warning("Unsloth not available, falling back to transformers")
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        model = AutoModelForCausalLM.from_pretrained(
            model_name, cache_dir=cache_dir,
            device_map="auto", load_in_4bit=True,
        )
        logger.info("Transformers model loaded (fallback)")
        return model, tokenizer
