import pytest

from pogo_pings.db.connection import get_connection
from pogo_pings.db.repositories.codes import CodeRepository
from pogo_pings.services.deduplicator import Deduplicator


@pytest.mark.asyncio
async def test_new_code_is_processed(
    deduplicator, mock_repository, notifier, promo_code
):
    mock_repository.code_exists.return_value = False
    notifier.send.return_value = True

    results = await deduplicator.process_codes([promo_code])

    notifier.send.assert_awaited_once_with(
        "EXAMPLE-CODE", ["Example reward"], "example.com"
    )

    mock_repository.add_code.assert_called_once()
    args = mock_repository.add_code.call_args.args
    assert args[:3] == ("EXAMPLE-CODE", ["Example reward"], "example.com")
    assert args[3] is not None

    assert results["processed"] == 1


@pytest.mark.asyncio
async def test_existing_code_is_skipped(
    deduplicator, mock_repository, notifier, promo_code
):
    mock_repository.code_exists.return_value = True

    results = await deduplicator.process_codes([promo_code])

    notifier.send.assert_not_awaited()
    mock_repository.add_code.assert_not_called()
    assert results["skipped"] == 1


@pytest.mark.asyncio
async def test_duplicate_codes_in_batch(
    deduplicator, mock_repository, notifier, promo_code
):
    mock_repository.code_exists.side_effect = [False, True]
    notifier.send.return_value = True

    await deduplicator.process_codes([promo_code, promo_code])

    notifier.send.assert_awaited_once_with(
        "EXAMPLE-CODE", ["Example reward"], "example.com"
    )


@pytest.mark.asyncio
async def test_failed_notification_is_not_saved(
    deduplicator, mock_repository, notifier, promo_code
):
    mock_repository.code_exists.return_value = False
    notifier.send.return_value = False

    results = await deduplicator.process_codes([promo_code])

    mock_repository.add_code.assert_not_called()
    assert results["failed"] == 1


@pytest.mark.asyncio
async def test_notification_failure_can_be_retried(
    deduplicator, mock_repository, notifier, promo_code
):
    mock_repository.code_exists.side_effect = [False, False]
    notifier.send.side_effect = [False, True]

    first_results = await deduplicator.process_codes([promo_code])
    second_results = await deduplicator.process_codes([promo_code])

    assert notifier.send.await_count == 2
    mock_repository.add_code.assert_called_once()
    args = mock_repository.add_code.call_args.args
    assert args[:3] == ("EXAMPLE-CODE", ["Example reward"], "example.com")
    assert args[3] is not None

    assert first_results["failed"] == 1
    assert second_results["processed"] == 1


@pytest.mark.asyncio
async def test_code_is_remembered_after_restart(tmp_path, notifier, promo_code):
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

    # Simulate the first application run
    repository = CodeRepository(db_path)
    deduplicator = Deduplicator(repository, notifier)

    notifier.send.return_value = True

    first_results = await deduplicator.process_codes([promo_code])

    assert first_results["processed"] == 1
    notifier.send.assert_awaited_once_with(
        "EXAMPLE-CODE", ["Example reward"], "example.com"
    )

    # Simulate application restart
    repository = CodeRepository(db_path)
    deduplicator = Deduplicator(repository, notifier)

    notifier.send.reset_mock()

    second_results = await deduplicator.process_codes([promo_code])

    assert second_results["skipped"] == 1
    notifier.send.assert_not_awaited()
