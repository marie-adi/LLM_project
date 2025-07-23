from langchain.agents import initialize_agent, AgentType, Tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json
# Importar tools
from server.tools.generate_post import generar_post
from server.tools.get_market_news import get_market_news
#from .tools.ask_rag import ask_rag  # este  luego

# Cargar entorno
load_dotenv()

# Cargar LLMs disponibles
llm_llama = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)

llm_turbo = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)



# Registrar tools
tools = [
    Tool.from_function(
        func=get_market_news,
        name="NoticiasFinancieras",
        description="""Consulta datos financieros usando un string JSON que incluye el ticker en el campo 'prompt'. 
"""
    ),
    Tool.from_function(
        func=generar_post,
        name="GeneradorDeContenido",
        description="""Genera análisis financieros, explicaciones educativas y contenido estructurado para redes sociales."""
        
# IMPORTANTE: Para usar esta herramienta, DEBES PASAR UN JSON COMPLETO con el siguiente formato:
# {"prompt": "tu texto aquí", "platform": "plataforma", "audience": "grupo-edad", "region": "region"}

# - Para "platform" usa: "linkedin", "twitter" o "instagram"
# - Para "audience" usa: "26-33" para jóvenes profesionales
# - Para "region" usa: "Spain" para España

# EJEMPLO CORRECTO: 
# {"prompt": "Análisis de Amazon", "platform": "linkedin", "audience": "26-33", "region": "Spain"}

# NO envíes solo el texto! Siempre usa el formato JSON completo."""
    )
]

# Sistema para el agente
system_message = """Eres un experto analista financiero cuya misión es proporcionar información clara y precisa sobre los mercados.

PROCESO DE TRABAJO:
1. Si hay ticker en el campo prompt de JSON string(AMZN, AAPL, etc.) → consulta NoticiasFinancieras primero SIEMPRE enviandole el JSON string completo.
2. Consulta cada ticker individual usando NoticiasFinancieras. SIEMPRE consulta UN SOLO ticker a la vez.
3. EJEMPLOS CORRECTOS: ^GSPC, ^DJI, AAPL, BTC-USD
4. EJEMPLOS INCORRECTOS: "^GSPC (S&P 500)", "Dow Jones ^DJI", "índices altos"
5. Si la consulta pide varios índices, haz múltiples llamadas consecutivas
6. Si consultaste NoticiasFinancieras devuelve un JSON string con campos: audience, platform, region, ticker, market_news.
3. SIEMPRE utiliza GeneradorDeContenido. Si antes consultaste NoticiasFinancieras usa GeneradorDeContenido, SIEMPRE incluye y analiza los datos market_news que devolvio NoticiasFinancieras. Si no consultaste NoticiasFinancieras, usa GeneradorDeContenido directamente con JSON string con campos: prompt,audience, platform, region.
4. Cuando generes contenido con GeneradorDeContenido, NUNCA lo resumas. 
5. Proporciona texto MINIMO 200 caracteres, claro y educativo.
6. Tu Final Answer = contenido completo generado (sin cambios), SIEMPRE minimo 200 caracteres. 


Para "AMZN tendencia":
1. [NoticiasFinancieras]: "AMZN"
2. [GeneradorDeContenido]: incluye datos de precio/tendencia
3. Final Answer: post completo generado

TICKERS PRINCIPALES:
- S&P 500: ^GSPC
- Dow Jones: ^DJI
- NASDAQ: ^IXIC
- Russell 2000: ^RUT
- IBEX 35: ^IBEX
- Bitcoin: BTC-USD
- Apple: AAPL
- Microsoft: MSFT
- Amazon: AMZN
- Google: GOOGL
- Tesla: TSLA



INSTRUCCIÓN CRÍTICA PARA FINAL ANSWER:
- Cuando uses GeneradorDeContenido, tu Final Answer DEBE ser EXACTAMENTE el contenido generado por esa herramienta
- NO resumas ni acortes el contenido del post
- NO agregues comentarios adicionales
- El post completo con formato, hashtags y estructura DEBE ser tu respuesta final
- Si se generan varios contenidos, entrega el último post completo como respuesta final.

Para preguntas sobre "índices más altos", consulta los principales índices y compara sus valores."
"""

# Crear el agente maestro
def run_agent(input: str) -> str:
    """
    Ejecuta el agente con el modelo especificado en el json_string
    Args:
        json_string (str): JSON string con los datos del frontend, incluye 'model', 'prompt', etc.
    """
    # Parsear el JSON string
    input_data = json.loads(input)
    
    # Obtener el modelo del input o usar llama por defecto
    model = input_data.get("model", "llama")
    # Seleccionar el LLM según el modelo
    selected_llm = llm_turbo if model == "turbo" else llm_llama
    
    # Crear el agente con el modelo seleccionado
    agent = initialize_agent(
        tools=tools,
        llm=selected_llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        system_message=system_message,
        max_iterations=10
    )
    
    # Ejecutar el agente con el input completo (que ya incluye el model)
    return agent.invoke({"input": input})


# INSTRUCCIONES CRÍTICAS - LEE ATENTAMENTE:
# 1. SIEMPRE consulta UN SOLO ticker a la vez con NoticiasFinancieras
# 2. NUNCA incluyas texto explicativo junto al ticker - envía SOLO el símbolo exacto
# 3. EJEMPLOS CORRECTOS: ^GSPC, ^DJI, AAPL, BTC-USD
# 4. EJEMPLOS INCORRECTOS: "^GSPC (S&P 500)", "Dow Jones ^DJI", "índices altos"
# 5. Si la consulta pide varios índices, haz múltiples llamadas consecutivas

