from fastapi import APIRouter, HTTPException, Query
import yfinance as yf

router = APIRouter()

@router.post("/agent/yahoo")
def get_ticker_data(
    symbol: str = Query(..., summary=  "Ticker Insight Service", description="Stock or crypto ticker symbol (e.g. 'AAPL', 'BTC-USD')")
):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info:
            raise ValueError("No data found for this symbol.")

        # Select useful fields
        result = {
            "symbol": symbol,
            "name": info.get("shortName"),
            "currentPrice": info.get("regularMarketPrice"),
            "currency": info.get("currency"),
            "marketCap": info.get("marketCap"),
            "dayHigh": info.get("dayHigh"),
            "dayLow": info.get("dayLow"),
            "52WeekHigh": info.get("fiftyTwoWeekHigh"),
            "52WeekLow": info.get("fiftyTwoWeekLow"),
            "dividendYield": info.get("dividendYield"),
            "previousClose": info.get("previousClose"),
            "open": info.get("open"),
            "summary": info.get("longBusinessSummary")
        }

        return {"status": "success", "data": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
