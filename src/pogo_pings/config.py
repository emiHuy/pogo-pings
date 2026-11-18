import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


def get_int(name: str, default: int, min: int) -> int:
    value = os.getenv(name, str(default))

    try:
        parsed = int(value)
    except ValueError:
        raise ValueError(f"{name} must be an integer, got: {value!r}")

    if parsed < min:
        raise ValueError(f"{name} must be at least {min}")

    return parsed


def get_float(name: str, default: float, min: float) -> float:
    value = os.getenv(name, str(default))

    try:
        parsed = float(value)
    except ValueError:
        raise ValueError(f"{name} must be a number, got: {value!r}")

    if not 0 < parsed or parsed < min:
        raise ValueError(f"{name} must be greater than or equal to {min}")

    return parsed


@dataclass(frozen=True)
class Config:
    app_env: str
    log_level: str
    webhook_url: str
    poll_interval: int
    http_timeout: float
    max_retries: int
    database_path: Path


def load_config() -> Config:
    app_env = os.getenv("APP_ENV", "development").lower()
    if app_env not in {"development", "testing", "production"}:
        raise ValueError(f"Invalid APP_ENV: {app_env}")

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(f"Invalid LOG_LEVEL: {log_level}")

    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("WEBHOOK_URL is missing from environment variables")
    parsed_url = urlparse(webhook_url)
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError("WEBHOOK_URL must be a valid HTTPS URL")

    return Config(
        app_env=app_env,
        log_level=log_level,
        webhook_url=webhook_url,
        poll_interval=get_int("POLL_INTERVAL", 300, 1),
        http_timeout=get_float("HTTP_TIMEOUT", 10.0, 0.1),
        max_retries=get_int("MAX_RETRIES", 3, 0),
        database_path=Path(os.getenv("DATABASE_PATH", "data/pogo_pings.db")),
    )
