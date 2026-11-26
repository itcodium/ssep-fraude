def build_synthesis_prompt(prediction, chunks) -> str:
    label = prediction["label"]

    context = "\n\n".join(
        f"[{c['source']} {c['section']}]\n{c['text']}"
        for c in chunks
    )

    return f"""\
Eres un analista de fraude.

Explica la predicción utilizando SOLAMENTE el contexto proporcionado.

Predicción:
{label}

Contexto:
{context}

Instrucciones ESTRICTAS:
- NO expliques.
- NO interpretes.
- NO resumas.
- NO infieras.
- NO añadas conclusiones.
- COPIA literalmente frases del contexto.
- Utiliza máximo una frase.
- Si la información no aparece textualmente en el contexto,
  responde exactamente:
  "No hay información suficiente."
- Toda afirmación debe poder copiarse literalmente del contexto.
- PROHIBIDO introducir conceptos que no aparezcan textualmente
  en el contexto (ej: "evasión fiscal", "transacción ilegal",
  "comportamiento normal", "actividad criminal").
- PROHIBIDO añadir valoraciones ("alta probabilidad",
  "alerta significativa", "riesgo elevado") salvo que
  estén en el contexto.
- PROHIBIDO usar términos distintos a los del contexto para
  describir la misma idea (no "modificada" por "clonada",
  no "en línea" por "online").
- Si el contexto no es suficiente: "No hay información suficiente."
- Responde en español.

Explicación:
"""