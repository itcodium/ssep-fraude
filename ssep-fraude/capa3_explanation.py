from pathlib import Path

# Prioridad por tipo de documento (mayor = más accionable)
DOC_PRIORITY = {
    "reglas_banco.txt": 3,       # más accionable: qué hacer
    "normativa_pci.txt": 2,      # compliance: qué registrar
    "precedentes.txt": 1,        # histórico: casos previos
}

def explain(prediction: dict, docs_dir: str = "docs") -> dict:
    label = prediction["label"]
    query_terms = label.replace("_", " ").split()

    candidates = []
    for doc_path in Path(docs_dir).glob("*.txt"):
        text = doc_path.read_text()
        score = sum(1 for term in query_terms if term in text.lower())
        if score > 0:
            candidates.append({
                "source": doc_path.name,
                "score": score / len(query_terms),
                "text": text.strip(),
            })

    candidates = [c for c in candidates if c["score"] >= 0.3]
    # Sort por score desc, luego prioridad desc, luego nombre asc (determinista)
    candidates.sort(key=lambda c: (
        -c["score"],
        -DOC_PRIORITY.get(c["source"], 0),
        c["source"],
    ))
    top = candidates[:2]

    if not top:
        return {
            "explanation": f"No hay normativa aplicable a '{label}'. Escalar a compliance.",
            "sources": [],
            "grounding_score": 0.0,
            "label": label,
        }

    explanation = (
        f"Predicción: {label} (confianza {prediction['confidence']:.2f}). "
        f"Factores: {', '.join(prediction['risk_factors']) or 'ninguno'}. "
        f"Según {top[0]['source']}: {top[0]['text'][:200]}..."
    )
    grounding = sum(c["score"] for c in top) / len(top)

    if grounding < 0.4:
        explanation += " [ADVERTENCIA: grounding bajo, verificar]"

    return {
        "explanation": explanation,
        "sources": [c["source"] for c in top],
        "grounding_score": grounding,
        "label": label,
    }