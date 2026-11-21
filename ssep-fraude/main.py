from observability import init_langfuse, flush, observe, propagate_attributes

init_langfuse()  # P4: trazas Langfuse; sin LANGFUSE_* corre igual que P3

from observability import enabled

print("Langfuse enabled:", enabled())

from capa1_ingestion import ingest
from capa2_model import classify
from capa3_explanation import explain


@observe(name="pipeline-ssep")
def run(path, card_id):
    with propagate_attributes(session_id=card_id):
        print(f"\n=== {card_id} ===\n")
        event = ingest(path, card_id)
        f = event["features"]
        print(f"[1] Transacción: {f['amount']}€ · {f['country']} · {f['hour']:02d}h · {f['merchant_category']}")

        prediction = classify(event)
        print(f"[2] Predicción: {prediction['label']} (confianza {prediction['confidence']:.2f}, incertidumbre {prediction['uncertainty']:.2f})")
        print(f"    Factores: {prediction['risk_factors'] or 'ninguno'}")

        result = explain(prediction)
        print(f"[3] Explicación: {result['explanation']}")
        print(f"    Fuentes: {result['sources']}")
        print(f"    Grounding: {result['grounding_score']:.2f}")

if __name__ == "__main__":
    run("datos/trans_normal.txt",     "CARD-7891")
    run("datos/trans_sospechosa.txt", "CARD-4532")
    run("datos/trans_fraude.txt",     "CARD-1024")
    flush()  # P4: obligatorio - los scripts cortos mueren antes del batcher
