import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

APP_DATABASE_PATH = os.getenv("APP_DATABASE_PATH", str(BASE_DIR / "health_predictions.db"))
AI_PROVIDER = os.getenv("AI_PROVIDER", "openrouter").strip().lower()
AI_API_KEY = os.getenv("AI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
AI_API_BASE_URL = os.getenv(
    "AI_API_BASE_URL",
    "https://openrouter.ai/api/v1/chat/completions",
)


def get_database_path() -> str:
    """Return the SQLite database path for the app."""
    path = Path(APP_DATABASE_PATH)
    if not path.is_absolute():
        path = BASE_DIR / path
    return str(path)
