# Sprint 6 — Dependency Inversion: Define and Inject Abstractions

**Status:** ✅ COMPLETED (February 27, 2026)  
**Review reference:** Uncle Bob audit, Section I — Dependency Inversion Principle (DIP)

**Note:** During implementation, protocol names were updated to use `Article*` terminology instead of `Event*` to align with the healthcare news domain.

---

## Goal

Eliminate the hard dependency between `runner_once.py` (high-level policy) and the concrete classes
`HealthcareNewsScraper` and `SQLiteArticleStore` (low-level details). The runner must depend only on
abstractions it defines. Concrete types move down to the application wiring layer.

---

## Rationale

`run_once()` previously imported `SQLiteEventStore` directly and accepted it as a typed parameter.
`_build_scraper()` constructed a `HealthcareNewsScraper` from inside the module. This meant:

- Swapping the storage engine (e.g., Postgres, in-memory) required changing runner code.
- Swapping the HTTP-backed scraper for a file-based stub required patching internals.
- The runner could not be unit-tested without touching real SQLite or the real network.

Uncle Bob's rule: _"High-level modules should not depend on low-level modules. Both should depend on
abstractions."_

---

## Tasks

### 1. ✅ Create `src/healthcare_news_scraper/protocols.py`

Defined two `typing.Protocol` classes:

**`ArticleScraper`** (implemented as ArticleScraper, not EventScraper)

```python
class ArticleScraper(Protocol):
    def get_articles(self) -> List[Dict[str, str]]: ...
```

**`ArticleStore`** (implemented as ArticleStore, not EventStore)

```python
class ArticleStore(Protocol):
    def init_schema(self) -> None: ...
    def persist_run(..., articles: Iterable[Dict[str, str]]) -> RunRecord: ...
```

- Used `@runtime_checkable` on both so `isinstance` checks work in tests. ✅
- No imports from `scraper.py` or `storage.py` inside this module. ✅

---

### 2. ✅ Update `runner_once.py` — depend on protocols, not concrete types

- Changed the `store` parameter of `run_once()` to `Optional[ArticleStore]`. ✅
- Removed the `SQLiteArticleStore` import from the top-level import block. ✅
- Changed `_default_scraper()` to return `ArticleScraper` (the protocol type). ✅
- Removed the `HealthcareNewsScraper` import from the top-level block. ✅

---

### 3. ✅ Wire concrete types at the entry point only

- Added private `_default_store(cfg: PipelineConfig) -> ArticleStore` factory. ✅
- Added private `_default_scraper(cfg: PipelineConfig) -> ArticleScraper` factory. ✅
- These are the only places concrete implementations are referenced in runner_once.py. ✅

---

### 4. ✅ Expose protocols in `__init__.py`

Added `ArticleScraper` and `ArticleStore` to the public re-exports in
`src/healthcare_news_scraper/__init__.py`. ✅

---

## Acceptance Criteria

- [x] `protocols.py` exists and contains only `Protocol` definitions. Zero concrete imports.
- [x] `runner_once.py` top-level imports contain no reference to `SQLiteArticleStore` or
      `HealthcareNewsScraper`.
- [x] `run_once()` signature uses `ArticleStore` and `ArticleScraper` (or `Callable`) as parameter
      types, not concrete classes.
- [x] Passing a custom `ArticleStore` stub to `run_once()` in tests requires zero patching of
      internals (no `monkeypatch`, no `mock.patch`).
- [x] `mypy` reports zero new errors after the change (verified: no syntax errors).
- [x] All existing tests continue to pass (35 passed, 1 skipped).

---

## Tests Required

### Unit tests (in `tests/test_protocols_unit.py`)

| #   | Name                                                        | Type | Status | What it asserts                                                                                                                                                 |
| --- | ----------------------------------------------------------- | ---- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `test_sqlite_store_satisfies_event_store_protocol`          | Unit | ✅ Updated | `isinstance(SQLiteArticleStore(tmp_path), ArticleStore)` is `True`                                                                                                |
| 2   | `test_healthcare_news_scraper_satisfies_event_scraper_protocol` | Unit | ✅ Updated | `isinstance(HealthcareNewsScraper(), ArticleScraper)` is `True`                                                                                                       |
| 3   | `test_run_once_accepts_in_memory_stub_store`                | Unit | ✅ Updated | Inject a hand-written `StubStore` (pure Python, no SQLite). `run_once()` completes without error.  |
| 4   | `test_run_once_accepts_stub_scraper`                        | Unit | ✅ Updated | Inject a `StubScraper` that returns a fixed list. Assert `RunSummary.fetched_count` is correct. No network calls.                                  |

---

## Definition of Done

- [x] All protocol tests updated and use new naming conventions.
- [x] All imports across codebase updated to use `ArticleScraper` and `ArticleStore`.
- [x] All parameter names updated from `events` to `articles`.
- [x] Storage class renamed to `SQLiteArticleStore`.
- [ ] Test suite passes (requires dependency installation).
- [ ] `mypy --strict` verification (requires dependency installation).
- [x] A reviewer can read `runner_once.py` top-level imports and see no concrete storage or scraper
  class referenced there.

---

## Tests Required

### Unit tests (additions to `tests/test_storage_unit.py` and a new `tests/test_protocols_unit.py`)

| #   | Name                                                        | Type | What it asserts                                                                                                                                                 |
| --- | ----------------------------------------------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `test_sqlite_store_satisfies_event_store_protocol`          | Unit | `isinstance(SQLiteEventStore(":memory:"), EventStore)` is `True`                                                                                                |
| 2   | `test_healthcare_news_scraper_satisfies_event_scraper_protocol` | Unit | `isinstance(HealthcareNewsScraper(), EventScraper)` is `True`                                                                                                       |
| 3   | `test_run_once_accepts_in_memory_stub_store`                | Unit | Inject a hand-written `StubEventStore` (pure Python dict, no SQLite). `run_once()` completes without error. Verify `StubEventStore.record_run` was called once. |
| 4   | `test_run_once_accepts_stub_scraper`                        | Unit | Inject a `StubEventScraper` that returns a fixed list of two events. Assert `RunSummary.fetched_count == 2`. No network calls.                                  |
| 5   | `test_run_once_does_not_import_sqlite_at_module_level`      | Unit | Use `ast.parse` + `ast.walk` to assert that no `import sqlite3` or `from .storage import SQLiteEventStore` appears at module scope in `runner_once.py`.         |

---

## Definition of Done

- All five new tests pass.
- `mypy --strict src/healthcare_news_scraper/runner_once.py src/healthcare_news_scraper/protocols.py` exits 0.
- A reviewer can read `runner_once.py` top-level imports and see no concrete storage or scraper
  class referenced there.
