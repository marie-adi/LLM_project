from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime
from loguru import logger
from server.tools.query_chroma import ChromaQuery
from server.services.lm_engine import LMEngine, GroqModel
from server.services.prompt_builder import PromptBuilder

router = APIRouter(
    prefix="/generate",
    tags=["Retrieve Existent Info in Chroma"],
    responses={404: {"description": "Collection not found"}},
)

class ChromaRequest(BaseModel):
    prompt: str
    audience: str = "26-85"
    platform: str = "instagram"
    region: str = "Spanish (Argentina)"
    n_results: int = 3
    similarity_threshold: float = 0.5

class ChromaResponse(BaseModel):
    output: str
    sources: List[str]
    confidence: float
    language: str
    processed_at: str

def get_chroma():
    return ChromaQuery()

def get_prompt_builder():
    return PromptBuilder()

@router.post("/chroma_rag", response_model=ChromaResponse)
async def chroma_rag_endpoint(
    request: ChromaRequest,
    chroma: ChromaQuery = Depends(get_chroma),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder)
):
    """Endpoint robusto con manejo de errores y respuestas claras"""
    try:
        # 1. Búsqueda en ChromaDB
        search_results = chroma.search(
            query=request.prompt,
            n_results=request.n_results,
            similarity_threshold=request.similarity_threshold
        )
        
        lang = search_results["language"]
        
        # 2. Manejar caso sin resultados
        if search_results["status"] != "success":
            return _build_no_results_response(request.prompt, lang)
        
        # 3. Construir respuesta con contexto
        return await _build_response_with_context(
            prompt=request.prompt,
            platform=request.platform,
            audience=request.audience,
            region=request.region,
            search_results=search_results,
            prompt_builder=prompt_builder
        )
        
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}")
        return _build_error_response(request.prompt)

async def _build_response_with_context(
    prompt: str,
    platform: str,
    audience: str,
    region: str,
    search_results: dict,
    prompt_builder: PromptBuilder
) -> ChromaResponse:
    """Construye respuesta con contexto de ChromaDB"""
    # 1. Construir contexto
    context = "\n".join(
        f"📚 Source: {source} (Relevance: {score:.0%})\n"
        f"{doc[:500]}{'...' if len(doc) > 500 else ''}"
        for doc, source, score in zip(
            search_results["documents"],
            search_results["sources"],
            search_results["scores"]
        )
    )
    
    # 2. Construir prompt aumentado
    base_prompt = prompt_builder.build_prompt(
        user_input=prompt,
        platform=platform,
        age_range=audience,
        region=region
    )
    
    augmented_prompt = (
        f"{base_prompt}\n\n"
        f"CONTEXT FROM KNOWLEDGE BASE:\n{context}\n\n"
        f"INSTRUCTIONS:\n"
        f"- Answer using this context as primary source\n"
        f"- Cite sources when possible\n"
        f"- If context is irrelevant, say so politely"
    )
    
    # 3. Generar respuesta
    confidence = sum(search_results["scores"]) / len(search_results["scores"])
    output = await LMEngine(model_name=GroqModel.GEMMA_9B).ask(augmented_prompt)

    if confidence < 0.75:
        output += "\n⚠️ Note: Retrieved information may be loosely related. Please interpret with caution."

    
    return ChromaResponse(
        output=output,
        sources=search_results["sources"],
        confidence=sum(search_results["scores"])/len(search_results["scores"]),
        language=search_results["language"],
        processed_at=datetime.now().isoformat()
    )

def _build_no_results_response(query: str, lang: str) -> ChromaResponse:
    """Respuesta cuando no hay resultados"""
    messages = {
    "en": (
        "I currently don't have specific information about this topic in my knowledge base. "
        "Feel free to consult trusted academic sources, or try our 'Thoth – Academic RAG' assistant for advanced research."
    ),
    "es": (
        "Actualmente no tengo información específica sobre este tema en mi base de conocimientos. "
        "Puedes consultar fuentes académicas confiables o probar con el asistente 'Thoth – Academic RAG' para investigación avanzada."
    ),
    "fr": (
        "Je ne dispose pas actuellement d'informations spécifiques sur ce sujet. "
        "Consultez des sources académiques fiables ou essayez l'assistant 'Thoth – Academic RAG' pour des recherches avancées."
    )
}

    
    return ChromaResponse(
        output=messages.get(lang, messages["en"]),
        sources=[],
        confidence=0.0,
        language=lang,
        processed_at=datetime.now().isoformat()
    )

def _build_error_response(query: str) -> ChromaResponse:
    """Respuesta cuando hay un error"""
    return ChromaResponse(
        output=(
            "Disculpa, estoy teniendo problemas para acceder a mi base de conocimiento. "
            "Por favor intenta nuevamente más tarde o pregunta sobre otro tema."
        ),
        sources=[],
        confidence=0.0,
        language="es",
        processed_at=datetime.now().isoformat()
    )