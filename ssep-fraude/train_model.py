"""
P1.2 — Entrenamiento del modelo real con dataset ULB.

Carga creditcard.csv (284,807 transacciones), entrena XGBoost con
scale_pos_weight por el desbalanceo extremo (0.17% fraude),
evalúa métricas y guarda el modelo en model.pkl.

Uso:
    python train_model.py
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
)
from xgboost import XGBClassifier
import joblib
from pathlib import Path


def load_dataset(csv_path: str = "datos/creditcard.csv") -> pd.DataFrame:
    """Carga el dataset ULB."""
    print(f"Cargando {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"  Filas: {len(df):,}")
    print(f"  Columnas: {len(df.columns)}")
    print(f"  Fraudes: {(df['Class'] == 1).sum():,} ({(df['Class'] == 1).mean() * 100:.3f}%)")
    print(f"  Normales: {(df['Class'] == 0).sum():,}")
    return df


def split_dataset(df: pd.DataFrame):
    """Split estratificado 80/20."""
    X = df.drop("Class", axis=1)
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"\nSplit:")
    print(f"  Train: {len(X_train):,} filas ({(y_train == 1).sum()} fraudes)")
    print(f"  Test:  {len(X_test):,} filas ({(y_test == 1).sum()} fraudes)")
    return X_train, X_test, y_train, y_test


def train_xgboost(X_train, y_train):
    """Entrena XGBoost con scale_pos_weight por el desbalanceo."""
    # Factor de compensación: cuántos negativos hay por cada positivo
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    print(f"\nscale_pos_weight: {scale_pos_weight:.2f}")

    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",
        random_state=42,
        n_jobs=-1,
        tree_method="hist",
    )

    print("Entrenando XGBoost...")
    model.fit(X_train, y_train)
    print("Entrenamiento completado.")
    return model


def evaluate_model(model, X_test, y_test):
    """Evalúa el modelo con métricas del dominio de fraude."""
    print("\n=== Evaluación ===")

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    roc_auc = roc_auc_score(y_test, y_proba)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1:        {f1:.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Fraude"]))

    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  TN={cm[0][0]:,}  FP={cm[0][1]:,}")
    print(f"  FN={cm[1][0]:,}  TP={cm[1][1]:,}")

    return {
        "roc_auc": roc_auc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def save_model(model, path: str = "model.pkl"):
    """Guarda el modelo con joblib."""
    joblib.dump(model, path)
    size_mb = Path(path).stat().st_size / (1024 * 1024)
    print(f"\nModelo guardado en {path} ({size_mb:.1f} MB)")


def main():
    # 1. Cargar
    df = load_dataset()

    # 2. Split
    X_train, X_test, y_train, y_test = split_dataset(df)

    # 3. Entrenar
    model = train_xgboost(X_train, y_train)

    # 4. Evaluar
    metrics = evaluate_model(model, X_test, y_test)

    # 5. Guardar
    save_model(model)

    # 6. Resumen final
    print("\n=== Resumen ===")
    if metrics["roc_auc"] >= 0.95 and metrics["recall"] >= 0.80:
        print("✓ Modelo válido para producción (ROC-AUC >= 0.95, Recall >= 0.80)")
    else:
        print("⚠ Revisar hiperparámetros: ROC-AUC o Recall por debajo del umbral")


if __name__ == "__main__":
    main()