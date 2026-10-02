from fastapi import FastAPI

app = FastAPI(
    title="Enterprise LLM Chatbot",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}