"""
LLM narrative generator - produces per-section narratives with hallucination guard.
"""

from __future__ import annotations
import re
from typing import Any, Optional
from loguru import logger
from fmva.config import LLM_TEMPERATURES, DEFAULT_MAX_NEW_TOKENS, HALLUCINATION_TOLERANCE
from fmva.exceptions import HallucinationError, LLMError


def generate_narrative(
    model, tokenizer, prompt: str,
    temperature: float = 0.3, max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
) -> str:
    """Generate a single narrative section from a prompt."""
    try:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            top_p=0.9,
            repetition_penalty=1.15,
            pad_token_id=tokenizer.eos_token_id,
        )
        text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return text.strip()
    except Exception as e:
        raise LLMError(f"Narrative generation failed: {e}")


def check_factual_grounding(
    narrative: str, ground_truth: dict[str, float],
    tolerance: float = HALLUCINATION_TOLERANCE,
) -> list[str]:
    """
    Check if numbers in the narrative match ground truth within tolerance.
    Returns list of flagged issues (empty = all OK).
    """
    flagged = []
    numbers_in_text = re.findall(r"\$?([\d,]+\.?\d*)\s*[MB]?", narrative)

    parsed = []
    for n in numbers_in_text:
        try:
            val = float(n.replace(",", ""))
            if val > 0.01:  # Skip trivially small numbers
                parsed.append(val)
        except ValueError:
            continue

    truth_vals = list(ground_truth.values())
    for val in parsed:
        matched = False
        for tv in truth_vals:
            if tv == 0:
                continue
            if abs(val - tv) / abs(tv) <= tolerance:
                matched = True
                break
            # Also check if the value matches after scaling (M vs raw)
            if abs(val - tv * 1e6) / abs(tv * 1e6) <= tolerance:
                matched = True
                break
        if not matched and val > 1.0:  # Only flag significant numbers
            flagged.append(f"${val:,.0f} not found in ground truth (tolerance ±{tolerance:.0%})")

    return flagged


def generate_full_report(
    model, tokenizer, prompts: dict[str, str],
    ground_truth: dict[str, float] = None,
) -> dict[str, str]:
    """Generate all narrative sections and optionally check for hallucinations."""
    narratives = {}
    for section, prompt in prompts.items():
        temp = LLM_TEMPERATURES.get(section, 0.3)
        logger.info(f"Generating narrative: {section} (temp={temp})")
        text = generate_narrative(model, tokenizer, prompt, temperature=temp)
        narratives[section] = text

    if ground_truth:
        for section, text in narratives.items():
            issues = check_factual_grounding(text, ground_truth)
            if issues:
                logger.warning(f"Hallucination flags in '{section}': {issues}")

    return narratives
