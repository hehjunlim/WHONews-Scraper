# Quick Docker Test Guide

**Fast 5-minute Docker testing guide** — Get started immediately!

---

## ⚡ Quick Test (60 seconds)

### 1. Build the image

```bash
docker compose build scraper
```

⏱️ **Takes:** 15-30 seconds (first time may take longer)

### 2. Run a test scrape

```bash
docker compose run --rm -e SCRAPER_LIMIT=5 scraper
```

⏱️ **Takes:** 20-40 seconds

**✅ Success looks like:**
```
INFO: Starting healthcare news scraper...
INFO: Fetching articles from WHO News...
INFO: Found XX total articles
INFO: Saving to database: /data/healthcare_news.db
INFO: Successfully stored 5 articles
INFO: Run completed successfully
```

### 3. Verify data was saved

```bash
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db 'SELECT COUNT(*) FROM products;'"
```

**✅ Should show:** `5` (or however many articles were scraped)

---

## 🎯 Common Test Scenarios

### Test with different filters

**Filter for outbreak news:**
```bash
docker compose run --rm -e SCRAPER_SEARCH_TERM=outbreak -e SCRAPER_LIMIT=10 scraper
```

**Filter for research:**
```bash
docker compose run --rm -e SCRAPER_SEARCH_TERM=research -e SCRAPER_LIMIT=10 scraper
```

**Get all articles (no limit):**
```bash
docker compose run --rm -e SCRAPER_LIMIT=0 scraper
```

### Check what's in the database

```bash
# Count articles
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db 'SELECT COUNT(*) FROM products;'"

# Show recent articles
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db 'SELECT title, category FROM products LIMIT 5;'"

# Show all runs
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db 'SELECT run_id, created_at, total_articles FROM runs;'"
```

---

## 🔄 Test Automated Scheduling

### Simulate multiple scheduled runs

```bash
# Run 1
echo "Run 1..."
docker compose run --rm scraper

# Wait a bit
sleep 3

# Run 2
echo "Run 2..."
docker compose run --rm scraper

# Run 3
echo "Run 3..."
docker compose run --rm scraper
```

### Verify multiple runs were recorded

```bash
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db 'SELECT COUNT(*) FROM runs;'"
```

**✅ Should show:** `3` (or the number of runs you did)

---

## 🧹 Cleanup After Testing

### Remove test data

```bash
# Remove the Docker volume (deletes all data)
docker compose down -v
```

### Remove the image

```bash
docker rmi garysguide-scraper-scraper
```

---

## ❓ Troubleshooting Quick Fixes

### Build fails?

```bash
# Clean build (no cache)
docker compose build --no-cache scraper
```

### Need to see what went wrong?

```bash
# Run with shell access
docker compose run --rm --entrypoint bash scraper

# Inside container, run manually
/app/scripts/run_once_entrypoint.sh
```

### Database not persisting?

```bash
# Check if volume exists
docker volume ls | grep healthcare

# Inspect the volume
docker volume inspect healthcare_news_data
```

---

## 📖 Full Documentation

For complete testing instructions, see:
- **[Full Docker Testing Guide](DOCKER_TESTING.md)** - Comprehensive Docker testing
- **[Kubernetes Testing Guide](DOCKER_KUBERNETES_TESTING.md)** - K8s deployment and testing

---

## ✅ You're Ready!

If all the above worked, you've successfully tested the Docker setup! 🎉

**Next steps:**
1. Set up automated scheduling (cron or Kubernetes)
2. Configure monitoring and alerts
3. Deploy to production

See the full testing guides for details!
