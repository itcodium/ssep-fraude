# Baseline de Evaluación RAGAS — Peldaño 5 (P5)

**Proyecto:** SSEP (`ssep-fraude`)  
**Fecha de validación:** 25 de noviembre de 2026  
**Estado del Gate P5:** **PASS** (`Faithfulness = 1.0000 >= 0.80` | `Cobertura = 100.0% >= 80.0%`)

---

## 1. Configuración del Entorno y Modelos

| Componente | Tecnología / Modelo | Parámetros Clave |
| :--- | :--- | :--- |
| **Síntesis (Capa 3)** | Ollama — `llama3.2:3b` | Extracción literal acotada a chunks recuperados |
| **Juez RAGAS** | Ollama — `gemma3:4b` | Ejecución secuencial (`max_workers=1`, `timeout=600s`, `max_retries=2`) |
| **Embeddings (RAG & Juez)** | Hugging Face (`paraphrase-multilingual-MiniLM-L12-v2`) | Corpus indexado de 367 chunks en Chroma local |
| **Reranker** | `mmarco-mMiniLMv2-L12-H384-v1` | Umbral de corte `_THRESHOLD = 0.55` |
| **Dataset de Evaluación** | `eval_dataset.py` | 20 casos (`question`, `answer`, `contexts`, `ground_truth`) |

---

## 2. Resultados Globales de Métricas RAGAS

Evaluación ejecutada sobre **20 queries** (80 evaluaciones individuales totales, 0 timeouts).

| Métrica | Score Promedio | Cobertura | Queries Evaluadas | Criterio Gate | Estado |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Faithfulness** | **1.0000** | 100.0% | 20 / 20 | `>= 0.80` | **PASS** |
| **Context Recall** | **0.8500** | 100.0% | 20 / 20 | Informativo | OK |
| **Context Precision** | **0.6500** | 100.0% | 20 / 20 | Informativo | OK |
| **Answer Relevancy** | **0.1212** | 100.0% | 20 / 20 | Informativo | Esperado* |

*\*Nota técnica sobre `Answer Relevancy`: el valor bajo responde al diseño de extracción literal de reglas/precedentes y a la abstención controlada sin paráfrasis libre, sumado a la generación de preguntas sintéticas en inglés por parte del juez local sobre respuestas breves en español.*

---

## 3. Desempeño y Latencia del Pipeline

| Indicador | Tiempo Medio | Observaciones |
| :--- | :---: | :--- |
| **Pipeline completo (Capas 1 → 3)** | **5.02 s** | Incluye ingesta, clasificación XGBoost/reglas y explicación |
| **RAG + LLM (Capa 3)** | **5.01 s** | ~2.0s en casos de abstención temprana; ~5.0–8.3s con síntesis |
| **Evaluación RAGAS (80 ops)** | **2907.85 s** (~48m 25s) | 36.32 s/it promedio en inferencia local secuencial |

---

## 4. Comportamiento por Categoría de Casos (20 Queries)

* **Casos con evidencia aplicable (12 queries — `CARD-4532`, `CARD-1024`, `CARD-5005`, `CARD-5006`, `CARD-6102`, `CARD-6103`, `CARD-0000`, `CARD-7001` a `CARD-7005`):**
  * `grounding_score` entre **0.80 y 0.97**.
  * Recuperación consistente de `reglas_banco.txt §3.2` y `precedentes.txt Caso 2024-0341`.
  * `Faithfulness = 1.0000` en el 100% de las respuestas.
* **Casos de abstención controlada (8 queries — `CARD-6101`, `CARD-6104`, `CARD-9901`, `CARD-8001` a `CARD-8003`, `CARD-9902`, `CARD-9903`):**
  * `grounding_score = 0.00` (filtrados por `_THRESHOLD = 0.55`).
  * Respuesta determinista sin invocación al LLM: `"No hay contexto recuperado. El sistema se abstuvo."`
  * `Faithfulness = 1.0000` sin alucinaciones ni falsos positivos generativos.

---

## 5. Cierre de Tareas P5

- [x] **P5.1:** Dataset de evaluación ampliado a 20 queries con `ground_truth` (`eval_dataset.py`).
- [x] **P5.2:** Suite RAGAS configurada con las 4 métricas (`faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`) y control de timeouts (`evaluate_p5.py`, `eval_diagnostics.py`).
- [x] **P5.3:** Baseline ejecutado con **100% de cobertura** y **`Faithfulness = 1.0000`** (`>= 0.80`).