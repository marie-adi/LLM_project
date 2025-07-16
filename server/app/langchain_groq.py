import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate

# Cargar variables de entorno
load_dotenv()

# Inicializar el modelo Groq
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",  # o el modelo que prefieras
    temperature=0.7
)

async def generate_response(prompt: str) -> str:
    """
    Genera una respuesta usando Groq a través de LangChain
    """
    try:
        # Crear template de prompt
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="Eres un asistente útil y amigable."),
            HumanMessage(content=prompt)
        ])
        
        # Formatear el prompt
        formatted_prompt = chat_template.format_messages()
        
        # Generar respuesta
        response = await llm.ainvoke(formatted_prompt)
        
        return response.content
        
    except Exception as e:
        raise Exception(f"Error al generar respuesta: {str(e)}")