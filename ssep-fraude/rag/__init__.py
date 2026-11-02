"""
P2 - RAG real: chunking, indexacion, retrieval.

Re-exporta la funcion `explain` para que `from rag import explain` funcione.
"""

from rag.retriever import explain

__all__ = ["explain"]