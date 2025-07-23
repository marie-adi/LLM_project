from langchain.agents import initialize_agent, AgentType, Tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
# Importar tools
from server.tools.generate_post import generar_post
from server.tools.get_market_news import get_market_news
#from .tools.ask_rag import ask_rag  # este  luego

# Cargar entorno
load_dotenv()

# Cargar LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)



# Registrar tools
tools = [
    Tool.from_function(
        func=get_market_news,
        name="NoticiasFinancieras",
        description="Consulta datos financieros usando ÚNICAMENTE el ticker exacto sin texto explicativo. EJEMPLOS CORRECTOS: ^GSPC, ^DJI, AAPL, BTC-USD. EJEMPLOS INCORRECTOS: ^DJI (Dow Jones), indices más altos, S&P 500. IMPORTANTE: Para cada ticker, haz una consulta separada."
    ),
    Tool.from_function(
        func=generar_post,
        name="GeneradorDeContenido",
        description="Genera análisis financieros, explicaciones educativas y contenido estructurado. Útil para sintetizar información de múltiples fuentes, explicar conceptos financieros, comparar datos y crear resúmenes."
    )
]

# Sistema para el agente
system_message = """Eres un experto analista financiero cuya misión es proporcionar información clara y precisa sobre los mercados.

INSTRUCCIONES CRÍTICAS - LEE ATENTAMENTE:
1. SIEMPRE consulta UN SOLO ticker a la vez con NoticiasFinancieras
2. NUNCA incluyas texto explicativo junto al ticker - envía SOLO el símbolo exacto
3. EJEMPLOS CORRECTOS: ^GSPC, ^DJI, AAPL, BTC-USD
4. EJEMPLOS INCORRECTOS: "^GSPC (S&P 500)", "Dow Jones ^DJI", "índices altos"
5. Si la consulta pide varios índices, haz múltiples llamadas consecutivas

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

PROCESO DE TRABAJO:
1. Primero, identifica qué tickers son relevantes para la consulta
2. Consulta cada ticker individual usando NoticiasFinancieras
3. Utiliza GeneradorDeContenido para analizar y explicar los datos recopilados
4. Proporciona conclusiones claras y educativas

Para preguntas sobre "índices más altos", consulta los principales índices y compara sus valores."""

# Crear el agente maestro
finance_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    system_message=system_message,
    max_iterations=10  # Aumentar intentos para investigación completa con múltiples consultas individuales
)
