from typing import Dict, Iterable, List

from healthcare_news_scraper.http import RequestsHttpClient
from healthcare_news_scraper.protocols import EventScraper, EventStore, HttpClient
from healthcare_news_scraper.runner_once import run_once
from healthcare_news_scraper.scraper import HealthcareNewsScraper
from healthcare_news_scraper.storage import SQLiteEventStore
from healthcare_news_scraper.config import PipelineConfig
from tests.http_doubles import StubHttpClient, StubHttpResponse


class StubScraper:
    def get_events(self) -> List[Dict[str, str]]:
        return [{"title": "Health Policy Update", "url": "https://www.who.int/news/item/001", "category": "policy", "date": "Wed"}]


class StubStore:
    def __init__(self) -> None:
        self.initialized = False
        self.persisted = False

    def init_schema(self) -> None:
        self.initialized = True

    def persist_run(
        self,
        *,
        source: str,
        fetched_at: str,
        search_term: str,
        record_limit: int,
        status: str,
        attempts: int,
        error: str,
        events: Iterable[Dict[str, str]],
    ) -> object:
        self.persisted = True
        event_list = list(events)
        return type(
            "RunRecordLike",
            (),
            {
                "run_id": 1,
                "status": status,
                "fetched_count": len(event_list),
                "attempts": attempts,
                "error": error,
            },
        )()


def test_sqlite_store_satisfies_event_store_protocol(tmp_path):
    db_path = tmp_path / "events.db"
    assert isinstance(SQLiteEventStore(str(db_path)), EventStore)


def test_healthcare_news_scraper_satisfies_event_scraper_protocol():
    assert isinstance(HealthcareNewsScraper(delay_seconds=0), EventScraper)


def test_requests_http_client_satisfies_http_client_protocol():
    assert isinstance(RequestsHttpClient(), HttpClient)


def test_stub_http_client_satisfies_http_client_protocol():
    assert isinstance(StubHttpClient([StubHttpResponse(text="ok")]), HttpClient)


def test_run_once_accepts_in_memory_stub_store(tmp_path):
    store = StubStore()
    cfg = PipelineConfig(db_path=str(tmp_path / "events.db"))

    summary = run_once(
        config=cfg,
        scrape_func=lambda _cfg: [
            {"title": "Health Policy Update", "url": "https://www.who.int/news/item/001", "category": "policy", "date": "Wed"}
        ],
        store=store,
    )

    assert store.initialized is True
    assert store.persisted is True
    assert summary.fetched_count == 1


def test_run_once_accepts_stub_scraper(tmp_path):
    store = StubStore()
    cfg = PipelineConfig(db_path=str(tmp_path / "events.db"))
    scraper = StubScraper()

    summary = run_once(config=cfg, scrape_func=lambda _cfg: scraper.get_events(), store=store)
    assert summary.fetched_count == 1
