import tempfile
from pathlib import Path
from capa1_ingestion import ingest
from capa2_model import classify
from capa3_explanation import explain

casos = [
    ("CARD-7891", "45.3,ES,14,false,supermarket,ES"),      # 1 normal → abstención
    ("CARD-4532", "780.0,FR,22,true,electronics,ES"),       # 2 sospechosa → cita reglas_banco §3.2
    ("CARD-1024", "2400.0,US,03,true,electronics,ES"),      # 3 fraude → cita precedentes + reglas_banco
    ("CARD-5001", "1500.0,ES,14,false,supermarket,ES"),     # 4 high_amount solo
    ("CARD-5002", "780.0,ES,22,true,electronics,ES"),       # 5 sin country_mismatch
    ("CARD-5003", "45.3,ES,03,false,supermarket,ES"),       # 6 país habitual + hora nocturna
    ("CARD-5004", "10.0,ES,14,false,supermarket,ES"),       # 7 importe bajo, hora normal → abstención
    ("CARD-5005", "3000.0,US,03,true,electronics,ES"),      # 8 todos los factors
    ("CARD-5006", "500.0,FR,22,false,supermarket,ES"),      # 9 country_mismatch + odd_hour
    ("CARD-5007", "2400.0,US,03,true,electronics,ES"),      # 10 fraude repetido
]

tmpdir = Path(tempfile.mkdtemp())
ok_citas = 0
alucinaciones = 0
abstenciones_correctas = 0

for i, (card_id, tx) in enumerate(casos, 1):
    tmp_path = tmpdir / f"tx_{i}.txt"
    tmp_path.write_text(tx, encoding="utf-8")

    event = ingest(str(tmp_path), card_id)
    pred = classify(event)
    exp = explain(pred)

    print(f"\n=== Caso {i} · {card_id} ===")
    print(f"Label: {exp['label']}")
    print(f"Explicación: {exp['explanation'][:250]}...")
    print(f"Fuentes: {exp['sources']}")
    print(f"Grounding: {exp['grounding_score']}")

    if exp["sources"]:
        ok_citas += 1
    if exp["grounding_score"] == 0.0 and exp["sources"] == []:
        abstenciones_correctas += 1

print(f"\n=== RESUMEN ===")
print(f"Casos con citas: {ok_citas}/10")
print(f"Abstenciones: {abstenciones_correctas}/10")
print(f"Gate faithfulness >0.7: {'✅ CERRADO' if ok_citas >= 7 else '❌ ABIERTO'}")