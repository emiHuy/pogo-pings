import asyncio
import logging

from pogo_pings.discovery.engine import DiscoveryEngine
from pogo_pings.services.deduplicator import Deduplicator

logger = logging.getLogger(__name__)


class PollingService:
    def __init__(
        self,
        discovery_engine: DiscoveryEngine,
        deduplicator: Deduplicator,
        poll_interval: int,
    ):
        if poll_interval <= 0:
            raise ValueError("poll_interval must be positive")

        self.discovery_engine = discovery_engine
        self.deduplicator = deduplicator
        self.poll_interval = poll_interval
        self._shutdown_event = asyncio.Event()

    async def poll(self) -> None:
        logger.info("Polling cycle started")

        codes = await self.discovery_engine.discover_codes()
        results = await self.deduplicator.process_codes(codes)

        logger.info(
            "Polling cycle completed: %s processed, %s skipped, %s failed",
            results["processed"],
            results["skipped"],
            results["failed"],
        )

    async def run(self) -> None:
        logger.info("Polling service started")

        try:
            while not self._shutdown_event.is_set():
                try:
                    await self.poll()
                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception("Polling cycle failed")

                if self._shutdown_event.is_set():
                    break

                logger.info("Next polling cycle in %s seconds", self.poll_interval)

                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=self.poll_interval,
                    )
                except TimeoutError:
                    pass

        finally:
            logger.info("Polling service stopped.")

    def stop(self) -> None:
        self._shutdown_event.set()
