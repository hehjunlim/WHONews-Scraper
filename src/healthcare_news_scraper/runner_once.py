from __future__ import annotations

import argparse
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

from .config import PipelineConfig, load_config_from_env
from .exceptions import ScraperNetworkError
from .filters import filter_articles_by_keyword
from .protocols import ArticleScraper, ArticleStore
from .scheduler import backoff_seconds, is_transient_error as scheduler_is_transient_error


logger = logging.getLogger("healthcare_news_scraper.runner")


class PartialScrapeError(Exception):
    def __init__(self, message: str, partial_articles: Optional[List[Dict[str, str]]] = None) -> None:
        super().__init__(message)
        self.partial_articles = partial_articles or []


@dataclass(frozen=True)
class RunSummary:
    run_id: int
    status: str
    source: str
    attempts: int
    fetched_count: int
    error: str



def is_transient_error(exc: Exception) -> bool:
    return scheduler_is_transient_error(exc)



def _default_scraper(_config: PipelineConfig) -> ArticleScraper:
    from .scraper import HealthcareNewsScraper

    return HealthcareNewsScraper()



def _run_scrape(config: PipelineConfig) -> List[Dict[str, str]]:
    if config.scraper_strategy != "web":
        raise ValueError(f"Unsupported SCRAPER_STRATEGY: {config.scraper_strategy}")

    scraper = _default_scraper(config)
    articles = scraper.get_articles()

    if config.scraper_search_term:
        articles = filter_articles_by_keyword(articles, config.scraper_search_term)

    if config.scraper_limit > 0:
        articles = articles[: config.scraper_limit]

    return articles



def run_once(
    config: Optional[PipelineConfig] = None,
    scrape_func: Optional[Callable[[PipelineConfig], List[Dict[str, str]]]] = None,
    store: Optional[ArticleStore] = None,
) -> RunSummary:
    cfg = config or load_config_from_env()
    scrape = scrape_func or _run_scrape
    article_store = store or _default_store(cfg)
    article_store.init_schema()

    attempts = 0
    articles: List[Dict[str, str]] = []
    error_message = ""

    while attempts < max(1, cfg.retry_attempts):
        attempts += 1
        try:
            articles = scrape(cfg)
            error_message = ""
            break
        except PartialScrapeError as exc:
            articles = list(exc.partial_articles)
            error_message = str(exc)
            break
        except ScraperNetworkError as exc:
            error_message = str(exc)
            if attempts >= max(1, cfg.retry_attempts) or not is_transient_error(exc):
                break
            sleep_seconds = backoff_seconds(cfg.retry_backoff_seconds, attempts)
            logger.warning("Transient error on attempt %s: %s. Retrying in %ss", attempts, exc, sleep_seconds)
            time.sleep(sleep_seconds)

    if articles and error_message:
        status = "partial"
    elif articles and not error_message:
        status = "success"
    elif not articles and error_message:
        status = "failure"
    else:
        status = "success"

    run_record = article_store.persist_run(
        source=cfg.scraper_strategy,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        search_term=cfg.scraper_search_term,
        record_limit=cfg.scraper_limit,
        status=status,
        attempts=attempts,
        error=error_message,
        articles=articles,
    )

    summary = RunSummary(
        run_id=run_record.run_id,
        status=run_record.status,
        source=cfg.scraper_strategy,
        attempts=run_record.attempts,
        fetched_count=run_record.fetched_count,
        error=run_record.error,
    )

    logger.info(
        "run_id=%s status=%s source=%s attempts=%s fetched_count=%s error=%s",
        summary.run_id,
        summary.status,
        summary.source,
        summary.attempts,
        summary.fetched_count,
        summary.error,
    )

    return summary


def _default_store(config: PipelineConfig) -> ArticleStore:
    from .storage import SQLiteArticleStore

    return SQLiteArticleStore(config.db_path)



def main() -> int:
    parser = argparse.ArgumentParser(description="Run healthcare news scraper once and persist to SQLite")
    parser.add_argument("--db-path", help="Override DB path for one-shot runs")
    parser.add_argument("--search-term", help="Override search term")
    parser.add_argument("--limit", type=int, help="Override article limit")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    cfg = load_config_from_env()
    if args.db_path:
        cfg = PipelineConfig(**{**cfg.__dict__, "db_path": args.db_path})
    if args.search_term is not None:
        cfg = PipelineConfig(**{**cfg.__dict__, "scraper_search_term": args.search_term})
    if args.limit is not None:
        cfg = PipelineConfig(**{**cfg.__dict__, "scraper_limit": args.limit})

    run_once(config=cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
