import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Absolute path to current directory (where this script lives)
BASE_DIR = os.path.dirname(__file__)

# Directory for persistent ChromaDB storage (inside /server/database)
CHROMA_PERSIST_DIRECTORY = os.path.join(BASE_DIR, "chroma_data")

# Directory where your financial PDFs are stored
PDF_DATA_DIRECTORY = os.path.join(BASE_DIR, "data_pdfs")

# Name of the Chroma collection
COLLECTION_NAME = "financial_documents"

# Embedding model served by Ollama
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"


def get_embedding_function():
    """
    Initializes and returns the Ollama embedding function.
    """
    return OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)


def load_documents(pdf_directory: str) -> List[Document]:
    """
    Loads all PDF files from the specified directory.
    Returns a list of LangChain Document objects.
    """
    all_documents = []
    print(f"Loading PDFs from: {pdf_directory}")
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_directory, filename)
            print(f"  - Loading {filepath}...")
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            all_documents.extend(docs)
    print(f"Total PDF pages loaded: {len(all_documents)}.")
    return all_documents


def split_documents_into_chunks(documents: List[Document]) -> List[Document]:
    """
    Splits full documents into smaller chunks to optimize embedding.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    print(f"Splitting {len(documents)} documents into chunks...")
    chunks = splitter.split_documents(documents)
    print(f"Total chunks created: {len(chunks)}.")
    return chunks


def add_documents_to_chroma(chunks: List[Document], embedding_function):
    """
    Adds new chunks to ChromaDB one by one, printing progress and catching errors.
    """
    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embedding_function,
        collection_name=COLLECTION_NAME
    )

    existing = db.get()
    existing_sources = {meta.get("source") for meta in existing["metadatas"]}
    new_chunks = [doc for doc in chunks if doc.metadata.get("source") not in existing_sources]

    print(f"Detected {len(existing_sources)} existing document sources.")
    print(f"Preparing to insert {len(new_chunks)} chunks that aren’t duplicates.")

    if not new_chunks:
        print("No new documents inserted (all were duplicates).")
        return

    for i, chunk in enumerate(new_chunks):
        try:
            print(f"Inserting chunk {i + 1}/{len(new_chunks)}")
            db.add_documents([chunk])
        except Exception as e:
            print(f"⚠️ Error inserting chunk {i + 1}: {e}")
            print(f"🧪 Chunk preview: {chunk.page_content[:300]}...")

    db.persist()
    print("✅ All chunks processed. ChromaDB updated.")

def create_or_update_vector_db(pdf_directory: str):
    """
    Main pipeline: loads, chunks, embeds, and stores documents in ChromaDB.
    """
    embedding_function = get_embedding_function()
    documents = load_documents(pdf_directory)

    if not documents:
        print("No PDFs found. Place some files in the folder before running.")
        return

    chunks = split_documents_into_chunks(documents)
    add_documents_to_chroma(chunks, embedding_function)


def query_chroma_db(query_text: str, k: int = 5) -> List[Document]:
    """
    Queries ChromaDB to retrieve the most relevant chunks to the input query.
    """
    embedding_function = get_embedding_function()

    try:
        db = Chroma(
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_function=embedding_function,
            collection_name=COLLECTION_NAME
        )
    except Exception as e:
        print(f"Failed to connect to ChromaDB: {e}")
        return []

    print(f"Searching ChromaDB for: '{query_text}'")
    results = db.similarity_search(query_text, k=k)
    print(f"Found {len(results)} relevant chunks.")
    return results


if __name__ == "__main__":
    if not os.path.exists(PDF_DATA_DIRECTORY):
        os.makedirs(PDF_DATA_DIRECTORY)
        print(f"Directory '{PDF_DATA_DIRECTORY}' created. Add your PDFs here.")
    else:
        print(f"Directory '{PDF_DATA_DIRECTORY}' found.")

    print("\n--- STEP 1: Creating or updating the vector database ---")
    create_or_update_vector_db(PDF_DATA_DIRECTORY)

    print("\n--- STEP 2: Running sample query ---")
    if os.path.exists(CHROMA_PERSIST_DIRECTORY):
        test_query = "How does Carl Menger explain the origin of money?"
        relevant_chunks = query_chroma_db(test_query, k=3)

        if relevant_chunks:
            print("\nRelevant chunks:")
            for i, chunk in enumerate(relevant_chunks):
                print(f"\n--- Chunk {i+1} ---")
                print(f"Source: {chunk.metadata.get('source', 'Unknown')}, Page: {chunk.metadata.get('page', 'Unknown')}")
                print(chunk.page_content[:500] + "...")
        else:
            print("No relevant chunks found.")
    else:
        print("ChromaDB folder not found. No query executed.")
