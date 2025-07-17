import os                     # To inport paths from the prompt folder
from langdetect import detect # Needed for language detection so the output can be in the same language as the input

# This goes from here to "server" (one folder above where it can look for the "prompt" folder)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def load_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_combined_prompt(user_input, platform, age_range, region=None):
    # 1. This funtion DETECTS the LANGUAGE of the input
    detected_language = detect(user_input)  # es', 'fr', 'ru', 'en', etc

    # 2. The function detects the language based on file names, which match the language codes used by the detector. It supports 4 specific languages; if none match, it defaults to English. 
    #    The language is always given by the input, if wrote in spanish, input_language = es 
    language_prompt_path = os.path.join(BASE_DIR, "prompts", "languages", f"{detected_language}.txt")
    if not os.path.exists(language_prompt_path):
        language_prompt_path = os.path.join(BASE_DIR, "prompts", "languages", "en.txt")

    # 3. Building the paths of the desired platform and age group
    #    In the front there are 2 dropdown buttons for the user to select the platform and age group
    platform_prompt_path = os.path.join(BASE_DIR, "prompts", "platforms", f"{platform}.txt")
    age_prompt_path = os.path.join(BASE_DIR, "prompts", "age_groups", f"{age_range}.txt")

    # 4. Loading the chosen prompts
    language_prompt = load_text(language_prompt_path)
    platform_prompt = load_text(platform_prompt_path)
    age_prompt = load_text(age_prompt_path)

    # 5. Mistral will always answer in the language input
    #    If the language of the input is in our cutomized prompts per languages, it will answer in that manner, otherwise will answer in for example japanese but with the styled prompt in english
    #    Also, there will be a new "region" button in the front so it can detect the variety of Spanish so it can answer in mexican, spanish, colombian, etc style. 
    #    and the same for English (UK style, American style, etc)
    if detected_language == "es" and region:
        response_instruction = f"\n\nRespond in Spanish adapted to the linguistic style of {region}."
    elif detected_language == "en" and region:
        response_instruction = f"\n\nRespond in English adapted to the linguistic style of {region}."
    else:
        response_instruction = f"\n\nRespond in {detected_language}. Adapt tone and cultural references accordingly."
    # 6. Combining prompts
    full_prompt = f"{language_prompt}\n\n{platform_prompt}\n\n{age_prompt}{response_instruction}"

    return full_prompt



  