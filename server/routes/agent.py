from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.agents.finance_agent import FinanceAgent
from loguru import logger

router = APIRouter(prefix="/agent", tags=["Agents"])

class AgentRequest(BaseModel):
    prompt: str
    platform: str = "linkedin"
    audience: str = "26-33"
    region: str = "Spain"
    model: str = "llama"

class AgentResponse(BaseModel):
    output: str

@router.post(
    "/finance_complete",
    response_model=AgentResponse,
    summary="Run the finance agent (Deep + Basic Yahoo)",
    description="Generates financial content tailored to a specific platform, audience, and region using a selected LLM model."
)
async def run_finance_agent(request: AgentRequest):
    try:
        logger.info(f"Finance Agent Request: {request}")
        agent = FinanceAgent(model_name=request.model)
        output = await agent.run(request)
        return AgentResponse(output=output)
    except Exception as e:
        logger.error(f"Finance agent failed: {e}")
        raise HTTPException(status_code=500, detail="Finance agent error")
