import sqlite3

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
