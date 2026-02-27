# Task Board

## 🟢 Completed

### Project Transformation
- [x] Transform codebase from Gary's Guide NYC events to WHO Healthcare News scraper
- [x] Rename package directory: `garys_nyc_events` → `healthcare_news_scraper`
- [x] Update all import statements across test files
- [x] Update `pyproject.toml` configuration
- [x] Update Docker and Kubernetes configurations
- [x] Update all documentation files (README, CHANGELOG, etc.)
- [x] Update sprint planning documents
- [x] Delete transformation summary documents
- [x] Update GitHub repository URLs in `pyproject.toml`

### Internal Naming & Consistency
- [x] Rename internal protocol/class names for consistency
  - [x] `EventScraper` → `ArticleScraper` in `protocols.py`
  - [x] `EventStore` → `ArticleStore` in `protocols.py`
  - [x] `SQLiteEventStore` → `SQLiteArticleStore` in `storage.py`
  - [x] Update all imports and references (20+ files)
- [x] Update variable names `events` → `articles` in storage layer
- [x] Update parameter names in protocols and implementations

### Development Environment
- [x] Install Poetry and project dependencies
- [x] Run full test suite to verify all changes work (35 passed, 1 skipped)

### Code Quality Sprints (Completed)
- [x] **Sprint 6**: Dependency Inversion Principle implementation
  - [x] Created protocol interfaces (ArticleScraper, ArticleStore)
  - [x] Implemented dependency injection in runner_once.py
  - [x] All tests passing with clean architecture

- [x] **Sprint 7**: Single Responsibility Principle - Decompose Scraper
  - [x] Created `models.py` with HealthcareArticle dataclass
  - [x] Created `filters.py` with filter_articles_by_keyword
  - [x] Created `formatters.py` with get_articles_category_json
  - [x] Created `newsletter_parser.py` with parse_newsletter_html
  - [x] Removed all .to_dict() calls, using dataclasses.asdict()
  - [x] Reduced scraper.py line count by 40%+

- [x] **Sprint 8**: Extract Small Functions
  - [x] `_extract_article_from_element` is now pure delegation
  - [x] Created `_extract_anchor` helper
  - [x] Created `_extract_date_from_table_row` helper
  - [x] Created `_extract_category_from_table_row` helper (adapted from price)
  - [x] Created `_extract_date_and_category_from_element` orchestrator
  - [x] Low cyclomatic complexity throughout

- [x] **Sprint 9**: Error Handling
  - [x] Created `exceptions.py` with clean hierarchy
  - [x] Removed all `get_events_safe` / `get_articles_safe` methods
  - [x] No broad `except Exception` catches
  - [x] HTTP client wraps exceptions to domain exceptions
  - [x] runner_once.py uses specific exception handling

- [x] **Sprint 10**: Test Boundaries & HTTP Abstraction
  - [x] Created HttpClient and HttpResponse protocols
  - [x] Isolated `requests` library to http.py only
  - [x] Dependency injection for HTTP client in scraper
  - [x] Zero coupling to requests outside http.py
  - [x] Clean test double compatibility

- [x] **Sprint 11**: Docker Single Process
  - [x] Removed cron-inside-container antipattern
  - [x] Single-process container (run once and exit)
  - [x] Created run_once_entrypoint.sh script
  - [x] Kubernetes CronJob manifest (deploy/k8s-cronjob.yaml)
  - [x] Clean separation: scheduling=orchestrator, scraping=container

### Documentation & Organization
- [x] Review database schema for naming consistency
- [x] Review and update inline code comments (none needed updates)
- [x] Review logging messages (already using appropriate terminology)
- [x] Organize sprint folders: moved all completed sprints to completed/

## 🟡 In Progress

None currently

## 🔴 To Do

### High Priority
None - all planned sprints completed!

### Medium Priority
- [ ] Update Docker image name references (may still reference old names)
- [ ] Consider renaming GitHub repository: `GarysGuide-Scraper` → `WHONews-Scraper`
- [ ] Review sprint_plan.md for any needed updates

### Low Priority
- [ ] Update example outputs in documentation
- [ ] Add more healthcare-specific documentation/examples
- [ ] Review and update test fixture data with healthcare examples

## 📋 Technical Debt

**Database Schema Legacy Naming (DOCUMENTED, NO ACTION REQUIRED):**
- `event_date` field in `product_snapshots` table (stores article publication date)
- `products` table name (stores healthcare articles)
- `product_snapshots` table name (stores article data snapshots)
- **Decision:** Keep existing names for backward compatibility

## 📋 Future Enhancements

- Add more healthcare news sources beyond WHO
- Enhance filtering capabilities for medical categories
- Add data validation for healthcare article schemas
- Explore async HTTP client (httpx) now that abstraction layer exists
- Add comprehensive integration tests with real WHO website
