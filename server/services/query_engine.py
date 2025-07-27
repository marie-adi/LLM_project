from server.services.prompt_builder import PromptBuilder
from server.services.lm_engine import LMEngine
from server.tools.yahoo_data import YahooFetcher
from server.tools.pdf_fetcher import PDFRetriever
from loguru import logger

class ContentQueryEngine:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.prompt_builder = PromptBuilder()
        self.lm_engine = LMEngine(model_name)
        self.yahoo = YahooFetcher()
        self.pdf_retriever = PDFRetriever()

    async def run_query(self, request) -> str:
        logger.info(f"Processing user input: {request.prompt}")

        # Step 1: Build initial prompt
        base_prompt = self.prompt_builder.build_prompt(
            user_input=request.prompt,
            platform=request.platform,
            age_range=request.audience,
            region=request.region
        )

        # Step 2: Retrieve market data (if ticker detected)
        market_info = self.yahoo.fetch(request.prompt)
        if market_info:
            logger.debug("Market data enrichment added.")

        # Step 3: Retrieve relevant PDF chunks
        document_chunks = self.pdf_retriever.search(request.prompt)
        doc_text = " | ".join([doc.page_content[:500] for doc in document_chunks]) if document_chunks else ""
        if doc_text:
            logger.debug("PDF-based content enrichment added.")

        # Step 4: Finalize prompt with enrichments
        enriched_prompt = f"""
{base_prompt}

--- Market Data ---
{market_info}

--- Supporting Knowledge ---
{doc_text}

--- User Request ---
{request.prompt}
"""
        logger.info("Final prompt composed. Sending to LLM.")
        return await self.lm_engine.ask(enriched_prompt)
