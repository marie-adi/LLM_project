import yfinance as yf
from loguru import logger

class YahooFetcher:
    def fetch(self, prompt: str) -> str:
        tickers = self._extract_tickers(prompt)
        if not tickers:
            return "No tickers detected."
        
        info = []
        for symbol in tickers:
            try:
                stock = yf.Ticker(symbol)
                data = stock.info
                info.append(f"{symbol}: Price {data.get('regularMarketPrice')}, Sector: {data.get('sector')}")
            except Exception as e:
                logger.warning(f"Error fetching {symbol}: {e}")
        
        return "\n".join(info)

    def _extract_tickers(self, text: str):
        common = ["AAPL", "MSFT", "AMZN", "TSLA", "BTC-USD", "GOOGL", "^GSPC", "^DJI"]
        return [t for t in common if t in text]
