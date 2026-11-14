import os

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if APP_ENV == "dev":
    print("Running in development mode")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is missing from environment variables")
