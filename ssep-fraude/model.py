"""
P1.3 — Módulo de carga e inferencia del modelo XGBoost.

Carga model.pkl (entrenado en P1.2 con dataset ULB) y expone una
función classify_ulb() que recibe las 30 features del CSV y devuelve
una predicción con contrato del Doc 0.
"""

import joblib
import numpy as np
from pathlib import Path

_MODEL_PATH = Path(__file__).parent / "model.pkl"

_model = None


def load_model():
    """Carga el modelo una sola vez (lazy loading)."""
    global _model
    if _model is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No existe {_MODEL_PATH}. Ejecuta train_model.py primero."
            )
        print(f"Cargando modelo desde {_MODEL_PATH}...")
        _model = joblib.load(_MODEL_PATH)
        print(f"Modelo cargado ({_model.n_features_in_} features)")
    return _model


def classify_ulb(features_ulb: dict) -> dict:
    """
    Clasifica una transacción en formato ULB (V1-V28 + Time + Amount).

    Args:
        features_ulb: dict con claves "Time", "V1"-"V28", "Amount"

    Returns:
        dict con contrato de predicción: {label, confidence, uncertainty,
        model_version, source_id, risk_factors}
    """
    model = load_model()

    # Orden exacto de columnas del CSV ULB
    columns = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]
    X = np.array([[features_ulb[c] for c in columns]])

    proba = model.predict_proba(X)[0]
    proba_fraude = float(proba[1])

    if proba_fraude >= 0.5:
        label = "fraude_confirmado"
        confidence = proba_fraude
    elif proba_fraude >= 0.2:
        label = "sospechosa"
        confidence = proba_fraude
    else:
        label = "normal"
        confidence = 1 - proba_fraude

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "uncertainty": round(1 - confidence, 4),
        "model_version": "xgboost-ulb-v1.0",
        "source_id": features_ulb.get("source_id", "unknown"),
        "risk_factors": _top_risk_factors(model, X, features_ulb),
    }


def _top_risk_factors(model, X, features_ulb: dict, top_k: int = 3) -> list:
    """
    Identifica las top-K features que más contribuyeron a la predicción.
    Placeholder: usa feature_importances_ globales del modelo.
    """
    importances = model.feature_importances_
    columns = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]

    indexed = list(enumerate(importances))
    indexed.sort(key=lambda x: x[1], reverse=True)

    return [columns[i] for i, _ in indexed[:top_k]]