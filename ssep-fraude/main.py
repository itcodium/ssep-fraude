from capa1_ingestion import ingest
from capa2_model import classify
from capa3_explanation import explain

def run(path, card_id):
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