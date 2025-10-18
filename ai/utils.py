# ai/utils.py
from __future__ import annotations
import os
from pathlib import Path
from typing import Tuple, List, Dict, Any

import faiss                   # pip install faiss-cpu
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EMB  = DATA / "embeddings"

_MODEL_CACHE = None  # singleton cache so we don't reload the model repeatedly


def get_device() -> str:
    """Return 'cuda' if available, else 'cpu' (SentenceTransformers auto-handles)."""
    # We deliberately keep it simple; ST handles device under the hood.
    return "cpu"


def load_embedder(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
                  ) -> SentenceTransformer:
    """
    Lazy-load a SentenceTransformer encoder and cache it for reuse.
    """
    global _MODEL_CACHE
    key = model_name
    if _MODEL_CACHE is None or _MODEL_CACHE.get("name") != key:
        model = SentenceTransformer(model_name)
        _MODEL_CACHE = {"name": key, "model": model}
    return _MODEL_CACHE["model"]


def embed_texts(texts: List[str], batch_size: int = 64) -> np.ndarray:
    """
    Encode a list of strings -> (N, D) float32 numpy array.
    """
    model = load_embedder()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=True,  # cosine search = inner product on normalized vectors
    ).astype("float32")
    return embeddings


def _load_faiss_and_meta(prefix: str) -> Tuple[faiss.Index, pd.DataFrame]:
    """
    Load a FAISS index (IVF/Flat/whatever) and the associated metadata csv.
    `prefix` is the file stem: e.g. 'cases' or 'knowledge'
    Expects:
      data/embeddings/{prefix}.index
      data/embeddings/{prefix}.npy  (OPTIONAL if you want to inspect vectors)
      data/embeddings/{prefix}_meta.csv
    """
    index_path = EMB / f"{prefix}.index"
    meta_path  = EMB / f"{prefix}_meta.csv"

    if not index_path.exists():
        raise FileNotFoundError(f"Missing FAISS index: {index_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing meta csv: {meta_path}")

    index = faiss.read_index(str(index_path))
    meta = pd.read_csv(meta_path)
    return index, meta


def load_cases_index() -> Tuple[faiss.Index, pd.DataFrame]:
    return _load_faiss_and_meta("cases")


def load_kb_index() -> Tuple[faiss.Index, pd.DataFrame]:
    return _load_faiss_and_meta("knowledge")


def search_index(
    index: faiss.Index,
    query_vecs: np.ndarray,
    top_k: int = 5,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Given FAISS index and (B, D) query vectors, return (scores, idx).
    We use inner product (cosine if vectors normalized).
    """
    # FAISS returns distances; for IP higher is better. We call them scores.
    scores, idx = index.search(query_vecs, top_k)
    return scores, idx


def pack_hits(
    meta: pd.DataFrame,
    scores: np.ndarray,
    idx: np.ndarray,
) -> List[List[Dict[str, Any]]]:
    """
    Convert FAISS output into python dicts with fields from meta.
    Returns list per query: [[{...hit1...}, {...hit2...}], ...]
    """
    results: List[List[Dict[str, Any]]] = []
    for q in range(idx.shape[0]):
        row = []
        for rank, (i, s) in enumerate(zip(idx[q], scores[q])):
            if i < 0:
                continue
            rec = meta.iloc[int(i)].to_dict()
            rec.update({"_score": float(s), "_rank": rank})
            row.append(rec)
        results.append(row)
    return results
