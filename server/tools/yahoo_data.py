import yfinance as yf
from loguru import logger
from typing import Dict, List, Optional
from keybert import KeyBERT
from deep_translator import GoogleTranslator

class YahooFinanceService:
    def __init__(self):
        self.kw_model = KeyBERT()
        self.ticker_map = {
            # Company names to tickers
            "apple": "AAPL", "amazon": "AMZN", "microsoft": "MSFT",
            # Add all your existing mappings
            # Indices
            "sp500": "^GSPC", "dow jones": "^DJI",
            # Crypto
            "bitcoin": "BTC-USD", "ethereum": "ETH-USD"
        }

    def detect_tickers(self, text: str) -> List[str]:
        """Enhanced ticker detection from natural language"""
        # Clean and translate if needed
        clean_text = self._preprocess_text(text)
        
        # Method 1: Direct ticker match
        direct_matches = [word.upper() for word in clean_text.split() 
                        if word.upper() in self.ticker_map.values()]
        
        # Method 2: Company name match
        keywords = [kw[0] for kw in self.kw_model.extract_keywords(clean_text)]
        name_matches = [self.ticker_map[kw.lower()] 
                       for kw in keywords 
                       if kw.lower() in self.ticker_map]
        
        return list(set(direct_matches + name_matches))

    def _preprocess_text(self, text: str) -> str:
        """Clean and translate text if needed"""
        try:
            if detect(text) != 'en':
                return GoogleTranslator(source='auto', target='en').translate(text)
            return text.lower()
        except Exception:
            return text.lower()

    def get_financial_data(self, ticker: str) -> Dict:
        """Get enriched financial data for storytelling"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period="1mo")
            
            return {
                "symbol": ticker,
                "name": info.get("longName", ticker),
                "current_price": info.get("currentPrice"),
                "currency": info.get("currency", "USD"),
                "change_pct": self._calculate_change(history),
                "sector": info.get("sector"),
                "summary": info.get("longBusinessSummary"),
                "key_metrics": {
                    "pe_ratio": info.get("trailingPE"),
                    "market_cap": info.get("marketCap"),
                    "52_week_high": info.get("fiftyTwoWeekHigh")
                }
            }
        except Exception as e:
            logger.error(f"Yahoo Finance error: {e}")
            return None

    def _calculate_change(self, history) -> float:
        """Calculate 1-month percentage change"""
        if len(history) < 2:
            return 0
        return ((history['Close'][-1] - history['Close'][0]) / history['Close'][0]) * 100