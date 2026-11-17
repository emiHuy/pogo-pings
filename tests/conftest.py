from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from pogo_pings.db.connection import get_connection
from pogo_pings.db.repositories.codes import CodeRepository
from pogo_pings.discovery.sources.base import PromoCode
from pogo_pings.services.deduplicator import Deduplicator


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


@pytest.fixture
def promo_code():
    return PromoCode(
        code="EXAMPLE-CODE",
        rewards=["Example reward"],
        source="example.com",
    )


@pytest.fixture
def repository(tmp_path):
    db_path = str(tmp_path / "test.db")

    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE seen_codes (
                code TEXT PRIMARY KEY,
                rewards TEXT NOT NULL,
                source TEXT NOT NULL,
                notified_at TEXT
            )
        """)

    return CodeRepository(db_path)


@pytest.fixture
def mock_repository():
    return MagicMock(spec=CodeRepository)


@pytest.fixture
def notifier():
    return MagicMock(send=AsyncMock())


@pytest.fixture
def deduplicator(mock_repository, notifier):
    return Deduplicator(mock_repository, notifier)
