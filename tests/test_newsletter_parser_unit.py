from pathlib import Path

from healthcare_news_scraper.newsletter_parser import parse_newsletter_html


def test_parse_newsletter_html_extracts_articles():
    html = Path("tests/fixtures/sample_newsletter.html").read_text()
    articles = parse_newsletter_html(html)

    assert len(articles) == 2
    assert articles[0]["title"] == "Alpha Event"


def test_parse_newsletter_html_ignores_unsubscribe_links():
    html = "<a href='https://example.com/unsubscribe'>Unsubscribe</a>"
    articles = parse_newsletter_html(html)
    assert articles == []
