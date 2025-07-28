from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.agents.finance_agent import FinanceAgent
from loguru import logger
from datetime import datetime

router = APIRouter(prefix="/agent", tags=["Multi-Source Finance Agent"])

class AgentRequest(BaseModel):
    prompt: str
    platform: str = "linkedin"
    audience: str = "26-85"
    region: str = "Spanish (Argentina)"
    model: str = "llama-3.1-8b-instant"

class AgentResponse(BaseModel):
    output: str
    sources_used: list[str] = []
    bias_disclosures: list[str] = []

@router.post(
    "/finance_complete",
    response_model=AgentResponse,
    summary="Multi-Source Finance Agent",
    description="This agent dynamically selects between live market data, document retrieval (RAG), and direct LLM reasoning to "
    "generate financial responses. It actively mitigates biases (regional, gender, absolutist), discloses data limitations, "
    "and synthesizes answers from diverse sources, adapting to the prompt’s nature."
)
async def run_finance_agent(request: AgentRequest):
    try:
        # Pre-process check for biased queries
        biased_terms = ["dump", "worthless", "trash", "suck"]
        if any(term in request.prompt.lower() for term in biased_terms):
            raise HTTPException(
                status_code=400,
                detail="Query contains potentially biased language. Please rephrase."
            )
            
        agent = FinanceAgent(model_name=request.model)
        result = await agent.run(request)
        
        # Post-process response
        if "I don't know" in result["output"]:
            result["output"] = "I couldn't find sufficient diverse sources to provide a balanced answer."
            
        return AgentResponse(
            output=result["output"],
            sources_used=result.get("sources", []),
            bias_disclosures=result.get("disclosures", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate balanced response"
        )