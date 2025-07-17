import gradio as gr
import requests

API_URL = "http://127.0.0.1:8001/generate"

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
        return f"❌ Error: {str(e)}"

with gr.Blocks(css="""
#prompt-box textarea {
    font-size: 1rem;
    padding: 1rem;
    border-radius: 1rem;
    background-color: #1e1e1e;
}
#output-box textarea {
    font-size: 1rem;
    padding: 1rem;
    border-radius: 1rem;
    background-color: #111;
    color: #f1f1f1;
}
#generate-button {
    background: linear-gradient(to right, #0d6efd, #6610f2);
    color: white;
    font-weight: bold;
    padding: 0.75rem 1.5rem;
    border-radius: 1rem;
    margin-top: 1rem;
}
""") as demo:

    gr.Markdown("## 🧠 Generador de Contenido AI")

    with gr.Column():
        prompt = gr.Textbox(
            label="¿Qué quieres generar?",
            placeholder="Escribe tu idea aquí...",
            lines=6,
            elem_id="prompt-box"
        )

        with gr.Row():
            audience = gr.Dropdown(
                label="Audiencia", choices=["gen z", "millenials", "estudiantes", "profesionales", "niños", "público general"], value="niños"
            )
            tone = gr.Dropdown(
                label="Tono", choices=["formal", "informal", "amigable", "técnico", "divertido"], value="amigable"
            )
            platform = gr.Dropdown(
                label="Plataforma", choices=["blog", "instagram", "linkedin", "x", "tiktok"], value="tiktok"
            )
            language = gr.Dropdown(
                label="Idioma", choices=["español", "inglés", "francés", "alemán"], value="español"
            )

        btn = gr.Button("🚀 Generar Contenido", elem_id="generate-button")

        output = gr.Textbox(label="Resultado", lines=10, elem_id="output-box")

        btn.click(
            generar_contenido,
            inputs=[prompt, audience, tone, platform, language],
            outputs=output
        )

demo.launch()
