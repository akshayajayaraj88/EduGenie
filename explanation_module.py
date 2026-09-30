"""Concept explanations.

Uses the local LaMini-Flan-T5-783M model when USE_LOCAL_MODEL=true and the
optional packages in requirements-local.txt are installed. Otherwise, or if the
local model fails, it falls back to Gemini so the feature always works.
"""

import logging
import os
import threading

import prompts
from gemini_client import generate

log = logging.getLogger("edugenie.explain")

LOCAL_MODEL_ID = os.getenv("LOCAL_MODEL_ID", "MBZUAI/LaMini-Flan-T5-783M")

_pipeline = None
_status = "disabled"  # disabled | loading | ready | failed
_lock = threading.Lock()


def local_enabled() -> bool:
    return os.getenv("USE_LOCAL_MODEL", "false").lower() in {"1", "true", "yes"}


def local_status() -> str:
    return _status


def _load():
    global _pipeline, _status
    try:
        import torch
        from transformers import pipeline

        if torch.backends.mps.is_available():
            device = "mps"  # Apple Silicon (M1/M2/M3) GPU
        elif torch.cuda.is_available():
            device = 0
        else:
            device = -1  # CPU
        log.info("Loading %s on %s ...", LOCAL_MODEL_ID, device)
        _pipeline = pipeline("text2text-generation", model=LOCAL_MODEL_ID, device=device)
        _status = "ready"
        log.info("Local explanation model ready.")
    except Exception as exc:
        _status = "failed"
        log.warning("Local model unavailable, using Gemini for explanations: %s", exc)


def load_local_model_in_background():
    """Start loading the local model without blocking server start-up."""
    global _status
    if not local_enabled():
        return
    with _lock:
        if _status in {"loading", "ready"}:
            return
        _status = "loading"
    threading.Thread(target=_load, daemon=True).start()


def explain_concept(concept: str, level: str = "beginner") -> tuple[str, str]:
    """Return (explanation, source) where source names the model used."""
    if _status == "ready" and _pipeline is not None:
        try:
            out = _pipeline(
                prompts.EXPLAIN_LOCAL.format(concept=concept, level=level),
                max_new_tokens=256,
                do_sample=False,
            )
            text = out[0]["generated_text"].strip()
            if text:
                return text, "LaMini-Flan-T5 (local)"
        except Exception as exc:
            log.warning("Local generation failed, falling back to Gemini: %s", exc)
    text = generate(prompts.EXPLAIN.format(concept=concept, level=level), system=prompts.SYSTEM)
    return text, "Gemini"
