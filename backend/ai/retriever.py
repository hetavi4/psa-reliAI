# ai/retriever.py
from __future__ import annotations
from typing import List, Dict, Any, Literal
import numpy as np

from .utils import (
    embed_texts,
    load_cases_index,
    load_kb_index,
    search_index,
    pack_hits,
)

Source = Literal["cases", "knowledge"]


class Retriever:
    """
    Thin wrapper that:
      - embeds the query
      - searches selected sources
      - returns hits merged with metadata
    """

    def __init__(self):
        self.cases_index, self.cases_meta = load_cases_index()
        self.kb_index, self.kb_meta = load_kb_index()

    def search(
        self,
        query: str,
        top_k: int = 5,
        sources: List[Source] | None = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        if not sources:
            sources = ["cases", "knowledge"]

        qv = embed_texts([query])  # (1, D)

        out: Dict[str, List[Dict[str, Any]]] = {}
        if "cases" in sources:
            scores, idx = search_index(self.cases_index, qv, top_k)
            out["cases"] = pack_hits(self.cases_meta, scores, idx)[0]
        if "knowledge" in sources:
            scores, idx = search_index(self.kb_index, qv, top_k)
            out["knowledge"] = pack_hits(self.kb_meta, scores, idx)[0]
        return out
