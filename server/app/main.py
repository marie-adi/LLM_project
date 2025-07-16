from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.langchain_groq import generate_response

app = FastAPI(title="Groq LangChain API", version="1.0.0")

class PromptInput(BaseModel):
    prompt: str

class ResponseOutput(BaseModel):
    output: str

@app.post("/generate", response_model=ResponseOutput)
async def generate(input: PromptInput):
    try:
        result = await generate_response(input.prompt)
        return ResponseOutput(output=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Groq LangChain API está funcionando"}
