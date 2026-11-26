# HANDOFF — Continuación técnica de SSEP-Fraude P5

Documento para una AI o desarrollador que retome el trabajo. Asume que ya leyó `README.md`.
Estado actual: **pipeline resuelto, juez RAGAS pendiente de reemplazo**.

---

## Estado exacto del código

### `capa3_explanation.py` — `_synthesize`

**Ya aplicado:**
- `seed=42, top_k=1, top_p=0.0, num_predict=300` en `ollama.generate(options=...)` (Fix C)
- Bloque `Instrucciones ESTRICTAS:` en el prompt (Fix B) con prohibiciones de alucinación semántica

**Pendiente (Fix B+):**
- La línea `factors = ", ".join(prediction.get("risk_factors", [])) or "ninguno"` SIGUE en `_synthesize`.
- El bloque del prompt `Factores de riesgo:\n{factors}` SIGUE presente.

**Acción Fix B+:**
1. Borrar la asignación `factors = ...`
2. Borrar del f-string del prompt el bloque `Factores de riesgo:\n{factors}`
3. No tocar el resto del prompt
4. Verificar que `label`, `confidence` y `context` siguen interpolados

**No tocar en este archivo:**
- `_build_query`, `_FACTOR_HUMAN`, `_get_embedder`, `_get_reranker`, `_get_collection`
- El flujo de `explain`: retrieval, rerank, threshold 0.25, top-3
- `_abstain`

### `evaluate_p5.py` — `run_for_eval`

**Ya aplicado:**
- Fix A: `contexts.append(f"[metadatos del clasificador] confianza={prediction['confidence']:.2f}")` cuando `contexts` no está vacío

**Pendiente (Fix D):**
- En `judge_llm = LangchainLLMWrapper(ChatOllama(...))`, añadir:
  ```python
  seed=42,
  num_predict=1024,
  model_kwargs={"options": {"top_k": 1, "top_p": 0.0}},
  ```

**Pendiente (Fix E, solo si Fix D no basta):**
- Envolver `evaluate(...)` en un bucle de 3 runs y tomar mediana por query.

**Configuración para run final (no diagnóstico):**
- `RunConfig(timeout=600, max_retries=2)` (no `max_retries=0`)
- Quitar `raise_exceptions=True` o ponerlo en `False`

**No tocar:**
- `EVAL_CASES` (salvo que se amplíe, ver roadmap)
- `run_for_eval` en su lógica de timings
- Las secciones 7-11 (diagnóstico, gate, resumen)

### `capa1_ingestion.py`, `capa2_model.py`

**No tocar.** Funcionan.

### Chroma / retrieval / reranker

**No tocar.** `grounding_score` está en 0.88-0.93.

---

## Cómo verificar que un fix funcionó

### Para Fix B+ (machine names fuera del prompt)

Ejecutar `python evaluate_p5.py` y buscar en la salida:

```
grep -iE "high_amount|odd_hour|online_electronics|country_mismatch" stdout.txt
```

Solo deben aparecer en la sección `QUESTION` (que los incluye por diseño), **nunca** en `ANSWER`. Si aparecen en `ANSWER` → Fix B+ no se aplicó o no funcionó.

### Para Fix C (determinismo de síntesis)

Ejecutar `python evaluate_p5.py` **dos veces** y comparar los `answer` de cada query:

```bash
python evaluate_p5.py > run1.txt
python evaluate_p5.py > run2.txt
diff <(grep -A3 "ANSWER:" run1.txt) <(grep -A3 "ANSWER:" run2.txt)
```

Si el diff está vacío → Fix C funciona (síntesis determinista). Si difiere → `seed` no está siendo respetado (verificar `options` en `ollama.generate`).

### Para Fix D (determinismo del juez)

Con Fix C ya aplicado, ejecutar `python evaluate_p5.py` dos veces y comparar la columna `faithfulness` del DataFrame:

```bash
python evaluate_p5.py | grep -A10 "DATAFRAME"
```

Si los scores por query son idénticos entre corridas → Fix D funciona. Si difieren → el juez ignora `seed` (pasar a Opción B: API).

### Para cualquier fix (test de regresión)

**Q2 y Q3 deben seguir dando answers byte-idénticos.** Si divergen, alguien rompió Fix C.

---

## Evidencia clave (para no repetir diagnósticos)

### Run 4 (Fix B + Fix C aplicados, juez 3B)

```
Q1: 1.0
Q2: 1.0   answer idéntico a Q3
Q3: 0.0   answer idéntico a Q2
Q4: 0.5
Media: 0.625
```

**Q2 y Q3 tienen el mismo `answer` y los mismos `contexts`, y scores opuestos.** Esto prueba que la varianza es 100% del juez, no del pipeline.

### Runs previos (referencia)

- Run 0 (juez sin seed, modelo 3B): 0.00 — juez falla formato
- Run 1 (qwen2.5:3b): 0.65 — varianza alta
- Run 2 (Fix A sin seed en síntesis): 0.42 — answers cambian entre corridas
- Run 3 (Fix A solo): 0.25 — peor por varianza del sintetizador
- Run 4 (Fix B + C): 0.625 — determinismo en síntesis, varianza solo en juez

**No aplicar Fix A de nuevo, ya está.** **No revertir Fix B/C, funcionan.**

---

## Stack técnico

- Python 3.11
- Ollama local (`http://127.0.0.1:11434`)
- Modelos: `llama3.2:3b` (síntesis), `qwen2.5:3b` (juez, a reemplazar)
- Dependencias clave: `ragas`, `langchain-ollama`, `langchain-huggingface`, `sentence-transformers`, `chromadb`
- Deprecaciones activas (no bloqueantes): `LangchainLLMWrapper`, `LangchainEmbeddingsWrapper`, import de `ragas.metrics` (migrar a `ragas.metrics.collections`)

---

## Orden de trabajo recomendado para la próxima AI

1. Leer `README.md` completo
2. Leer este `HANDOFF_AI.md` completo
3. Ejecutar `python evaluate_p5.py` **una vez** para confirmar el baseline actual (debería reproducir 0.625 si Fix C sigue activo)
4. Verificar el diff de answers de dos corridas consecutivas (test de Fix C)
5. Aplicar **Fix D** (seed del juez) → ejecutar → comparar con baseline
6. Si score ≥ 0.85 → **cerrar P5**. Documentar en README sección 7 (nueva fila en la tabla)
7. Si score < 0.85 → aplicar **Fix E** (mediana de 3)
8. Si aún < 0.85 → escalar a **Opción B** (juez por API)
9. Opcional (defensa en profundidad): aplicar **Fix B+**

## Criterio de cierre

- Score ≥ 0.80 en 3 corridas consecutivas
- Cobertura ≥ 0.80
- Gate `P5` imprime `✅ PASS`
- Sin regresión: Q2 y Q3 siguen dando answers idénticos

---

## Restricciones del entorno

- Todo local, sin API keys en iteración 1
- CPU-only (no asumir GPU)
- Tiempo de evaluación aceptable: hasta ~15 min por corrida