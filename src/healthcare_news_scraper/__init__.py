from importlib.metadata import PackageNotFoundError, version

from .filters import filter_articles_by_keyword
from .formatters import get_articles_category_json
from .models import HealthcareArticle
from .newsletter_parser import parse_newsletter_html
from .protocols import EventScraper, EventStore, HttpClient, HttpResponse
from .scraper import HealthcareNewsScraper, scrape_default_healthcare_news

try:
    __version__ = version("healthcare_news_scraper")
except PackageNotFoundError:  # pragma: no cover - local editable usage
    __version__ = "0.0.0"

__all__ = [
    "HealthcareArticle",
    "HealthcareNewsScraper",
    "EventScraper",
    "EventStore",
    "HttpClient",
    "HttpResponse",
    "filter_articles_by_keyword",
    "scrape_default_healthcare_news",
    "get_articles_category_json",
    "parse_newsletter_html",
    "__version__",
]
