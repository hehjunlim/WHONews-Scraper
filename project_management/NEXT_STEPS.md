# Next Steps

## Immediate Actions (Next Session)

### 1. Run Test Suite ⏱️ 5 min
```bash
poetry install
poetry run pytest -v
```
**Why:** Verify that all import changes and transformations haven't broken anything.

### 2. Review Database Schema ⏱️ 10 min
- Check `storage.py` for table names
- Look for any SQL that references "events" table
- Run `scripts/verify_db.sh` if available
- Check `sql/verify_schema.sql`

**Files to check:**
- `src/healthcare_news_scraper/storage.py`
- `scripts/sql/*.sql`

### 3. Decide on Internal Naming ⏱️ 5 min
**Question:** Should we rename internal classes/protocols for consistency?

**Option A: Rename Everything** (Recommended for long-term maintainability)
- Pros: Complete consistency, easier for new developers
- Cons: Touches 20+ files, risk of breaking things
- Effort: ~30 minutes

**Option B: Leave Internal Names**
- Pros: Less risk, faster
- Cons: Confusing for future maintenance
- Effort: 0 minutes

**Recommendation:** Option A - Do it now while context is fresh.

## If Choosing Option A: Rename Internal Names

### Step 1: Update Protocols ⏱️ 15 min
1. `protocols.py`:
   - `EventScraper` → `ArticleScraper`
   - `EventStore` → `ArticleStore`

2. Update imports in all files:
   - `runner_once.py`
   - `__init__.py`
   - All test files (10 files)

### Step 2: Update Storage Class ⏱️ 10 min
1. `storage.py`:
   - `SQLiteEventStore` → `SQLiteArticleStore`

2. Update imports:
   - `runner_once.py`
   - Test files
   - Sprint documentation (if keeping accurate)

### Step 3: Update Variable Names ⏱️ 20 min
Search and replace `events` → `articles` in:
- Function parameters
- Local variables
- Comments
- (Be careful not to change "events" in historical context like "events table")

### Step 4: Test Everything ⏱️ 5 min
```bash
poetry run pytest -v
poetry run mypy src/
```

## Future Sessions

### Session 2: Code Quality
- Address sprint 07: SRP decomposition
- Extract small functions (sprint 08)
- Improve error handling (sprint 09)

### Session 3: Testing & Boundaries
- HTTP abstraction improvements (sprint 10)
- Test boundary implementation

### Session 4: Deployment
- Docker single process (sprint 11)
- Deploy to production
- Update GitHub repository name

## Questions to Resolve

1. Should we keep the sprint planning documents or archive them?
2. Do we want to rename the GitHub repository?
3. Are we keeping the "Gary's Guide" references in git history or squashing?
4. Should we add more healthcare news sources beyond WHO?

## Resources

- Sprint plans: `sprints/`
- Current tests: `tests/`
- Documentation: `docs/`
- Database verification: `scripts/verify_db.sh`
