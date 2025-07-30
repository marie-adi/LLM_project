# Código de Polina
import json
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from server.services.prompt_builder import get_combined_prompt
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()


# Instancias de LLMs disponibles
llm_llama = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)
# Puedes agregar aquí otro modelo, por ejemplo "gpt-3.5-turbo" (ajusta el nombre según disponibilidad en Groq)
llm_turbo = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)

def generar_post(input: str) -> str:
    # Manejo seguro de JSON
    print("[DEBUG]: ######### INTENTO POST  ###########")
    try:
        print(f"[DEBUG]: DATA received for post generation : {json.loads(input)}")
        data = json.loads(input)
    except json.JSONDecodeError:
        # Si falla el parsing de JSON, usar el input como prompt
        print("[DEBUG]: Input is not valid JSON, using as prompt")
        data = {"prompt": input}
    

    prompt = data.get("prompt")
    platform = data.get("platform", "twitter")
    age_range = data.get("audience", "20-25")
    region = data.get("region", "Spain")
    model = data.get("model", "turbo")  # Por defecto llama

    if not prompt:
        return "❌ Error: Prompt is required."

    prompt_final = get_combined_prompt(prompt, platform, age_range, region)
    prompt_final += f"\n\nIdea base: {prompt}"

    chat_template = ChatPromptTemplate.from_messages([
        SystemMessage(content="Eres un asistente útil y amigable especializado en crear contenido."),
        HumanMessage(content=prompt_final)
    ])

    formatted_prompt = chat_template.format_messages()

    # Selección del modelo
    if model == "turbo":
        llm_selected = llm_turbo # versatil
    else:
        llm_selected = llm_llama # instant
        
    print(f"[DEBUG] Loading llm model: {model}")

    response = llm_selected.invoke(formatted_prompt)
    return response.content
