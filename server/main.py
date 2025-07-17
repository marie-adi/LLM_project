from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
<<<<<<< HEAD:server/main.py
from server.groq_wrapper import generate_response
=======
from app.groq_wrapper import generate_response
>>>>>>> 39adcdb9f05f96018d059e0d34e372b990ebf680:server/app/main.py
from typing import Literal, Optional


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
