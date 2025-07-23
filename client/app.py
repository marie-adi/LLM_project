import gradio as gr
import requests

API_ENDPOINTS = {
    "General": "http://127.0.0.1:8001/generate",
    "Marketing": "http://127.0.0.1:8001/agent/marketing",
    "Finanzas": "http://127.0.0.1:8001/agent/finance"
}

# Función que retorna formato completo para ChatInterface y copia
def chat_wrapper(message, history, model, audience, platform, region):
    payload = {
        "prompt": message,
        "audience": audience,
        "platform": platform,
        "region": region
    }
    try:
        response = requests.post(API_ENDPOINTS[model], json=payload)
        response.raise_for_status()
        output = response.json().get("output", "No response received.")
    except Exception as e:
        output = f"❌ Error: {str(e)}"

    # ✅ Devuelve mensaje como lista de tipo "messages"
    return [{"role": "assistant", "content": output}], gr.update(value=output, visible=True)

with gr.Blocks(css="""
#header {
    text-align: center;
    color: #1e40af;
    font-size: 2rem;
    font-weight: bold;
    margin: 1rem;
}
#chatbox .message.user {
    background-color: #e0f2fe;
    color: #1e40af;
}
#chatbox .message.bot {
    background-color: #F2F2F2;
    color: #1e40af;
}

""") as demo:

    # Título
    gr.Markdown("<div id='header'>🤖 FinancIA — Asistente de Contenido Financiero</div>")

    # Selector de modelo
    model_selector = gr.Dropdown(
        choices=["General", "Marketing", "Finanzas"],
        value="General",
        label="Modelo"
    )

    # Ajustes toggle
    show_settings = gr.State(value=False)
    toggle_btn = gr.Button("⚙️ Ajustes")

    with gr.Column(visible=False) as config_panel:
        audience = gr.Dropdown(
            label="Grupo de edad",
            choices=["08-11", "12-15", "16-19", "20-25", "26-85"],
            value="20-25"
        )
        platform = gr.Dropdown(
            label="Plataforma",
            choices=["instagram", "twitter", "linkedin"],
            value="instagram"
        )
        region = gr.Dropdown(
                label="Region",
                choices=[
                    # English
                    "English (Australia)",
                    "English (Canada)",
                    "English (Ireland)",
                    "English (India)",
                    "English (Kenya)",
                    "English (Nigeria)",
                    "English (New Zealand)",
                    "English (Pakistani)",
                    "English (United Kingdom)",
                    "English (United States)",
                    "English (South Africa)",

                    # Spanish
                    "Spanish (Argentina)",
                    "Spanish (Bolivia)",
                    "Spanish (Chile)",
                    "Spanish (Colombia)",
                    "Spanish (Cuba)",
                    "Spanish (Ecuador)",
                    "Spanish (Spain)",
                    "Spanish (Mexico)",
                    "Spanish (Peru)",
                    "Spanish (Uruguay)",
                    "Spanish (Venezuela)",

                    # French
                    "French (Belgium)",
                    "French (Canada)",
                    "French (Switzerland)",
                    "French (Ivory Coast)",
                    "French (Cameroon)",
                    "French (Algeria)",
                    "French (France)",
                    "French (Morocco)",
                    "French (Senegal)",
                    "French (Tunisia)",

                    # Fallback
                    "Other"
             ],
        value="Spanish (Mexico)"
        )

    # Campo copiable, oculto hasta que haya respuesta
    output_text = gr.Textbox(
        label="Haz clic para copiar la respuesta ✂️",
        visible=False,
        interactive=False,
        lines=6,
        show_copy_button=True
    )

    # Chat Interface con output completo y botón de copiar
    chatbot = gr.ChatInterface(
        fn=chat_wrapper,
        chatbot=gr.Chatbot(elem_id="chatbox", type="messages"),
        type="messages",
        textbox=gr.Textbox(placeholder="¿Qué contenido necesitas hoy?", scale=9),
        additional_inputs=[model_selector, audience, platform, region],
        additional_outputs=[output_text],
        title="",
    )

    # Toggle de ajustes
    def toggle_settings(current):
        return not current, gr.update(visible=not current)

    toggle_btn.click(
        fn=toggle_settings,
        inputs=show_settings,
        outputs=[show_settings, config_panel]
    )

demo.launch()
