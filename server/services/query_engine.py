import os
from typing import List
from loguru import logger
from server.services.prompt_builder import PromptBuilder
from server.services.lm_engine import LMEngine
from server.tools.pdf_fetcher import PDFRetriever
from server.database.chroma_db import (create_or_update_vector_db,query_chroma_db)


class ContentQueryEngine:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.prompt_builder = PromptBuilder()
        self.lm_engine = LMEngine(model_name)
        self.pdf_retriever = PDFRetriever(
            save_dir="server/database/data_pdfs",
            max_results=5,
            categories=None
        )

    async def run_query(self, request) -> str:
        logger.info(f"Processing user input: {request.prompt}")

        # Prompt base
        base_prompt = self.prompt_builder.build_prompt(
            user_input=request.prompt,
            platform=request.platform,
            age_range=request.audience,
            region=request.region
        )

        # Download PDFs 
        pdf_paths: List[str] = self.pdf_retriever.retrieve(request.prompt)
        doc_text = ""

        if pdf_paths:
            # Indexa ChromaDB
            create_or_update_vector_db(self.pdf_retriever.save_dir)

            # 5) Recuperar chunks relevantes
            chunks = query_chroma_db(request.prompt, k=5)
            doc_text = " | ".join([c.page_content[:500] for c in chunks])
            logger.debug("PDF-based content enrichment added.")

            # Eliminate PDFs to not surcharge
            for path in pdf_paths:
                try:
                    os.remove(path)
                except Exception as e:
                    logger.error(f"Error deleting temporary PDF {path}: {e}")
            logger.debug("Temporary PDF files cleaned up.")

        # Make final prompt
        enriched_prompt = f"""
{base_prompt}

--- Supporting Knowledge ---
{doc_text}

--- User Request ---
{request.prompt}
"""
        logger.info("Final prompt composed. Sending to LLM.")
        return await self.lm_engine.ask(enriched_prompt)
