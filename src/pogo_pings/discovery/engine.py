import logging

from .processor import process_codes
from .sources.base import PromoCode, PromoCodeSource

logger = logging.getLogger(__name__)


class DiscoveryEngine:
    def __init__(self, sources: list[PromoCodeSource]):
        self.sources = sources

    async def discover_codes(self) -> list[PromoCode]:
        discovered_codes = []

        for source in self.sources:
            logger.debug(
                "Fetching codes from %s (%s)",
                source.SOURCE,
                source.URL,
            )

            try:
                codes = await source.fetch_codes()
                discovered_codes.extend(process_codes(codes))

            except Exception:
                logger.exception(
                    "Failed to fetch codes from %s (%s)",
                    source.SOURCE,
                    source.URL,
                )

        return discovered_codes
