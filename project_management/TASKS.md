# Task Board

## 🟢 Completed

- [x] Transform codebase from Gary's Guide NYC events to WHO Healthcare News scraper
- [x] Rename package directory: `garys_nyc_events` → `healthcare_news_scraper`
- [x] Update all import statements across test files
- [x] Update `pyproject.toml` configuration
- [x] Update Docker and Kubernetes configurations
- [x] Update all documentation files (README, CHANGELOG, etc.)
- [x] Update sprint planning documents
- [x] Delete transformation summary documents
- [x] Update GitHub repository URLs in `pyproject.toml`

## 🟡 In Progress

None currently

## 🔴 To Do

### High Priority
- [ ] Rename internal protocol/class names for consistency
  - [ ] `EventScraper` → `ArticleScraper` in `protocols.py`
  - [ ] `EventStore` → `ArticleStore` in `protocols.py`
  - [ ] `SQLiteEventStore` → `SQLiteArticleStore` in `storage.py`
  - [ ] Update all imports and references (20+ files)
- [ ] Update variable names `events` → `articles` throughout codebase
- [ ] Run full test suite to verify all changes work
- [ ] Update database schema if needed (check if table names reference "events")

### Medium Priority
- [ ] Review and update inline code comments for healthcare context
- [ ] Update logging messages to use healthcare terminology
- [ ] Review SQL queries and table names in `storage.py`
- [ ] Update Docker image name in deployment files
- [ ] Consider renaming GitHub repository: `GarysGuide-Scraper` → `HealthcareNews-Scraper`

### Low Priority
- [ ] Update example outputs in documentation
- [ ] Add healthcare-specific documentation/examples
- [ ] Review and update test fixture data
- [ ] Update sprint plans to reflect healthcare news context (if keeping them)

## 📋 Backlog

- Implement features from sprint plans (sprints 07-11)
- Add more healthcare news sources beyond WHO
- Enhance filtering capabilities for medical categories
- Add data validation for healthcare article schemas
- Improve error handling and logging
