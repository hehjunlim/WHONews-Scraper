import os
import pytest

from healthcare_news_scraper.scraper import scrape_default_healthcare_news


@pytest.mark.e2e
@pytest.mark.skipif(os.getenv("RUN_E2E") != "1", reason="Set RUN_E2E=1 to enable live test")
def test_live_site_scrape():
    articles = scrape_default_healthcare_news(delay_seconds=2.0)
    assert isinstance(articles, list)
