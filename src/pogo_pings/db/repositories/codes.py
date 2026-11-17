import json

from pogo_pings.db.connection import get_connection
from pogo_pings.discovery.sources.base import PromoCode


class CodeRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def code_exists(self, code: str) -> bool:
        with get_connection(self.db_path) as conn:
            result = conn.execute(
                "SELECT 1 from seen_codes WHERE code = ?",
                (code,),
            ).fetchone()

        return result is not None

    def add_code(
        self,
        code: str,
        rewards: list[str],
        source: str,
        notified_at: str | None = None,
    ) -> bool:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO seen_codes (
                    code,
                    rewards,
                    source,
                    notified_at
                ) VALUES (?, ?, ?, ?)
                """,
                (code, json.dumps(rewards), source, notified_at),
            )

        return cursor.rowcount == 1
