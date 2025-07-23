from langchain.agents import initialize_agent, AgentType, Tool
from server.tools.generate_post import generar_post
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)

tools = [
    Tool.from_function(
        func=generar_post,
        name="GeneradorDeContenido",
        description="Genera contenido escrito para redes sociales."
    )
]

marketing_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)
