import json
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from server.services.prompt_builder import get_combined_prompt
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)

def generar_post(input: str) -> str:
    # Manejo seguro de JSON
    try:
        # Verificar si el input parece un JSON válido
        if isinstance(input, str) and input.strip() and input.strip().startswith("{"):
            data = json.loads(input)
        else:
            # Si no es JSON, tratar el input completo como prompt
            data = {"prompt": input}
    except json.JSONDecodeError:
        # Si falla el parsing de JSON, usar el input como prompt
        data = {"prompt": input}
    
    prompt = data.get("prompt")
    platform = data.get("platform", "twitter")
    age_range = data.get("audience", "20-25")
    region = data.get("region", "Spain")

    if not prompt:
        return "❌ Error: Prompt is required."

    prompt_final = get_combined_prompt(prompt, platform, age_range, region)
    prompt_final += f"\n\nIdea base: {prompt}"

    chat_template = ChatPromptTemplate.from_messages([
        SystemMessage(content="Eres un asistente útil y amigable especializado en crear contenido."),
        HumanMessage(content=prompt_final)
    ])

    formatted_prompt = chat_template.format_messages()
    response = llm.invoke(formatted_prompt)
    return response.content
