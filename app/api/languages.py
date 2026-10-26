
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1",
    tags=["Languages"],
)


@router.get("/languages")
def get_supported_languages():
    """Return the languages supported by the chatbot."""
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "sw", "name": "Kiswahili"},
        ]
    }
