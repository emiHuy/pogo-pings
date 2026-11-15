import logging

from .processor import process_codes
from .sources.base import BaseSource, PromoCode

logger = logging.getLogger(__name__)


class DiscoveryEngine:
    def __init__(self, sources: list[BaseSource]):
        self.sources = sources

    async def discover_codes(self) -> list[PromoCode]:
        discovered_codes = []

        for source in self.sources:
            try:
                codes = await source.fetch_codes()
                discovered_codes.extend(process_codes(codes))

            except Exception:
                logger.exception(
                    "Failed to fetch codes from %s",
                    source.__class__.__name__,
                )

        return discovered_codes
