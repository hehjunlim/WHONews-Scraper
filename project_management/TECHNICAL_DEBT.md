# Technical Debt

## High Priority

### 1. ✅ **RESOLVED** - Inconsistent Internal Naming
**Status:** COMPLETED February 27, 2026

**Original Issue:** Protocol and class names used "Event" terminology while the domain is healthcare articles.

**Resolution:**
- ✅ `EventScraper` → `ArticleScraper` in `protocols.py`
- ✅ `EventStore` → `ArticleStore` in `protocols.py`
- ✅ `SQLiteEventStore` → `SQLiteArticleStore` in `storage.py`
- ✅ Updated 20+ files with new imports
- ✅ All tests passing (35 passed, 1 skipped)

### 2. ✅ **RESOLVED** - Variable Naming Throughout Codebase
**Status:** COMPLETED February 27, 2026

**Original Issue:** Variables named `events` should be `articles` for consistency.

**Resolution:**
- ✅ Updated `storage.py` parameter from `events` to `articles`
- ✅ Updated local variables `event_list` → `article_list`
- ✅ Updated loop variables `event` → `article`
- ✅ Updated protocol definitions

### 3. **NEW** - Database Schema Legacy Naming
**Status:** DOCUMENTED - No immediate action required

**Issue:** Database schema contains legacy field and table names from Gary's Guide system:
- **Field:** `event_date` in `product_snapshots` table (stores article publication date)
- **Table:** `products` (stores articles)
- **Table:** `product_snapshots` (stores article data snapshots)

**Location:** `src/healthcare_news_scraper/storage.py` - SCHEMA_SQL

**Impact:** 
- Low for new installations
- High for existing databases (would require migration)

**Current Behavior:**
```python
# The event_date field stores: article.get("date", "")
# Products table stores: healthcare articles
# Product_snapshots stores: article data at observation time
```

**Recommended Action:**
- **Option A (Breaking Change):** Create migration script to rename tables/fields
  - `products` → `articles`
  - `product_snapshots` → `article_snapshots`
  - `event_date` → `publish_date` or `article_date`
  - Effort: High (migration + testing)
  - Risk: High (data migration, backward compatibility)

- **Option B (Current Approach - RECOMMENDED):** 
  - Leave schema as-is for backward compatibility
  - Document that "products" means "articles" in this context
  - New installations will use these table names
  - Effort: None
  - Risk: None

**Decision:** Option B - Document but don't change. The table names are internal implementation details not exposed to users.

## Medium Priority

### 4. GitHub Repository Name
**Issue:** Repository still named `GarysGuide-Scraper` on GitHub

**Current:** `hehjunlim/GarysGuide-Scraper`
**Desired:** `hehjunlim/WHONews-Scraper`

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
