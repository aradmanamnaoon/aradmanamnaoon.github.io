import json
import os
import re

# --- EXACT FILES TO PROCESS (Hardcoded based on your terminal output) ---
HTML_FILES = [
    "index.html",
    "projects/index.html",
    "blog/index.html",
    "blog/evaluatable-multi-agent-rag-langgraph/index.html",
    "blog/agent-evals/agent-evals.html",
    "blog/hugging-face-nllb-gradient-accumulation-bug/index.html",
    "blog/agentic-rag/agentic-rag.html"
]

ARTICLES_JSON = "articles.json"
SITEMAP_XML = "sitemap.xml"
SITE_URL = "https://aradmanamnaoon.github.io"
MAX_ARTICLES_TO_SHOW = 3

# --- Favicon Injection ---
FAVICON_LINKS = '''
    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
'''

def inject_favicons(html_content):
    if 'rel="icon"' in html_content:
        return html_content
    if '</head>' in html_content:
        return html_content.replace('</head>', FAVICON_LINKS + '</head>')
    return html_content

# --- Blog List Generation ---
def generate_blog_html(articles):
    blog_cards_html = '<div class="blog-list-container">\n'
    
    # Sort by date descending and limit to top 3
    sorted_articles = sorted(articles, key=lambda x: x.get('date', ''), reverse=True)
    top_articles = sorted_articles[:MAX_ARTICLES_TO_SHOW]
    
    for article in top_articles:
        tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in article.get('tags', [])])
        
        blog_cards_html += f'''
        <div class="blog-card" style="margin-bottom: 2rem; border-bottom: 1px solid #eee; padding-bottom: 1rem;">
            <h3 style="margin-bottom: 0.5rem;"><a href="{article['url']}" style="text-decoration: none; color: inherit;">{article['title']}</a></h3>
            <div class="blog-meta" style="font-size: 0.9rem; color: #666; margin-bottom: 1rem;">
                <span class="blog-date">{article.get('dateDisplay', article['date'])}</span>
                <span class="blog-readtime" style="margin-left: 1rem;">{article.get('readTime', '')}</span>
            </div>
            <p style="margin-bottom: 1rem;">{article['description']}</p>
            <div class="blog-tags" style="font-size: 0.8rem;">{tags_html}</div>
        </div>'''
    
    blog_cards_html += '</div>'
    return blog_cards_html

def inject_blog_list(html_content, articles):
    # 1. Use explicit markers if they exist
    pattern = r'(<!-- BLOG_LIST_START -->).*?(<!-- BLOG_LIST_END -->)'
    if re.search(pattern, html_content, re.DOTALL):
        print("  -> Found BLOG_LIST markers. Injecting.")
        return re.sub(pattern, f'\\1\n{generate_blog_html(articles)}\n\\2', html_content, flags=re.DOTALL)
    
    # 2. Fallback: Look for the "Writing." heading
    writing_pattern = r'(<h[1-6][^>]*>.*?Writing\..*?</h[1-6]>)'
    if re.search(writing_pattern, html_content, re.IGNORECASE | re.DOTALL):
        print("  -> Found 'Writing.' heading. Injecting.")
        return re.sub(writing_pattern, f'\\1\n{generate_blog_html(articles)}', html_content, flags=re.IGNORECASE | re.DOTALL)
    
    # 3. Fallback: Look for "Notes" heading (from your screenshot)
    notes_pattern = r'(<h[1-6][^>]*>.*?Notes.*?</h[1-6]>)'
    if re.search(notes_pattern, html_content, re.IGNORECASE | re.DOTALL):
        print("  -> Found 'Notes' heading. Injecting.")
        return re.sub(notes_pattern, f'\\1\n{generate_blog_html(articles)}', html_content, flags=re.IGNORECASE | re.DOTALL)
        
    print("  -> Warning: No suitable heading found. Skipping list injection.")
    return html_content

# --- Sitemap Generation ---
def generate_sitemap(articles):
    urls = [
        f"<url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>",
        f"<url><loc>{SITE_URL}/blog/</loc><priority>0.8</priority></url>",
        f"<url><loc>{SITE_URL}/projects/</loc><priority>0.8</priority></url>"
    ]
    for article in articles:
        urls.append(f"<url><loc>{SITE_URL}{article['url']}</loc><priority>0.6</priority></url>")
    
    sitemap_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {''.join(urls)}
</urlset>'''
    
    with open(SITEMAP_XML, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print(f"✅ Generated sitemap.xml with {len(urls)} URLs.")

# --- Main Execution ---
def main():
    if not os.path.exists(ARTICLES_JSON):
        print(f"❌ Error: {ARTICLES_JSON} not found in current folder.")
        return
    
    with open(ARTICLES_JSON, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"📄 Processing {len(HTML_FILES)} files...\n")
    
    for filepath in HTML_FILES:
        if not os.path.exists(filepath):
            print(f"⚠️  Skipping missing file: {filepath}")
            continue
        
        print(f"Processing: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # 1. Inject favicons into ALL files
        html = inject_favicons(html)
        
        # 2. Inject blog list ONLY into homepage and blog index
        if filepath in ['index.html', 'blog/index.html']:
            html = inject_blog_list(html, articles)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
    
    # Generate sitemap
    generate_sitemap(articles)

if __name__ == "__main__":
    main()