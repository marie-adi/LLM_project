import gradio as gr
import requests

API_URL = "http://127.0.0.1:8001/generate"  # Asegúrate que coincida con tu puerto backend

def generar_contenido(prompt, audience, tone, platform, language):
    payload = {
        "prompt": prompt,
        "audience": audience,
        "tone": tone,
        "platform": platform,
        "language": language
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json().get("output", "Sin respuesta")
    except Exception as e:
        return f"Error: {str(e)}"

with gr.Blocks(title="Generador de Contenido AI con FastAPI + Groq") as demo:
    gr.Markdown("## Generador de Contenido AI con FastAPI + Groq")

    prompt = gr.Textbox(label="Prompt base", placeholder="Escribe tu idea o tema aquí...", lines=2)

    with gr.Row():
        audience = gr.Dropdown(label="Audiencia", choices=["estudiantes", "profesionales", "niños", "público general"])
        tone = gr.Dropdown(label="Tono", choices=["formal", "informal", "amigable", "técnico", "divertido"])

    with gr.Row():
        platform = gr.Dropdown(label="Plataforma", choices=["blog", "instagram", "linkedin", "twitter", "tiktok"])
        language = gr.Dropdown(label="Idioma", choices=["español", "inglés", "francés", "alemán"])

    btn = gr.Button("Generar Contenido")
    output = gr.Textbox(label="Resultado", lines=10)

    btn.click(
        generar_contenido,
        inputs=[prompt, audience, tone, platform, language],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch()
