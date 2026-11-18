"""
P2.2 - Chunking semantico (v4: filtro de TOC + descarte de titulos).

Divide por seccion/párrafo/linea con marcador, sin depender
del formato exacto de line endings.

Nuevo en v4:
- Ignora lineas de tabla de contenidos (puntos suspensivos)
- Descarta chunks que sean solo un titulo de seccion sin cuerpo
- MIN_CHUNK_CHARS subido a 100
- Eliminado patron generico \d+\s+[A-Z] (capturaba TOC)

Uso:
    python chunk_docs.py
"""

import json
import re
from pathlib import Path


MIN_CHUNK_CHARS = 100
MAX_CHUNK_CHARS = 1000

# Marcadores de seccion al inicio de una linea
SECTION_PATTERN = re.compile(
    r"^\s*("
    # --- Patrones originales (docs sintéticos en español) ---
    r"PCI-DSS\s+§[\d.]+"
    r"|§[\d.]+"
    r"|Caso\s+\d{4}-\d+"
    r"|Reglas internas[^:\n]*:"
    r"|Procedimiento[^:\n]*:"
    # --- Normativa inglesa ---
    r"|Requirement\s+\d+(?:\.\d+)*"      # PCI DSS v4.0.1: "Requirement 10.2.1"
    r"|Recommendation\s+\d+"             # FATF: "Recommendation 20"
    r"|Appendix\s+[A-Z]"                 # "Appendix B"
    # --- Papers arXiv ---
    r"|\d+\.\d+\s+[A-Z][^\n]{3,60}"      # "1.1 Credit card transactions dataset"
    r"|Abstract"
    r"|Introduction"
    r"|Conclusion"
    r")",
    re.MULTILINE,
)

# Patron para detectar lineas de tabla de contenidos (puntos suspensivos)
TOC_PATTERN = re.compile(r"\.\s*\.\s*\.")


def _split_into_blocks(text):
    """
    Divide el texto en bloques logicos.
    1. Ignora lineas de tabla de contenidos
    2. Divide por lineas que empiezan con marcador de seccion
    """
    lines = text.split("\n")
    blocks = []
    current = []

    for line in lines:
        # Ignorar lineas de tabla de contenidos (puntos suspensivos)
        if TOC_PATTERN.search(line):
            continue

        if SECTION_PATTERN.match(line) and current:
            block = "\n".join(current).strip()
            if block:
                blocks.append(block)
            current = [line]
        else:
            current.append(line)

    if current:
        block = "\n".join(current).strip()
        if block:
            blocks.append(block)

    return blocks


def _subdivide_large(block, max_chars):
    """Subdivide un bloque > max_chars por doble newline o por oraciones."""
    if len(block) <= max_chars:
        return [block]

    # Intentar dividir por doble newline primero
    sub_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", block) if p.strip()]
    if len(sub_paragraphs) > 1:
        result = []
        for sp in sub_paragraphs:
            result.extend(_subdivide_large(sp, max_chars))
        return result

    # Fallback: dividir por oraciones
    sentences = re.split(r"(?<=[.!?])\s+", block)
    result = []
    current = ""
    for s in sentences:
        if len(current) + len(s) > max_chars and current:
            result.append(current.strip())
            current = s
        else:
            current += " " + s if current else s
    if current.strip():
        result.append(current.strip())
    return result


def chunk_file(path: Path) -> list:
    """Divide un .txt en chunks por seccion/parrafo."""
    text = path.read_text(encoding="utf-8", errors="replace")
    # Normalizar TODOS los line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if not text.strip():
        return []

    # Dividir por marcadores de seccion
    blocks = _split_into_blocks(text)

    chunks = []
    chunk_counter = 0

    for block in blocks:
        if len(block) < MIN_CHUNK_CHARS:
            continue

        # Detectar seccion al inicio del bloque
        section_match = SECTION_PATTERN.match(block)
        section = section_match.group(1).strip() if section_match else None

        # Subdividir si es muy grande
        subblocks = _subdivide_large(block, MAX_CHUNK_CHARS)

        for subblock in subblocks:
            if len(subblock) < MIN_CHUNK_CHARS:
                continue

            # Descartar si es solo un titulo de seccion (sin cuerpo)
            first_line = subblock.split("\n")[0].strip()
            rest = subblock[len(first_line):].strip()
            if len(rest) < 30:
                continue

            chunks.append({
                "id": f"{path.stem}_{chunk_counter:03d}",
                "text": subblock,
                "source": path.name,
                "section": section,
            })
            chunk_counter += 1

    return chunks


def main():
    docs_dir = Path("docs")
    output_path = Path("chunks.json")

    if not docs_dir.exists():
        print(f"ERROR: {docs_dir} no existe")
        return

    txt_files = sorted(docs_dir.glob("*.txt"))
    if not txt_files:
        print(f"ERROR: no hay archivos .txt en {docs_dir}/")
        return

    print(f"Procesando {len(txt_files)} archivos de {docs_dir}/...\n")

    all_chunks = []
    for path in txt_files:
        chunks = chunk_file(path)
        all_chunks.extend(chunks)
        print(f"  {path.name}: {len(chunks)} chunks")
        # Mostrar secciones detectadas
        sections = set(c["section"] for c in chunks if c["section"])
        if sections:
            for s in sorted(sections):
                print(f"      - {s}")

    output_path.write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nTotal: {len(all_chunks)} chunks")
    print(f"Guardado en {output_path}")

    if all_chunks:
        sizes = [len(c["text"]) for c in all_chunks]
        print(f"\nEstadisticas:")
        print(f"  Minimo: {min(sizes):,} chars")
        print(f"  Maximo: {max(sizes):,} chars")
        print(f"  Media:  {sum(sizes) // len(sizes):,} chars")


if __name__ == "__main__":
    main()