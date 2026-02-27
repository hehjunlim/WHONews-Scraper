# Technical Debt

## High Priority

### 1. Inconsistent Internal Naming
**Issue:** Protocol and class names use "Event" terminology while the domain is healthcare articles.

**Location:**
- `src/healthcare_news_scraper/protocols.py`: `EventScraper`, `EventStore`
- `src/healthcare_news_scraper/storage.py`: `SQLiteEventStore`

**Impact:** Confusing for developers, inconsistent with domain language

**Effort:** Medium (20+ files to update)

**Risk:** Medium (could break tests if not careful)

### 2. Variable Naming Throughout Codebase
**Issue:** Variables named `events` should be `articles` for consistency.

**Location:** Throughout `runner_once.py`, `storage.py`, test files

**Impact:** Medium - reduces code clarity

**Effort:** Medium (systematic search/replace needed)

**Risk:** Low (variable names are local)

### 3. Database Schema Unknown
**Issue:** Database table names may still reference "events" instead of "articles"

**Location:** `storage.py` SQL statements

**Impact:** High if changing (migration needed), Low if leaving as-is

**Investigation Needed:** Check actual SQL CREATE/INSERT statements

## Medium Priority

### 4. GitHub Repository Name
**Issue:** Repository still named `GarysGuide-Scraper` on GitHub

**Impact:** Low - just metadata

**Effort:** Low (GitHub rename feature)

**Risk:** Low (GitHub handles redirects)

### 5. Docker Image Name
**Issue:** Docker compose may reference old image names

**Location:** `docker-compose.yml`, `Dockerfile`, `deploy/k8s-cronjob.yaml`

**Impact:** Low - deployment configuration

**Effort:** Low

### 6. Test Fixtures Outdated
**Issue:** Test fixtures (`tests/fixtures/`) still have Gary's Guide HTML

**Location:**
- `tests/fixtures/sample_events_page.html`
- `tests/fixtures/sample_newsletter.html`

**Impact:** Low - tests still work but fixtures are misleading

**Effort:** Medium (need real WHO HTML samples)

## Low Priority

### 7. Sprint Documentation Relevance
**Issue:** Sprint plans were written for Gary's Guide context

**Question:** Should we keep them or create new healthcare-focused sprints?

**Impact:** Low - documentation only

**Decision Needed:** Archive vs. Keep vs. Rewrite

### 8. Code Comments May Reference Old Context
**Issue:** Inline comments might reference NYC events

**Effort:** Low (manual review)

**Impact:** Low

### 9. Example Outputs Outdated
**Issue:** Documentation may show example JSON with old event structure

**Impact:** Low - documentation accuracy

**Effort:** Low (update examples)

## Architecture Debt (From Sprint Plans)

These are improvements planned in the sprint documents:

1. **SRP Violations** (Sprint 07)
   - `scraper.py` has too many responsibilities
   - Need to extract filtering and formatting logic

2. **Long Functions** (Sprint 08)
   - Functions over 20 lines should be decomposed
   - Extract small, focused functions

3. **Error Handling** (Sprint 09)
   - Remove unsafe `get_events_safe` pattern
   - Implement proper exception hierarchy

4. **HTTP Abstraction** (Sprint 10)
   - Better test boundaries for HTTP calls
   - Dependency injection for HTTP client

5. **Docker Multi-Process** (Sprint 11)
   - Current Docker setup may run multiple processes
   - Should follow single-process container pattern

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-27 | Keep `EventScraper`/`EventStore` names temporarily | Focus on documentation first, defer internal refactoring |
| 2026-02-27 | Update all user-facing documentation | Users see package name, not internal protocols |
| 2026-02-27 | Delete transformation summary docs | No longer needed, cluttering workspace |

## Cleanup Checklist

When addressing technical debt, use this checklist:

- [ ] Run tests before changes: `pytest -v`
- [ ] Make changes systematically (one category at a time)
- [ ] Run tests after each category: `pytest -v`
- [ ] Update documentation to match code changes
- [ ] Run type checker: `mypy src/`
- [ ] Run linter: `ruff check src/`
- [ ] Update this document with completion status
- [ ] Commit with clear message explaining what debt was addressed
