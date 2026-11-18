import asyncio
import logging
import signal

import httpx

from pogo_pings.config import load_config
from pogo_pings.db.init import initialize_database
from pogo_pings.db.repositories.codes import CodeRepository
from pogo_pings.discovery.engine import DiscoveryEngine
from pogo_pings.discovery.sources.leekduck import LeekDuckSource
from pogo_pings.notifications.discord import DiscordNotifier
from pogo_pings.services.deduplicator import Deduplicator
from pogo_pings.services.polling import PollingService

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)


async def main() -> None:
    config = load_config()

    logging.basicConfig(
        level=config.log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    logger.info("PoGO Pings started")
    logger.debug("Debug logging is enabled")
    logger.info("Running in %s mode", config.app_env)

    initialize_database(config.database_path)
    repository = CodeRepository(config.database_path)

    async with httpx.AsyncClient(timeout=config.http_timeout) as client:
        sources = [LeekDuckSource(client)]

        notifier = DiscordNotifier(
            client=client,
            webhook_url=config.webhook_url,
            max_retries=config.max_retries,
        )

        discovery_engine = DiscoveryEngine(sources)
        deduplicator = Deduplicator(repository, notifier)

        polling_service = PollingService(
            discovery_engine,
            deduplicator,
            poll_interval=config.poll_interval,
        )

        register_signal_handlers(polling_service)

        await polling_service.run()

        logger.info("PoGO Pings stopped")


def register_signal_handlers(polling_service: PollingService) -> None:
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, polling_service.stop)


if __name__ == "__main__":
    asyncio.run(main())
