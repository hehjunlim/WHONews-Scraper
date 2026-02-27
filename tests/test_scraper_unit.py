from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from healthcare_news_scraper.exceptions import ScraperNetworkError, ScraperTimeoutError
from healthcare_news_scraper.scraper import HealthcareNewsScraper
from tests.http_doubles import FailingHttpClient, StubHttpClient, StubHttpResponse


def _first_tag(html: str):
    return BeautifulSoup(html, "html.parser").find()


def test_parse_articles_extracts_basic_fields():
    html = Path("tests/fixtures/sample_events_page.html").read_text()
    scraper = HealthcareNewsScraper(delay_seconds=0)

    articles = scraper.parse_articles(html)

    assert len(articles) == 2
    titles = {article["title"] for article in articles}
    urls = {article["url"] for article in articles}
    categories = {article["category"] for article in articles}
    dates = {article["date"] for article in articles}

    assert "New Cancer Treatment Study" in titles
    assert any(url.startswith("https://www.who.int/") or "/" in url for url in urls)
    assert any("Thu Feb 06" in date for date in dates)


def test_parse_articles_handles_empty_html():
    scraper = HealthcareNewsScraper(delay_seconds=0)
    articles = scraper.parse_articles("<html></html>")
    assert articles == []


def test_extract_anchor_returns_none_when_no_link():
    scraper = HealthcareNewsScraper(delay_seconds=0)
    element = _first_tag("<div>No link</div>")
    assert element is not None
    assert scraper._extract_anchor(element) is None


def test_extract_anchor_returns_none_when_title_empty():
    scraper = HealthcareNewsScraper(delay_seconds=0)
    element = _first_tag("<div><a href='/news/x'> </a></div>")
    assert element is not None
    assert scraper._extract_anchor(element) is None


def test_extract_anchor_returns_title_and_href():
    scraper = HealthcareNewsScraper(delay_seconds=0)
    element = _first_tag("<div><a href='/news/x'>Title</a></div>")
    assert element is not None
    assert scraper._extract_anchor(element) == ("Title", "/news/x")


def test_extract_date_from_table_row_first_cell():
    scraper = HealthcareNewsScraper(delay_seconds=0)
    row = _first_tag("<tr><td>Mon Jan 6</td><td>Article</td></tr>")
    assert row is not None
    cells = row.find_all("td")
    assert scraper._extract_date_from_table_row(cells) == "Mon Jan 6"


def test_extract_category_from_table_row_last_cell():
    scraper = HealthcareNewsScraper(delay_seconds=0)
    row = _first_tag("<tr><td>Mon Jan 6</td><td>Article</td><td>research study</td></tr>")
    assert row is not None
    cells = row.find_all("td")
    category = scraper._extract_category_from_table_row(cells)
    assert category == "research"


def test_extract_date_and_category_prefers_table_row():
    scraper = HealthcareNewsScraper(delay_seconds=0)
    row = _first_tag("<tr><td>Thu Feb 06</td><td><a href='/news/1'>Research Article</a></td><td>clinical research</td></tr>")
    assert row is not None
    date, category = scraper._extract_date_and_category_from_element(row)
    assert date == "Thu Feb 06"
    assert category == "research"


def test_extract_date_and_category_falls_back_to_blob():
    scraper = HealthcareNewsScraper(delay_seconds=0)
    element = _first_tag("<div><a href='/news/1'>Research Article</a> Thu Feb 06 study clinical</div>")
    assert element is not None
    date, category = scraper._extract_date_and_category_from_element(element)
    assert "Thu Feb 06" in date
    assert category == "research"


def test_scraper_uses_injected_http_client():
    html = Path("tests/fixtures/sample_events_page.html").read_text()
    client = StubHttpClient([StubHttpResponse(text=html)])
    scraper = HealthcareNewsScraper(delay_seconds=0, http_client=client)
    articles = scraper.get_articles()
    assert client.calls == 1
    assert len(articles) == 2


def test_fetch_html_raises_scraper_network_error_on_connection_error():
    scraper = HealthcareNewsScraper(delay_seconds=0, http_client=FailingHttpClient())
    with pytest.raises(ScraperNetworkError):
        scraper.get_articles()


def test_fetch_html_raises_scraper_timeout_error_on_timeout():
    scraper = HealthcareNewsScraper(
        delay_seconds=0,
        http_client=FailingHttpClient(exc=ScraperTimeoutError("timeout")),
    )
    with pytest.raises(ScraperTimeoutError):
        scraper.get_articles()


def test_fetch_html_raises_scraper_network_error_on_http_error():
    client = StubHttpClient([StubHttpResponse(text="bad", status_code=500)])
    scraper = HealthcareNewsScraper(delay_seconds=0, http_client=client)
    with pytest.raises(ScraperNetworkError):
        scraper.get_articles()
