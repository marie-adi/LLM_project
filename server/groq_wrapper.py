import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from .services.prompt_builder import get_combined_prompt



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
    user_input = data.prompt
    platform = data.platform or "twitter"
    age_range = data.audience or "20-25"
    region = data.region or "Spain"

    prompt_final = get_combined_prompt(
        user_input=user_input,
        platform=platform,
        age_range=age_range,
        region=region
    )

    # Añadimos la idea base al final, como nota creativa
    prompt_final += f"\n\nIdea base: {user_input}"

    
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