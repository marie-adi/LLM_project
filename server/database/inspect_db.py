import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

BASE_DIR = os.path.dirname(__file__)
CHROMA_PERSIST_DIRECTORY = os.path.join(BASE_DIR, "chroma_data")
COLLECTION_NAME = "financial_documents"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

def inspect_chroma():
    """
    Lists total chunks and PDFs inserted into ChromaDB.
    """
    embedding = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embedding,
        collection_name=COLLECTION_NAME
    )

    docs = db.get()
    sources = set(meta.get("source") for meta in docs["metadatas"] if "source" in meta)

    print(f"\n🧠 Total chunks stored: {len(docs['documents'])}")
    print(f"📚 Unique PDFs inserted: {len(sources)}")

    print("\n📁 List of sources:")
    for s in sorted(sources):
        print("  - " + s)

if __name__ == "__main__":
    inspect_chroma()
