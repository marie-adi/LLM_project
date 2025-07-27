from server.tools.yahoo_data import YahooFetcher
from server.tools.pdf_fetcher import PDFRetriever
from server.services.lm_engine import LMEngine
from loguru import logger

class FinanceAgent:
    def __init__(self, model_name: str = "llama"):
        self.yahoo = YahooFetcher()
        self.pdfs = PDFRetriever()
        self.lm = LMEngine(model_name)

    async def run(self, request):
        ticker_data = self.yahoo.fetch(request.prompt)
        pdf_chunks = self.pdfs.search(request.prompt)

        enriched_prompt = f"""
User request: {request.prompt}
Market Info: {ticker_data}
Supporting PDFs: {" | ".join([chunk.page_content[:300] for chunk in pdf_chunks])}
Platform: {request.platform}, Audience: {request.audience}, Region: {request.region}
"""

        return await self.lm.ask(enriched_prompt)
