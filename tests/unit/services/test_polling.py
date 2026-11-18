import asyncio

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


@pytest.mark.asyncio
async def test_service_stops_when_shutdown_requested(
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

    task = asyncio.create_task(polling_service.run())
    await asyncio.sleep(0)

    polling_service.stop()
    await asyncio.wait_for(task, timeout=1)

    mock_discovery_engine.discover_codes.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_does_not_start_another_cycle_after_shutdown(
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

    task = asyncio.create_task(polling_service.run())

    while mock_discovery_engine.discover_codes.await_count == 0:
        await asyncio.sleep(0)

    polling_service.stop()
    await asyncio.wait_for(task, timeout=1)

    mock_discovery_engine.discover_codes.assert_awaited_once()
    mock_deduplicator.process_codes.assert_awaited_once_with([])


@pytest.mark.asyncio
async def test_shutdown_during_poll_waits_for_cycle_to_finish(
    polling_service,
    mock_discovery_engine,
    mock_deduplicator,
):
    discovery_started = asyncio.Event()
    finish_discovery = asyncio.Event()

    async def discover_codes():
        discovery_started.set()
        await finish_discovery.wait()
        return []

    mock_discovery_engine.discover_codes.side_effect = discover_codes
    mock_deduplicator.process_codes.return_value = {
        "processed": 0,
        "skipped": 0,
        "failed": 0,
    }

    task = asyncio.create_task(polling_service.run())
    await discovery_started.wait()

    polling_service.stop()
    assert not task.done()

    finish_discovery.set()
    await asyncio.wait_for(task, timeout=1)

    mock_deduplicator.process_codes.assert_awaited_once_with([])
    mock_discovery_engine.discover_codes.assert_awaited_once()
