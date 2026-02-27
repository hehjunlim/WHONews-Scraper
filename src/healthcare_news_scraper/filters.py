from __future__ import annotations

from typing import Dict, List


def filter_articles_by_keyword(
    articles: List[Dict[str, str]],
    keyword: str,
) -> List[Dict[str, str]]:
    needle = keyword.lower().strip()
    if not needle:
        return articles
    return [article for article in articles if needle in article.get("title", "").lower() or needle in article.get("category", "").lower()]
