import sqlite3

import httpx
import pytest


@pytest.fixture
def connection():
    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE seen_codes (
            code TEXT PRIMARY KEY,
            first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    yield connection

    connection.close()


@pytest.fixture
def mock_http(monkeypatch):
    def mock(module, handler):
        original_client = httpx.AsyncClient

        def create_client(**kwargs):
            return original_client(
                transport=httpx.MockTransport(handler),
                **kwargs,
            )

        monkeypatch.setattr(module.httpx, "AsyncClient", create_client)

    return mock
