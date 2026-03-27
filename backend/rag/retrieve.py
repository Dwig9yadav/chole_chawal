import json
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np

from backend.rag.ingest import INDEX_PATH, META_PATH, get_embedder

_loaded_index = None
_loaded_meta: List[Dict] = []


def _load_if_needed() -> bool:
    global _loaded_index, _loaded_meta

    if _loaded_index is not None and _loaded_meta:
        return True

    if not INDEX_PATH.exists() or not META_PATH.exists():
        return False

    _loaded_index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, "r", encoding="utf-8") as f:
        _loaded_meta = json.load(f)
    return True


def retrieve_docs(query: str, k: int = 4) -> List[Dict]:
    if not query.strip():
        return []

    if not _load_if_needed():
        return []

    embedder = get_embedder()
    q_vec = embedder.encode([query], normalize_embeddings=True)
    q_vec = np.array(q_vec, dtype="float32")

    top_k = min(max(1, k), len(_loaded_meta))
    scores, idxs = _loaded_index.search(q_vec, top_k)

    results: List[Dict] = []
    for score, idx in zip(scores[0], idxs[0]):
        if idx < 0 or idx >= len(_loaded_meta):
            continue
        row = dict(_loaded_meta[idx])
        row["score"] = float(score)
        results.append(row)
    return results
