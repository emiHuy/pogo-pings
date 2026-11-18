import httpx
import pytest

from pogo_pings.discovery.sources.leekduck import LeekDuckSource
from tests.conftest import mock_http


@pytest.mark.asyncio
async def test_fetch_codes():
    html = """
    <div class="promo-card">
        <div class="code-display">
            <p class="text">POKEMON123</p>
        </div>
        <ul class="reward-list">
            <li class="reward">
                <span class="reward-label">Poké Balls</span>
            </li>
        </ul>
    </div>
    """

    async with mock_http(lambda request: httpx.Response(200, text=html)) as client:
        source = LeekDuckSource(client)
        codes = await source.fetch_codes()

    assert len(codes) == 1
    assert codes[0].code == "POKEMON123"
    assert codes[0].rewards == ["Poké Balls"]


@pytest.mark.asyncio
async def test_fetch_multiple_codes():
    html = """
    <div class="promo-card">
        <div class="code-display">
            <p class="text">CODE123</p>
        </div>
    </div>

    <div class="promo-card">
        <div class="code-display">
            <p class="text">CODE456</p>
        </div>
    </div>
    """

    async with mock_http(lambda request: httpx.Response(200, text=html)) as client:
        source = LeekDuckSource(client)
        codes = await source.fetch_codes()

    assert len(codes) == 2
    assert codes[0].code == "CODE123"
    assert codes[1].code == "CODE456"


@pytest.mark.asyncio
async def test_fetch_codes_skips_missing_code():
    html = """
    <div class="promo-card">
        <div class="code-display"></div>
    </div>

    <div class="promo-card">
        <div class="code-display">
            <p class="text">VALID123</p>
        </div>
    </div>
    """

    async with mock_http(lambda request: httpx.Response(200, text=html)) as client:
        source = LeekDuckSource(client)
        codes = await source.fetch_codes()

    assert len(codes) == 1
    assert codes[0].code == "VALID123"


@pytest.mark.asyncio
async def test_fetch_codes_empty_page():
    async with mock_http(
        lambda request: httpx.Response(200, text="<html></html>")
    ) as client:
        source = LeekDuckSource(client)
        codes = await source.fetch_codes()

    assert codes == []


@pytest.mark.asyncio
async def test_fetch_codes_http_error():
    async with mock_http(lambda request: httpx.Response(500)) as client:
        source = LeekDuckSource(client)

        with pytest.raises(httpx.HTTPStatusError):
            await source.fetch_codes()
