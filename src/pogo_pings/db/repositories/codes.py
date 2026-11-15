from pogo_pings.db.connection import get_connection


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

    def add_code(self, code: str) -> bool:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO seen_codes (code) VALUES (?)",
                (code,),
            )

        return cursor.rowcount == 1
