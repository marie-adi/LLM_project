import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Same config as chroma_db.py
BASE_DIR = os.path.dirname(__file__)
CHROMA_PERSIST_DIRECTORY = os.path.join(BASE_DIR, "chroma_data")
COLLECTION_NAME = "financial_documents"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

def delete_documents_by_source(pdf_name: str):
    """
    Deletes all chunks associated with a specific PDF file.
    """
    embedding = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embedding,
        collection_name=COLLECTION_NAME
    )

    all_docs = db.get()
    metadatas = all_docs["metadatas"]
    ids_to_delete = [
        all_docs["ids"][i]
        for i, meta in enumerate(metadatas)
        if pdf_name in meta.get("source", "")
    ]

    if not ids_to_delete:
        print(f"No chunks found for PDF containing: '{pdf_name}'")
        return

    print(f"Deleting {len(ids_to_delete)} chunks associated with '{pdf_name}'...")
    db.delete(ids=ids_to_delete)
    print("✅ Deletion complete.")

if __name__ == "__main__":
    filename = input("Enter part of the PDF filename to delete (e.g. 'Menger'): ")
    delete_documents_by_source(filename)
