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
        language = detect(user_input)
        logger.info(f"Detected input language: {language}")

        paths = {
            "base": os.path.join(PROMPT_DIR, "base.txt"),
            "language": os.path.join(PROMPT_DIR, "languages", f"{language}.txt"),
            "platform": os.path.join(PROMPT_DIR, "platforms", f"{platform}.txt"),
            "age": os.path.join(PROMPT_DIR, "age_groups", f"{age_range}.txt"),
            "dialect": os.path.join(PROMPT_DIR, "dialects", f"{self.normalize_region(region)}.txt")
        }

        if not os.path.exists(paths["language"]):
            paths["language"] = os.path.join(PROMPT_DIR, "languages", "en.txt")

        logger.debug(f"Prompt templates: {paths}")

        # Load individual prompt components
        base = self._load_file(paths["base"])
        language_block = self._load_file(paths["language"])
        dialect = self._load_file(paths["dialect"])
        platform_block = self._load_file(paths["platform"])
        age_block = self._load_file(paths["age"])

        # Compose response instruction
        if language in ["es", "en", "fr"] and region:
            response_instruction = f"\n\nRespond in {language} adapted to the linguistic style of {region}."
        else:
            response_instruction = f"\n\nRespond in {language}. Adapt tone and cultural references accordingly."

        return f"{base}\n\n{language_block}\n\n{dialect}\n\n{platform_block}\n\n{age_block}{response_instruction}"
