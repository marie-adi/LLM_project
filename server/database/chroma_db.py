import os
from typing import List, Dict, Any

# Librerías para cargar y procesar documentos
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Librerías para Embeddings y ChromaDB
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Directorio donde se almacenarán los datos de ChromaDB (persistente en disco)
CHROMA_PERSIST_DIRECTORY = "./chroma_data"
# Nombre de la colección en ChromaDB donde guardaremos nuestros documentos
COLLECTION_NAME = "financial_documents"
# Modelo de Ollama a usar para los embeddings. 
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text" # Asegúrarse de que este modelo esté disponible en Ollama


def get_embedding_function():
    """
    Inicializa y devuelve la función de embedding utilizando Ollama.
    """
    # Asegúrarse de que el servidor Ollama esté corriendo y el modelo esté descargado.
    return OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)

def load_documents(pdf_directory: str) -> List[Document]:
    """
    Carga todos los archivos PDF de un directorio dado.
    Args:
        pdf_directory (str): Ruta al directorio que contiene los PDFs.
    Returns:
        List[Document]: Una lista de objetos Document de LangChain.
    """
    all_documents = []
    print(f"Cargando documentos desde: {pdf_directory}")
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_directory, filename)
            print(f"  - Cargando {filepath}...")
            # Usa PyPDFLoader para cargar el PDF
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            all_documents.extend(docs)
    print(f"Total de documentos PDF cargados: {len(all_documents)} páginas.")
    return all_documents

def split_documents_into_chunks(documents: List[Document]) -> List[Document]:
    """
    Divide los documentos largos en trozos (chunks) más pequeños.
    Esto es crucial para que el modelo de embedding y el LLM puedan procesarlos eficientemente.
    Args:
        documents (List[Document]): Lista de documentos (páginas de PDF).
    Returns:
        List[Document]: Lista de chunks de documentos.
    """
    # RecursiveCharacterTextSplitter intenta dividir el texto de forma inteligente.
    # chunk_size: el tamaño máximo de cada chunk (en caracteres o tokens, depende del splitter).
    # chunk_overlap: cuánto se superponen los chunks adyacentes. Ayuda a mantener el contexto.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # Un tamaño común para chunks.
        chunk_overlap=200,    # Superposición para mantener el contexto.
        length_function=len,  # len para contar caracteres. Para tokens, se usaría tiktoken.
        is_separator_regex=False,
    )
    print(f"Dividiendo {len(documents)} documentos en chunks...")
    chunks = text_splitter.split_documents(documents)
    print(f"Total de chunks creados: {len(chunks)}.")
    return chunks

def add_documents_to_chroma(chunks: List[Document], embedding_function):
    """
    Añade los chunks de documentos a la base de datos Chroma.
    Si la base de datos ya existe, se añaden los nuevos documentos.
    Args:
        chunks (List[Document]): Los chunks de texto a añadir.
        embedding_function: La función de embedding a usar.
    """
    # Cargar la base de datos existente o crear una nueva si no existe
    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embedding_function,
        collection_name=COLLECTION_NAME
    )

    print(f"Añadiendo {len(chunks)} chunks a ChromaDB...")
    db.add_documents(chunks)
    db.persist() # Asegurarse que los cambios se guarden en disco
    print("Chunks añadidos y base de datos persistida.")

def create_or_update_vector_db(pdf_directory: str):
    """
    Proceso completo para cargar PDFs, dividirlos y añadirlos/actualizar la base de datos vectorial.
    """
    embedding_function = get_embedding_function()

    # 1. Cargar documentos
    documents = load_documents(pdf_directory)
    if not documents:
        print("No se encontraron documentos PDF para procesar.")
        return

    # 2. Dividir documentos en chunks
    chunks = split_documents_into_chunks(documents)

    # 3. Añadir chunks a ChromaDB
    add_documents_to_chroma(chunks, embedding_function)

def query_chroma_db(query_text: str, k: int = 5) -> List[Document]:
    """
    Realiza una búsqueda de similitud en ChromaDB y devuelve los chunks más relevantes.
    Args:
        query_text (str): La pregunta o consulta del usuario.
        k (int): El número de chunks más relevantes a devolver.
    Returns:
        List[Document]: Una lista de los documentos (chunks) más relevantes.
    """
    embedding_function = get_embedding_function()
    
    # Cargar la base de datos existente
    try:
        db = Chroma(
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_function=embedding_function,
            collection_name=COLLECTION_NAME
        )
    except Exception as e:
        print(f"Error al cargar la base de datos Chroma: {e}")
        print("Asegúrate de haber ejecutado 'create_or_update_vector_db' al menos una vez para inicializarla.")
        return []

    print(f"Buscando en ChromaDB para la consulta: '{query_text}'...")
    # Realiza la búsqueda de similitud. Esto convierte la query_text en un embedding
    # busca los embeddings más cercanos en la base de datos.
    results = db.similarity_search(query_text, k=k)
    print(f"Encontrados {len(results)} chunks relevantes.")
    return results


if __name__ == "__main__":
    PDF_DATA_DIRECTORY = "../data_pdfs" 
    
    # Asegúrarse de que el directorio exista
    if not os.path.exists(PDF_DATA_DIRECTORY):
        os.makedirs(PDF_DATA_DIRECTORY)
        print(f"Directorio '{PDF_DATA_DIRECTORY}' creado. Por favor, coloca tus PDFs de prueba aquí.")
    else:
        print(f"Directorio '{PDF_DATA_DIRECTORY}' encontrado.")

#PASOS
    # Asegúrarse de que Ollama esté corriendo y el modelo de embeddings esté descargado
    # Abrir terminal y ejecutar:
    # ollama serve
    # ollama pull nomic-embed-text

    print("\n--- PASO 1: Creando/Actualizando la Base de Datos Vectorial ---")
    create_or_update_vector_db(PDF_DATA_DIRECTORY)

    print("\n--- PASO 2: Realizando una consulta de prueba ---")
    if os.path.exists(CHROMA_PERSIST_DIRECTORY): # Solo intentar consultar si la DB se creó
        test_query = "¿Cuál fue el ingreso bruto del año fiscal 2023?"
        relevant_chunks = query_chroma_db(test_query, k=3)

        if relevant_chunks:
            print("\nChunks relevantes encontrados:")
            for i, chunk in enumerate(relevant_chunks):
                print(f"\n--- Chunk {i+1} ---")
                print(f"Fuente: {chunk.metadata.get('source', 'Desconocida')}, Página: {chunk.metadata.get('page', 'Desconocida')}")
                print(chunk.page_content[:500] + "...") # Mostrar solo los primeros 500 caracteres
        else:
            print("No se encontraron chunks relevantes o la base de datos no está inicializada.")
    else:
        print("La base de datos Chroma no fue creada. No se puede realizar la consulta de prueba.")