import sqlite3
from contextlib import contextmanager


@contextmanager
def get_connection(db_path: str):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
    finally:
        connection.close()
