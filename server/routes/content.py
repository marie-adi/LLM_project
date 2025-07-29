from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.services.prompt_builder import PromptBuilder
from server.services.lm_engine import LMEngine, GroqModel
from loguru import logger

router = APIRouter(prefix="/generate", tags=["General Knowledge Agent"])

class ContentRequest(BaseModel):
    prompt: str
    audience: str = "08-11"
    platform: str = "twitter"
    region: str = "Spanish (Argentina)"

class ContentResponse(BaseModel):
    output: str

# Inicializa el builder y el engine de manera global para reutilizar conexiones
prompt_builder = PromptBuilder()
lm_engine = LMEngine(model_name= GroqModel.LLAMA3_8B)

@router.post(
    "/basic/",
    summary="Create economic posts for LinkedIn, Twitter, or Instagram",
    description="Generates educational and platform-tailored content based on topic, audience, region, and prompt."
)
async def generate_content(request: ContentRequest):
    try:
        logger.info(f"Received content request: {request}")

        # 1) Usar build_prompt en lugar de build
        enriched_prompt = prompt_builder.build_prompt(
            user_input=request.prompt,
            platform=request.platform,
            age_range=request.audience,
            region=request.region
        )

        # 2) Llamada al modelo Llama Instant (Groq API)
        output = await lm_engine.ask(enriched_prompt)

        return ContentResponse(output=output)

    except Exception as e:
        logger.error(f"Error generating content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Generation failed")