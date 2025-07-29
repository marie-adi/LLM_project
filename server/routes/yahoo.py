from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.tools.yahoo_data import YahooFinanceService
from server.services.prompt_builder import PromptBuilder
from typing import Dict, Any

router = APIRouter(prefix="/yahoo", tags=["Market Data"])
service = YahooFinanceService()

class StoryRequest(BaseModel):
    prompt: str
    platform: str = "instagram"
    age_range: str = "20-25"
    region: str = None

@router.post("/financial-story")
async def generate_story(request: StoryRequest):
    """
    Generates financial stories from natural language queries.
    Uses your existing PromptBuilder unchanged.
    """
    try:
        # Step 1: Detect tickers from user input
        tickers = service.detect_tickers(request.prompt)
        if not tickers:
            raise HTTPException(400, "No supported tickers identified")
        
        # Step 2: Fetch enriched financial data
        financial_data = {
            ticker: service.get_financial_data(ticker)
            for ticker in tickers
        }
        
        # Step 3: Build context for your existing prompt builder
        context = {
            "user_input": request.prompt,
            "financial_data": financial_data,
            "analysis_type": "educational"  # Can be dynamic based on request
        }
        
        # Step 4: Use your EXISTING prompt builder (unchanged)
        prompt = PromptBuilder().build_prompt(
            user_input=request.prompt,
            platform=request.platform,
            age_range=request.age_range,
            region=request.region
        )
        
        # The financial data will be available in your prompt templates
        # through the existing mechanism
        
        return {
            "status": "success",
            "detected_tickers": tickers,
            "financial_data": financial_data,
            "prompt": prompt  # For debugging
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Story generation failed: {str(e)}")