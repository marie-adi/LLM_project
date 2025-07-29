import os
import yfinance as yf
from langdetect import detect
from loguru import logger
from typing import Dict, List, Optional
from deep_translator import GoogleTranslator

class YahooFetcher:
    def __init__(self):
        self.ticker_map = {
            # Correcciones comunes
            "appl": "AAPL", "aapl": "AAPL", "apple": "AAPL",
            "msft": "MSFT", "micro": "MSFT", "microsoft": "MSFT",
            "amzn": "AMZN", "amz": "AMZN", "amazon": "AMZN",
            "googl": "GOOGL", "google": "GOOGL",
            "tsla": "TSLA", "tesla": "TSLA",
            "meta": "META", "facebook": "META",
            "nvda": "NVDA", "nvidia": "NVDA",
            
            # Índices
            "sp500": "^GSPC", "s&p500": "^GSPC",
            "dow": "^DJI", "dow jones": "^DJI",
            "nasdaq": "^IXIC",
            
            # Cripto
            "btc": "BTC-USD", "bitcoin": "BTC-USD",
            "eth": "ETH-USD", "ethereum": "ETH-USD"
        }

    def detect_tickers(self, text: str) -> List[str]:
        """Detección de tickers con soporte multilingüe"""
        try:
            # Detección de idioma y traducción si es necesario
            lang = detect(text)
            if lang != 'en':
                text = GoogleTranslator(source='auto', target='en').translate(text)

            clean_text = text.lower().strip()
            found = []
            
            # Búsqueda exacta
            for word in clean_text.split():
                if word in self.ticker_map:
                    found.append(self.ticker_map[word])
            
            # Búsqueda por substrings
            for name, ticker in self.ticker_map.items():
                if name in clean_text and ticker not in found:
                    found.append(ticker)
            
            return list(set(found))
            
        except Exception as e:
            logger.error(f"Ticker detection error: {e}")
            return []

    def get_financial_data(self, ticker: str) -> Dict:
        """Obtiene datos con estructura garantizada"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1mo")
            
            # Datos base obligatorios
            data = {
                "symbol": ticker,
                "name": info.get("longName", ticker),
                "country": info.get("country", "N/A"),
                "current_price": info.get("currentPrice", 0),
                "currency": info.get("currency", "USD"),
                "change_pct": self._calculate_change(hist),
                "sector": info.get("sector", "N/A"),
                "summary": info.get("longBusinessSummary", "No summary available"),
                "url": self.format_yahoo_url(ticker)
            }
            
            # Métricas con valores por defecto robustos
            metrics = {
                "pe_ratio": info.get("trailingPE", "N/A"),
                "market_cap": self._format_market_cap(info.get("marketCap")),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", "N/A")
            }
            
            # Dos formatos de acceso para máxima compatibilidad
            data.update({
                # Formato plano
                "pe_ratio": metrics["pe_ratio"],
                "market_cap": metrics["market_cap"],
                "fifty_two_week_high": metrics["fifty_two_week_high"],
                # Formato anidado
                "key_metrics": metrics
            })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting data for {ticker}: {str(e)}")
            # Devuelve estructura vacía pero válida
            return {
                "symbol": ticker,
                "name": ticker,
                "country": "N/A",
                "current_price": 0,
                "currency": "USD",
                "change_pct": 0,
                "sector": "N/A",
                "summary": "Data not available",
                "pe_ratio": "N/A",
                "market_cap": "N/A",
                "fifty_two_week_high": "N/A",
                "key_metrics": {
                    "pe_ratio": "N/A",
                    "market_cap": "N/A",
                    "fifty_two_week_high": "N/A"
                },
                "url": self.format_yahoo_url(ticker)
            }

    def format_yahoo_url(self, ticker: str) -> str:
        """Formatea URLs para tickers normales e índices"""
        if ticker.startswith("^"):
            return f"https://finance.yahoo.com/quote/%5E{ticker[1:]}/"
        return f"https://finance.yahoo.com/quote/{ticker}/"

    def load_yahoo_prompt(self) -> str:
        """Carga la plantilla específica para Yahoo"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "prompt_yahoo.txt")
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load yahoo prompt: {e}")
            return ""
        

    def prepare_prompt_data(self, financial_data: Dict, request: Dict) -> Dict:
        """Prepara los datos para el formateo de la plantilla"""
        data = financial_data.copy()
        data.update({
            "style": "technical" if request.get("detail_level") == "advanced" else "simple",
            "detail_level": request.get("detail_level", "simple"),
            "input_language": detect(request.get("prompt", ""))
        })
        
        # Flatten key_metrics para el formateo
        data.update({
            "key_metrics.pe_ratio": data["key_metrics"]["pe_ratio"],
            "key_metrics.market_cap": data["key_metrics"]["market_cap"],
            "key_metrics.fifty_two_week_high": data["key_metrics"]["fifty_two_week_high"]
        })
        return data


    def _calculate_change(self, history) -> float:
        """Cálculo de cambio porcentual"""
        if len(history) < 2:
            return 0.0
        return ((history['Close'][-1] - history['Close'][0]) / history['Close'][0]) * 100

    def _format_market_cap(self, value: float) -> str:
        """Formatea la capitalización de mercado"""
        if not value:
            return "N/A"
        if value >= 1e12:
            return f"${value/1e12:.2f}T"
        return f"${value/1e9:.2f}B"

    

    