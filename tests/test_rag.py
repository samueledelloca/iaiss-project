"""Scientific RAG tests (lexical path, offline-safe)."""
from __future__ import annotations
import pytest
from c9n2a import paths, rag

pytestmark = pytest.mark.skipif(
    not (paths.DATA_RAW / "pmc" / "PMC12657233.jats.xml").exists(),
    reason="paper corpus not fetched")

def test_corpus_builds():
    passages = rag.build_corpus()
    assert len(passages) > 100
    assert any("survival" in p.text.lower() for p in passages)

def test_lexical_retrieval_is_relevant():
    idx = rag.RagIndex(rag.build_corpus())
    hits = idx.query("CD4 T cells mediate C9orf72 response", k=3, method="lexical")
    assert hits and hits[0]["score"] > 0
    joined = " ".join(h["text"].lower() for h in hits)
    assert "cd4" in joined
