"""
P2.3 - Indexacion de chunks en Chroma con embeddings.

Lee chunks.json, genera embeddings con sentence-transformers
y los almacena en una coleccion de Chroma persistente en ./chroma_db/

Uso como CLI:
    python index_docs.py
"""

import json
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "fraude_docs"
BATCH_SIZE = 32


def main():
    chunks_path = Path("chunks.json")
    if not chunks_path.exists():
        print(f"ERROR: {chunks_path} no existe. Ejecuta primero chunk_docs.py")
        return

    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    print(f"Cargados {len(chunks)} chunks de {chunks_path}")

    print(f"\nCargando modelo {MODEL_NAME}...")
    print(f"(primera vez descarga ~470 MB, ten paciencia)")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Modelo cargado. Dimension: {model.get_sentence_embedding_dimension()}")

    print(f"\nInicializando Chroma en {CHROMA_DIR}...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Coleccion anterior '{COLLECTION_NAME}' eliminada")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"Coleccion '{COLLECTION_NAME}' creada")

    print(f"\nGenerando embeddings...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    print(f"\nInsertando en Chroma...")
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=embeddings.tolist(),
        metadatas=[
            {"source": c["source"], "section": c["section"] or ""}
            for c in chunks
        ],
    )

    print(f"\nOK: {collection.count()} chunks indexados")
    print(f"Coleccion: {COLLECTION_NAME}")
    print(f"Directorio: {CHROMA_DIR}")


if __name__ == "__main__":
    main()