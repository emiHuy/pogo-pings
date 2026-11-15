def test_code_does_not_exist(repository):
    assert repository.code_exists("POKEMON123") is False


def test_add_code(repository):
    assert repository.add_code("POKEMON123") is True
    assert repository.code_exists("POKEMON123") is True


def test_duplicate_code_is_not_inserted(repository):
    assert repository.add_code("POKEMON123") is True
    assert repository.add_code("POKEMON123") is False
