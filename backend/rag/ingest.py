import json
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
EMBED_DIR = DATA_DIR / "embeddings"
INDEX_PATH = EMBED_DIR / "index.faiss"
META_PATH = EMBED_DIR / "metadata.json"

_model = None


def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    clean = " ".join(text.split())
    if not clean:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        chunks.append(clean[start:end])
        start += max(1, chunk_size - overlap)
    return chunks


def extract_pdf_chunks(pdf_path: Path) -> List[Dict]:
    reader = PdfReader(str(pdf_path))
    rows: List[Dict] = []
    for page_idx, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        for chunk in chunk_text(page_text):
            rows.append(
                {
                    "text": chunk,
                    "source": pdf_path.name,
                    "page": page_idx,
                }
            )
    return rows


def rebuild_index() -> Dict:
    EMBED_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    all_rows: List[Dict] = []
    for pdf_file in PDF_DIR.glob("*.pdf"):
        all_rows.extend(extract_pdf_chunks(pdf_file))

    if not all_rows:
        return {"chunks": 0, "pdfs": 0, "message": "No PDFs found in data/pdfs"}

    embedder = get_embedder()
    vectors = embedder.encode([r["text"] for r in all_rows], normalize_embeddings=True)
    vectors = np.array(vectors, dtype="float32")

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, ensure_ascii=True, indent=2)

    return {
        "chunks": len(all_rows),
        "pdfs": len(list(PDF_DIR.glob("*.pdf"))),
        "message": "RAG index rebuilt",
    }
