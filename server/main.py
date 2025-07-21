from fastapi import FastAPI, HTTPException
from pydantic import BaseModel # Import BaseModel for request and response validation
from server.groq_wrapper import generate_response
from typing import Literal, Optional
#from server.agents import marketing_agent, finance_agent
from server.agents.marketing_agent import marketing_agent
from server.agents.finance_agent import finance_agent
import json



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
        input_data = data.model_dump() # Convert Pydantic model to dict
        result = marketing_agent.invoke({"input": json.dumps(input_data)}) # LangChain requiere strings, así que después se convierte a JSON
        
        if isinstance(result, dict) and "output" in result:
            content = result["output"]
        elif isinstance(result, dict) and "input" in result:
            content = result["input"]
        else:
            content = str(result)
            
        return ResponseOutput(output=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/agent/finance", response_model=ResponseOutput)
async def finance_agent_generate(data: ContentRequest):
    try:
        input_data = data.model_dump()  # Convert Pydantic model to dict
        result = finance_agent.invoke({"input": json.dumps(input_data)})  # LangChain requiere strings, así que después se convierte a JSON
        
        if isinstance(result, dict) and "output" in result:
            content = result["output"]
        elif isinstance(result, dict) and "input" in result:
            content = result["input"]
        else:
            content = str(result)
            
        return ResponseOutput(output=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

