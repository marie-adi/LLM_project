from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.agents.finance_agent import FinanceAgent
from loguru import logger

router = APIRouter(prefix="/agent", tags=["Financial Analysis Agent"])

# Available models with descriptions
AVAILABLE_MODELS = {
    "llama-3.1-8b-instant": {
        "name": "LLaMA 3 8B Instant",
        "description": "Fast responses for general financial queries"
    },
    "llama-3.3-70b-versatile": {
        "name": "LLaMA 3 70B Versatile",
        "description": "High-quality analysis for complex questions"
    },
    "gemma2-9b-it": {
        "name": "Gemma 9B IT",
        "description": "Efficient balanced performance"
    }
}

class AgentRequest(BaseModel):
    prompt: str
    platform: str = "linkedin"
    audience: str = "26-85"
    region: str = "Spanish (Argentina)"
    model: str = "llama-3.1-8b-instant"  # Default model

class AgentResponse(BaseModel):
    output: str
    sources_used: list[str]
    bias_disclosures: list[str]
    model_used: str
    processing_time_ms: float = None

@router.post(
    "/finance_complete",
    response_model=AgentResponse,
    summary="Multi-source financial analysis",
    description="""Analyzes financial queries using:
    - Live market data (Yahoo Finance)
    - Document retrieval (RAG)
    - Direct LLM reasoning
    Select model via the 'model' parameter"""
)
async def run_finance_agent(request: AgentRequest):
    try:
        # Validate model selection
        if request.model not in AVAILABLE_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model. Available options: {list(AVAILABLE_MODELS.keys())}"
            )

        # Check for biased language
        biased_terms = ["dump", "worthless", "trash", "suck"]
        if any(term in request.prompt.lower() for term in biased_terms):
            raise HTTPException(
                status_code=400,
                detail="Query contains potentially biased language. Please rephrase."
            )
            
        # Initialize agent with selected model
        agent = FinanceAgent(model_name=request.model)
        
        # Process request
        result = await agent.run(request)
        
        # Handle empty responses
        if "I don't know" in result["output"]:
            result["output"] = "I couldn't find sufficient diverse sources to provide a balanced answer."
            
        return AgentResponse(
            output=result["output"],
            sources_used=result["sources"],
            bias_disclosures=result["disclosures"],
            model_used=result["model_used"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

@router.get("/available_models")
async def list_models():
    """List available LLM models with descriptions"""
    return {
        "available_models": AVAILABLE_MODELS,
        "default": "llama-3.1-8b-instant"
    }