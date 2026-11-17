from urllib.parse import urlencode

EMBED_COLOR = 0x5865F2

EMBED_TITLE = "📢 New Promo Code!"
EMBED_AUTHOR = "PoGO Promo Alerts"
EMBED_AUTHOR_ICON = "https://pngimg.com/uploads/pokeball/pokeball_PNG24.png"
EMBED_DESCRIPTION = "A new redemption code has been discovered!"

PROMO_CODE_FIELD = "🏷️ Promo Code"
REWARDS_FIELD = "🎁 Rewards"

REDEMPTION_URL = "https://store.pokemongo.com/offer-redemption"


def create_redemption_url(code: str) -> str:
    params = urlencode({"passcode": code})
    return f"{REDEMPTION_URL}?{params}"


def create_promo_embed(code: str, rewards: list[str], source: str) -> dict:
    return {
        "title": EMBED_TITLE,
        "description": (
            f"{EMBED_DESCRIPTION}\n\n"
            f"[🔗 Redeem on Niantic]({create_redemption_url(code)})"
        ),
        "color": EMBED_COLOR,
        "author": {
            "name": EMBED_AUTHOR,
            "icon_url": EMBED_AUTHOR_ICON,
        },
        "fields": [
            {
                "name": PROMO_CODE_FIELD,
                "value": f"`{code}`",
                "inline": True,
            },
            {
                "name": REWARDS_FIELD,
                "value": "\n".join(f"• {reward}" for reward in rewards),
                "inline": True,
            },
        ],
        "footer": {
            "text": f"Source: {source}",
        },
    }
