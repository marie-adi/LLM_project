from langchain.agents import initialize_agent, AgentType, Tool
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from server.services.prompt_builder import get_combined_prompt
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)


def generar_post(data: dict) -> str:
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

# Definir herramientas
tools = [
    Tool.from_function(
        func=lambda prompt: generar_post,
        name="GeneradorDeContenido",
        description="Genera contenido escrito para redes sociales."
    )
]

# Inicializar agente
marketing_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
# def generate_response(data):
#     try:
#         response = marketing_agent.invoke({
#             "prompt": data.prompt,
#             "platform": data.platform or "blog",
#             "age_range": data.age_group or "20-25",
#             "region": data.region or "Spain"
#         })
#         return response
#     except Exception as e:
#         raise ValueError(f"Error generating response: {str(e)}")