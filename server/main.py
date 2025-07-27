from fastapi import FastAPI
from server.routes import content, agent
from loguru import logger

app = FastAPI(title="LLM API", version="1.0.0")

# Include routers
app.include_router(content.router)
app.include_router(agent.router)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "LLM API is running!"}
