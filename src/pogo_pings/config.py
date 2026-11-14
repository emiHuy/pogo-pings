import os

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    raise ValueError(f"Invalid LOG_LEVEL: {LOG_LEVEL}")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is missing from environment variables")
