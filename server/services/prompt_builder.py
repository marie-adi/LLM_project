import os                       # To import paths from the prompt folder
from langdetect import detect   # Needed for language detection so the output can be in the same language as the input

# This goes from here to "server" (one folder above where it can look for the "prompt" folder)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def load_text(path):
    """Reads and returns the content of a text file."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def normalize_region(region_label):
    """
    Converts region dropdown label into standardized dialect code.
    Example:
        "Spanish (Mexico)" -> "es_mx"
        "English (United Kingdom)" -> "en_uk"
    """
    region_map = {
        # English dialects
        "English (Australia)":      "en_au",
        "English (Canada)":         "en_ca",
        "English (Ireland)":        "en_ie",
        "English (India)":          "en_in",
        "English (Kenya)":          "en_ke",
        "English (Nigeria)":        "en_ng",
        "English (New Zeland)":     "en_nz",
        "English (Pakistani)":      "en_pk",
        "English (United Kingdom)": "en_uk",
        "English (United States)":  "en_us",
        "English (South Africa)":   "en_za",

        # Spanish dialects
        "Spanish (Argentina)":      "es_ar",
        "Spanish (Bolivia)":        "es_bo",
        "Spanish (Chile)":      "es_cl",
        "Spanish (Colombia)":   "es_co",
        "Spanish (Cuba)":       "es_cu",
        "Spanish (Ecuador)":    "es_ec",
        "Spanish (Spain)":      "es_es",
        "Spanish (Mexico)":     "es_mx",
        "Spanish (Peru)":       "es_pe",
        "Spanish (Uruguay)":    "es_uy",
        "Spanish (Veneuela)":   "es_ve",

        # French dialects
        "French (Belgium)":     "fr_be",
        "French (Canada)":      "fr_ca",
        "French (Switzerland)": "fr_ch",
        "French (Ivory Coast)": "fr_ci",
        "French (Cameroon)":    "fr_cm",
        "French (Algeria)":     "fr_dz",
        "French (France)":      "fr_fr",
        "French (Morocco)":     "fr_ma",
        "French (Senegal)":     "fr_sn",
        "French (Tunisia)":     "fr_tn",

        # Fallback dialect
        "Other": "default"
    }

    return region_map.get(region_label, None)  # Returns None if not found

def get_combined_prompt(user_input, platform, age_range, region=None):
    """
    Builds a full prompt by combining:
    - base.txt: defines the system's personality and strategic depth
    - language.txt: adapts tone, idioms, and cultural references
    - dialect.txt: if available, adds regional flavor
    - platform.txt: adapts formatting and style to Instagram, LinkedIn, or X
    - age_group.txt: adapts educational depth and emotional tone
    - response_instruction: sets the output language and regional style
    """

    # 1. Detect language of user input
    detected_language = detect(user_input)  # Example: 'es', 'fr', 'en'

    # 2. Paths for static prompt modules
    base_prompt_path      = os.path.join(BASE_DIR, "prompts", "base.txt")
    language_prompt_path  = os.path.join(BASE_DIR, "prompts", "languages", f"{detected_language}.txt")
    platform_prompt_path  = os.path.join(BASE_DIR, "prompts", "platforms", f"{platform}.txt")
    age_prompt_path       = os.path.join(BASE_DIR, "prompts", "age_groups", f"{age_range}.txt")

    # 3. Fallback to English if language-specific file doesn't exist
    if not os.path.exists(language_prompt_path):
        language_prompt_path = os.path.join(BASE_DIR, "prompts", "languages", "en.txt")

    # 4. Load all core prompts
    base_prompt     = load_text(base_prompt_path)
    language_prompt = load_text(language_prompt_path)
    platform_prompt = load_text(platform_prompt_path)
    age_prompt      = load_text(age_prompt_path)

    # 5. Load dialect prompt if region is provided and mapped
    normalized_dialect_code = normalize_region(region) if region else None

    if normalized_dialect_code:
        dialect_prompt_path = os.path.join(BASE_DIR, "prompts", "dialects", f"{normalized_dialect_code}.txt")
    else:
        dialect_prompt_path = os.path.join(BASE_DIR, "prompts", "dialects", "default.txt") # This is the fallback

    dialect_prompt = load_text(dialect_prompt_path) if os.path.exists(dialect_prompt_path) else ""


    # 6. Response instruction: sets expected output tone/language
    if detected_language in ["es", "en", "fr"] and region:
        response_instruction = f"\n\nRespond in {detected_language} adapted to the linguistic style of {region}."
    else:
        response_instruction = f"\n\nRespond in {detected_language}. Adapt tone and cultural references accordingly."

    # 7. Combine everything in proper order
    full_prompt = (
        f"{base_prompt}\n\n"
        f"{language_prompt}\n\n"
        f"{dialect_prompt}\n\n"
        f"{platform_prompt}\n\n"
        f"{age_prompt}"
        f"{response_instruction}"
    )

    return full_prompt
