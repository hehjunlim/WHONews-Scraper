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
# Check cron schedule
docker exec healthcare-news-scheduler crontab -l

# View cron execution logs
docker exec healthcare-news-scheduler tail -f /var/log/cron.log

# View scheduler container logs
docker logs healthcare-news-scheduler --follow

# Restart scheduler
docker compose restart scheduler

# Stop scheduler
docker compose stop scheduler

# Change schedule (edit .env or set environment variable)
CRON_SCHEDULE="0 8 * * *" docker compose up -d scheduler

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

## 🎨 Frontend Sample

A complete, modern web interface is included to visualize today's healthcare news!

### Quick Preview

![Sample Frontend](https://via.placeholder.com/800x400/667eea/ffffff?text=WHO+Healthcare+News+Dashboard)

**Features:**
- 📊 Real-time article display with category filtering
- 🎨 Modern, responsive design with purple gradient theme
- 🏷️ Color-coded categories (Research, Outbreak, Policy, Public Health)
- 📱 Mobile-friendly card-based layout
- 🔄 Auto-refresh capability

### View the Sample

**Option 1: Static Sample (with demo data)**
```bash
# Open the self-contained sample HTML
open examples/frontend_sample.html
```

**Option 2: Generate with Real Data**
```bash
# Scrape live WHO news and generate HTML
python examples/generate_frontend.py

# This will:
# 1. Fetch latest articles from WHO
# 2. Generate todays_news.html with real data  
# 3. Open in your default browser
```

### Integration Example

```python
from healthcare_news_scraper import scrape_default_healthcare_news
import json

# Scrape articles
articles = scrape_default_healthcare_news()

# Generate JSON for frontend
articles_json = json.dumps(articles, indent=2)
print(f"Found {len(articles)} articles for your dashboard!")
```

**See [examples/README.md](examples/README.md) for:**
- Complete integration guide
- Flask/FastAPI backend examples
- Database integration patterns
- Customization instructions
- Production deployment options

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

#### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER                         │
│                         (runner_once.py)                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 1. Load config    2. Scrape    3. Filter    4. Persist       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│   SCRAPER    │          │   FILTERS    │          │   STORAGE    │
│  (scraper.py)│          │ (filters.py) │          │ (storage.py) │
│              │          │              │          │              │
│ Implements:  │          │ Implements:  │          │ Implements:  │
│ ArticleScraper│         │ • Keyword    │          │ ArticleStore │
│              │          │   filtering  │          │              │
└──────┬───────┘          │ • Category   │          └──────┬───────┘
       │                  │   filtering  │                 │
       │ uses             └──────────────┘                 │ uses
       ▼                                                    ▼
┌──────────────┐                                   ┌──────────────┐
│     HTTP     │                                   │   MODELS     │
│   (http.py)  │                                   │ (models.py)  │
│              │                                   │              │
│ Implements:  │                                   │ HealthcareArticle│
│ HttpClient   │                                   │  dataclass   │
│              │                                   └──────────────┘
│ Wraps:       │
│ requests lib │
└──────────────┘

                    DATA FLOW: WHO News → HTTP → Parser → Filter → SQLite
```

#### Source Tree

```
WHONews-Scraper/
├── src/
│   └── healthcare_news_scraper/
│       ├── __init__.py              # Public API exports
│       ├── config.py                # Environment variable configuration
│       ├── exceptions.py            # Domain exception hierarchy
│       ├── filters.py               # Keyword/category filtering
│       ├── formatters.py            # JSON output formatting
│       ├── http.py                  # HTTP client (only file importing requests)
│       ├── models.py                # HealthcareArticle dataclass
│       ├── newsletter_parser.py     # Newsletter HTML parsing
│       ├── protocols.py             # typing.Protocol interfaces (DIP boundaries)
│       ├── runner_once.py           # Main pipeline orchestration
│       ├── scheduler.py             # Retry/backoff helpers
│       ├── scraper.py               # Web scraping implementation
│       └── storage.py               # SQLite persistence
│
├── tests/
│   ├── __init__.py
│   ├── http_doubles.py              # Test doubles for HTTP layer
│   ├── test_e2e_live.py             # Live integration test (skipped by default)
│   ├── test_filter_unit.py          # Filter logic tests
│   ├── test_newsletter_parser_unit.py
│   ├── test_package_unit.py         # Package imports test
│   ├── test_protocols_unit.py       # Protocol compliance tests
│   ├── test_public_api_unit.py      # Public API tests
│   ├── test_scheduler_unit.py       # Retry logic tests
│   ├── test_scraper_unit.py         # Scraping logic tests
│   ├── test_storage_unit.py         # Database persistence tests
│   └── fixtures/
│       ├── sample_events_page.html  # Test fixture for scraper
│       └── sample_newsletter.html   # Test fixture for newsletter parser
│
├── docs/
│   ├── DOCKER_KUBERNETES_TESTING.md
│   ├── DOCKER_TESTING.md
│   ├── DOCKER_TEST_RESULTS.md
│   ├── QUICK_DOCKER_TEST.md
│   ├── RUNBOOK.md
│   ├── SUBMISSION_CHECKLIST.md
│   ├── TESTING_STRATEGY.md
│   └── TRACEABILITY.md
│
├── project_management/
│   ├── README.md
│   ├── NEXT_STEPS.md
│   ├── SESSION_LOG.md
│   ├── STATUS.md
│   ├── TASKS.md
│   └── TECHNICAL_DEBT.md
│
├── sprints/
│   ├── sprint_plan.md
│   ├── active/                      # Empty - all sprints complete
│   ├── completed/                   # Completed code quality sprints
│   │   ├── sprint_06_dip_protocols.md
│   │   ├── sprint_07_srp_decompose_scraper.md
│   │   ├── sprint_08_extract_small_functions.md
│   │   ├── sprint_09_error_handling.md
│   │   ├── sprint_10_test_boundaries_http_abstraction.md
│   │   └── sprint_11_docker_single_process.md
│   └── planned/                     # Empty - all planned work complete
│
├── scripts/
│   ├── build_review_bundle.sh       # Create submission bundle
│   ├── run_once_entrypoint.sh       # Docker entrypoint
│   ├── verify_build.sh              # Verify Docker build
│   ├── verify_db.sh                 # Check SQLite database
│   └── sql/
│       ├── verify_latest_runs.sql
│       ├── verify_schema.sql
│       └── verify_snapshot_counts.sql
│
├── deploy/
│   └── k8s-cronjob.yaml             # Kubernetes CronJob manifest
│
├── examples/                         # 🎨 Frontend samples and integration guides
│   ├── README.md                    # Frontend documentation and deployment guide
│   ├── frontend_sample.html         # Self-contained demo with sample data
│   ├── generate_frontend.py         # Generate HTML with real scraped data
│   └── styles.css                   # Stylesheet for generated pages
│
├── Dockerfile                        # Single-process container (run once & exit)
├── docker-compose.yml                # Local development Docker config
├── pyproject.toml                    # Poetry dependencies and config
├── README.md                         # This file
├── CHANGELOG.md                      # Version history
├── CONTRIBUTING.md                   # Development guidelines
└── LICENSE                           # MIT License
```

#### Module Responsibilities

The package is split into **focused, single-purpose modules** following SOLID principles:

| Module                 | Responsibility                                           | Protocol/Interface       |
| ---------------------- | -------------------------------------------------------- | ------------------------ |
| `scraper.py`           | HTTP fetching and HTML parsing of healthcare news pages  | `ArticleScraper`         |
| `runner_once.py`       | Pipeline orchestration (scrape → filter → persist)       | Uses protocols           |
| `storage.py`           | SQLite persistence (`SQLiteArticleStore`)                | `ArticleStore`           |
| `filters.py`           | Keyword/category filtering logic                         | Pure function            |
| `formatters.py`        | JSON serialization for AI/downstream use                 | Pure function            |
| `newsletter_parser.py` | Parses newsletter HTML exports as a fallback             | Pure function            |
| `http.py`              | `requests` adapter — the only file that uses HTTP        | `HttpClient`             |
| `protocols.py`         | `typing.Protocol` interfaces for all boundaries          | Defines abstractions     |
| `exceptions.py`        | Domain exception hierarchy                               | Exception classes        |
| `models.py`            | `HealthcareArticle` dataclass                            | Data model               |
| `config.py`            | Loads configuration from environment variables           | Configuration dataclass  |
| `scheduler.py`         | Retry/backoff helpers                                    | Utility functions        |

**Design Principles:**
- **Dependency Inversion:** High-level modules depend on abstractions (protocols), not concrete implementations
- **Single Responsibility:** Each module has one clear purpose
- **Open/Closed:** Easy to extend (new scrapers, new storage) without modifying existing code
- **Interface Segregation:** Protocols define minimal, focused contracts
- **Dependency Injection:** All dependencies injected, making testing simple

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
- 🎨 **[Frontend Examples](examples/README.md)** — Sample web interfaces, integration guides, deployment options ⭐ **Start here for UI**
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
