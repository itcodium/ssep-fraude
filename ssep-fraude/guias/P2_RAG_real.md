
**Modelo entrenado:** `model.pkl` (0.3 MB, gitignored). Regenerable con `python train_model.py`.

**Test de P1:** `python test_model.py` clasifica datos ULB reales y verifica el adapter.

### Lo que P1 **no** hace (y P2 sí)

- P1 produce `risk_factors` como lista de strings (`['high_amount', 'odd_hour', ...]`).
- P1 **no explica** por qué esos factores son relevantes. Eso es P2: traducir `risk_factors` a query en lenguaje natural (`_build_query`), recuperar chunks relevantes (Chroma), rerankearlos (`mmarco`), y sintetizar una explicación con fuentes citadas.

**Para P3:** el `_synthesize` actual usa una plantilla que concatena `prediction` + snippets de chunks. P3 lo reemplaza por una llamada a Ollama que genera una explicación en lenguaje natural citando las fuentes. **P1 no se toca en P3** — el `label` y `confidence` siguen viniendo del modelo.

---

## 1. Resumen ejecutivo

P2 está **cerrado**. El pipeline RAG funciona end-to-end con:
- **367 chunks** indexados en Chroma (embeddings multilingües)
- **5 archivos fuente** en `docs/`
- **Retrieval + reranker** operativos
- **Las 3 reglas SSEP intactas** (verificado en `main.py`)

**P2.4 (reranker `bge`) deferido conscientemente.** `mmarco` es suficiente para el corpus actual.

**Siguiente:** P3 (LLM como synthesizer).

---

## 2. Estado del corpus (`docs/`)

| Archivo | Chunks | Origen | Rol |
|---------|--------|--------|-----|
| `fraud_survey.txt` | 217 | Paper arXiv 2010.06479 (Lucas & Jurgovsky, 2020) | Contexto técnico: dataset shift, imbalance, sequence modeling |
| `pci_dss_resumen.txt` | 145 | Extracto Requisito 10 PCI DSS v4.0.1 | Normativa: logging, monitoreo, detección de anomalías |
| `normativa_pci.txt` | 1 | Sintético | Referencia PCI-DSS §10.2 |
| `precedentes.txt` | 3 | Sintético | Casos 2024-0195, 2024-0287, 2024-0341 |
| `reglas_banco.txt` | 1 | Sintético | §3.2 patrón de riesgo alto |
| **Total** | **367** | | |

**Nota:** `pci_dss_resumen_full.txt` (PCI DSS completo, 2732 chunks) fue **eliminado** de `docs/` para evitar contaminar el corpus. Si se necesita, está en `.bak` o se re-descarga.

**Estadísticas de chunks:** min 104 chars, max 997, media 280.

---

## 3. Cambios en `chunking.py` (v4)

### Patrones añadidos a `SECTION_PATTERN`

```python
# Normativa inglesa
r"|Requirement\s+\d+(?:\.\d+)*"      # "Requirement 10.2.1"
r"|Recommendation\s+\d+"             # FATF
r"|Appendix\s+[A-Z]"

# Papers arXiv
r"|\d+\.\d+\s+[A-Z][^\n]{3,60}"      # "1.1 Credit card transactions dataset"
r"|Abstract"
r"|Introduction"
r"|Conclusion"