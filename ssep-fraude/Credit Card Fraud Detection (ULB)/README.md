# Dataset: Credit Card Fraud Detection (ULB)

Este directorio contiene las instrucciones para descargar el dataset usado en el Peldaño 1 (P1) del proyecto. **El dataset no está versionado en git** por su tamaño (~150 MB).

## Origen

- **Nombre:** Credit Card Fraud Detection
- **Autor:** Machine Learning Group — Université Libre de Bruxelles (ULB)
- **Fuente:** [kaggle.com/mlg-ulb/creditcardfraud](https://www.kaggle.com/mlg-ulb/creditcardfraud)
- **Licencia:** Open Database License (ODbL) v1.0

## Contenido del dataset

| Característica | Valor |
|---|---|
| Transacciones totales | 284,807 |
| Transacciones fraudulentas | 492 (0.172%) |
| Features | 30 (V1-V28 anonimizadas + Time + Amount) |
| Tamaño del CSV | ~150 MB |
| Periodo | 2 días de septiembre 2013 |
| Clientes europeos | sí |
| Desbalanceo | extremo (492 / 284,807) |

**Nota sobre el desbalanceo:** el dataset es extremadamente desbalanceado. Al entrenar XGBoost, hay que usar `scale_pos_weight` o técnicas de remuestreo (SMOTE, undersampling). Un clasificador trivial que prediga siempre "normal" tendría 99.8% de accuracy pero 0% de recall en fraude.

## Cómo descargar

### Opción A — Descarga manual desde Kaggle (recomendado)

1. Ve a [kaggle.com/mlg-ulb/creditcardfraud](https://www.kaggle.com/mlg-ulb/creditcardfraud)
2. Inicia sesión con tu cuenta de Kaggle (crear cuenta es gratis)
3. Click en el botón **"Download"** (esquina superior derecha)
4. Acepta los términos del dataset
5. Se descarga un archivo `archive.zip` (~150 MB)
6. Extrae el CSV:

```bash
# Desde la raíz de ssep-fraude/
unzip "Credit Card Fraud Detection (ULB)/archive.zip" -d datos/