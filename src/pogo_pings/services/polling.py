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

        while True:
            try:
                await self.poll()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Polling cycle failed")

            logger.info("Next polling cycle in %s seconds", self.poll_interval)
            await asyncio.sleep(self.poll_interval)
