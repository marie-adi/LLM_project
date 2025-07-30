from fastapi import FastAPI
from server.routes import basic_content, agent,image, yahoo, simple_rag_chroma
from loguru import logger
from server.routes.query_rag import router as query_router


app = FastAPI(title="LLM API", version="1.0.0")

# These are all in server/routes folder
app.include_router(basic_content.router)
app.include_router(agent.router)
app.include_router(query_router)            # This is the RAG so it goes to arxiv search and retrieve info for chorma database
app.include_router(image.router) 
app.include_router(yahoo.router) 
app.include_router(simple_rag_chroma.router) # This is the simple rag that goes to the already existent info in chroma database

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "LLM API is running!"}


from server.routes.yahoo import router as yahoo_router
app.include_router(yahoo_router)



