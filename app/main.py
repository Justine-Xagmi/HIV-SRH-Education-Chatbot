
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.languages import router as languages_router
from app.api.chat import router as chat_router
from app.core.config import APP_NAME


STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title=APP_NAME,
    description="An educational HIV and sexual and reproductive health information service.",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
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
def root(request: Request):
    """Serve the web interface to browsers and JSON to API clients."""

    accept_header = request.headers.get("accept", "")

    if "text/html" in accept_header:
        return FileResponse(STATIC_DIR / "index.html")

    return {
        "message": "HIV/SRH Education Chatbot API is running.",
        "docs": "/docs",
    }
