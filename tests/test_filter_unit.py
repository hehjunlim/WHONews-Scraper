from healthcare_news_scraper.filters import filter_articles_by_keyword


def test_filter_articles_by_keyword_matches_title_and_category():
    articles = [
        {"title": "New Research on Cancer Treatment", "category": "research"},
        {"title": "Product Meetup", "category": "general"},
        {"title": "Policy Update", "category": "policy"},
    ]

    filtered = filter_articles_by_keyword(articles, "research")
    assert len(filtered) == 1
    assert filtered[0]["title"] == "New Research on Cancer Treatment"


def test_filter_articles_by_keyword_empty_returns_all():
    articles = [{"title": "Health Summit", "category": "general"}]
    assert filter_articles_by_keyword(articles, "") == articles
