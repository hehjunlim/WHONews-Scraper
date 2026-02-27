#!/usr/bin/env python3
"""
Sample script to generate today's news front-end with real data from the scraper.

This demonstrates how to:
1. Scrape today's healthcare news
2. Generate an HTML page with the results
3. Serve it locally for viewing

Usage:
    python examples/generate_frontend.py
    # Opens browser with today's news
"""

from datetime import datetime
from pathlib import Path
from healthcare_news_scraper import scrape_default_healthcare_news
import json


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Today's WHO Healthcare News - {date}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🏥 WHO Healthcare News</h1>
            <div class="date-badge">📅 {date} - Today's Update</div>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-label">Total Articles</span>
                    <span class="stat-value">{total_count}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Last Updated</span>
                    <span class="stat-value" style="font-size: 1.2rem;">{update_time}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Source</span>
                    <span class="stat-value" style="font-size: 1.2rem;">WHO</span>
                </div>
            </div>
        </header>

        <div class="filters">
            <div class="filter-buttons">
                <button class="filter-btn active" data-category="all">All Categories</button>
                <button class="filter-btn" data-category="research">Research</button>
                <button class="filter-btn" data-category="outbreak">Outbreak</button>
                <button class="filter-btn" data-category="policy">Policy</button>
                <button class="filter-btn" data-category="public_health">Public Health</button>
            </div>
        </div>

        <div class="articles-grid" id="articles-container">
            <!-- Articles rendered dynamically -->
        </div>
    </div>

    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh News</button>

    <script>
        const articles = {articles_json};
        let currentFilter = 'all';

        function renderArticles(filter = 'all') {{
            const container = document.getElementById('articles-container');
            const filteredArticles = filter === 'all' 
                ? articles 
                : articles.filter(article => article.category === filter);

            if (filteredArticles.length === 0) {{
                container.innerHTML = '<div class="no-results"><h2>No articles found</h2></div>';
                return;
            }}

            container.innerHTML = filteredArticles.map(article => `
                <div class="article-card ${{article.category}}" onclick="window.open('${{article.url}}', '_blank')">
                    <span class="category-badge ${{article.category}}">${{article.category.replace('_', ' ')}}</span>
                    <h3 class="article-title">${{article.title}}</h3>
                    <p class="article-date">📅 ${{article.date}}</p>
                    <p class="article-source">Source: ${{article.source}}</p>
                    <a href="${{article.url}}" class="read-more" onclick="event.stopPropagation()">Read Full Article →</a>
                </div>
            `).join('');
        }}

        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentFilter = this.getAttribute('data-category');
                renderArticles(currentFilter);
            }});
        }});

        renderArticles();
    </script>
</body>
</html>
"""


def generate_todays_news_page(output_path: str = "examples/todays_news.html") -> None:
    """
    Scrape latest news and generate an HTML page.
    
    Args:
        output_path: Where to save the generated HTML file
    """
    print("🔍 Scraping WHO healthcare news...")
    
    try:
        # Scrape the latest news
        articles = scrape_default_healthcare_news(delay_seconds=1.5)
        
        if not articles:
            print("⚠️  No articles found. Using sample data.")
            articles = [
                {
                    "title": "No articles found - WHO website may be temporarily unavailable",
                    "date": datetime.now().strftime("%a, %b %d, %Y"),
                    "category": "general",
                    "url": "https://www.who.int/news",
                    "source": "healthcare_web"
                }
            ]
        
        # Prepare template data
        now = datetime.now()
        template_data = {
            "date": now.strftime("%B %d, %Y"),
            "update_time": now.strftime("%I:%M %p"),
            "total_count": len(articles),
            "articles_json": json.dumps(articles, indent=2)
        }
        
        # Generate HTML
        html_content = HTML_TEMPLATE.format(**template_data)
        
        # Ensure examples directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True)
        
        # Write HTML file
        output_file.write_text(html_content, encoding='utf-8')
        
        print(f"✅ Generated {len(articles)} articles")
        print(f"📄 Saved to: {output_file.absolute()}")
        print(f"\n🌐 Open in browser: file://{output_file.absolute()}")
        
        # Try to open in default browser
        try:
            import webbrowser
            webbrowser.open(f"file://{output_file.absolute()}")
            print("🚀 Opening in default browser...")
        except Exception:
            print("💡 Copy the URL above to view in your browser")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have healthcare_news_scraper installed:")
        print("   poetry install")


if __name__ == "__main__":
    generate_todays_news_page()
