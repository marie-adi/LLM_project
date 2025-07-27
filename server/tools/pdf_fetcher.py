from keybert import KeyBERT
import arxiv
import os

kw_model = KeyBERT()

def extract_keywords(text: str, top_n: int = 5):
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words='english'
    )
    return [kw[0] for kw in keywords[:top_n]]

class PDFRetriever:
    def __init__(self, save_dir: str = "server/database/data_pdfs", max_results: int = 5):
        self.save_dir = save_dir
        self.max_results = max_results

    def retrieve(self, query: str):
        os.makedirs(self.save_dir, exist_ok=True)
        keywords = extract_keywords(query)
        search_query = " AND ".join(keywords)

        search = arxiv.Search(
            query=search_query + " AND cat:econ",
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        client = arxiv.Client()
        downloaded_files = []

        for i, result in enumerate(client.results(search)):
            try:
                filename = f"{self.save_dir}/arxiv_{i}.pdf"
                result.download_pdf(filename=filename)
                downloaded_files.append(filename)
                print(f"Downloaded: {filename}")
            except Exception as e:
                print(f"Failed to download {result.title}: {e}")

        return downloaded_files
