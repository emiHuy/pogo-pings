from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx


@dataclass
class PromoCode:
    code: str
    rewards: list[str]
    source: str


class PromoCodeSource(ABC):
    SOURCE: str
    URL: str

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @abstractmethod
    async def fetch_codes(self) -> list[PromoCode]:
        """Fetch and return raw promo code candidates."""
        raise NotImplementedError
