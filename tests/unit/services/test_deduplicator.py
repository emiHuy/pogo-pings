import pytest

from pogo_pings.db.connection import get_connection
from pogo_pings.db.repositories.codes import CodeRepository
from pogo_pings.services.deduplicator import Deduplicator


@pytest.mark.asyncio
async def test_new_code_is_processed(deduplicator, mock_repository, notifier):
    mock_repository.code_exists.return_value = False
    notifier.send.return_value = True

    results = await deduplicator.process_codes(["POGO2026"])

    notifier.send.assert_awaited_once_with("POGO2026")
    mock_repository.add_code.assert_called_once_with("POGO2026")
    assert results["processed"] == 1


@pytest.mark.asyncio
async def test_existing_code_is_skipped(deduplicator, mock_repository, notifier):
    mock_repository.code_exists.return_value = True

    results = await deduplicator.process_codes(["POGO2026"])

    notifier.send.assert_not_awaited()
    assert results["skipped"] == 1


@pytest.mark.asyncio
async def test_duplicate_codes_in_batch(deduplicator, mock_repository, notifier):
    mock_repository.code_exists.side_effect = [False, True]
    notifier.send.return_value = True

    await deduplicator.process_codes(["POGO2026", "POGO2026"])

    notifier.send.assert_awaited_once_with("POGO2026")


@pytest.mark.asyncio
async def test_failed_notification_is_not_saved(
    deduplicator, mock_repository, notifier
):
    mock_repository.code_exists.return_value = False
    notifier.send.return_value = False

    results = await deduplicator.process_codes(["POGO2026"])

    mock_repository.add_code.assert_not_called()
    assert results["failed"] == 1


@pytest.mark.asyncio
async def test_notification_failure_can_be_retried(
    deduplicator, mock_repository, notifier
):
    mock_repository.code_exists.side_effect = [False, False]
    notifier.send.side_effect = [False, True]

    first_results = await deduplicator.process_codes(["POGO2026"])
    second_results = await deduplicator.process_codes(["POGO2026"])

    assert notifier.send.await_count == 2
    mock_repository.add_code.assert_called_once_with("POGO2026")

    assert first_results["failed"] == 1
    assert second_results["processed"] == 1


@pytest.mark.asyncio
async def test_code_is_remembered_after_restart(tmp_path, notifier):
    db_path = str(tmp_path / "test.db")

    # Simulate the first application run
    repository = CodeRepository(db_path)
    deduplicator = Deduplicator(repository, notifier)

    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE seen_codes (
                code TEXT PRIMARY KEY,
                first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    notifier.send.return_value = True

    first_results = await deduplicator.process_codes(["POGO2026"])

    assert first_results["processed"] == 1
    notifier.send.assert_awaited_once_with("POGO2026")

    # Simulate application restart
    repository = CodeRepository(db_path)
    deduplicator = Deduplicator(repository, notifier)

    notifier.send.reset_mock()

    second_results = await deduplicator.process_codes(["POGO2026"])

    assert second_results["skipped"] == 1
    notifier.send.assert_not_awaited()
