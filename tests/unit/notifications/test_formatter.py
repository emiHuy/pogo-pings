from urllib.parse import parse_qs, urlparse

from pogo_pings.notifications.formatter import (
    EMBED_AUTHOR,
    EMBED_COLOR,
    EMBED_TITLE,
    PROMO_CODE_FIELD,
    REDEMPTION_LINK_FIELD,
    REDEMPTION_URL,
    REWARDS_FIELD,
    create_promo_embed,
    create_redemption_url,
)


def test_create_redemption_url():
    url = create_redemption_url("EXAMPLE-123")

    parsed = urlparse(url)

    assert parsed.query == "passcode=EXAMPLE-123"


def test_create_redemption_url_encodes_code():
    url = create_redemption_url("EXAMPLE 123")

    parsed = urlparse(url)

    assert parse_qs(parsed.query) == {"passcode": ["EXAMPLE 123"]}


def test_create_promo_embed():
    embed = create_promo_embed(
        code="EXAMPLE-123",
        rewards=["Poké Balls", "Stardust"],
        source="Example Source",
    )

    assert embed["title"] == EMBED_TITLE
    assert embed["color"] == EMBED_COLOR
    assert embed["author"]["name"] == EMBED_AUTHOR

    assert embed["fields"] == [
        {
            "name": PROMO_CODE_FIELD,
            "value": "`EXAMPLE-123`",
            "inline": True,
        },
        {
            "name": REWARDS_FIELD,
            "value": "• Poké Balls\n• Stardust",
            "inline": True,
        },
        {
            "name": REDEMPTION_LINK_FIELD,
            "value": f"{REDEMPTION_URL}?passcode=EXAMPLE-123",
            "inline": False,
        },
    ]

    assert embed["footer"]["text"] == "Source: Example Source"
