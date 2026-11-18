"""
P2.5 - Capa 3 con RAG real + P3 - Sintesis con LLM.

Reemplaza el keyword matching por:
- Embeddings multilingues (sentence-transformers)
- Vector store (Chroma)
- Reranker cross-encoder
- Threshold 0.25

P3: _synthesize usa Ollama (llama3.2:3b) con prompt grounded
en lugar de plantilla concatenada. El contrato de salida
{explanation, sources, grounding_score, label} no cambia.

Contrato de salida (sin cambios): {explanation, sources, grounding_score, label}
"""

import math
import chromadb
import ollama
from sentence_transformers import SentenceTransformer, CrossEncoder


_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_RERANKER_NAME = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
_CHROMA_DIR = "./chroma_db"
_COLLECTION_NAME = "fraude_docs"
_TOP_K = 20          # antes 10 → más candidatos al reranker
_TOP_N = 3
_THRESHOLD = 0.25    # antes 0.35 → permisivo

_OLLAMA_MODEL = "llama3.2:3b"


# Traducción de risk_factors a lenguaje natural
_FACTOR_HUMAN = {
    "high_amount": "importe alto",
    "odd_hour": "horario nocturno",
    "online_electronics": "compra online de electronica",
    "country_mismatch": "pais distinto al habitual",
}


_embedder = None
_reranker = None
_collection = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(_MODEL_NAME)
    return _embedder


def _get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(_RERANKER_NAME)
    return _reranker


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=_CHROMA_DIR)
        _collection = client.get_collection(name=_COLLECTION_NAME)
    return _collection


def _sigmoide(x):
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _build_query(prediction):
    """
    Construye la query de retrieval en lenguaje natural.

    Usa los risk_factors traducidos a español para que matcheen mejor
    con los chunks (que están en español).
    """
    label = prediction["label"].replace("_", " ")
    factors = prediction.get("risk_factors", [])
    factors_human = [ _FACTOR_HUMAN.get(f, f) for f in factors ]
    factors_text = ", ".join(factors_human) if factors_human else "ninguno"

    return (
        f"Transaccion {label} con {factors_text}. "
        f"Que significa este patron de riesgo y que accion tomar?"
    )


def explain(prediction):
    """Genera una explicacion grounded usando RAG + LLM (P3)."""
    label = prediction["label"]
    query = _build_query(prediction)

    embedder = _get_embedder()
    query_embedding = embedder.encode(query, normalize_embeddings=True).tolist()

    collection = _get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=_TOP_K,
    )

    chunks = []
    if results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            chunks.append({
                "id": doc_id,
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "section": results["metadatas"][0][i].get("section", ""),
            })

    if not chunks:
        return _abstain(label)

    reranker = _get_reranker()
    pairs = [(query, c["text"]) for c in chunks]
    raw_scores = reranker.predict(pairs)

    for chunk, raw in zip(chunks, raw_scores):
        chunk["rerank_score"] = _sigmoide(float(raw))

    filtered = [c for c in chunks if c["rerank_score"] >= _THRESHOLD]
    filtered.sort(key=lambda c: c["rerank_score"], reverse=True)
    top = filtered[:_TOP_N]

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
    }


def _abstain(label):
    return {
        "explanation": f"No hay documentacion relevante para '{label}'. Escalar a compliance.",
        "sources": [],
        "grounding_score": 0.0,
        "label": label,
    }


def _synthesize(prediction, chunks):
    """
    P3: Genera explicacion con LLM (Ollama) usando prompt grounded.

    El LLM recibe SOLO los chunks como contexto. Si no hay info suficiente,
    debe decir "No hay información suficiente" en lugar de alucinar.
    El contrato 3->Consumidor no cambia: explanation sigue siendo string.
    """
    label = prediction["label"]
    confidence = prediction["confidence"]
    factors = ", ".join(prediction.get("risk_factors", [])) or "ninguno"

    context = "\n\n".join(
        f"[{c['source']} {c['section']}]\n{c['text']}"
        for c in chunks
    )

    prompt = f"""Eres un analista de fraude. Explica la predicción usando SOLO el contexto proporcionado.

Predicción: {label}
Confianza: {confidence:.2f}
Factores de riesgo: {factors}

Contexto:
{context}

Instrucciones:
- Redacta una explicación en lenguaje natural, en 2-3 frases.
- Integra las citas de forma natural dentro del texto, no las repitas al final de cada frase.
- Usa el formato [archivo sección] solo una vez por fuente citada.
- No inventes información que no esté en el contexto.
- Si el contexto no responde a la pregunta, di "No hay información suficiente".
- Responde en español.

Explicación:"""

    response = ollama.generate(model=_OLLAMA_MODEL, prompt=prompt)
    return response["response"].strip()