import os                       # To import paths from the prompt folder
from langdetect import detect   # Needed for language detection so the output can be in the same language as the input

# This goes from here to "server" (one folder above where it can look for the "prompt" folder)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def load_text(path):
    """Reads and returns the content of a text file."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_combined_prompt(user_input, platform, age_range, region=None):
    """
    Builds a full prompt by combining:
    - base.txt: defines the system's personality and strategic depth
    - language.txt: adapts tone, idioms, and cultural references
    - platform.txt: adapts formatting and style to Instagram, LinkedIn, or X
    - age_group.txt: adapts educational depth and emotional tone
    - response_instruction: sets the output language and regional style
    """

    # 1. This function DETECTS the LANGUAGE of the input
    detected_language = detect(user_input)  # 'es', 'fr', 'ru', 'en', etc.

    # 2. The function detects the language based on file names, which match the language codes used by the detector.
    #    It supports specific languages; if none match, it defaults to English.
    #    The language is always given by the input; if written in Spanish, input_language = 'es'
    language_prompt_path = os.path.join(BASE_DIR, "prompts", "languages", f"{detected_language}.txt")
    if not os.path.exists(language_prompt_path):
        language_prompt_path = os.path.join(BASE_DIR, "prompts", "languages", "en.txt")

    # 3. Building the paths of the desired platform and age group
    #    In the front there are 2 dropdown buttons for the user to select the platform and age group
    base_prompt_path = os.path.join(BASE_DIR, "prompts", "base.txt")
    platform_prompt_path = os.path.join(BASE_DIR, "prompts", "platforms", f"{platform}.txt")
    age_prompt_path = os.path.join(BASE_DIR, "prompts", "age_group", f"{age_range}.txt")

    # 4. Loading the chosen prompts
    base_prompt = load_text(base_prompt_path)
    language_prompt = load_text(language_prompt_path)
    platform_prompt = load_text(platform_prompt_path)
    age_prompt = load_text(age_prompt_path)

    # 5. Mistral will always answer in the language of the input.
    #    If the language of the input is in our customized prompts per language, it will answer in that manner.
    #    Otherwise, it will answer in the detected language (e.g., Japanese) but with the styled prompt in English.
    #    Also, there will be a new "region" button in the front so it can detect the variety of Spanish (Mexican, Castilian, Colombian, etc.)
    #    and the same for English (UK style, American style, etc.)
    if detected_language == "es" and region:
        response_instruction = f"\n\nRespond in Spanish adapted to the linguistic style of {region}."
    elif detected_language == "en" and region:
        response_instruction = f"\n\nRespond in English adapted to the linguistic style of {region}."
    else:
        response_instruction = f"\n\nRespond in {detected_language}. Adapt tone and cultural references accordingly."

    # 6. Combining prompts in the correct order
    full_prompt = (
        f"{base_prompt}\n\n"
        f"{language_prompt}\n\n"
        f"{platform_prompt}\n\n"
        f"{age_prompt}"
        f"{response_instruction}"
    )

    return full_prompt
