import healthcare_news_scraper
from healthcare_news_scraper import HealthcareArticle, ArticleScraper, ArticleStore, HealthcareNewsScraper, scrape_default_healthcare_news


def test_public_api_exports():
    assert HealthcareArticle
    assert HealthcareNewsScraper
    assert ArticleScraper
    assert ArticleStore
    assert scrape_default_healthcare_news
    assert not hasattr(healthcare_news_scraper, "get_events_safe")
