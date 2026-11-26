"""
Capa 3: explicación grounded.
Orquesta retrieval + síntesis. El LLM es inyectable vía core.factories.
"""

from core.config import load_config
from core.factories import create_synth_llm
from retrieval import build_query, retrieve_and_rerank
from prompts import build_synthesis_prompt

_synth_llm = None


def _get_synth_llm():
    global _synth_llm
    if _synth_llm is None:
        _synth_llm = create_synth_llm(load_config())
    return _synth_llm


def explain(prediction):
    label = prediction["label"]
    query = build_query(prediction)
    top = retrieve_and_rerank(query)

    if not top:
        return _abstain(label)

    explanation = _synthesize(prediction, top)

    grounding = sum(c["rerank_score"] for c in top) / len(top)

    return {
        "explanation": explanation,
        "sources": [
            f"{c['source']}" + (f" {c['section']}" if c["section"] else "")
            for c in top
        ],
        "grounding_score": round(grounding, 3),
        "label": label,
        "chunks_text": [c["text"] for c in top],
    }


def _abstain(label):
    return {
        "explanation": "No hay contexto recuperado. El sistema se abstuvo.",
        "sources": [],
        "grounding_score": 0.0,
        "label": label,
        "chunks_text": [],
    }


def _synthesize(prediction, chunks):
    prompt = build_synthesis_prompt(prediction, chunks)
    return _get_synth_llm().generate(prompt)