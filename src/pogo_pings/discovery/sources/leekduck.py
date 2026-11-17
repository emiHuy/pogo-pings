import httpx
from bs4 import BeautifulSoup

from .base import BaseSource, PromoCode


class LeekDuckScraper(BaseSource):
    URL = "https://leekduck.com/promo-codes/"
    SOURCE = "leekduck.com"

    async def fetch_codes(self) -> list[PromoCode]:
        codes = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.URL)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        promo_cards = soup.select('div[class="promo-card"]')

        for pc in promo_cards:
            code_element = pc.select_one('div[class="code-display"] > p[class="text"]')

            if code_element is None:
                continue

            code = code_element.get_text(strip=True)

            rewards = [
                r.get_text(strip=True)
                for r in pc.select(
                    'ul[class="reward-list"] > li[class="reward"] > span[class="reward-label"]'
                )
            ]

            codes.append(PromoCode(code=code, rewards=rewards, source=self.SOURCE))

        return codes
