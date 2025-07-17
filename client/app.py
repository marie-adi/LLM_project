import gradio as gr
import requests

API_URL = "http://127.0.0.1:8001/generate"

def generate_content(prompt, age_group, platform, region):
    payload = {
        "prompt": prompt,
        "age_group": age_group,
        "platform": platform,
        "region": region
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json().get("output", "No response received.")
    except Exception as e:
        return f"❌ Error: {str(e)}"

with gr.Blocks(css="""
body {
    background-color: #fefefe;
    color: #333;
    font-family: 'Segoe UI', sans-serif;
}
#prompt-box textarea,
#output-box textarea {
    background-color: #fff9ec;
    color: #333;
    font-size: 1rem;
    padding: 1rem;
    border-radius: 1rem;
    border: 1px solid #ccc;
}
#prompt-box textarea::placeholder {
    color: #888;
}
#generate-button {
    background: linear-gradient(to right, #ffe1a0, #ffe9b9);
    color: black;
    font-weight: bold;
    padding: 0.75rem 1.5rem;
    border-radius: 1rem;
    margin-top: 1rem;
    transition: all 0.3s ease-in-out;
}
#generate-button:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
""") as demo:
    
    gr.Markdown("<h2 style='text-align: center;'>🧠💰 AI Finance Content Generator</h2>")

    with gr.Column():
        prompt = gr.Textbox(
            label="What do you want to generate?",
            placeholder="Describe your idea or request...",
            lines=6,
            elem_id="prompt-box"
        )

        with gr.Row():
            age_group = gr.Dropdown(
                label="Age group",
                choices=["08-11", "12-15", "16-19", "20-25", "26-85"],
                value="12-15"
            )
            platform = gr.Dropdown(
                label="Platform",
                choices=["instagram", "twitter", "linkedin"],
                value="instagram"
            )
            region = gr.Dropdown(
                label="Region",
                choices=[
                    ("Spanish (Mexico)", "es_MX"),
                    ("Spanish (Spain)", "es_ES"),
                    ("Spanish (Argentina)", "es_AR"),
                    ("English (United States)", "en_US"),
                    ("English (United Kingdom)", "en_UK"),
                    ("English (Australia)", "en_AU"),
                    ("French (France)", "fr_FR"),   
                    ("Russian (Russia)", "ru_RU"),
                        ],
             value="es_MX"  
                )
        submit_btn = gr.Button("🚀 Generate", elem_id="generate-button")

        output = gr.Textbox(label="Generated text", lines=10, elem_id="output-box")

        submit_btn.click(
            generate_content,
            inputs=[prompt, age_group, platform, region],
            outputs=output
        )

demo.launch()