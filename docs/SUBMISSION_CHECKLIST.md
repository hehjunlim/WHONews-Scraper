# Submission Checklist

## Final Validation Commands

- [ ] `poetry install`
- [ ] `poetry run pytest`
- [ ] `DB_PATH=./local_articles.db poetry run healthcare-news-run-once`
- [ ] `DB_PATH=./local_articles.db ./scripts/verify_db.sh`
- [ ] `docker compose up --build -d`
- [ ] `docker compose logs -f scheduler`
- [ ] `docker compose exec scheduler /app/scripts/verify_db.sh /data/healthcare_news.db`
- [ ] Restart verification: `docker compose restart scheduler` and verify data still exists

## Pass/Fail Summary

- [ ] Scraper runs and writes to SQLite
- [ ] Scheduled runs occur automatically
- [ ] Docker deployment works
- [ ] DB persists across restarts (named volume)
- [ ] Tests pass
- [ ] Docs are sufficient for a new user
