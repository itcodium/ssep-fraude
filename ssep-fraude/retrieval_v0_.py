 import math
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder

_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_RERANKER_NAME = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
_CHROMA_DIR = "./chroma_db"
_COLLECTION_NAME = "fraude_docs"
_TOP_K, _TOP_N, _THRESHOLD = 20, 3, 0.55

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


def build_query(prediction) -> str:
    label = prediction["label"].replace("_", " ")
    factors = prediction.get("risk_factors", [])
    factors_human = [_FACTOR_HUMAN.get(f, f) for f in factors]
    factors_text = ", ".join(factors_human) if factors_human else "ninguno"
    return (
        f"Transaccion {label} con {factors_text}. "
        f"Que significa este patron de riesgo y que accion tomar?"
    )


def retrieve_and_rerank(query: str) -> list[dict]:
    """Devuelve top-N chunks con rerank_score >= threshold, ordenados desc."""
    embedder = _get_embedder()
    query_embedding = embedder.encode(
        query, normalize_embeddings=True
    ).tolist()

    collection = _get_collection()
    results = collection.query(
        query_embeddings=[query_embedding], n_results=_TOP_K
    )

    chunks = []
    if results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            chunks.append(
                {
                    "id": doc_id,
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i]["source"],
                    "section": results["metadatas"][0][i].get("section", ""),
                }
            )

    if not chunks:
        return []

    reranker = _get_reranker()
    pairs = [(query, c["text"]) for c in chunks]
    raw_scores = reranker.predict(pairs)

    for chunk, raw in zip(chunks, raw_scores):
        chunk["rerank_score"] = _sigmoide(float(raw))

    filtered = [c for c in chunks if c["rerank_score"] >= _THRESHOLD]
    filtered.sort(key=lambda c: c["rerank_score"], reverse=True)
    return filtered[:_TOP_N]