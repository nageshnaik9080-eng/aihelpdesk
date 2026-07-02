"""Embedding function for the Embedding Agent (design doc Section 8.2.1).

Backend selection (resolved ONCE, then fixed so all vectors share a dimension):
  1. Gemini `text-embedding-004` when a Gemini key is configured (FR-6/FR-7).
  2. `sentence-transformers` (all-MiniLM-L6-v2) if installed.
  3. A deterministic hashing bag-of-words vector so the RAG / duplicate pipeline
     still functions end-to-end with no external deps.

The active backend is reported via `embedding_backend()` for AI-governance logs.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import logging
import re

import numpy as np

from app.core.config import get_settings

logger = logging.getLogger("helpdesk.embeddings")
settings = get_settings()

_DIM = 384  # hashing-fallback dimensionality
_TOKEN_RE = re.compile(r"[a-z0-9]+")

_mode: str | None = None            # "gemini" | "st" | "hash"
_backend = "unresolved"
_st_model = None

# Hard wall-clock bound so a network/auth hang can never stall a request.
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="embed")
_EMBED_TIMEOUT_S = 20


def _resolve_backend() -> None:
    """Pick the embedding backend exactly once and cache it."""
    global _mode, _backend, _st_model
    if _mode is not None:
        return

    # 1) Gemini embeddings (probe once, hard-bounded so a hang can't stall startup)
    if settings.gemini_api_key:
        try:
            _EXECUTOR.submit(_probe_gemini).result(timeout=12)
            _mode = "gemini"
            _backend = f"gemini/{settings.gemini_embedding_model}"
            logger.info("Embedding backend: %s", _backend)
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gemini embeddings unavailable (%s); trying local backends.", exc)

    # 2) sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer

        _st_model = SentenceTransformer("all-MiniLM-L6-v2")
        _mode = "st"
        _backend = "sentence-transformers/all-MiniLM-L6-v2"
        logger.info("Embedding backend: %s", _backend)
        return
    except Exception as exc:  # noqa: BLE001
        logger.warning("sentence-transformers unavailable (%s); using hashing fallback.", exc)

    # 3) hashing fallback
    _mode = "hash"
    _backend = "hashing-fallback-384d"


def _probe_gemini() -> None:
    import google.generativeai as genai

    from app.core.tls import genai_transport

    configure_kwargs = {"api_key": settings.gemini_api_key}
    transport = genai_transport()
    if transport:
        configure_kwargs["transport"] = transport
    genai.configure(**configure_kwargs)
    genai.embed_content(
        model=settings.gemini_embedding_model,
        content="ping",
        task_type="retrieval_document",
        request_options={"timeout": 10},
    )


def _gemini_embed(text: str) -> list[float]:
    import google.generativeai as genai

    result = genai.embed_content(
        model=settings.gemini_embedding_model,
        content=text,
        task_type="retrieval_document",
        request_options={"timeout": _EMBED_TIMEOUT_S},
    )
    return list(result["embedding"])


def _hash_embed(text: str) -> list[float]:
    """Deterministic, dependency-free embedding: hashed token frequencies, L2-normalized."""
    vec = np.zeros(_DIM, dtype=np.float32)
    for tok in _TOKEN_RE.findall(text.lower()):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        vec[h % _DIM] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec.tolist()


def embed(text: str) -> list[float]:
    _resolve_backend()
    if _mode == "gemini":
        try:
            return _EXECUTOR.submit(_gemini_embed, text).result(timeout=_EMBED_TIMEOUT_S + 3)
        except Exception as exc:  # noqa: BLE001 — a single transient failure shouldn't crash
            logger.warning("Gemini embed failed for one item (%s); hashing this one.", exc)
            return _hash_embed(text)
    if _mode == "st" and _st_model is not None:
        emb = _st_model.encode(text, normalize_embeddings=True)
        return np.asarray(emb, dtype=np.float32).tolist()
    return _hash_embed(text)


def embed_many(texts: list[str]) -> list[list[float]]:
    return [embed(t) for t in texts]


def embedding_backend() -> str:
    _resolve_backend()
    return _backend
