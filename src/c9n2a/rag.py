"""Scientific RAG over the paper corpus.

Chunks the Nature full text (JATS sections) and the Supplementary Information text
into passages and indexes them for retrieval. Uses semantic embeddings
(fastembed, ONNX, no torch) when the model is available, and always builds a
lexical BM25 index as an offline-safe fallback / hybrid component. The Literature
Agent and the report use this to ground statements in the paper's own text.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from . import paths

JATS = paths.DATA_RAW / "pmc" / "PMC12657233.jats.xml"
SI = paths.LITERATURE / "paper" / "SI_MOESM1.txt"
INDEX_DIR = paths.LITERATURE / "index"


@dataclass
class Passage:
    id: str
    section: str
    text: str


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 40]


def build_corpus() -> list[Passage]:
    passages: list[Passage] = []
    if JATS.exists():
        root = ET.fromstring(JATS.read_bytes())
        for sec in root.iter("sec"):
            title_el = sec.find("title")
            title = "".join(title_el.itertext()).strip() if title_el is not None else "section"
            text = " ".join("".join(sec.itertext()).split())
            # chunk ~3 sentences
            sents = _sentences(text)
            for i in range(0, len(sents), 3):
                chunk = " ".join(sents[i:i + 3])
                if chunk:
                    passages.append(Passage(f"jats:{title[:20]}:{i}", title, chunk))
    if SI.exists():
        for i, chunk in enumerate(_sentences(SI.read_text())):
            passages.append(Passage(f"si:{i}", "Supplementary Information", chunk))
    return passages


class RagIndex:
    def __init__(self, passages: list[Passage]):
        self.passages = passages
        self._bm25 = None
        self._embed = None
        self._emb_matrix = None

    def _ensure_bm25(self):
        if self._bm25 is None:
            from rank_bm25 import BM25Okapi
            self._tokens = [re.findall(r"\w+", p.text.lower()) for p in self.passages]
            self._bm25 = BM25Okapi(self._tokens)

    def _ensure_embed(self):
        if self._embed is False:
            return
        if self._embed is None:
            try:
                import numpy as np
                from fastembed import TextEmbedding
                self._embed = TextEmbedding("BAAI/bge-small-en-v1.5")
                vecs = list(self._embed.embed([p.text for p in self.passages]))
                self._emb_matrix = np.array(vecs)
            except Exception:
                self._embed = False  # offline / unavailable -> BM25 only

    def query(self, q: str, k: int = 5, method: str = "auto") -> list[dict]:
        self._ensure_bm25()
        import numpy as np
        bm = np.array(self._bm25.get_scores(re.findall(r"\w+", q.lower())))
        scores = bm / (bm.max() + 1e-9)
        if method in ("auto", "hybrid"):
            self._ensure_embed()
            if self._embed:
                qv = np.array(list(self._embed.embed([q]))[0])
                sims = self._emb_matrix @ qv / (
                    np.linalg.norm(self._emb_matrix, axis=1) * np.linalg.norm(qv) + 1e-9)
                scores = 0.5 * scores + 0.5 * (sims - sims.min()) / (np.ptp(sims) + 1e-9)
        top = np.argsort(scores)[::-1][:k]
        return [{"id": self.passages[i].id, "section": self.passages[i].section,
                 "score": float(scores[i]), "text": self.passages[i].text} for i in top]


_INDEX: RagIndex | None = None


def get_index() -> RagIndex:
    global _INDEX
    if _INDEX is None:
        _INDEX = RagIndex(build_corpus())
    return _INDEX


def build_and_save(out_dir: Path | None = None) -> int:
    out_dir = Path(out_dir or INDEX_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    passages = build_corpus()
    (out_dir / "corpus.jsonl").write_text(
        "\n".join(json.dumps({"id": p.id, "section": p.section, "text": p.text})
                  for p in passages))
    return len(passages)
