def code_exists(conn, code):
    result = conn.execute(
        "SELECT 1 from seen_codes WHERE code = ?",
        (code,),
    ).fetchone()

    return result is not None


def add_code(conn, code):
    cursor = conn.execute(
        "INSERT OR IGNORE INTO seen_codes (code) VALUES (?)",
        (code,),
    )

    return cursor.rowcount == 1
