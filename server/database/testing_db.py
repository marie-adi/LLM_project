# ESTO DEBE DE SER ELIMINADO, SE HIZO MOMENTANEAMENTE
import os
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# 1. Obtener la ruta base (chroma_data)
BASE_DIR = Path(__file__).parent.parent.parent  # Sube 3 niveles desde el script
CHROMA_BASE_DIR = BASE_DIR / "chroma_data"

# 2. Verificar si existe chroma_data
if not os.path.exists(CHROMA_BASE_DIR):
    raise FileNotFoundError(f"No se encontró el directorio: {CHROMA_BASE_DIR}")

# 3. Buscar subcarpetas (Chroma guarda los datos en una subcarpeta con nombre aleatorio)
subdirs = [d for d in os.listdir(CHROMA_BASE_DIR) if os.path.isdir(os.path.join(CHROMA_BASE_DIR, d))]

if not subdirs:
    raise FileNotFoundError(f"No hay subcarpetas dentro de {CHROMA_BASE_DIR}. ¿Has cargado datos en ChromaDB?")

# 4. Seleccionar la primera subcarpeta (asumimos que es la correcta)
CHROMA_PERSIST_DIRECTORY = os.path.join(CHROMA_BASE_DIR, subdirs[0])

print("\n--- Depuración de rutas ---")
print(f"Ruta base del proyecto: {BASE_DIR}")
print(f"Directorio chroma_data: {CHROMA_BASE_DIR}")
print(f"Subcarpetas encontradas: {subdirs}")
print(f"Usando persist_directory: {CHROMA_PERSIST_DIRECTORY}")
print("--------------------------\n")

# 5. Verificar archivos dentro de la subcarpeta
print("Contenido de la subcarpeta ChromaDB:")
for file in os.listdir(CHROMA_PERSIST_DIRECTORY):
    print(f" - {file}")

# 6. Cargar ChromaDB
try:
    embedding = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embedding
    )
    
    # 7. Obtener y mostrar estadísticas
    docs = db.get()
    metas = docs["metadatas"]
    unique_sources = set(meta.get("source") for meta in metas if "source" in meta)
    
    print(f"\nTotal de chunks: {len(docs['documents'])}")
    print(f"PDFs únicos insertados: {len(unique_sources)}")
    print("\nListado de documentos:")
    for source in sorted(unique_sources):
        print(f" - {source}")

except Exception as e:
    print(f"\n❌ Error al cargar ChromaDB: {str(e)}")
    print("Posibles causas:")
    print("- La base de datos está corrupta")
    print("- No tienes permisos de lectura")
    print("- Versión incompatible de ChromaDB")