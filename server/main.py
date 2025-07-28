from fastapi import FastAPI
from server.routes import content, agent, yahoo
from loguru import logger
from server.routes.query import router as query_router

app = FastAPI(title="LLM API", version="1.0.0")

# Include routers
app.include_router(content.router)
app.include_router(agent.router)
app.include_router(query_router)
app.include_router(yahoo.router)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "LLM API is running!"}



