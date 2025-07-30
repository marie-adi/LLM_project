import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
from loguru import logger
import os
from langdetect import detect, LangDetectException
from keybert import KeyBERT
from rake_nltk import Rake
import spacy
from langdetect import detect
from collections import OrderedDict

class ChromaQuery:
    def __init__(self):
        """Inicializador robusto con manejo de colección"""
        try:
            # Configuración de ChromaDB
            self.client = chromadb.PersistentClient(path="data/chroma_db")
            self.embed_func = embedding_functions.DefaultEmbeddingFunction()
            
            # Cargar modelos NLP
            self.kw_model = KeyBERT()
            self.rake = Rake()
            self.nlp = spacy.load("en_core_web_sm")
            
            # Crear colección si no existe
            self.collection_name = "main_collection"
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=self.embed_func
                )
                logger.info(f"Using existing collection: {self.collection_name}")
            except Exception as e:
                logger.warning(f"Collection not found, creating new: {self.collection_name}")
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embed_func
                )
            
        except Exception as e:
            logger.critical(f"Initialization failed: {str(e)}")
            raise

    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        # RAKE
        self.rake.extract_keywords_from_text(text)
        rake_keywords = self.rake.get_ranked_phrases()[:top_n]

        # SpaCy
        doc = self.nlp(text)
        spacy_keywords = [chunk.text.strip() for chunk in doc.noun_chunks][:top_n]
        named_entities = list({ent.text.strip() for ent in doc.ents})[:top_n]

        # KeyBERT
        bert_kws = self.kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words="english"
        )
        bert_keywords = [kw[0].strip() for kw in bert_kws[:top_n]]

        # Combine and preserve order
        all_keywords = rake_keywords + spacy_keywords + bert_keywords + named_entities
        unique_keywords = list(dict.fromkeys(all_keywords))  # Ordered deduplication

        return unique_keywords
            

    def search(self, query: str, n_results: int = 3, similarity_threshold: float = 0.7) -> Dict:
        """Búsqueda segura con manejo de errores"""
        try:
            # 1. Detección de idioma
            try:
                lang = detect(query)
            except LangDetectException:
                lang = "en"
            
            logger.info(f"Searching for: '{query[:50]}...' in {lang}")

            keywords = self.extract_keywords(query)
            query_text = " ".join(keywords)

            # 2. Búsqueda en ChromaDB
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # 3. Filtrar por similitud
            filtered = [
                (doc, meta, 1-dist)
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
                if (1-dist) >= similarity_threshold
            ]
            
            if not filtered:
                return {
                    "documents": [],
                    "sources": [],
                    "scores": [],
                    "language": lang,
                    "status": "no_results"
                }
            
            # 4. Procesar resultados
            documents, metadatas, scores = zip(*filtered)
            
            return {
                "documents": documents,
                "sources": [meta.get("source", "unknown") for meta in metadatas],
                "scores": scores,
                "language": lang,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {
                "documents": [],
                "sources": [],
                "scores": [],
                "language": "en",
                "status": "error"
            }