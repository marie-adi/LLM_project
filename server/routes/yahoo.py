from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.tools.yahoo_data import YahooFetcher
from server.services.prompt_builder import PromptBuilder
from server.services.lm_engine import LMEngine, GroqModel
from typing import Dict
from loguru import logger
from langdetect import detect

router = APIRouter(prefix="/yahoo", tags=["Market Data Tickers from Yahoo"])
yahoo_service = YahooFetcher()
prompt_builder = PromptBuilder()
lm_engine = LMEngine(model_name=GroqModel.LLAMA3_70B)

class StoryRequest(BaseModel):
    prompt: str
    audience: str = "20-25"
    platform: str = "instagram"
    region: str = "Spanish (Argentina)"
    detail_level: str = "simple"

class StoryResponse(BaseModel):
    story: str
    ticker: str
    yahoo_link: str

@router.post("/financial-story", response_model=StoryResponse)
async def generate_story(request: StoryRequest):
    try:
        # 1. Validación básica
        if not request.prompt or len(request.prompt.strip()) < 2:
            raise HTTPException(400, detail="Prompt is too short")

        # 2. Detección de tickers con manejo de errores
        try:
            tickers = yahoo_service.detect_tickers(request.prompt)
            if not tickers:
                raise HTTPException(400, detail="No financial instruments identified in query")
        except Exception as e:
            logger.warning(f"Ticker detection warning: {str(e)}")
            tickers = []  # Continuamos para dar una respuesta útil

        # 3. Obtener datos con estructura garantizada
        financial_data = {}
        if tickers:
            financial_data = {ticker: yahoo_service.get_financial_data(ticker) for ticker in tickers}
            main_ticker = tickers[0]
        else:
            # Modo de fallback para cuando no se detectan tickers
            main_ticker = "AAPL"  # Ticker de ejemplo
            financial_data = {main_ticker: yahoo_service.get_financial_data(main_ticker)}

        ticker_data = financial_data[main_ticker]

        # 4. Preparación robusta del contexto
        try:
            input_language = detect(request.prompt)
        except:
            input_language = "en"  # Default si falla la detección

        context = {
                "symbol":         ticker_data["symbol"],
                "name":           ticker_data["name"],
                "country":        ticker_data.get("country", "—"),
                "current_price":  ticker_data["current_price"],
                "currency":       ticker_data["currency"],
                "change_pct":     ticker_data["change_pct"],
                "sector":         ticker_data["sector"],
                "summary":        ticker_data["summary"],
                # Aplanamos las key_metrics
                "pe_ratio":           ticker_data["key_metrics"]["pe_ratio"],
                "market_cap":         ticker_data["key_metrics"]["market_cap"],
                "fifty_two_week_high": ticker_data["key_metrics"]["fifty_two_week_high"],
                "style":           "technical" if request.detail_level == "advanced" else "simple",
                "detail_level":    request.detail_level,
                "input_language":   input_language,
                "url":              ticker_data["url"]
            }

        # 5. Generación del prompt
        try:
            base_prompt = prompt_builder.build_prompt(
                user_input=request.prompt,
                platform=request.platform,
                age_range=request.audience,
                region=request.region
            )
            yahoo_prompt = yahoo_service.load_yahoo_prompt().format(**context)
            full_prompt = f"{base_prompt}\n\n{yahoo_prompt}"
        except Exception as e:
            logger.error(f"Prompt construction failed: {str(e)}")
            raise HTTPException(500, "Content generation error")

        # 6. Generación de la historia
        try:
            story = await lm_engine.ask(full_prompt)
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            story = f"Could not generate analysis for {main_ticker}. Please visit {ticker_data['url']} for direct data."

        return StoryResponse(
            story=story,
            ticker=main_ticker,
            yahoo_link=ticker_data["url"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, "Financial story generation service is currently unavailable")