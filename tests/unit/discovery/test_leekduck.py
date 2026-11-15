import httpx
import pytest

from pogo_pings.discovery.sources import leekduck
from pogo_pings.discovery.sources.leekduck import LeekDuckScraper


@pytest.mark.asyncio
async def test_fetch_codes(mock_http):
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

    mock_http(
        leekduck,
        lambda request: httpx.Response(200, text=html),
    )

    scraper = LeekDuckScraper()
    codes = await scraper.fetch_codes()

    assert len(codes) == 1
    assert codes[0].code == "POKEMON123"
    assert codes[0].rewards == ["Poké Balls"]


@pytest.mark.asyncio
async def test_fetch_multiple_codes(mock_http):
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

    mock_http(
        leekduck,
        lambda request: httpx.Response(200, text=html),
    )

    scraper = LeekDuckScraper()
    codes = await scraper.fetch_codes()

    assert len(codes) == 2
    assert codes[0].code == "CODE123"
    assert codes[1].code == "CODE456"


@pytest.mark.asyncio
async def test_fetch_codes_skips_missing_code(mock_http):
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

    mock_http(
        leekduck,
        lambda request: httpx.Response(200, text=html),
    )

    scraper = LeekDuckScraper()
    codes = await scraper.fetch_codes()

    assert len(codes) == 1
    assert codes[0].code == "VALID123"


@pytest.mark.asyncio
async def test_fetch_codes_empty_page(mock_http):
    mock_http(
        leekduck,
        lambda request: httpx.Response(200, text="<html></html>"),
    )

    scraper = LeekDuckScraper()
    codes = await scraper.fetch_codes()

    assert codes == []


@pytest.mark.asyncio
async def test_fetch_codes_http_error(mock_http):
    mock_http(
        leekduck,
        lambda request: httpx.Response(500),
    )

    scraper = LeekDuckScraper()

    with pytest.raises(httpx.HTTPStatusError):
        await scraper.fetch_codes()
