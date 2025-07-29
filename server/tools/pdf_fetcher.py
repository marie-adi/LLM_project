import os
from typing import List
from keybert import KeyBERT
from rake_nltk import Rake
import spacy
import arxiv  
from arxiv import Client, SortCriterion
from loguru import logger
from deep_translator import GoogleTranslator
import langdetect

# Inicializa modelos
kw_model = KeyBERT()
rake = Rake()
nlp = spacy.load("en_core_web_sm")


def extract_with_keybert(text: str, top_n: int = 5) -> List[str]:
    kws = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english"
    )
    return [kw[0] for kw in kws[:top_n]]


def extract_with_rake(text: str, top_n: int = 5) -> List[str]:
    rake.extract_keywords_from_text(text)
    return rake.get_ranked_phrases()[:top_n]


def extract_named_entities(text: str) -> List[str]:
    doc = nlp(text)
    return list({ent.text for ent in doc.ents})


def translate_if_needed(text: str, target_lang="en") -> str:
    try:
        src = langdetect.detect(text)
        if src != target_lang:
            return GoogleTranslator(source=src, target=target_lang).translate(text)
    except Exception:
        pass
    return text


def build_arxiv_query(
    clean_keywords: List[str],
    translated_text: str = None,
    categories: List[str] = None
) -> str:
    terms = list({kw.strip() for kw in clean_keywords if kw.strip()})
    if not terms:
        query_body = f'"{translated_text}"' if translated_text else ""
    else:
        quoted = [f'"{t}"' for t in terms]
        query_body = " OR ".join(quoted)

    if categories:
        cat_clause = " OR ".join(f"cat:{c}" for c in categories)
        if query_body:
            return f"({query_body}) AND ({cat_clause})"
        return cat_clause

    return query_body


def search_arxiv_and_download(query: str, save_dir: str, max_results: int) -> List[str]:
    os.makedirs(save_dir, exist_ok=True)
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=SortCriterion.Relevance
    )
    client = Client()
    downloaded = []

    for result in client.results(search):
        # 1) ID from PDF is extracted
        paper_id = result.entry_id.split("/")[-1]  # e.g. "2407.12345"
        filename = f"{paper_id}.pdf" # the name of the pdf must change everytime otherwise the database will detect "duplicates" since it is using metadata
        path = os.path.join(save_dir, filename)

        try:
            result.download_pdf(filename=path)
            logger.info(f"✅ Downloaded: {path}")
            downloaded.append(path)
        except Exception as e:
            logger.error(f"❌ Failed to download '{result.title}': {e}")

    return downloaded


class PDFRetriever:
    def __init__(
        self,
        save_dir: str = "server/database/data_pdfs",
        max_results: int = 5,
        categories: List[str] = None
    ):
        self.save_dir = save_dir
        self.max_results = max_results
        self.categories = categories

    def retrieve(self, query: str) -> List[str]:
        # 1) Traducción + extracción de keywords
        translated = translate_if_needed(query)
        kb = extract_with_keybert(translated)
        rk = extract_with_rake(translated)
        ne = extract_named_entities(translated)
        combined = set(kb + rk + ne)
        clean = [
            kw for kw in combined
            if len(kw.split()) > 1
            and len(kw) > 4
            and not any(ch.isdigit() for ch in kw)
        ]

        # 2) Construir query y descargar
        primary_q = build_arxiv_query(clean, translated, self.categories)
        logger.info(f"🔎 arXiv query: {primary_q}")
        paths = search_arxiv_and_download(primary_q, self.save_dir, self.max_results)

        # 3) Fallback con texto completo
        if not paths:
            logger.warning("⚠️ No PDFs encontrados. Reintentando con texto completo…")
            fallback_q = build_arxiv_query([], translated, self.categories)
            logger.info(f"🔎 Fallback query: {fallback_q}")
            paths = search_arxiv_and_download(fallback_q, self.save_dir, self.max_results)

        return paths
