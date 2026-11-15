from .sources.base import PromoCode


def normalize_code(code: str) -> str:
    return code.strip().upper()


def is_valid_code(code: str) -> bool:
    return bool(code.strip())


def process_codes(codes: list[PromoCode]) -> list[PromoCode]:
    processed = []

    for promo in codes:
        code = normalize_code(promo.code)

        if not is_valid_code(code):
            continue

        processed.append(
            PromoCode(
                code=code,
                rewards=promo.rewards,
            )
        )

    return processed
