import logging
from datetime import UTC, datetime
from typing import Literal, Protocol

from pogo_pings.discovery.sources.base import PromoCode

logger = logging.getLogger(__name__)

ProcessResult = Literal["processed", "skipped", "failed"]


class Repository(Protocol):
    def code_exists(self, code: str) -> bool: ...
    def add_code(
        self,
        code: str,
        rewards: list[str],
        source: str,
        notified_at: str | None = None,
    ) -> bool: ...


class Notifier(Protocol):
    async def send(self, code: str, rewards: list[str], source: str) -> bool: ...


class Deduplicator:
    def __init__(self, repository: Repository, notifier: Notifier):
        self.repository = repository
        self.notifier = notifier

    async def process_codes(self, codes: list[PromoCode]) -> dict[str, int]:
        results = {"processed": 0, "skipped": 0, "failed": 0}

        for code in codes:
            try:
                result = await self._process_code(code)
                results[result] += 1
            except Exception:
                logger.exception("Failed process code %s", code)
                results["failed"] += 1
                continue

        return results

    async def _process_code(self, code: PromoCode) -> ProcessResult:
        if self.repository.code_exists(code.code):
            return "skipped"

        success = await self.notifier.send(code.code, code.rewards, code.source)

        if not success:
            return "failed"

        notified_at = datetime.now(UTC).isoformat()

        self.repository.add_code(
            code.code,
            code.rewards,
            code.source,
            notified_at,
        )
        return "processed"
