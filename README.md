# healthcare_news_scraper

> Automated healthcare news aggregation from WHO and other sources — extract, filter, and persist medical news articles with a single command.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 📖 Background & Importance

Healthcare professionals, researchers, and data scientists need timely access to medical news from authoritative sources. However:

- **Manual monitoring is time-consuming** — Checking WHO and other healthcare news sites daily is inefficient
- **News gets buried** — Important outbreak alerts or research updates can be missed
- **Data silos exist** — Healthcare news isn't easily integrated into AI pipelines or analytical workflows
- **Historical tracking is difficult** — Understanding trends requires persistent storage of articles over time

**This tool solves these problems by:**

✅ **Automating collection** — Runs on a schedule (cron, Kubernetes) to continuously gather healthcare news  
✅ **Filtering intelligently** — Extract only articles matching your keywords (e.g., "outbreak", "vaccine", "research")  
✅ **Providing clean data** — Structured JSON output ready for AI analysis, dashboards, or alerts  
✅ **Maintaining history** — SQLite database tracks all articles across runs for trend analysis  
✅ **Being production-ready** — Built with error handling, retries, testing, and Docker deployment

**Use cases:**
- Monitor disease outbreaks and public health alerts
- Track medical research announcements
- Feed healthcare news into AI/ML pipelines
- Generate automated healthcare news digests
- Analyze trends in global health coverage

---

## 🚀 Quick Start

### Installation

```bash
# Via pip
pip install healthcare_news_scraper

# Or for development with Poetry
git clone https://github.com/atg25/HealthcareNews-Scraper.git
cd HealthcareNews-Scraper
poetry install
```

### Run Your First Scrape

**Option 1: Simple Python script**

```python
from healthcare_news_scraper import scrape_default_healthcare_news

# Scrape all current healthcare news
articles = scrape_default_healthcare_news(delay_seconds=1.5)
print(f"Found {len(articles)} articles")
print(articles[0])  # See the first article
```

**Option 2: Command-line with database persistence**

```bash
# Scrape and save to SQLite
DB_PATH=./healthcare_news.db poetry run healthcare-news-run-once

# Verify it worked
DB_PATH=./healthcare_news.db ./scripts/verify_db.sh
```

**Option 3: Docker (recommended for production)**

```bash
# Build and run
docker compose build scraper
docker compose run --rm scraper

# Schedule daily at 8 AM with cron
0 8 * * * cd /path/to/project && docker compose run --rm scraper
```

That's it! You now have automated healthcare news collection running.

---

## ✨ Features

### What This Tool Does

- **Scrapes** healthcare news websites (WHO News, etc.) and extracts structured article data
- **Filters** articles by keyword or category (e.g., "research", "policy", "outbreak", "vaccine")
- **Persists** every run and its results to a local SQLite database with full history
- **Formats** filtered articles as clean JSON ready for downstream use (AI pipelines, analytics, etc.)
- **Parses newsletter HTML** as a fallback data source when live scraping is not possible
- **Retries automatically** on transient network errors with configurable backoff
- **Runs as a one-shot container** — schedule it externally with cron or Kubernetes (no daemon processes)

### Article Data Structure

Each article contains five fields:

| Field      | Example                                         | Description                              |
| ---------- | ----------------------------------------------- | ---------------------------------------- |
| `title`    | `"New COVID-19 Variant Detected"`               | Article headline                         |
| `date`     | `"Wed, Mar 5"`                                  | Publication date                         |
| `category` | `"outbreak"` or `"research"` or `"policy"`      | Auto-categorized topic                   |
| `url`      | `"https://www.who.int/news/..."`                | Full article URL                         |
| `source`   | `"healthcare_web"` or `"healthcare_newsletter"` | How the article was obtained             |

---

## 📚 Usage Examples

## 📚 Usage Examples

### Basic Scraping

**Simple one-liner:**

```python
from healthcare_news_scraper import scrape_default_healthcare_news

articles = scrape_default_healthcare_news(delay_seconds=1.5)
# Returns: [{"title": ..., "date": ..., "category": ..., "url": ..., "source": ...}, ...]
```

**With more control using the class:**

```python
from healthcare_news_scraper import HealthcareNewsScraper

scraper = HealthcareNewsScraper(
    delay_seconds=1.0,    # Wait between requests (be polite to servers)
    timeout_seconds=10,   # Per-request timeout
)
articles = scraper.get_articles()
```

### Filtering Articles

**Filter by keyword:**

```python
from healthcare_news_scraper import filter_articles_by_keyword

# Get only research articles
research_articles = filter_articles_by_keyword(articles, "research")

# Get outbreak-related news
outbreak_articles = filter_articles_by_keyword(articles, "outbreak")

# Case-insensitive match on title or category
vaccine_news = filter_articles_by_keyword(articles, "vaccine")
```

### Export as JSON

```python
from healthcare_news_scraper import get_articles_category_json

json_str = get_articles_category_json(articles, category="research")
print(json_str)
# Pretty-printed JSON array of research-related articles
```

### Parse Newsletter HTML (Offline Mode)

If you have a healthcare newsletter saved as HTML (e.g., from your email client):

```python
from healthcare_news_scraper import parse_newsletter_html

with open("newsletter.html") as f:
    raw_html = f.read()

articles = parse_newsletter_html(raw_html)
# Returns article dicts with source="healthcare_newsletter"
# Automatically skips unsubscribe, social, and sponsor links
```

### Full Pipeline (Scrape + Persist)

Run the complete workflow with database persistence:

```bash
DB_PATH=./healthcare_news.db poetry run healthcare-news-run-once
```

This will:
1. Scrape healthcare news sources
2. Apply any configured keyword filter and article limit
3. Save run metadata and all articles to SQLite database
4. Print a summary

Verify the database:

```bash
DB_PATH=./healthcare_news.db ./scripts/verify_db.sh
```

---

## ⚙️ Configuration

All settings are controlled via **environment variables** (no config files needed).

| Variable                | Default                    | Description                                                                  |
| ----------------------- | -------------------------- | ---------------------------------------------------------------------------- |
| `DB_PATH`               | `/data/healthcare_news.db` | Path to the SQLite database file                                             |
| `SCRAPER_SEARCH_TERM`   | _(none)_                   | Keyword to filter article titles or categories (e.g., `research`, `outbreak`) |
| `SCRAPER_LIMIT`         | `0`                        | Max articles to keep per run (`0` = keep all)                                |
| `SCRAPER_STRATEGY`      | `web`                      | Scraper backend (`web` is the only current option)                           |
| `RETRY_ATTEMPTS`        | `3`                        | How many times to retry on a network failure                                 |
| `RETRY_BACKOFF_SECONDS` | `5`                        | Seconds to wait between retries (linear backoff)                             |
| `API_TOKEN`             | _(none)_                   | Reserved for a future API-based scraper strategy                             |

**Example — filter to research articles, cap at 20:**

```bash
SCRAPER_SEARCH_TERM=research SCRAPER_LIMIT=20 DB_PATH=./articles.db poetry run healthcare-news-run-once
```

---

## 🐳 Docker Deployment

The container runs **once and exits** (one-shot pattern). Schedule it externally — no cron daemon runs inside.

### Build and Run

```bash
# Build the image
docker compose build scraper

# Run one scrape pass
docker compose run --rm scraper

# Override configuration at runtime
docker compose run --rm \
  -e DB_PATH=/data/articles.db \
  -e SCRAPER_SEARCH_TERM=outbreak \
  scraper
```

### Schedule with Cron

**Host cron (runs daily at 8 AM):**

```cron
0 8 * * * cd /path/to/project && docker compose run --rm scraper
```

### Kubernetes CronJob

Deploy to Kubernetes for production scheduling:

```bash
kubectl apply -f deploy/k8s-cronjob.yaml
```

See [docs/RUNBOOK.md](docs/RUNBOOK.md) for detailed deployment instructions.

---

## 🏗️ Advanced Topics

### Database Schema

Articles are stored in three tables:

- **`runs`** — One row per pipeline execution (timestamp, status, source, attempts)
- **`products`** — Deduplicated article records (title + URL = unique key)
- **`product_snapshots`** — Links each run to the articles captured in that run

This design lets you:
- Query article history across runs
- Detect when articles appear or disappear
- Track scraper performance over time

### Error Handling

The package raises **typed domain exceptions** — no silent failures:

| Exception             | When It's Raised                                        |
| --------------------- | ------------------------------------------------------- |
| `ScraperNetworkError` | HTTP error, connection refused, or bad status code      |
| `ScraperTimeoutError` | Request timed out (subclass of `ScraperNetworkError`)   |
| `ScraperParseError`   | HTML structure could not be parsed into articles        |
| `StorageError`        | SQLite read/write failure                               |

**Behavior:**
- Transient errors (`ScraperNetworkError`) are **retried automatically**
- Non-transient errors **propagate immediately** (fail fast)

### Architecture

The package is split into **focused, single-purpose modules** following SOLID principles:

| Module                 | Responsibility                                           |
| ---------------------- | -------------------------------------------------------- |
| `scraper.py`           | HTTP fetching and HTML parsing of healthcare news pages  |
| `runner_once.py`       | Pipeline orchestration (scrape → filter → persist)       |
| `storage.py`           | SQLite persistence (`SQLiteArticleStore`)                |
| `filters.py`           | Keyword/category filtering logic                         |
| `formatters.py`        | JSON serialization for AI/downstream use                 |
| `newsletter_parser.py` | Parses newsletter HTML exports as a fallback             |
| `http.py`              | `requests` adapter — the only file that uses HTTP        |
| `protocols.py`         | `typing.Protocol` interfaces for all boundaries          |
| `exceptions.py`        | Domain exception hierarchy                               |
| `models.py`            | `HealthcareArticle` dataclass                            |
| `config.py`            | Loads configuration from environment variables           |
| `scheduler.py`         | Retry/backoff helpers                                    |

---

## 🛠️ Development

### Setup

```bash
# Clone and install
git clone https://github.com/atg25/HealthcareNews-Scraper.git
cd HealthcareNews-Scraper
poetry install

# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=healthcare_news_scraper

# Type checking
poetry run mypy src/

# Verify Docker build
./scripts/verify_build.sh
```

### Testing Philosophy

Tests use **injected HTTP doubles** — no real network calls, no `requests-mock`. This ensures:
- ✅ Fast test execution (no network latency)
- ✅ Deterministic results (no flaky tests)
- ✅ Offline development (works without internet)
- ✅ Clear boundaries (HTTP layer is isolated)

See [docs/TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md) for details.

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## 📖 Documentation

### 🚀 Getting Started
- 📋 **[Project Management](project_management/README.md)** — Task tracking, status, next steps ⭐ **Start here for development**
- ⚡ **[Quick Docker Test](docs/QUICK_DOCKER_TEST.md)** — 5-minute Docker quick start
- 📊 **[Docker Test Results](docs/DOCKER_TEST_RESULTS.md)** — Latest testing results and verification

### 🐳 Docker & Deployment
- 🧪 **[Docker Testing Guide](docs/DOCKER_TESTING.md)** — Complete Docker testing tutorial (8 steps)
- ☸️ **[Kubernetes Testing Guide](docs/DOCKER_KUBERNETES_TESTING.md)** — K8s deployment and testing (9 steps)
- 🚀 **[Runbook](docs/RUNBOOK.md)** — Deployment, scheduling, and operations

### 📚 Development & Architecture
- 🧪 **[Testing Strategy](docs/TESTING_STRATEGY.md)** — Test boundaries and design philosophy
- 🔗 **[Requirements Traceability](docs/TRACEABILITY.md)** — Requirement-to-code mapping
- ✅ **[Submission Checklist](docs/SUBMISSION_CHECKLIST.md)** — Project deliverable checklist

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙋 Support

- **Issues:** [GitHub Issues](https://github.com/atg25/HealthcareNews-Scraper/issues)
- **Documentation:** See `docs/` folder
- **Development:** See `project_management/` folder

---