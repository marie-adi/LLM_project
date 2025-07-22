from services.prompt_builder import get_combined_prompt

# Testing----------------------------------------------------------------
user_input = "Comment développer son intelligence émotionnelle ?"    #   |
platform = "instagram"                                               #   |
age_range = "20-25"                                                  #   |
region = "UK"                                                        #   |
# -----------------------------------------------------------------------

prompt = get_combined_prompt(user_input, platform, age_range, region)
# POLINA!!!! este es el prompt que debe de recibir mistral al que llamamos con la API de groq. En la caja hay un ejemplo tipo 
