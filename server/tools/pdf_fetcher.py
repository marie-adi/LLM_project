from keybert import KeyBERT
from rake_nltk import Rake
import spacy
import arxiv
import os
from loguru import logger
from deep_translator import GoogleTranslator
import langdetect

# Modelos iniciales
kw_model = KeyBERT()
rake = Rake()
nlp = spacy.load("en_core_web_sm")

def extract_with_keybert(text: str, top_n: int = 5):
    kws = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words='english'
    )
    return [kw[0] for kw in kws[:top_n]]

def extract_with_rake(text: str, top_n: int = 5):
    rake.extract_keywords_from_text(text)
    return rake.get_ranked_phrases()[:top_n]

def extract_named_entities(text: str):
    doc = nlp(text)
    return list({ent.text for ent in doc.ents if len(ent.text.split()) >= 1})

def translate_if_needed(text: str, target_lang="en") -> str:
    try:
        src = langdetect.detect(text)
        if src != target_lang:
            return GoogleTranslator(source=src, target=target_lang).translate(text)
    except Exception:
        pass
    return text

class PDFRetriever:
    def __init__(self,
                 save_dir: str = "server/database/data_pdfs",
                 max_results: int = 5,
                 categories: list[str] = None):
        self.save_dir = save_dir
        self.max_results = max_results
        self.categories = categories

    def retrieve(self, query: str):
        os.makedirs(self.save_dir, exist_ok=True)
        translated = translate_if_needed(query)

        # 1) Tres extractores distintos
        kb = extract_with_keybert(translated, top_n=5)
        rk = extract_with_rake(translated,   top_n=5)
        ne = extract_named_entities(translated)

        logger.debug(f"🔍 KeyBERT kws: {kb}")
        logger.debug(f"🔍 RAKE phrases: {rk}")
        logger.debug(f"🔍 NER entities: {ne}")

        # 2) Unimos y limpiamos
        combined = set(kb + rk + ne)
        clean = [
            kw.strip() for kw in combined
            if len(kw.split()) > 1        # al menos dos palabras
            and len(kw) > 4               # más de 4 caracteres
            and not any(char.isdigit() for char in kw)
        ]

        # 3) Si no queda nada, fallback al texto completo
        if not clean:
            search_query = translated
        else:
            search_query = " AND ".join(clean)

        # 4) Añadir filtro de categorías (opcional)
        if self.categories:
            cats = " OR ".join(f"cat:{c}" for c in self.categories)
            search_query = f"({search_query}) AND ({cats})"

        logger.info(f"🔍 Original   : {query}")
        logger.info(f"🌐 Translated : {translated}")
        logger.info(f"🧠 Final kws  : {clean}")
        logger.info(f"🔎 arXiv query: {search_query}")

        # 5) Búsqueda y descarga
        search = arxiv.Search(
            query=search_query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        client = arxiv.Client()
        downloaded = []

        for i, result in enumerate(client.results(search)):
            try:
                path = os.path.join(self.save_dir, f"arxiv_{i}.pdf")
                result.download_pdf(path)
                logger.info(f"✅ Downloaded: {path}")
                downloaded.append(path)
            except Exception as e:
                logger.error(f"❌ Failed to download '{result.title}': {e}")

        if not downloaded:
            logger.warning("⚠️ No PDFs downloaded — quizás la query aún es demasiado específica.")

        return downloaded
