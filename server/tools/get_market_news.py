import yfinance as yf
from datetime import datetime, timedelta
import json

def get_market_news(input: str) -> str:
    """
    Devuelve noticias o datos de mercado basados en un ticker financiero (por ejemplo, 'AAPL', 'TSLA', 'BTC-USD').

    Input puede ser un ticker directo o un JSON con el campo prompt.
    """
    
    print("[DEBUG]: ######### INTENTO NEWS  ###########")
    try:
        print(f"[DEBUG]: DATA received for NEWS: {input}")
        print(f"[DEBUG]: DATA received for NEWS a JSON : {json.loads(input)}")
        data = json.loads(input)
        if not isinstance(data, dict):
            # Si no es un dict, envolver en dict
            data = {"prompt": input}
    except Exception:
        print("[DEBUG]: NO SE LEYO JSON !!!!!!!!!!!")
        data = {"prompt": input}

    try:
        # EXTRAÍDO: ticker_input es el contenido de prompt
        ticker_input = data.get("prompt", "").strip() if input else ""

        # Parsing adicional solo si prompt es JSON string (igual que antes)
        if isinstance(ticker_input, str) and ticker_input and ticker_input.startswith("{") and ticker_input.endswith("}"):
            try:
                nested_data = json.loads(ticker_input)
                if isinstance(nested_data, dict) and "prompt" in nested_data:
                    ticker_input = nested_data.get("prompt", "").strip()
            except:
                pass
        
        common_tickers = {
            "S&P 500": "^GSPC", 
            "S&P": "^GSPC",
            "DOW JONES": "^DJI",
            "DOW": "^DJI",
            "NASDAQ": "^IXIC",
            "COMPOSITE": "^IXIC",
            "RUSSELL": "^RUT",
            "RUSSELL 2000": "^RUT",
            "NYSE COMPOSITE": "^NYA",
            "IBEX 35": "^IBEX",
            "IBEX": "^IBEX",
            "DAX": "^GDAXI",
            "NIKKEI": "^N225",
            "FTSE": "^FTSE",
            "BITCOIN": "BTC-USD",
            "BTC": "BTC-USD",
            "ETHEREUM": "ETH-USD",
            "ETH": "ETH-USD",
            "APPLE": "AAPL",
            "MICROSOFT": "MSFT",
            "GOOGLE": "GOOGL",
            "AMAZON": "AMZN",
            "TESLA": "TSLA",
            "META": "META",
            "FACEBOOK": "META",
            "NVIDIA": "NVDA"
        }
        
        ticker = None
        
        clean_input = ticker_input
        while "(" in clean_input and ")" in clean_input:
            start = clean_input.find("(")
            end = clean_input.find(")", start)
            if start != -1 and end != -1:
                clean_input = clean_input[:start].strip() + " " + clean_input[end+1:].strip()
            else:
                break
                
        clean_input = clean_input.replace('"', '').replace("'", "").strip()
        
        common_tickers_values = set(common_tickers.values())
        common_tickers_keys = set(k.upper() for k in common_tickers.keys())
        words = clean_input.upper().split()

        for w in words:
            if w in common_tickers_values or w in common_tickers_keys:
                ticker = w
                break
        
        if "^" in clean_input:
            parts = clean_input.split()
            for part in parts:
                if part.startswith("^"):
                    ticker = part.split(",")[0].strip()
                    break
                    
        elif "-" in clean_input and "USD" in clean_input.upper():
            parts = clean_input.split()
            for part in parts:
                if "-" in part and "USD" in part.upper():
                    ticker = part.split(",")[0].strip()
                    break
                    
        # elif clean_input.isupper() and len(clean_input) <= 5 and clean_input.isalpha():
        #     ticker = clean_input
            
        else:
            for common_name, common_ticker in common_tickers.items():
                if clean_input.upper() == common_name.upper():
                    ticker = common_ticker
                    break
                    
            if not ticker:
                for common_name, common_ticker in common_tickers.items():
                    if common_name.upper() in clean_input.upper():
                        ticker = common_ticker
                        break
        
        if not ticker and len(ticker_input) <= 5 and "," not in ticker_input and " " not in ticker_input:
            ticker = ticker_input.upper()
        
        if not ticker:
            return """⚠️ No se pudo identificar un ticker válido en su consulta. 
            
Por favor, pruebe con alguno de estos tickers:
- Índices: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ), ^IBEX (IBEX 35)
- Criptomonedas: BTC-USD (Bitcoin), ETH-USD (Ethereum)
- Acciones: AAPL (Apple), MSFT (Microsoft), GOOGL (Google), AMZN (Amazon), TSLA (Tesla)"""
        
        stock = yf.Ticker(ticker)
        
        try:
            history = stock.history(period="5d")
            if history.empty:
                return f"⚠️ No se encontraron datos para el ticker '{ticker}'. Verifique que sea un símbolo válido."
        except Exception as e:
            return f"⚠️ Error al obtener datos para '{ticker}': {str(e)}. Intente con otro ticker como ^GSPC o AAPL."

        info = stock.info

        name = info.get("longName") or info.get("shortName") or ticker
        
        current_price = None
        for price_field in ["currentPrice", "regularMarketPrice", "previousClose", "open"]:
            current_price = info.get(price_field)
            if current_price is not None:
                break
        
        if current_price is None:
            if not history.empty:
                current_price = history['Close'].iloc[-1]
            else:
                current_price = "N/A"
        
        currency = info.get("currency", "USD")
        
        change_pct = None
        if not history.empty and len(history) > 1:
            first_price = history['Close'].iloc[0]
            last_price = history['Close'].iloc[-1]
            if first_price and last_price:
                change_pct = ((last_price - first_price) / first_price) * 100
        
        market_cap = info.get("marketCap")
        market_cap_str = f"{market_cap:,.0f}" if market_cap is not None else "N/A"
        
        if current_price != "N/A":
            current_price_str = f"{current_price:,.2f}"
        else:
            current_price_str = "N/A"
            
        previous_close = info.get("previousClose")
        previous_close_str = f"{previous_close:,.2f}" if previous_close is not None else "N/A"
        
        sector = info.get("sector") or info.get("quoteType", "Desconocido")

        if not history.empty:
            price_trend = [f"{price:.2f}" for price in history['Close'].to_list()]
            
            if len(price_trend) > 1:
                trend_emoji = ""
                if change_pct is not None:
                    if change_pct > 3:
                        trend_emoji = "🚀 Fuerte subida"
                    elif change_pct > 0:
                        trend_emoji = "📈 Subida"
                    elif change_pct == 0:
                        trend_emoji = "➡️ Estable"
                    elif change_pct > -3:
                        trend_emoji = "📉 Bajada"
                    else:
                        trend_emoji = "💥 Fuerte bajada"
            else:
                trend_emoji = "ℹ️ Datos insuficientes para tendencia"
        else:
            price_trend = ["No hay datos históricos disponibles"]
            trend_emoji = "❓ Sin datos"
            
        change_str = f"{change_pct:+.2f}%" if change_pct is not None else "N/A"

        response = f"""
📊 {name} ({ticker})

• Precio actual: {current_price_str} {currency}
• Cierre anterior: {previous_close_str} {currency}
• Cambio 5 días: {change_str} {trend_emoji}
• Sector: {sector}
• Cap. de mercado: {market_cap_str}

📈 Precios últimos 5 días:
{price_trend}

Fuente: Yahoo Finance
"""

        # --- AÑADIDO: incluir los campos extras recibidos sin perderlos ---
        # Se añaden audience, platform, region si están en data
        audience = data.get("audience", "")
        platform = data.get("platform", "")
        region = data.get("region", "")

        data["market_news"] = response
        data["ticker"] = ticker
        data["audience"] = audience
        data["platform"] = platform
        data["region"] = region
        
        return json.dumps(data, ensure_ascii=False)

    except Exception as e:
        error_msg = str(e)
        
        if "No data found" in error_msg or "delisted" in error_msg:
            return f"""⚠️ No se encontraron datos para '{ticker}'.

Pruebe con alguno de estos tickers populares:
• Índices principales: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ)
• Acciones tecnológicas: AAPL (Apple), MSFT (Microsoft), GOOGL (Google)
• Criptomonedas: BTC-USD (Bitcoin), ETH-USD (Ethereum)
"""
        elif "HTTP Error" in error_msg:
            return f"""⚠️ Error de conexión con Yahoo Finance.

Por favor, intente de nuevo con uno de estos tickers válidos:
• ^GSPC (S&P 500)
• ^DJI (Dow Jones)
• ^IXIC (NASDAQ)
• AAPL (Apple)
• MSFT (Microsoft)
"""
        else:
            return f"""❌ Error al obtener datos de mercado: {error_msg}

Pruebe con un ticker específico como:
• ^GSPC (S&P 500)
• ^DJI (Dow Jones) 
• AAPL (Apple)
"""

