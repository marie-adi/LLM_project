import os
from langdetect import detect
from loguru import logger

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROMPT_DIR = os.path.join(BASE_DIR, "prompts")

class PromptBuilder:
    def __init__(self):
        self.region_map = self._load_region_map()

    def _load_region_map(self):
        return {
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
            "Spanish (Argentina)":      "es_ar",
            "Spanish (Bolivia)":        "es_bo",
            "Spanish (Chile)":          "es_cl",
            "Spanish (Colombia)":       "es_co",
            "Spanish (Cuba)":           "es_cu",
            "Spanish (Ecuador)":        "es_ec",
            "Spanish (Spain)":          "es_es",
            "Spanish (Mexico)":         "es_mx",
            "Spanish (Peru)":           "es_pe",
            "Spanish (Uruguay)":        "es_uy",
            "Spanish (Veneuela)":       "es_ve",
            "French (Belgium)":         "fr_be",
            "French (Canada)":          "fr_ca",
            "French (Switzerland)":     "fr_ch",
            "French (Ivory Coast)":     "fr_ci",
            "French (Cameroon)":        "fr_cm",
            "French (Algeria)":         "fr_dz",
            "French (France)":          "fr_fr",
            "French (Morocco)":         "fr_ma",
            "French (Senegal)":         "fr_sn",
            "French (Tunisia)":         "fr_tn",
            "Other": "default"
        }

    def normalize_region(self, region_label: str) -> str:
        return self.region_map.get(region_label, "default")

    def _load_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to load prompt file: {path} | {e}")
            return ""

    def build_prompt(self, user_input: str, platform: str, age_range: str, region: str = None) -> str:
        # Step 1: Detect language with enhanced reliability
        try:
            language = detect(user_input)
            # Validate against supported languages
            supported_languages = ["en", "es", "fr"]  # Add others as needed
            if language not in supported_languages:
                language = "en"  # Default to English for unsupported languages
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            language = "en"
        
        logger.info(f"Detected language: {language}")

        # Step 2: Normalize region but only use it if compatible with detected language
        normalized_region = self.normalize_region(region) if region else None
        region_language = normalized_region.split('_')[0] if normalized_region and '_' in normalized_region else None
        
        # Step 3: Determine if we should use regional adaptation
        use_regional_adaptation = (
            region_language and 
            region_language == language and
            language in ["en", "es", "fr"]  # Only for languages we have regional variants for
        )
        
        # Step 4: Build paths
        paths = {
            "base": os.path.join(PROMPT_DIR, "base.txt"),
            "language": os.path.join(PROMPT_DIR, "languages", f"{language}.txt"),
            "platform": os.path.join(PROMPT_DIR, "platforms", f"{platform}.txt"),
            "age": os.path.join(PROMPT_DIR, "age_groups", f"{age_range}.txt"),
            "dialect": os.path.join(PROMPT_DIR, "dialects", 
                                f"{normalized_region}.txt" if use_regional_adaptation else "default.txt")
        }

        # Ensure language file exists
        if not os.path.exists(paths["language"]):
            logger.warning(f"Language file not found for {language}, falling back to English")
            paths["language"] = os.path.join(PROMPT_DIR, "languages", "en.txt")

        # Load components
        components = {key: self._load_file(path) for key, path in paths.items()}

        # Step 5: Build response instruction
        if use_regional_adaptation:
            response_instruction = (
                f"\n\nRespond in {language}, adapting your response to the linguistic style of {region}. "
                f"Maintain all regional expressions and vocabulary appropriate for {region}."
            )
        else:
            response_instruction = (
                f"\n\nRespond in {language}. "
                f"Do not use regional adaptations as the input language doesn't match the selected region."
            )
        
        # Special case for unsupported languages
        if language not in supported_languages:
            response_instruction += (
                "\n\nNote: The user's language isn't fully supported. "
                "Keep the response simple and easy to understand."
            )

        return (
            f"{components['base']}\n\n"
            f"{components['language']}\n\n"
            f"{components['dialect']}\n\n"
            f"{components['platform']}\n\n"
            f"{components['age']}\n\n"
            f"{response_instruction}"
        )