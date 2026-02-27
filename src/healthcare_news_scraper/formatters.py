from __future__ import annotations

import json
from typing import Dict, List

from .filters import filter_articles_by_keyword


def get_articles_category_json(articles: List[Dict[str, str]], category: str = "research") -> str:
    filtered_articles = filter_articles_by_keyword(articles, category)
    return json.dumps(filtered_articles, ensure_ascii=False, indent=2)
