from __future__ import annotations

import time
from dataclasses import asdict
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .exceptions import ScraperNetworkError
from .http import RequestsHttpClient
from .models import HealthcareArticle
from .protocols import HttpClient


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

NEWS_LINK_FRAGMENT = "/news/"
CATEGORY_KEYWORDS = {
    "research": ["study", "research", "clinical", "trial"],
    "policy": ["policy", "regulation", "law", "mandate"],
    "outbreak": ["outbreak", "epidemic", "pandemic", "disease"],
    "public_health": ["health", "vaccination", "prevention", "screening"],
}
DATE_TOKENS = [
    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun",
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


class HealthcareNewsScraper:
    BASE_URL = "https://www.who.int/news"

    def __init__(
        self,
        delay_seconds: float = 1.5,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout_seconds: int = 10,
        http_client: Optional[HttpClient] = None,
    ) -> None:
        self.delay_seconds = delay_seconds
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self._http = http_client or RequestsHttpClient()

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def _fetch_html(self, url: str) -> str:
        time.sleep(self.delay_seconds)
        try:
            response = self._http.get(url, headers=self._headers(), timeout=self.timeout_seconds)
            response.raise_for_status()
            return response.text
        except ScraperNetworkError:
            raise

    def _clean(self, value: Optional[str]) -> str:
        return value.strip() if value else ""

    def _normalize_url(self, href: str) -> str:
        return urljoin(self.BASE_URL, href)

    def _extract_category(self, text: str) -> str:
        normalized = " ".join(text.split()).lower()
        if not normalized:
            return "general"
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in normalized for keyword in keywords):
                return category
        return "general"

    def _extract_date(self, text: str) -> str:
        normalized = " ".join(text.split())
        if not normalized:
            return ""
        if any(token in normalized for token in DATE_TOKENS):
            return normalized
        return ""

    def _extract_anchor(self, element: Tag) -> Optional[Tuple[str, str]]:
        link = element.find("a", href=True)
        if not link:
            return None

        title = self._clean(link.get_text())
        href = self._clean(link.get("href"))
        if not title or not href:
            return None
        return title, href

    def _extract_date_from_table_row(self, cells: List[Tag]) -> str:
        if not cells:
            return ""
        return self._extract_date(self._clean(cells[0].get_text(" ")))

    def _extract_category_from_table_row(self, cells: List[Tag]) -> str:
        if len(cells) <= 1:
            return "general"
        return self._extract_category(self._clean(cells[-1].get_text(" ")))

    def _extract_date_and_category_from_element(self, element: Tag) -> Tuple[str, str]:
        date = ""
        category = ""

        if element.name == "tr":
            cells = element.find_all("td")
            date = self._extract_date_from_table_row(cells)
            category = self._extract_category_from_table_row(cells)

        text_blob = self._clean(element.get_text(" "))
        if not date:
            date = self._extract_date(text_blob)
        if not category:
            category = self._extract_category(text_blob)
        return date, category

    def _extract_article_from_element(self, element: Tag) -> Optional[HealthcareArticle]:
        anchor = self._extract_anchor(element)
        if anchor is None:
            return None

        title, href = anchor
        url = self._normalize_url(href)
        date, category = self._extract_date_and_category_from_element(element)
        return HealthcareArticle(title=title, date=date, category=category, url=url, source="healthcare_web")

    def _candidate_elements(self, soup: BeautifulSoup) -> Iterable[Tag]:
        for link in soup.select("a[href]"):
            href = link.get("href", "")
            if NEWS_LINK_FRAGMENT not in href:
                continue
            container = link.find_parent(["tr", "li", "div", "article"])
            yield container if container else link

    def parse_articles(self, html: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        articles: List[HealthcareArticle] = []

        for element in self._candidate_elements(soup):
            article = self._extract_article_from_element(element)
            if article:
                articles.append(article)

        unique = {}
        for article in articles:
            key = (article.title, article.url)
            unique[key] = article

        return [asdict(article) for article in unique.values()]

    def get_articles(self) -> List[Dict[str, str]]:
        html = self._fetch_html(self.BASE_URL)
        return self.parse_articles(html)


def scrape_default_healthcare_news(delay_seconds: float = 1.5) -> List[Dict[str, str]]:
    return HealthcareNewsScraper(delay_seconds=delay_seconds).get_articles()
