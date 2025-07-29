from fastapi import FastAPI
from server.routes import basic_content, agent,image
from loguru import logger
from server.routes.query_rag import router as query_router

app = FastAPI(title="LLM API", version="1.0.0")

# These are all in server/routes folder
app.include_router(basic_content.router)
app.include_router(agent.router)
app.include_router(query_router) # This is the RAG so it goes to arxiv search and retrieve info for chorma db
app.include_router(image.router) 

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "LLM API is running!"}


from server.routes.yahoo import router as yahoo_router
app.include_router(yahoo_router)



