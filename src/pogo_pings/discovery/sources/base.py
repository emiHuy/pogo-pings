from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PromoCode:
    code: str
    rewards: list[str]


class BaseSource(ABC):

    @abstractmethod
    async def fetch_codes(self) -> list[PromoCode]:
        """Fetch and return raw promo code candidates."""
        raise NotImplementedError
