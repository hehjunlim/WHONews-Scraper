# Frontend Examples

This directory contains sample frontends showing how to display healthcare news scraped by the WHO News Scraper.

## Files

### `frontend_sample.html`
A complete, self-contained HTML page with embedded CSS and JavaScript showing today's healthcare news.

**Features:**
- Modern, responsive design
- Category filtering (Research, Outbreak, Policy, Public Health)
- Article cards with color-coded categories
- Sample data showing 12 articles
- Click to open full articles in new tab

**To view:**
```bash
open examples/frontend_sample.html
# or
python -m http.server 8000
# then navigate to http://localhost:8000/examples/frontend_sample.html
```

### `generate_frontend.py`
Python script that scrapes REAL data from WHO and generates an HTML page with live results.

**Usage:**
```bash
# Make sure you're in the project root
cd /path/to/WHONews-Scraper

# Run the generator
python examples/generate_frontend.py

# This will:
# 1. Scrape latest WHO news
# 2. Generate todays_news.html with real data
# 3. Open it in your default browser
```

**Output:**
- Creates `examples/todays_news.html` with today's scraped articles
- Automatically opens in browser
- Refresh the page by running the script again

### `styles.css`
Separate CSS stylesheet used by the generated HTML.

**Features:**
- Purple gradient background
- Card-based layout
- Smooth animations and hover effects
- Mobile-responsive design
- Color-coded categories

## Integration Examples

### 1. Static Site Generation

Generate a static news page daily with cron:

```bash
# Add to your crontab:
0 8 * * * cd /path/to/WHONews-Scraper && python examples/generate_frontend.py
```

This creates a fresh `todays_news.html` every morning at 8 AM.

### 2. Flask/FastAPI Backend

Serve articles from a REST API:

```python
from flask import Flask, jsonify
from healthcare_news_scraper import scrape_default_healthcare_news

app = Flask(__name__)

@app.route('/api/articles')
def get_articles():
    articles = scrape_default_healthcare_news()
    return jsonify(articles)

if __name__ == '__main__':
    app.run(debug=True)
```

Then update the frontend's `fetchLatestNews()` function to call `/api/articles`.

### 3. Database Integration

Pull from your SQLite database instead of live scraping:

```python
import sqlite3
import json
from pathlib import Path

def get_todays_articles_from_db(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get articles from the latest run
    cursor.execute("""
        SELECT p.title, ps.event_date, ps.category, p.url, p.source
        FROM product_snapshots ps
        JOIN products p ON ps.product_id = p.id
        JOIN runs r ON ps.run_id = r.id
        WHERE r.id = (SELECT MAX(id) FROM runs)
    """)
    
    articles = []
    for row in cursor.fetchall():
        articles.append({
            "title": row[0],
            "date": row[1],
            "category": row[2],
            "url": row[3],
            "source": row[4]
        })
    
    conn.close()
    return articles
```

## Customization

### Change Colors

Edit `styles.css` to customize the color scheme:

```css
/* Background gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Category colors */
.article-card.research { border-left-color: #4299e1; }
.article-card.outbreak { border-left-color: #f56565; }
```

### Add More Filters

Update the filter buttons in the HTML:

```html
<button class="filter-btn" data-category="vaccine">Vaccines</button>
<button class="filter-btn" data-category="clinical">Clinical Trials</button>
```

### Mobile Optimization

The design is already responsive, but you can adjust breakpoints in `styles.css`:

```css
@media (max-width: 768px) {
    /* Mobile styles */
}
```

## Production Deployment

### 1. Nginx Static Hosting

```nginx
server {
    listen 80;
    server_name news.example.com;
    
    root /var/www/healthcare-news;
    index todays_news.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

### 2. GitHub Pages

1. Push generated HTML to `gh-pages` branch
2. Enable GitHub Pages in repository settings
3. Access at `https://username.github.io/WHONews-Scraper/`

### 3. Docker + Nginx

Create a Dockerfile:

```dockerfile
FROM nginx:alpine
COPY examples/todays_news.html /usr/share/nginx/html/index.html
COPY examples/styles.css /usr/share/nginx/html/styles.css
EXPOSE 80
```

## Screenshots

The frontend displays:
- **Header** with date badge and statistics
- **Filter bar** to show only specific categories
- **Article grid** with card-based layout
- **Color-coded categories** for easy visual scanning
- **Floating refresh button** to reload data

Each article card shows:
- Category badge (color-coded)
- Article title
- Publication date
- Source (healthcare_web or healthcare_newsletter)
- Read more link

## Contributing

To improve the frontend examples:

1. Fork the repository
2. Make your changes in the `examples/` directory
3. Test with real scraped data
4. Submit a pull request

Ideas for enhancements:
- Dark mode toggle
- Search functionality
- Date range filtering
- Export to PDF
- Social sharing buttons
- Article bookmarking
