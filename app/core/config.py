
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load local settings when .env exists.
# Otherwise, use safe development defaults.
load_dotenv(PROJECT_ROOT / ".env")

APP_NAME = os.getenv(
    "APP_NAME",
    "HIV_SRH_Education_Chatbot",
)

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()

APP_DEBUG = os.getenv("APP_DEBUG", "false").strip().lower() == "true"

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en").strip().lower()

SUPPORTED_LANGUAGES = [
    language.strip().lower()
    for language in os.getenv("SUPPORTED_LANGUAGES", "en,sw").split(",")
    if language.strip()
]

# Optional for now so the existing in-memory application
# and tests continue to work before database integration.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip() or None

if not SUPPORTED_LANGUAGES:
    raise ValueError("At least one supported language must be configured.")

if DEFAULT_LANGUAGE not in SUPPORTED_LANGUAGES:
    raise ValueError(
        "DEFAULT_LANGUAGE must be included in SUPPORTED_LANGUAGES."
    )

if APP_ENV not in {"development", "testing", "production"}:
    raise ValueError(
        "APP_ENV must be development, testing, or production."
    )
