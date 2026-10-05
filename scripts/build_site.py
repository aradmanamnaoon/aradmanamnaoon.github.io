import json
import os
import re
from datetime import datetime

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_JSON = os.path.join(BASE_DIR, 'articles.json')
INDEX_HTML = os.path.join(BASE_DIR, 'index.html')
SITEMAP_XML = os.path.join(BASE_DIR, 'sitemap.xml')
BLOG_DIR = os.path.join(BASE_DIR, 'blog')
SITE_URL = "https://aradmanamnaoon.github.io"

# --- Favicon Injection ---
FAVICON_LINKS = '''
    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
'''

def inject_favicons(html_content):
    """Injects favicon links into the <head> if they don't already exist."""
    if 'rel="icon"' in html_content:
        return html_content  # Already has favicons
    
    # Insert before </head>
    if '</head>' in html_content:
        return html_content.replace('</head>', FAVICON_LINKS + '</head>')
    return html_content

# --- Blog List Updating ---
def update_blog_list(html_content, articles):
    """Updates the blog list section in index.html based on articles.json."""
    # Create HTML for blog cards
    blog_cards_html = ""
    for article in articles:
        blog_cards_html += f'''
        <div class="blog-card">
            <h3><a href="{article['url']}">{article['title']}</a></h3>
            <p class="blog-date">{article['date']}</p>
            <p>{article['description']}</p>
        </div>'''
    
    # Replace content between markers (assuming your index.html has these markers)
    # If you don't have markers, you need to add them around your blog list.
    pattern = r'(<!-- BLOG_LIST_START -->).*?(<!-- BLOG_LIST_END -->)'
    replacement = f'\\1{blog_cards_html}\\2'
    
    if re.search(pattern, html_content, re.DOTALL):
        return re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    else:
        print("Warning: BLOG_LIST_START/END markers not found in index.html. Skipping blog list update.")
        return html_content

# --- Sitemap Generation ---
def generate_sitemap(articles):
    """Generates a valid sitemap.xml."""
    urls = [
        f"<url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>",
        f"<url><loc>{SITE_URL}/projects/</loc><priority>0.8</priority></url>",
        f"<url><loc>{SITE_URL}/blog/</loc><priority>0.8</priority></url>"
    ]
    
    for article in articles:
        urls.append(f"<url><loc>{SITE_URL}{article['url']}</loc><priority>0.6</priority></url>")
    
    sitemap_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {''.join(urls)}
</urlset>'''
    
    with open(SITEMAP_XML, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print(f"Generated sitemap.xml with {len(urls)} URLs.")

# --- Main Execution ---
def main():
    # 1. Load Articles
    if not os.path.exists(ARTICLES_JSON):
        print(f"Error: {ARTICLES_JSON} not found. Please create it.")
        return
    
    with open(ARTICLES_JSON, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # 2. Process Index.html
    if os.path.exists(INDEX_HTML):
        with open(INDEX_HTML, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Inject Favicons
        html = inject_favicons(html)
        # Update Blog List
        html = update_blog_list(html, articles)
        
        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(html)
        print("Updated index.html (favicons + blog list).")
    else:
        print(f"Error: {INDEX_HTML} not found.")
    
    # 3. Process Blog Posts (Inject Favicons into all HTML files in /blog/)
    if os.path.exists(BLOG_DIR):
        for root, dirs, files in os.walk(BLOG_DIR):
            for file in files:
                if file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        blog_html = f.read()
                    
                    blog_html = inject_favicons(blog_html)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(blog_html)
        print(f"Updated favicons in all blog HTML files.")
    else:
        print(f"Warning: Blog directory {BLOG_DIR} not found.")
    
    # 4. Generate Sitemap
    generate_sitemap(articles)

if __name__ == "__main__":
    main()