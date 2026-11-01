"""
Test rápido de P1.3: verificar que classify_ulb() produce predicciones
coherentes con filas reales del dataset ULB.
"""

import pandas as pd
from model import classify_ulb


def test_real_rows():
    print("Cargando dataset...")
    df = pd.read_csv("datos/creditcard.csv")

    # 1. Una transacción normal real (Class=0)
    normal = df[df["Class"] == 0].iloc[0]
    features = normal.drop("Class").to_dict()
    features["source_id"] = "CARD-TEST-NORMAL"
    result = classify_ulb(features)
    print(f"\n[1] Transacción NORMAL (real, Class=0):")
    print(f"    Label:      {result['label']}")
    print(f"    Confianza:  {result['confidence']}")
    print(f"    Factores:   {result['risk_factors']}")

    # 2. Una transacción fraudulenta real (Class=1)
    fraude = df[df["Class"] == 1].iloc[0]
    features = fraude.drop("Class").to_dict()
    features["source_id"] = "CARD-TEST-FRAUDE"
    result = classify_ulb(features)
    print(f"\n[2] Transacción FRAUDE (real, Class=1):")
    print(f"    Label:      {result['label']}")
    print(f"    Confianza:  {result['confidence']}")
    print(f"    Factores:   {result['risk_factors']}")

    # 3. Verificar que el modelo distingue
    print("\n=== Veredicto ===")
    print("Si [1] dice 'normal' y [2] dice 'fraude_confirmado', el modelo funciona.")


if __name__ == "__main__":
    test_real_rows()