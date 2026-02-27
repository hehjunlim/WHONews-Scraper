from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

from bs4 import BeautifulSoup

from .models import HealthcareArticle


def parse_newsletter_html(raw_html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(raw_html, "html.parser")
    articles: List[HealthcareArticle] = []

    ignore_tokens = [
        "unsubscribe",
        "view in browser",
        "privacy",
        "sponsor",
        "advertise",
        "mailto:",
        "facebook.com",
        "twitter.com",
        "linkedin.com",
    ]

    for link in soup.find_all("a", href=True):
        title = link.get_text(strip=True)
        url = link.get("href", "").strip()
        if not title or not url:
            continue
        if any(token in url.lower() for token in ignore_tokens):
            continue
        if any(token in title.lower() for token in ignore_tokens):
            continue

        articles.append(
            HealthcareArticle(
                title=title,
                date="",
                category="general",
                url=url,
                source="healthcare_newsletter",
            )
        )

    unique = {(a.title, a.url): a for a in articles}
    return [asdict(article) for article in unique.values()]
