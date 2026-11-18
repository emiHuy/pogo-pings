import asyncio
import logging

import httpx

from pogo_pings.notifications.formatter import create_promo_embed

logger = logging.getLogger(__name__)


class DiscordNotifier:
    def __init__(self, client: httpx.AsyncClient, webhook_url: str, max_retries: int):
        self.client = client
        self.webhook_url = webhook_url
        self.max_retries = max_retries

    async def send(self, code: str, rewards: list[str], source: str) -> bool:
        embed = create_promo_embed(code, rewards, source)

        try:
            for attempt in range(self.max_retries + 1):
                try:
                    response = await self.client.post(
                        self.webhook_url,
                        json={"embeds": [embed]},
                    )

                    if response.status_code == 429:
                        delay = self._get_retry_after(response)
                        logger.warning("Discord rate limited code %s", code)

                    else:
                        response.raise_for_status()
                        logger.info(
                            "Successfully sent promo code %s to Discord",
                            code,
                        )
                        return True

                except httpx.HTTPStatusError as e:
                    status = e.response.status_code

                    # Retry server errors and potentially temporary client errors.
                    if status not in (408, 425) and status < 500:
                        logger.error(
                            "Discord rejected code %s with status %s",
                            code,
                            status,
                        )
                        return False

                    delay = 2**attempt
                    logger.warning(
                        "Discord returned status %s for code %s",
                        status,
                        code,
                    )

                except httpx.HTTPError as e:
                    delay = 2**attempt
                    logger.warning(
                        "HTTP error sending code %s: %s",
                        code,
                        e,
                    )

                if attempt == self.max_retries:
                    break

                logger.info(
                    "Retrying code %s in %s seconds",
                    code,
                    delay,
                )
                await asyncio.sleep(delay)

        except httpx.HTTPError:
            logger.exception("Unexpected HTTP client error")

        logger.error(
            "Failed to send promo code %s after %s attempts",
            code,
            self.max_retries + 1,
        )
        return False

    @staticmethod
    def _get_retry_after(response: httpx.Response) -> float:
        try:
            return min(60.0, max(0.0, float(response.headers["Retry-After"])))
        except (KeyError, ValueError):
            pass

        try:
            return max(0.0, float(response.json()["retry_after"]))
        except (KeyError, ValueError, TypeError):
            logger.warning("Could not read Discord retry delay; using 1 second")
            return 1.0
