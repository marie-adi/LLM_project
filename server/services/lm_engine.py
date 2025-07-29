import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger
from enum import Enum

load_dotenv()

class GroqModel(str, Enum):
    """Supported Groq models (no max_tokens)"""
    LLAMA3_8B = "llama-3.1-8b-instant"     # This is faster
    LLAMA3_70B = "llama-3.3-70b-versatile" # This is a large one
    GEMMA_9B = "gemma2-9b-it"              # This is the more basic one

class LMEngine:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """
        Initialize with either:
        - String model name ("llama-3.1-8b-instant")
        - Or GroqModel enum value (GroqModel.LLAMA3_8B)
        """
        # Convert enum to string if needed
        if isinstance(model_name, GroqModel):
            model_name = model_name.value
            
        # Validate model name
        valid_models = [m.value for m in GroqModel]
        if model_name not in valid_models:
            raise ValueError(f"Invalid model. Available: {valid_models}")

        self.model_name = model_name
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,  # Use string directly
            temperature=0.7
        )
        logger.info(f"LM Engine initialized with model: {model_name}")

    async def ask(self, prompt: str) -> str:
        """Generate response from LLM"""
        try:
            messages = [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content=prompt)
            ]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return "Failed to generate response."