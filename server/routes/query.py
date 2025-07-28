from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from server.services.query_engine import ContentQueryEngine
from server.utils.query_depth import is_deep_query
from loguru import logger

router = APIRouter()
engine = ContentQueryEngine()

class QueryRequest(BaseModel):
    prompt: str = Field(..., description="Economics query")
    platform: str = "linkedin"
    audience: str = "26-85"
    region: str = "Spanish (Argentina)"

@router.post("/query/ask", tags=["Academic Research Agent (PDF/arXiv-focused)"], summary="(Knowledge Retrieval Agent) Retrieves scholarly data from arXiv and embeds it using ChromaDB.", description="Detects depth, enriches context via academic sources, and generates educational content for social platforms.")
async def ask_query(request: QueryRequest):
    user_query = request.prompt
    logger.info(f"Received query: {user_query}")

    try:
        # Use deep query check to log behavior only — no enrichment yet
        if is_deep_query(user_query):
            logger.info("🧠 Detected deep economics query — enrichment recommended but not active.")
        else:
            logger.info("💬 Standard-level query — sending to LLM directly.")
        
    
        # Build prompt with available metadata
        final_prompt = (
            f"Platform: {request.platform}\n"
            f"Audience: {request.audience}\n"
            f"Region: {request.region}\n"
            f"Prompt: {user_query}"
        )

        # Send to your content engine
        response = await engine.run_query(request)
        return {"response": response}

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query.")
