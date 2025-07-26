import yfinance as yf
from datetime import datetime, timedelta
import json

def get_market_yahoo(input: str) -> str:
    """
    Devuelve noticias o datos de mercado basados en un ticker financiero (por ejemplo, 'AAPL', 'TSLA', 'BTC-USD').

    Input puede ser un ticker directo o un JSON con el campo prompt.
    """
    
    print("[DEBUG]: ######### INTENTO NEWS  ###########")
    try:
        print(f"[DEBUG]: DATA received for NEWS: {input}")
        print(f"[DEBUG]: DATA received for NEWS a JSON : {json.loads(input)}")
        data = json.loads(input)
    except Exception:
        print("[DEBUG]: NO SE LEYO JSON !!!!!!!!!!!")
        data = {"prompt": input}

    try:
        # Primero, tratar el input como texto plano
        ticker_input = data.get("prompt", "").strip() if input else ""
        
        # Solo intentar parsear como JSON si el input parece JSON válido
        if isinstance(ticker_input, str) and ticker_input and ticker_input.startswith("{") and ticker_input.endswith("}"):
            try:
                data = json.loads(ticker_input)
                if isinstance(data, dict) and "prompt" in data:
                    ticker_input = data.get("prompt", "").strip()
            except:
                # Si falla el parsing de JSON, seguimos con el input original
                pass
        
        # Lista de tickers comunes para detectarlos en la entrada
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
        
        # CRITICAL FIX: Extraer solo el ticker sin texto adicional
        # Buscar patrones como ^GSPC, ^DJI, AAPL, etc.
        ticker = None
        
        # Remover paréntesis y texto dentro de ellos para limpiar descripciones
        clean_input = ticker_input
        while "(" in clean_input and ")" in clean_input:
            start = clean_input.find("(")
            end = clean_input.find(")", start)
            if start != -1 and end != -1:
                clean_input = clean_input[:start].strip() + " " + clean_input[end+1:].strip()
            else:
                break
                
        # Remover comillas si están presentes
        clean_input = clean_input.replace('"', '').replace("'", "").strip()
        
        # CASO 1: Si empieza con ^ seguido de letras, es un índice - extraer solo el símbolo
        if "^" in clean_input:
            parts = clean_input.split()
            for part in parts:
                if part.startswith("^"):
                    # Extraer solo el símbolo del ticker (^GSPC, ^DJI, etc.)
                    ticker = part.split(",")[0].strip()
                    break
                    
        # CASO 2: Si contiene un ticker criptomoneda (con guion)
        elif "-" in clean_input and "USD" in clean_input.upper():
            parts = clean_input.split()
            for part in parts:
                if "-" in part and "USD" in part.upper():
                    ticker = part.split(",")[0].strip()
                    break
                    
        # CASO 3: Si es un símbolo de acción simple (1-5 letras mayúsculas)
        elif clean_input.isupper() and len(clean_input) <= 5 and clean_input.isalpha():
            ticker = clean_input
            
        # CASO 4: Buscar coincidencias exactas en nombres comunes
        else:
            for common_name, common_ticker in common_tickers.items():
                if clean_input.upper() == common_name.upper():
                    ticker = common_ticker
                    break
                    
            # CASO 5: Si todavía no hay ticker, buscar como substring
            if not ticker:
                for common_name, common_ticker in common_tickers.items():
                    if common_name.upper() in clean_input.upper():
                        ticker = common_ticker
                        break
        
        # Si todavía no hay ticker y parece un input simple, usarlo directamente
        if not ticker and len(ticker_input) <= 5 and "," not in ticker_input and " " not in ticker_input:
            ticker = ticker_input.upper()
        
        # Si no hay ticker identificado, dar instrucciones claras
        if not ticker:
            return """⚠️ No se pudo identificar un ticker válido en su consulta. 
            
Por favor, pruebe con alguno de estos tickers:
- Índices: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ), ^IBEX (IBEX 35)
- Criptomonedas: BTC-USD (Bitcoin), ETH-USD (Ethereum)
- Acciones: AAPL (Apple), MSFT (Microsoft), GOOGL (Google), AMZN (Amazon), TSLA (Tesla)"""
        
        # Si no se ha encontrado un ticker válido, dar mensaje informativo
        if not ticker:
            return """⚠️ No se pudo identificar un ticker válido en su consulta.

Por favor, use alguno de estos tickers populares:
• Índices: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ)
• Criptomonedas: BTC-USD (Bitcoin), ETH-USD (Ethereum)
• Acciones: AAPL (Apple), MSFT (Microsoft), GOOGL (Google)"""

        # Crear objeto Ticker con el símbolo limpio
        stock = yf.Ticker(ticker)
        
        # Intentar obtener datos históricos para validar el ticker
        try:
            history = stock.history(period="5d")
            if history.empty:
                return f"⚠️ No se encontraron datos para el ticker '{ticker}'. Verifique que sea un símbolo válido."
        except Exception as e:
            return f"⚠️ Error al obtener datos para '{ticker}': {str(e)}. Intente con otro ticker como ^GSPC o AAPL."

        # Obtener datos básicos
        info = stock.info

        # Extraer solo los datos que existan con valores por defecto seguros
        name = info.get("longName") or info.get("shortName") or ticker
        
        # Intentar obtener el precio actual usando diferentes campos
        current_price = None
        for price_field in ["currentPrice", "regularMarketPrice", "previousClose", "open"]:
            current_price = info.get(price_field)
            if current_price is not None:
                break
        
        if current_price is None:
            # Si no podemos obtener el precio de info, intentar con el último valor del historial
            if not history.empty:
                current_price = history['Close'].iloc[-1]
            else:
                current_price = "N/A"
        
        currency = info.get("currency", "USD")
        
        # Cambio porcentual en los últimos 5 días
        change_pct = None
        if not history.empty and len(history) > 1:
            first_price = history['Close'].iloc[0]
            last_price = history['Close'].iloc[-1]
            if first_price and last_price:
                change_pct = ((last_price - first_price) / first_price) * 100
        
        # Formatear los campos
        market_cap = info.get("marketCap")
        market_cap_str = f"{market_cap:,.0f}" if market_cap is not None else "N/A"
        
        # Formatear el precio actual
        if current_price != "N/A":
            current_price_str = f"{current_price:,.2f}"
        else:
            current_price_str = "N/A"
            
        # Obtener el cierre anterior
        previous_close = info.get("previousClose")
        previous_close_str = f"{previous_close:,.2f}" if previous_close is not None else "N/A"
        
        # Sector o categoría
        sector = info.get("sector") or info.get("quoteType", "Desconocido")

        # Tendencia más legible
        if not history.empty:
            price_trend = [f"{price:.2f}" for price in history['Close'].to_list()]
            
            # Crear una representación visual de la tendencia con emojis
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
            
        # Cambio porcentual formateado
        change_str = f"{change_pct:+.2f}%" if change_pct is not None else "N/A"

        response = f"""
📊 {name} ({ticker})

• Precio actual: {current_price_str} {currency}
• Cierre anterior: {previous_close_str} {currency}
• Cambio 5 días: {change_str} {trend_emoji}
• Sector: {sector}
• Cap. de mercado: {market_cap_str}

� Precios últimos 5 días:
{price_trend}

Fuente: Yahoo Finance
"""
        data["market_news"] = response
        return json.dumps(data, ensure_ascii=False)

    except Exception as e:
        error_msg = str(e)
        
        # Mejorar mensajes de error comunes
        if "No data found" in error_msg or "delisted" in error_msg:
            return f"""⚠️ No se encontraron datos para '{ticker}'.

Pruebe con alguno de estos tickers populares:
• Índices principales: ^GSPC (S&P 500), ^DJI (Dow Jones), ^IXIC (NASDAQ)
• Acciones tecnológicas: AAPL (Apple), MSFT (Microsoft), GOOGL (Google)
• Criptomonedas: BTC-USD (Bitcoin), ETH-USD (Ethereum)
"""
        # Si hay un error de HTTP, probablemente sea un problema de conexión
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
