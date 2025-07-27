from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.services.query_engine import ContentQueryEngine
from loguru import logger

router = APIRouter(prefix="/generate", tags=["Content"])

class ContentRequest(BaseModel):
    prompt: str
    audience: str = "20-25"
    platform: str = "twitter"
    region: str = "Spain"

class ContentResponse(BaseModel):
    output: str

@router.post("/", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    try:
        logger.info(f"Received content request: {request}")
        engine = ContentQueryEngine()
        result = await engine.run_query(request)
        return ContentResponse(output=result)
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail="Generation failed")
