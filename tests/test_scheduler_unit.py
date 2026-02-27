import pytest

from healthcare_news_scraper.config import PipelineConfig
from healthcare_news_scraper.exceptions import ScraperNetworkError
from healthcare_news_scraper.runner_once import PartialScrapeError, is_transient_error, run_once
from healthcare_news_scraper.scheduler import validate_cron_schedule
from healthcare_news_scraper.storage import SQLiteEventStore


def test_validate_cron_schedule_positive():
    validate_cron_schedule("0 */6 * * *")


def test_validate_cron_schedule_negative():
    with pytest.raises(ValueError):
        validate_cron_schedule("invalid cron")


def test_retry_on_transient_error(tmp_path, monkeypatch):
    db_path = tmp_path / "events.db"
    store = SQLiteEventStore(str(db_path))

    calls = {"count": 0}

    def fake_scrape(_config):
        calls["count"] += 1
        if calls["count"] == 1:
            raise ScraperNetworkError("temporary timeout")
        return [{"title": "Health Policy Update", "url": "https://www.who.int/news/item/001", "category": "policy", "date": "Wed"}]

    monkeypatch.setattr("time.sleep", lambda _seconds: None)

    summary = run_once(
        config=PipelineConfig(db_path=str(db_path), retry_attempts=3, retry_backoff_seconds=0.01),
        scrape_func=fake_scrape,
        store=store,
    )

    assert calls["count"] == 2
    assert summary.status == "success"
    assert summary.fetched_count == 1


def test_no_retry_on_non_transient_error(tmp_path):
    db_path = tmp_path / "events.db"
    store = SQLiteEventStore(str(db_path))

    calls = {"count": 0}

    def fake_scrape(_config):
        calls["count"] += 1
        raise ValueError("bad config")

    with pytest.raises(ValueError):
        run_once(
            config=PipelineConfig(db_path=str(db_path), retry_attempts=5, retry_backoff_seconds=0.01),
            scrape_func=fake_scrape,
            store=store,
        )

    assert calls["count"] == 1


def test_transient_error_classifier():
    assert is_transient_error(ScraperNetworkError("timeout")) is True
    assert is_transient_error(ValueError("bad")) is False


def test_partial_status_when_some_data_and_error(tmp_path):
    db_path = tmp_path / "events.db"
    store = SQLiteEventStore(str(db_path))

    def fake_scrape(_config):
        raise PartialScrapeError(
            "upstream parse warning",
            partial_events=[
                {
                    "title": "Medical Research Breakthrough",
                    "url": "https://www.who.int/news/item/002",
                    "category": "research",
                    "date": "Thu",
                }
            ],
        )

    summary = run_once(
        config=PipelineConfig(db_path=str(db_path), retry_attempts=3),
        scrape_func=fake_scrape,
        store=store,
    )

    assert summary.status == "partial"
    assert summary.fetched_count == 1
    assert "upstream parse warning" in summary.error
