from pathlib import Path

from pogo_pings.db.connection import get_connection

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def initialize_database(db_path):
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection(db_path) as conn:
        conn.executescript(schema)
