import os
import tempfile
import time
from pathlib import Path

from capa1_ingestion import ingest
from capa2_model import classify
from capa3_explanation import explain


DEBUG_EVAL = os.getenv("DEBUG_EVAL", "0") == "1"


def run_for_eval(tx_str: str, card_id: str):
    tmp = Path(tempfile.mkdtemp()) / f"{card_id}.txt"
    tmp.write_text(tx_str, encoding="utf-8")

    t0 = time.perf_counter()
    event = ingest(str(tmp), card_id)
    t1 = time.perf_counter()

    prediction = classify(event)
    t2 = time.perf_counter()

    result = explain(prediction)
    t3 = time.perf_counter()

    if DEBUG_EVAL:
        print("\n=== EXPLANATION ===")
        print(result["explanation"])
        print("\n=== CONTEXTS ===")
        for ctx in result["chunks_text"]:
            print(ctx)
        print("\n====================")
        print("\n=== DEBUG EXPLAIN ===")
        print("keys:", result.keys())
        print("chunks_text:", result.get("chunks_text"))
        print("sources:", result.get("sources"))
        print("grounding:", result.get("grounding_score"))
        print()

    factors = ", ".join(prediction.get("risk_factors", [])) or "ninguno"
    question = (
        f"Transaccion "
        f"{prediction['label'].replace('_', ' ')} "
        f"con factores {factors}. "
        f"Explica el riesgo y la accion recomendada."
    )

    contexts = list(result.get("chunks_text", []))
    if not contexts:
        contexts = ["No hay contexto recuperado. El sistema se abstuvo."]

    return {
        "question": question,
        "answer": result["explanation"],
        "contexts": contexts,
        "grounding_score": result["grounding_score"],
        "timings": {
            "ingest": t1 - t0,
            "classify": t2 - t1,
            "explain": t3 - t2,
            "pipeline": t3 - t0,
        },
    }