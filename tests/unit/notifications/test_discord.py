import httpx
import pytest

import pogo_pings.notifications.discord as discord_module
from pogo_pings.notifications.discord import DiscordNotifier
from tests.conftest import mock_http


@pytest.mark.asyncio
async def test_successful_delivery():
    async with mock_http(lambda request: httpx.Response(204)) as client:
        notifier = DiscordNotifier(
            client=client,
            webhook_url="https://discord.test/webhook",
            max_retries=3,
        )

        result = await notifier.send("ABC123", ["Coins"], "Test")

    assert result is True


@pytest.mark.asyncio
async def test_rate_limit_retries_delivery(mock_sleep):
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(429, headers={"Retry-After": "2"})

        return httpx.Response(204)

    async with mock_http(handler) as client:
        notifier = DiscordNotifier(
            client=client,
            webhook_url="https://discord.test/webhook",
            max_retries=3,
        )

        result = await notifier.send("ABC123", ["Coins"], "Test")

    assert result is True
    assert attempts == 2
    assert mock_sleep == [2.0]


@pytest.mark.asyncio
async def test_retries_exhausted(mock_sleep):
    async with mock_http(lambda request: httpx.Response(500)) as client:
        notifier = DiscordNotifier(
            client=client,
            webhook_url="https://discord.test/webhook",
            max_retries=2,
        )

        result = await notifier.send("ABC123", ["Coins"], "Test")

    assert result is False
    assert mock_sleep == [1, 2]


@pytest.mark.asyncio
async def test_permanent_http_error_is_not_retried(mock_sleep):
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(400)

    async with mock_http(handler) as client:
        notifier = DiscordNotifier(
            client=client,
            webhook_url="https://discord.test/webhook",
            max_retries=3,
        )

        result = await notifier.send("ABC123", ["Coins"], "Test")

    assert result is False
    assert attempts == 1
    assert mock_sleep == []


@pytest.mark.asyncio
async def test_server_error_retries_delivery(mock_sleep):
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            return httpx.Response(500)

        return httpx.Response(204)

    async with mock_http(handler) as client:
        notifier = DiscordNotifier(
            client=client,
            webhook_url="https://discord.test/webhook",
            max_retries=3,
        )

        result = await notifier.send("ABC123", ["Coins"], "Test")

    assert result is True
    assert attempts == 2
    assert mock_sleep == [1]
