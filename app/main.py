
from fastapi import FastAPI

from app.api.languages import router as languages_router
from app.api.chat import router as chat_router
from app.core.config import APP_NAME

app = FastAPI(
    title=APP_NAME,
    description="An educational HIV and sexual and reproductive health information service.",
    version="0.1.0",
)

app.include_router(languages_router)
app.include_router(chat_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Return a basic service health status."""
    return {
        "status": "ok",
        "application": APP_NAME,
    }


@app.get("/", tags=["General"])
def root():
    """Return basic API information."""
    return {
        "message": "HIV/SRH Education Chatbot API is running.",
        "docs": "/docs",
    }
