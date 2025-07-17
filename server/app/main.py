from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.groq_wrapper import generate_response
from typing import Literal, Optional


app = FastAPI(title="Groq LangChain API", version="1.0.0")

class ResponseOutput(BaseModel):
    output: str

class ContentRequest(BaseModel):
    prompt: str               
    topic: Optional[str] = None     
    audience: Optional[str] = None
    tone: Optional[str] = None
    platform: Optional[str] = None
    language: Optional[str] = None

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
