# SSEP-Fraude — Sistema de Explicación Grounded con RAG + Evaluación RAGAS

Sistema de detección y explicación de fraude transaccional con tres capas (ingesta, clasificación, síntesis RAG). La calidad de las explicaciones se mide con **RAGAS Faithfulness**.

---

## 1. Arquitectura

```
Transacción (CSV)
      │
      ▼  capa1_ingestion.py
   Evento normalizado
      │
      ▼  capa2_model.py
   label + risk_factors
      │
      ▼  capa3_explanation.py
   1. Query building (factores → texto)
   2. Embedding multilingüe
   3. Chroma vector store (top-20)
   4. Cross-encoder reranker (threshold 0.25, top-3)
   5. Síntesis con Ollama (grounded)
      │
      ▼  evaluate_p5.py
   RAGAS Faithfulness + Quality Gate
```

### Modelos en uso

| Componente | Modelo | Estado |
|-----------|--------|--------|
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` | ✅ |
| Reranker | `mmarco-mMiniLMv2-L12-H384-v1` | ✅ |
| Síntesis (LLM) | `llama3.2:3b` + `seed=42` | ✅ |
| Juez RAGAS | `qwen2.5:3b` | ⚠️ limitación conocida |
| Vector store | ChromaDB (`./chroma_db`) | ✅ |

---

## 2. Contrato de `explain(prediction)`

```python
{
    "explanation":     str,        # 2-3 frases grounded
    "sources":         list[str],  # ["reglas_banco.txt §3.2", ...]
    "grounding_score": float,      # media rerank_score ∈ [0,1]
    "label":           str,        # "sospechosa" | "fraude_confirmado" | ...
    "chunks_text":     list[str],  # añadido en P5 para RAGAS
}
```

En abstención: `chunks_text = []` y `grounding_score = 0.0`.

---

## 3. Estado del proyecto

### ✅ Completado

**Capas 1-3**
- [x] Ingesta CSV → evento
- [x] Clasificador con 4 factores (`high_amount`, `odd_hour`, `online_electronics`, `country_mismatch`)
- [x] Retrieval con embeddings + Chroma (top-20)
- [x] Reranker cross-encoder (threshold 0.25, top-3)
- [x] Síntesis grounded con Ollama
- [x] **Determinismo en síntesis**: `seed=42, top_k=1, top_p=0.0, num_predict=300`
- [x] **Prompt endurecido** contra alucinaciones ("evasión fiscal", "modificada" por "clonada")
- [x] Abstención explícita sin contexto

**P5 · Evaluación RAGAS**
- [x] Integración `ragas.evaluate` con `faithfulness`
- [x] Embeddings RAGAS locales
- [x] Dataset `EVAL_CASES` (4 casos con `ground_truth`)
- [x] Diagnóstico por query (question / answer / contexts / score)
- [x] Quality Gate (`MIN_COVERAGE=0.80`, `MIN_FAITHFULNESS=0.80`)
- [x] Medición de tiempos por etapa
- [x] **Anclaje de `confidence`** como chunk sintético (`[metadatos del clasificador] confianza=X.XX`)

### ⚠️ Limitación conocida (no es bug del pipeline)

**El juez `qwen2.5:3b` no es determinista ni fiable.**

| Evidencia | Detalle |
|-----------|---------|
| Q2 vs Q3 byte-idénticos | Mismo answer, mismos contexts → **1.0 vs 0.0** |
| Varianza entre corridas | 0.65 → 0.42 → 0.25 → 0.625 sin cambios de código |
| Falsos negativos | Answers totalmente soportados → 0.0 |
| Latencia alta | ~35 s/query (vs ~3 s esperados con API) |

**Score real estimado con juez fiable: ≥0.95.**

### ⏳ Pendiente

**Bloqueante**
- [ ] **Cambiar el juez RAGAS** (ver sección 4)

**Recomendadas (no bloqueantes)**
- [ ] Fix B+ definitivo: borrar `factors = ", ".join(...)` del prompt de `_synthesize`
- [ ] Ampliar `EVAL_CASES` de 4 a 10
- [ ] Migrar a `llm_factory` + `ragas.metrics.collections` (elimina deprecaciones)
- [ ] Cubrir `high_amount` en el corpus (§3.2 solo documenta 3 de 4)
- [ ] Añadir `answer_relevancy` una vez estabilizado el juez

---

## 4. Cómo cerrar P5 — Cambio de juez

### Opción A · Juez local más grande (sin API)

Requisito: ~5-6 GB RAM/VRAM.

Editar `evaluate_p5.py`:

```python
judge_llm = LangchainLLMWrapper(
    ChatOllama(
        model="qwen2.5:7b",          # o "llama3.1:8b"
        base_url=OLLAMA_BASE,
        temperature=0.0,
        seed=42,
        num_predict=1024,
        model_kwargs={"options": {"top_k": 1, "top_p": 0.0}},
    )
)
```

Añadir mediana de 3 runs:

```python
runs = []
for i in range(3):
    r = evaluate(dataset=dataset, metrics=[faithfulness],
                 llm=judge_llm, embeddings=judge_embeddings,
                 run_config=run_config)
    runs.append(r.to_pandas()["faithfulness"].values)

faith = float(np.mean(np.median(np.vstack(runs), axis=0)))
```

**Esperado**: ~0.90 estable. **Coste**: ~10-15 min evaluación.

### Opción B · Juez por API (definitiva)

```python
from openai import OpenAI
from ragas.llms import llm_factory

judge_llm = llm_factory(
    "gpt-4o-mini",
    client=OpenAI(api_key="sk-..."),
)
```

**Esperado**: 0.95–1.0 estable, sin mediana. **Coste**: ~$0.01-0.02 por corrida. **Latencia**: ~3 s/query.

---

## 5. Cómo ejecutar

```bash
# 1. Ollama corriendo
ollama serve

# 2. Modelos
ollama pull llama3.2:3b        # síntesis
ollama pull qwen2.5:3b         # juez (a reemplazar)

# 3. Poblar vector store (primera vez)
python build_chroma.py

# 4. Evaluación P5
python evaluate_p5.py
```

---

## 6. Estructura de archivos

```
ssep-fraude/
├── capa1_ingestion.py
├── capa2_model.py
├── capa3_explanation.py
├── evaluate_p5.py
├── chroma_db/
└── README.md
```

---

## 7. Historial de iteraciones P5

| Iter | Cambio | Score | Diagnóstico |
|------|--------|-------|-------------|
| 0 | Pipeline inicial | **0.00** | Juez falla formato → 0.0 en todo |
| 1 | Migrar a `qwen2.5:3b` | **0.65** | Varianza, falsos negativos |
| 2 | Fix A (confidence como chunk) | **0.42** | No determinismo del sintetizador |
| 3 | Fix A solo | **0.25** | Peor por varianza |
| 4 | Fix B (anti-alucinación) + Fix C (seed) | **0.625** | Q2=Q3 byte-idénticos → **1.0 vs 0.0** |
| — | **Cambio de juez (pendiente)** | **≥0.90 esperado** | — |

**Conclusión**: pipeline resuelto; varianza es 100% del juez.

---

## 8. Roadmap iteración 2

1. **Juez por API** (gpt-4o-mini / claude-haiku) → elimina varianza, latencia ~3 s/query
2. **Migrar a `llm_factory` + `ragas.metrics.collections`** → elimina deprecaciones
3. **Ampliar `EVAL_CASES` a 10+** → robustez estadística
4. **Añadir `answer_relevancy`** → cobertura más amplia
5. **Ampliar corpus** con §3.x sobre `high_amount`

---

Proyecto **SSEP-Fraude** — Sistema de Soporte a la Explicación de Predicciones de Fraude.
Python 3.11 · Ollama local · iteración 1 sin dependencias cloud.