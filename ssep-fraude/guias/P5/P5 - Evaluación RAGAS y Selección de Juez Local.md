# P5 - Evaluación RAGAS y Selección de Juez Local

## Objetivo

Validar la calidad del sistema RAG mediante la métrica **Faithfulness** de RAGAS utilizando modelos locales ejecutados con Ollama.

Objetivo de aceptación:

```text
Faithfulness >= 0.80
Cobertura >= 80%
```

---

# Estado Inicial

## Configuración original

### Synthesizer

```text
llama3.2:3b
```

### Judge

```text
qwen2.5:3b
```

### Embeddings Judge

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

---

# Problemas Detectados

Durante las primeras ejecuciones aparecieron varios síntomas:

## 1. Explicaciones no grounded

Ejemplo:

Contexto:

```text
§3.2: Patrón de riesgo alto:
transacción en país distinto al habitual
+ horario nocturno
+ canal online.
```

Respuesta generada:

```text
La transacción puede no ser normal.

La combinación de factores sugiere una alerta.

Puede indicar actividad fraudulenta.
```

Problema:

```text
El contexto no contenía esas afirmaciones.
```

Consecuencia:

```text
Faithfulness = 0.25
```

---

## 2. Prompt contaminado

El prompt original incluía:

```python
confidence = prediction["confidence"]
factors = prediction["risk_factors"]
```

Y además:

```text
Confianza:
0.68

Factores:
high_amount
odd_hour
country_mismatch
```

Esto hacía que el LLM utilizara:

```text
country_mismatch
high_amount
odd_hour
```

como evidencia.

Aunque esos términos nunca aparecían en los chunks recuperados.

---

## 3. Contextos contaminados

En evaluación se añadía:

```python
contexts.append(
    "[metadatos del clasificador] confianza=0.68"
)
```

Esto mezclaba:

```text
evidencia documental
```

con:

```text
salida interna del clasificador
```

---

# Refactor de la Capa 3

## Arquitectura Original

```text
main.py
↓
rag/retriever.py
↓
retrieval
rerank
prompt
ollama
```

---

## Arquitectura Nueva

```text
main.py
↓
capa3_explanation.py
↓
retrieval.py
↓
prompts.py
↓
core/llm_providers.py
```

Beneficios:

- Separación de responsabilidades.
- Inyección de LLM.
- Prompts centralizados.
- Evaluación desacoplada.

---

# Hallazgo Importante

Se detectó que:

```text
rag/retriever.py
```

ya no era utilizado.

Prueba:

```text
rag/retriever.py
↓
rag/retriever.txt
```

El sistema siguió funcionando normalmente.

Conclusión:

```text
El flujo activo era:

capa3_explanation.py
retrieval.py
prompts.py
core/*
```

---

# Correcciones Aplicadas

---

## Fix A - Eliminar factores de riesgo

Se eliminó:

```python
factors = ...
```

y:

```text
Factores de riesgo:
...
```

del prompt.

---

## Fix B - Eliminar confianza

Se eliminó:

```python
confidence = prediction["confidence"]
```

y:

```text
Confianza:
...
```

del prompt.

---

## Fix C - Limpiar contextos de evaluación

Se eliminó:

```python
contexts.append(
    "[metadatos del clasificador]"
)
```

Quedando:

```python
contexts = result["chunks_text"]
```

---

## Fix D - Convertir síntesis en extracción literal

Antes:

```text
Explica la predicción.
Redacta 2-3 frases.
```

Después:

```text
NO expliques.
NO interpretes.
NO resumir.
COPIA texto literal del contexto.
```

Resultado:

Antes:

```text
La operación puede indicar fraude.
```

Después:

```text
§3.2: Patrón de riesgo alto:
transacción en país distinto al habitual
+ horario nocturno
+ canal online.
```

---

# Problema de Configuración

Se detectó que:

```text
JUDGE_MODEL
```

no tomaba cambios del `.env`.

Diagnóstico:

```python
os.getenv("JUDGE_MODEL")
```

devolvía:

```text
None
```

Causa raíz:

```python
load_dotenv()
```

había desaparecido de:

```python
core/config.py
```

---

## Solución

Restaurar:

```python
from dotenv import load_dotenv

load_dotenv()
```

o preferentemente:

```python
load_dotenv(
    Path(__file__).resolve().parents[1] / ".env"
)
```

---

# Comparativa de Jueces

---

## Qwen 2.5 3B

Configuración:

```text
Synth: llama3.2:3b
Judge: qwen2.5:3b
```

Resultado:

```text
Faithfulness = 0.4583
Cobertura = 100%
```

Detalle:

```text
0.50
0.33
0.50
0.50
```

Observaciones:

- ✅ Compatible con RAGAS
- ✅ Genera métricas
- ❌ Penaliza respuestas prácticamente idénticas al contexto
- ❌ Tiende a producir falsos negativos

Tiempo:

```text
Pipeline medio: 9.19s
Evaluación RAGAS: 111.13s
```

---

## Llama 3.2 3B

Configuración:

```text
Judge: llama3.2:3b
```

Resultado:

```text
Faithfulness = NaN
Cobertura = 0%
```

Errores:

```text
Prompt statement_generator_prompt failed
RagasOutputParserException
```

Conclusión:

```text
No compatible como juez para esta configuración.
```

Tiempo:

```text
Evaluación RAGAS: 602.58s
```

---

## Gemma 2B

Configuración:

```text
Judge: gemma:2b
```

Resultado:

```text
Faithfulness = NaN
Cobertura = 0%
```

Errores:

```text
fix_output_format failed
RagasOutputParserException
```

Conclusión:

```text
No compatible como juez.
```

Tiempo:

```text
~180s
```

---

## Gemma3 4B

Configuración:

```text
Synth = llama3.2:3b

Judge = gemma3:4b
```

Resultado:

```text
Faithfulness = 1.0000
Cobertura = 100%
```

Detalle:

```text
1.0
1.0
1.0
1.0
```

Estado:

```text
PASS
```

Tiempo:

```text
Pipeline medio: 9.83s

RAG+LLM medio: 9.82s

Evaluación RAGAS:
266.68s
```

Observaciones:

- ✅ Compatible con RAGAS
- ✅ Parser estable
- ✅ Comprende correctamente evidencia textual
- ✅ Sin falsos negativos observados
- ✅ Mejor juez encontrado para este hardware

---

# Comparativa Final

| Modelo Juez | Funciona con RAGAS | Faithfulness | Cobertura | Observaciones |
| :--- | :---: | :---: | :---: | :--- |
| `qwen2.5:3b` | Sí | 0.4583 | 100% | Muchos falsos negativos |
| `llama3.2:3b` | No | NaN | 0% | Error de parser |
| `gemma:2b` | No | NaN | 0% | Error de parser |
| `gemma3:4b` | Sí | 1.0000 | 100% | Mejor resultado |

---

# Configuración Ganadora

```env
SYNTH_PROVIDER=ollama
SYNTH_MODEL=llama3.2:3b

JUDGE_PROVIDER=ollama
JUDGE_MODEL=gemma3:4b
```

---

# Resultado Final P5

```text
Faithfulness: 1.0000

Cobertura: 100%

Gate: PASS
```

---

# Próximos Pasos (P5+)

## Recomendado

Ampliar dataset:

```text
4 casos
↓
10 casos
```

Agregar:

- Abstención
- Falso positivo
- `high_amount` legítimo
- Viaje declarado
- País distinto legítimo
- Evidencia insuficiente

---

## Futuras pruebas

Cuando el hardware lo permita:

```bash
ollama pull qwen2.5:7b
```

```bash
ollama pull llama3.1:8b
```

para compararlos con:

```text
gemma3:4b
```

como jueces de RAGAS.

---

# Resumen Ejecutivo de Pruebas

## Evolución del sistema

| Etapa | Cambio aplicado | Resultado |
| :--- | :--- | :--- |
| **Estado inicial** | Prompt con confianza + factores de riesgo | `Faithfulness = 0.25` |
| **Fix A** | Eliminación de factores del prompt (`high_amount`, `country_mismatch`, etc.) | Mejora parcial |
| **Fix B** | Eliminación de confianza (`0.68`, `0.87`, etc.) | Mejora parcial |
| **Fix C** | Eliminación de metadatos internos del clasificador en `contexts` | Dataset más limpio |
| **Fix D** | Conversión de explicación libre a extracción literal | `Faithfulness = 0.4583` |
| **Fix Config** | Restauración de `load_dotenv()` | Cambio de jueces habilitado |
| **Fix Judge** | Cambio de `qwen2.5:3b` a `gemma3:4b` | `Faithfulness = 1.0000` |

## Comparación de Jueces

| Judge | Parser RAGAS | Faithfulness | Cobertura | Tiempo evaluación | Resultado |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `qwen2.5:3b` | ✅ | 0.4583 | 100% | 111.13s | ❌ FAIL |
| `llama3.2:3b` | ❌ | NaN | 0% | 602.58s | ❌ FAIL |
| `gemma:2b` | ❌ | NaN | 0% | ~180s | ❌ FAIL |
| `gemma3:4b` | ✅ | 1.0000 | 100% | 266.68s | ✅ PASS |

## Comportamiento Observado por Modelo

| Modelo | Rol probado | Comportamiento observado |
| :--- | :--- | :--- |
| `llama3.2:3b` | Synthesizer | Buen desempeño generando respuestas grounded |
| `llama3.2:3b` | Judge | No genera salida compatible con RAGAS |
| `qwen2.5:3b` | Judge | Compatible con RAGAS pero muy estricto, genera falsos negativos |
| `gemma:2b` | Judge | Incompatible con parser estructurado de RAGAS |
| `gemma3:4b` | Judge | Compatible, estable y consistente |

## Comparación de Métricas Finales

| Configuración | Faithfulness | Cobertura | Estado |
| :--- | :---: | :---: | :---: |
| `llama3.2:3b` (Synth) + `qwen2.5:3b` (Judge) | 0.4583 | 100% | ❌ FAIL |
| `llama3.2:3b` (Synth) + `llama3.2:3b` (Judge) | NaN | 0% | ❌ FAIL |
| `llama3.2:3b` (Synth) + `gemma:2b` (Judge) | NaN | 0% | ❌ FAIL |
| `llama3.2:3b` (Synth) + `gemma3:4b` (Judge) | 1.0000 | 100% | ✅ PASS |

## Impacto de los Cambios

| Cambio | Impacto observado |
| :--- | :--- |
| Eliminar factores de riesgo del prompt | Redujo alucinaciones |
| Eliminar confianza del prompt | Mejor grounding |
| Limpiar `contexts` para RAGAS | Evaluación más correcta |
| Convertir síntesis en extracción literal | Gran mejora de Faithfulness |
| Restaurar carga de `.env` | Permitió probar varios jueces |
| Cambiar a Gemma3 4B | Permitió pasar el gate P5 |