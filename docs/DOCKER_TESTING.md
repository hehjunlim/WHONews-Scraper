# Docker Testing Tutorial

Complete guide to testing the Healthcare News Scraper with Docker.

---

## 🎯 Prerequisites

Before you begin, verify you have the required tools:

```bash
# Check Docker
docker --version
# Expected: Docker version 20.10+ or later

# Check Docker Compose
docker compose version
# Expected: Docker Compose version v2.0+ or later

# Check you're in the project directory
pwd
# Should show: /path/to/GarysGuide-Scraper
```

---

## 🏗️ Step 1: Build the Docker Image

### Build the image

```bash
docker compose build scraper
```

**What this does:**
- Downloads Python 3.12-slim base image
- Installs SQLite3
- Copies your source code into the image
- Installs the `healthcare_news_scraper` package
- Sets up the entrypoint script

**Expected output:**
```
[+] Building 15-30s
=> [1/7] FROM docker.io/library/python:3.12-slim
=> [2/7] RUN apt-get update && apt-get install...
=> [7/7] RUN pip install --no-cache-dir .
=> exporting to image
```

### Verify the image was created

```bash
docker images | grep scraper
```

**Expected output:**
```
garysguide-scraper-scraper   latest   1e8d566a73d3   2 minutes ago   200MB
```

---

## 🧪 Step 2: Test Run (Dry Run)

### Test with environment variables

Run a single scrape with custom configuration:

```bash
docker compose run --rm \
  -e SCRAPER_SEARCH_TERM=research \
  -e SCRAPER_LIMIT=5 \
  -e DB_PATH=/data/test_articles.db \
  scraper
```

**What this does:**
- Creates a temporary container
- Scrapes WHO news site
- Filters for articles containing "research"
- Limits results to 5 articles
- Saves to `/data/test_articles.db` inside container
- `--rm` automatically removes container after completion

**Expected output:**
```
INFO: Starting healthcare news scraper...
INFO: Fetching articles from WHO News...
INFO: Found 47 total articles
INFO: Filtering by keyword: research
INFO: After filtering: 5 articles (limit: 5)
INFO: Saving to database: /data/test_articles.db
INFO: Successfully stored 5 articles
INFO: Run completed successfully
```

### Test with different filters

**Get outbreak news:**
```bash
docker compose run --rm -e SCRAPER_SEARCH_TERM=outbreak scraper
```

**Get all articles (no filter):**
```bash
docker compose run --rm -e SCRAPER_SEARCH_TERM="" scraper
```

**Limit to 10 articles:**
```bash
docker compose run --rm -e SCRAPER_LIMIT=10 scraper
```

---

## 📊 Step 3: Verify Data Persistence

### Check what's in the Docker volume

The data is stored in a Docker volume named `healthcare_news_data`.

**List all volumes:**
```bash
docker volume ls | grep healthcare
```

**Expected output:**
```
local     healthcare_news_data
```

### Inspect the volume

```bash
docker volume inspect healthcare_news_data
```

**Expected output:**
```json
[
    {
        "CreatedAt": "2026-02-27T...",
        "Driver": "local",
        "Mountpoint": "/var/lib/docker/volumes/healthcare_news_data/_data",
        "Name": "healthcare_news_data"
    }
]
```

### Access the database file

**Option 1: Run a shell in the container**
```bash
docker compose run --rm --entrypoint /bin/bash scraper
```

Then inside the container:
```bash
# Check if database exists
ls -lh /data/

# Query the database
sqlite3 /data/healthcare_news.db "SELECT COUNT(*) FROM products;"

# See recent runs
sqlite3 /data/healthcare_news.db "SELECT * FROM runs ORDER BY created_at DESC LIMIT 5;"

# Exit the container
exit
```

**Option 2: Use the built-in verification script**
```bash
docker compose run --rm --entrypoint /app/scripts/verify_db.sh scraper
```

**Expected output:**
```
=== Database Verification ===
Database: /data/healthcare_news.db
Size: 24K

=== Table Counts ===
runs: 3
products: 45
product_snapshots: 87

=== Recent Runs ===
run_id | created_at | status | source | total_articles
1      | 2026-02-27 10:00:00 | success | web | 20
2      | 2026-02-27 11:00:00 | success | web | 15
3      | 2026-02-27 12:00:00 | success | web | 10
```

---

## 🔄 Step 4: Test Automated Scheduling

### Test with Docker Compose (Simple)

Run the scraper using default settings from `docker-compose.yml`:

```bash
docker compose run --rm scraper
```

This uses environment variables defined in `docker-compose.yml`:
- `DB_PATH=/data/healthcare_news.db`
- `SCRAPER_STRATEGY=web`
- etc.

### Simulate Scheduled Runs

Run multiple times to simulate a scheduled job:

```bash
# Run 1
docker compose run --rm scraper
sleep 5

# Run 2
docker compose run --rm scraper
sleep 5

# Run 3
docker compose run --rm scraper
```

**Verify multiple runs:**
```bash
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db 'SELECT run_id, created_at, total_articles FROM runs;'"
```

---

## ⏰ Step 5: Test with Host Cron

### Set up a cron job (macOS/Linux)

Edit your crontab:

```bash
crontab -e
```

Add this line (runs daily at 8:00 AM):

```cron
0 8 * * * cd /Users/hehjunlim/IS421/GarysGuide-Scraper && docker compose run --rm scraper >> /tmp/healthcare-scraper.log 2>&1
```

**Explanation:**
- `0 8 * * *` = Every day at 8:00 AM
- `cd /Users/hehjunlim/IS421/GarysGuide-Scraper` = Navigate to project
- `docker compose run --rm scraper` = Run the scraper
- `>> /tmp/healthcare-scraper.log 2>&1` = Log output

### Test the cron job immediately

Instead of waiting for 8 AM, run it now:

```bash
cd /Users/hehjunlim/IS421/GarysGuide-Scraper && \
docker compose run --rm scraper >> /tmp/healthcare-scraper.log 2>&1
```

### Check the log file

```bash
cat /tmp/healthcare-scraper.log
```

### View cron job for testing every 5 minutes

For testing purposes, you can run it more frequently:

```cron
*/5 * * * * cd /Users/hehjunlim/IS421/GarysGuide-Scraper && docker compose run --rm scraper >> /tmp/healthcare-scraper.log 2>&1
```

**Remember to change it back to daily after testing!**

---

## 🚀 Step 6: Advanced Testing

### Test with custom configuration file

Create a `.env` file in the project root:

```bash
cat > .env << EOF
SCRAPER_SEARCH_TERM=vaccine
SCRAPER_LIMIT=20
DB_PATH=/data/vaccine_news.db
RETRY_ATTEMPTS=5
RETRY_BACKOFF_SECONDS=10
EOF
```

Run with the `.env` file (Docker Compose loads it automatically):

```bash
docker compose run --rm scraper
```

### Test error handling

**Test with bad configuration:**
```bash
docker compose run --rm -e DB_PATH=/read-only/test.db scraper
```

This should fail gracefully with a `StorageError`.

**Expected output:**
```
ERROR: StorageError: Cannot write to database: /read-only/test.db
ERROR: Permission denied
```

### Test network retry logic

You can't easily simulate network failures, but you can verify the retry configuration works:

```bash
docker compose run --rm \
  -e RETRY_ATTEMPTS=5 \
  -e RETRY_BACKOFF_SECONDS=2 \
  scraper
```

If there's a network issue, you'll see:
```
WARNING: Network error, retrying (attempt 1/5)...
WARNING: Waiting 2 seconds before retry...
```

### Monitor container resources

While a scrape is running (in one terminal):
```bash
docker compose run --rm scraper
```

In another terminal, monitor resource usage:
```bash
docker stats
```

**Expected output:**
```
CONTAINER ID   NAME                       CPU %   MEM USAGE / LIMIT
a1b2c3d4e5f6   healthcare-news-scraper    2.5%    45MiB / 1.95GiB
```

---

## 📝 Step 7: Verify Database Contents

### Run SQL queries against the database

```bash
# Count total articles
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db 'SELECT COUNT(*) as total FROM products;'"

# Show recent articles
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db 'SELECT title, date, category FROM products LIMIT 5;'"

# Show runs by status
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db 'SELECT status, COUNT(*) as count FROM runs GROUP BY status;'"

# Show articles by category
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db 'SELECT category, COUNT(*) as count FROM products GROUP BY category;'"
```

### Export data to JSON

```bash
docker compose run --rm --entrypoint bash scraper -c \
  "sqlite3 /data/healthcare_news.db '.mode json' 'SELECT * FROM products LIMIT 10;'" > articles.json

cat articles.json
```

---

## 🧹 Step 8: Cleanup

### Remove containers

Docker Compose with `--rm` automatically removes containers, but if you ran without it:

```bash
docker ps -a | grep healthcare-news-scraper
docker rm <container_id>
```

### Remove the volume (WARNING: Deletes all data!)

```bash
docker volume rm healthcare_news_data
```

### Remove the image

```bash
docker rmi garysguide-scraper-scraper
```

### Remove everything and start fresh

```bash
docker compose down -v
docker rmi garysguide-scraper-scraper
```

Then rebuild:
```bash
docker compose build scraper
```

---

## 🐛 Troubleshooting

### Issue: Build fails with "No module named 'healthcare_news_scraper'"

**Solution:** Make sure you're in the project root directory and `pyproject.toml` exists.

```bash
ls -la pyproject.toml
docker compose build scraper --no-cache
```

### Issue: Container exits immediately without output

**Solution:** Check the container logs:

```bash
docker compose logs scraper
```

### Issue: Database file not found

**Solution:** The volume might not be mounted correctly. Check volume:

```bash
docker volume inspect healthcare_news_data
```

### Issue: Permission denied when writing to database

**Solution:** The `/data` directory should be automatically created. If not:

```bash
docker compose run --rm --entrypoint bash scraper -c "mkdir -p /data && ls -la /data"
```

### Issue: Network timeout errors

**Solution:** Increase retry settings:

```bash
docker compose run --rm \
  -e RETRY_ATTEMPTS=10 \
  -e RETRY_BACKOFF_SECONDS=15 \
  scraper
```

---

## ✅ Success Criteria

You've successfully tested the Docker setup when:

- [x] Image builds without errors
- [x] Container runs and scrapes articles
- [x] Database file is created in the volume
- [x] Articles are stored in the database
- [x] Multiple runs append new data
- [x] Environment variables override defaults
- [x] Container exits cleanly after completion
- [x] Logs show clear success/error messages

---

## 📚 Next Steps

1. **Set up production scheduling** - See [Kubernetes tutorial](DOCKER_KUBERNETES_TESTING.md)
2. **Monitor logs** - Set up log aggregation (see [docs/RUNBOOK.md](../docs/RUNBOOK.md))
3. **Backup data** - Create automated database backups
4. **Scale up** - Add more news sources or deploy to cloud

---

## 💡 Pro Tips

- **Use `.env` files** for local development configurations
- **Use volume mounts** for easy database access: `-v $(pwd)/data:/data`
- **Tag your images** for version control: `docker tag scraper:latest scraper:v1.0.0`
- **Check logs regularly** when running via cron
- **Test locally first** before scheduling automated runs
- **Monitor disk usage** - databases can grow over time

Happy testing! 🚀
