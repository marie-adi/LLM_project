from services.prompt_builder import get_combined_prompt

# Testing----------------------------------------------------------------
user_input = "Comment développer son intelligence émotionnelle ?"    #   |
platform = "instagram"                                               #   |
age_range = "20-25"                                                  #   |
# -----------------------------------------------------------------------

prompt_fro_mistral = get_combined_prompt(user_input, platform, age_range)
# POLINA!!!! este es el prompt que debe de recibir mistral al que llamamos con la API de groq. En la caja hay un ejemplo tipo 
