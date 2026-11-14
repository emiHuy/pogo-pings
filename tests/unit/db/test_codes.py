from pogo_pings.db.repositories.codes import add_code, code_exists


def test_code_does_not_exist(connection):
    assert code_exists(connection, "POKEMON123") is False


def test_add_code(connection):
    assert add_code(connection, "POKEMON123") is True
    assert code_exists(connection, "POKEMON123") is True


def test_duplicate_code_is_not_inserted(connection):
    assert add_code(connection, "POKEMON123") is True
    assert add_code(connection, "POKEMON123") is False
