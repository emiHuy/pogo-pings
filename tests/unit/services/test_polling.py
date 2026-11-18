import pytest

from pogo_pings.services.polling import PollingService


@pytest.mark.asyncio
async def test_poll_processes_discovered_codes(
    polling_service,
    mock_discovery_engine,
    mock_deduplicator,
):
    codes = ["CODE123", "CODE456"]

    mock_discovery_engine.discover_codes.return_value = codes
    mock_deduplicator.process_codes.return_value = {
        "processed": 2,
        "skipped": 0,
        "failed": 0,
    }

    await polling_service.poll()

    mock_discovery_engine.discover_codes.assert_awaited_once()
    mock_deduplicator.process_codes.assert_awaited_once_with(codes)


@pytest.mark.asyncio
async def test_poll_handles_no_discovered_codes(
    polling_service,
    mock_discovery_engine,
    mock_deduplicator,
):
    mock_discovery_engine.discover_codes.return_value = []
    mock_deduplicator.process_codes.return_value = {
        "processed": 0,
        "skipped": 0,
        "failed": 0,
    }

    await polling_service.poll()

    mock_deduplicator.process_codes.assert_awaited_once_with([])


@pytest.mark.asyncio
async def test_poll_propagates_discovery_error(
    polling_service,
    mock_discovery_engine,
    mock_deduplicator,
):
    mock_discovery_engine.discover_codes.side_effect = RuntimeError("Discovery failed")

    with pytest.raises(RuntimeError, match="Discovery failed"):
        await polling_service.poll()

    mock_deduplicator.process_codes.assert_not_awaited()


@pytest.mark.asyncio
async def test_poll_propagates_processing_error(
    polling_service,
    mock_discovery_engine,
    mock_deduplicator,
):
    mock_discovery_engine.discover_codes.return_value = ["CODE123"]

    mock_deduplicator.process_codes.side_effect = RuntimeError("Processing failed")

    with pytest.raises(RuntimeError, match="Processing failed"):
        await polling_service.poll()


def test_polling_interval_must_be_positive(
    mock_discovery_engine,
    mock_deduplicator,
):
    with pytest.raises(ValueError, match="poll_interval must be positive"):
        PollingService(
            discovery_engine=mock_discovery_engine,
            deduplicator=mock_deduplicator,
            poll_interval=0,
        )
