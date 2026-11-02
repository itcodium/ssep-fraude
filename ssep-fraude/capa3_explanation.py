"""
Capa 3 - Explicacion.

Fachada fina: la implementacion real vive en rag/retriever.py.

main.py importa `from capa3_explanation import explain` y no sabe
si por debajo hay keyword matching (P1) o RAG semantico (P2). El
contrato es el mismo: {explanation, sources, grounding_score, label}.

Cuando P3 anada LLM al synthesizer, esta fachada sigue sin cambiar
desde la perspectiva de main.py.
"""

from rag.retriever import explain

__all__ = ["explain"]