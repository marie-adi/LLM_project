import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate

#from app.prompts.blog import get_blog_prompt

# Cargar variables de entorno
load_dotenv()

# Inicializar el modelo Groq
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    #model_name="llama3-70b-8192",  # o el modelo que prefieras llama-3.1-8b-instant  llama-3.3-70b-versatile
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)

async def generate_response(data) -> str:
    """
    Genera una respuesta usando Groq a través de LangChain
    """
    prompt_base = data.prompt
    topic = data.topic or "general"
    audience = data.audience or "general audience"
    tone = data.tone or "neutral"
    platform = data.platform or "blog"
    language = data.language or "Spanish"

    # Construir prompt final combinando todos los parámetros
    prompt_final = (
        f"Genera un contenido en {language} sobre el tema '{topic}' adaptado para {audience}.\n"
        f"Tono: {tone}.\n"
        f"Plataforma: {platform}.\n"
        f"Texto base o idea: {prompt_base}\n\n"
        "El contenido debe estar listo para publicar."
    )
    
    try:
        # Crear template de prompt
        chat_template = ChatPromptTemplate.from_messages([
            SystemMessage(content="Eres un asistente útil y amigable especializado en crear contenido."),
            HumanMessage(content=prompt_final)
        ])
        
        # Formatear el prompt
        formatted_prompt = chat_template.format_messages()
        
        # Generar respuesta
        response = await llm.ainvoke(formatted_prompt)
        
        return response.content
        
    except Exception as e:
        raise Exception(f"Error al generar respuesta: {str(e)}")