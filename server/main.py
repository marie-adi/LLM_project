from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from server.groq_wrapper import generate_response
from typing import Literal, Optional
from server.agents.marketing_agent import marketing_agent


app = FastAPI(title="Groq LangChain API", version="1.0.0")

class ResponseOutput(BaseModel):
    output: str

class ContentRequest(BaseModel):
    prompt: str                 
    audience: Optional[str] = None
    platform: Optional[str] = None
    region: Optional[str] = None

@app.post("/generate", response_model=ResponseOutput)
async def generate(data: ContentRequest):
    try:
        result = await generate_response(data)
        return ResponseOutput(output=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Groq LangChain API está funcionando"}

@app.post("/agent/marketing", response_model=ResponseOutput)
async def agent_generate(data: ContentRequest):
    try:
        result = marketing_agent.run(data.prompt)
        return ResponseOutput(output=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
