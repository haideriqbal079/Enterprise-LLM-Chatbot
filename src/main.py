from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.chat import router as chat_router


app = FastAPI(
    title="Enterprise LLM Chatbot",
    version="0.1.0",
)


app.include_router(chat_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Prometheus monitoring
Instrumentator().instrument(app).expose(app)