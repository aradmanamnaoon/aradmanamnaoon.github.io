#!/usr/bin/env python3
"""
============================================================================
 ARADMANAMNAOON — Complete Site Build System v3.0
============================================================================

 A single, self-healing script that manages the entire website build process.

 WHAT'S NEW IN v3.0
 ------------------
 *  Robust HTML div-matcher that handles nested <div> elements correctly
 *  Complete blog layout repair (removes stale cards from hero section)
 *  Duplicate archive section detection and cleanup
 *  Marker placement verification and auto-fix
 *  Structural HTML validation before/after changes
 *  --fix-layout mode for targeted blog/index.html repair
 *  Progress counters on every phase
 *  Detailed error reporting with line numbers where possible
 *  Automatic detection of misplaced AUTO markers
 *  Full preprocessing pipeline: analyze → plan → apply → verify

 FEATURES
 --------
 1.  File organization and repair
 2.  Blog filename standardization (rename to index.html)
 3.  Blog archive section reconstruction
 4.  articles.json URL repair and schema validation
 5.  Article URL → file existence validation
 6.  Favicon injection into every HTML file
 7.  Live project fetching from GitHub API
 8.  Live model fetching from Hugging Face API
 9.  Live dataset fetching from Hugging Face API
 10. Project scoring (stars, forks, downloads, likes, recency)
 11. Curated project overrides
 12. Homepage top-3 project rendering
 13. Paginated full project list rendering
 14. Homepage top-3 article rendering
 15. Full blog archive rendering
 16. sitemap.xml generation
 17. robots.txt generation
 18. Internal link validation
 19. Auto-backup of every modified file
 20. Dry-run, no-fetch, verbose, rollback, fix-layout, and validate modes
 21. Stale content cleanup (with proper nested div handling)
 22. Old backup cleanup (30-day retention)
 23. Comprehensive error handling
 24. Detailed progress reporting
 25. Structural HTML validation
 26. Blog hero/archive layout enforcement

 USAGE
 -----
     cd /workspaces/aradmanamnaoon.github.io
     python scripts/build_site.py

 OPTIONS
 -------
     --dry-run       Preview changes without writing
     --no-fetch      Skip API calls
     --verbose       Extra detail
     --rollback      Restore all .build-backup files
     --validate      Only validate, don't rebuild
     --fix-layout    Only repair blog/index.html structure and exit

============================================================================
"""

import os
import re
import sys
import json
import shutil
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ============================================================================
#  GLOBAL CONFIGURATION
# ============================================================================

BASE_DIR = os.getcwd()
SITE_URL = "https://aradmanamnaoon.github.io"
SITE_NAME = "ARADMANAMNAOON"

GITHUB_USER = "aradmanamnaoon"
HF_USER = "aradmanamnaoon"

MAX_PROJECTS_HOMEPAGE = 3
MAX_ARTICLES_HOMEPAGE = 3
PROJECTS_PER_PAGE = 6

# CLI flags
DRY_RUN = "--dry-run" in sys.argv
NO_FETCH = "--no-fetch" in sys.argv
VERBOSE = "--verbose" in sys.argv
ROLLBACK = "--rollback" in sys.argv
VALIDATE_ONLY = "--validate" in sys.argv
FIX_LAYOUT_ONLY = "--fix-layout" in sys.argv

# Repos to skip during project fetch
SKIP_REPOS = {"aradmanamnaoon.github.io", ".github"}

# Folders to skip during walks
SKIP_FOLDERS = {
    ".git", "node_modules", "scripts", "dist",
    "assets", ".github", ".vscode", ".devcontainer",
    "__pycache__", ".pytest_cache"
}

# Backup suffix
BACKUP_SUFFIX = ".build-backup"

# Protected files (never auto-deleted, but URLs may still be fixed)
PROTECTED_FILES = {
    "articles.json",
    "CNAME",
    ".nojekyll",
}

# ============================================================================
#  CURATED PROJECT OVERRIDES
#  Every entry here overrides the live API data with hand-crafted content.
# ============================================================================

CURATED = {
    "ai-research-assistant-platform": {
        "type": "Agentic AI · Multi-agent systems · RAG",
        "title": "AI Research Assistant Platform",
        "description": "A production-style research assistant built around a LangGraph multi-agent workflow. Planning, retrieval, research, tool execution, synthesis, and bounded reflection work with ChromaDB RAG, persistent state, LangSmith observability, FastAPI, streaming responses, and Docker-ready deployment.",
        "metrics": [
            {"value": "103", "label": "Offline tests"},
            {"value": "5", "label": "Agent roles"},
            {"value": "REST + SSE", "label": "API surface"},
        ],
        "tags": ["LangGraph", "LangChain", "LangSmith", "ChromaDB", "FastAPI", "Docker"],
        "featured": True,
    },
    "persian-lm-from-scratch": {
        "type": "Persian NLP · Transformers · From-scratch training",
        "title": "Persian GPT — 110M Transformer From Scratch",
        "description": "A decoder-only GPT-style language model built end to end for Persian: cleaned Wikipedia corpus, custom 32K BPE tokenizer, transformer training, n-gram baselines, and held-out evaluation.",
        "metrics": [
            {"value": "110.4M", "label": "Parameters"},
            {"value": "244M", "label": "Training tokens"},
            {"value": "14.52", "label": "Test perplexity"},
        ],
        "tags": ["PyTorch", "Transformers", "Causal LM", "BPE", "Persian NLP"],
        "featured": True,
    },
    "medical-image-segmentation": {
        "type": "Medical AI · 3D computer vision · Segmentation",
        "title": "3D Cardiac MRI Segmentation",
        "description": "A voxel-level cardiac MRI segmentation pipeline using PyTorch, MONAI, and a 3D U-Net.",
        "metrics": [
            {"value": "0.8821", "label": "Best validation Dice"},
            {"value": "3D U-Net", "label": "Architecture"},
            {"value": "100", "label": "Training epochs"},
        ],
        "tags": ["PyTorch", "MONAI", "3D U-Net", "Medical Imaging", "DiceCELoss"],
        "featured": True,
    },
    "jibay2-medical-v2": {
        "type": "Medical NLP · QLoRA · Clinical summarization",
        "title": "Jibay2 Medical — Clinical Note Summarization",
        "description": "A QLoRA fine-tune of JibayAi/Jibay_2 for converting fragmented clinical shorthand into structured patient summaries.",
        "metrics": [
            {"value": "2,634", "label": "Dataset examples"},
            {"value": "1.4403", "label": "Best validation loss"},
            {"value": "~5.7 min", "label": "Training time"},
        ],
        "tags": ["QLoRA", "Unsloth", "TRL", "PEFT", "Clinical NLP"],
    },
    "messy2json-qwen-0.5b": {
        "type": "LLM fine-tuning · QLoRA · Structured extraction",
        "title": "Messy2JSON — Lightweight Structured Extraction",
        "description": "Qwen2.5-0.5B fine-tuned with QLoRA to convert messy English text into structured JSON.",
        "metrics": [
            {"value": "99.82%", "label": "Mean token accuracy"},
            {"value": "0.0045", "label": "Validation loss"},
            {"value": "~0.85%", "label": "Trainable parameters"},
        ],
        "tags": ["Qwen2.5", "QLoRA", "PEFT", "4-bit NF4", "Structured Output"],
    },
    "nllb-en-fa-psych-translation": {
        "type": "Machine translation · English → Persian · Psychology",
        "title": "NLLB English-to-Persian Psychology Translation",
        "description": "A domain adaptation of NLLB-200-distilled-600M for English-to-Persian psychology translation.",
        "metrics": [
            {"value": "0.6B", "label": "Base-model scale"},
            {"value": "EN → FA", "label": "Translation direction"},
            {"value": "NLLB", "label": "Seq2seq architecture"},
        ],
        "tags": ["NLLB-200", "Transformers", "Machine Translation", "Persian", "Psychology"],
    },
}

# ============================================================================
#  FAVICON LINKS
# ============================================================================

FAVICON_LINKS = '''    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">'''

# ============================================================================
#  BLOG ARCHIVE TEMPLATE
#  This is the canonical structure used when the archive section needs
#  to be rebuilt. It matches the CSS classes in blog/index.html.
# ============================================================================

BLOG_ARCHIVE_TEMPLATE = '''    <!-- =====================================================
         ARTICLE ARCHIVE
         ===================================================== -->
    <section
      class="blog-archive"
      aria-labelledby="writing-heading"
    >
      <div class="blog-shell">
        <div class="blog-section-head">
          <div class="blog-section-number">
            01 / Archive
          </div>
          <h2
            class="blog-section-title"
            id="writing-heading"
          >
            Latest writing
          </h2>
        </div>

        <div class="blog-post-list">
          <!-- AUTO:BLOG_ARTICLES:START -->
          <!-- AUTO:BLOG_ARTICLES:END -->
        </div>
      </div>
    </section>

'''

# ============================================================================
#  LOGGING UTILITIES
# ============================================================================

# Global counters for progress reporting
STATS = {
    "files_written": 0,
    "files_backed_up": 0,
    "html_files_scanned": 0,
    "favicons_added": 0,
    "articles_processed": 0,
    "projects_fetched": 0,
    "stale_blocks_removed": 0,
    "layout_repairs": 0,
}


def log(msg, level="info"):
    """Print a formatted log message with an optional level prefix."""
    prefixes = {
        "info": "   ",
        "step": "\n▶",
        "ok": "   ✓",
        "warn": "   ⚠️ ",
        "err": "   ❌",
        "repair": "   🔧",
        "new": "   ➕",
        "scan": "   🔎",
        "save": "   💾",
    }
    print(f"{prefixes.get(level, '   ')} {msg}")


def section(title):
    """Print a section divider with a centered title."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def subsection(title):
    """Print a lighter-weight subsection divider."""
    print()
    print(f"── {title} " + "─" * max(0, 66 - len(title)))


def print_stats():
    """Print the global stats summary."""
    print()
    print("─" * 70)
    print("  Build statistics:")
    print(f"    Files written:        {STATS['files_written']}")
    print(f"    Backups created:      {STATS['files_backed_up']}")
    print(f"    HTML files scanned:   {STATS['html_files_scanned']}")
    print(f"    Favicons added:       {STATS['favicons_added']}")
    print(f"    Articles processed:   {STATS['articles_processed']}")
    print(f"    Projects fetched:     {STATS['projects_fetched']}")
    print(f"    Stale blocks removed: {STATS['stale_blocks_removed']}")
    print(f"    Layout repairs:       {STATS['layout_repairs']}")
    print("─" * 70)


# ============================================================================
#  FILE I/O UTILITIES
# ============================================================================

def file_exists(rel_path):
    """Check if a file exists relative to BASE_DIR."""
    return os.path.exists(os.path.join(BASE_DIR, rel_path))


def read_file(rel_path):
    """Read a file relative to BASE_DIR."""
    with open(os.path.join(BASE_DIR, rel_path), encoding='utf-8') as f:
        return f.read()


def write_file(rel_path, content, backup=True):
    """Write a file, optionally backing up the original first."""
    full_path = os.path.join(BASE_DIR, rel_path)
    if DRY_RUN:
        log(f"[DRY RUN] Would write {rel_path}")
        return
    if backup and os.path.exists(full_path):
        try:
            shutil.copy2(full_path, full_path + BACKUP_SUFFIX)
            STATS["files_backed_up"] += 1
        except Exception:
            pass
    os.makedirs(os.path.dirname(full_path) or BASE_DIR, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    STATS["files_written"] += 1


# ============================================================================
#  HTML PARSING UTILITIES
#  These handle nested <div> tags correctly — the old regex-based approach
#  was the root cause of the layout bug.
# ============================================================================

def find_matching_closing_div(html, start_pos):
    """
    Given the index of an opening '<div' tag, return the index just after
    the matching '</div>'. Handles arbitrarily deep nesting.
    Returns -1 if no matching close is found.
    """
    if start_pos < 0 or start_pos >= len(html):
        return -1

    depth = 0
    i = start_pos
    n = len(html)

    while i < n:
        # Check for opening <div (with word boundary)
        if html.startswith('<div', i):
            # Make sure next char is whitespace or >
            if i + 4 >= n or html[i + 4] in ' >\t\n\r/':
                depth += 1
                i += 4
                continue
        # Check for closing </div>
        if html.startswith('</div>', i):
            depth -= 1
            i += 6
            if depth == 0:
                return i
            continue
        i += 1

    return -1


def find_all_blocks(html, opening_pattern):
    """
    Find all blocks in HTML that start with a given opening pattern
    and end with its matching closing tag.

    Returns a list of (start_index, end_index) tuples, where end_index
    points to just after the closing tag.
    """
    blocks = []
    pattern = re.compile(opening_pattern)
    pos = 0

    while True:
        match = pattern.search(html, pos)
        if not match:
            break

        start = match.start()
        # Determine the div position for depth counting
        div_pos = html.find('<div', start)
        if div_pos == -1 or div_pos > match.end():
            # Fallback: use the match end
            pos = match.end()
            continue

        end = find_matching_closing_div(html, div_pos)
        if end == -1:
            pos = match.end()
            continue

        blocks.append((start, end))
        pos = end

    return blocks


def strip_blocks_by_pattern(html, opening_pattern, label="block"):
    """
    Remove all blocks matching the given opening pattern, using proper
    div-nesting matching. Returns (new_html, count_removed).
    """
    blocks = find_all_blocks(html, opening_pattern)
    if not blocks:
        return html, 0

    # Remove blocks from the end so indices stay valid
    new_html = html
    for start, end in reversed(blocks):
        new_html = new_html[:start] + new_html[end:]
        STATS["stale_blocks_removed"] += 1

    if blocks:
        log(f"Removed {len(blocks)} {label}(s)", "repair")

    return new_html, len(blocks)


def count_blocks(html, opening_pattern):
    """Count blocks matching a pattern (using nested div matching)."""
    return len(find_all_blocks(html, opening_pattern))


# ============================================================================
#  DATE / SLUG UTILITIES
# ============================================================================

def parse_iso(dt_str):
    """Parse an ISO 8601 datetime string."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def days_since(dt):
    """Days since a datetime (used for recency scoring)."""
    if dt is None:
        return 9999
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).days


def slugify(text):
    """Convert text to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:80]


# ============================================================================
#  STEP 1: ROLLBACK
# ============================================================================

def rollback_all():
    """Restore all .build-backup files and exit."""
    section("ROLLBACK")
    restored = 0
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS and not d.startswith('.')]
        for f in files:
            if f.endswith(BACKUP_SUFFIX):
                backup_path = os.path.join(root, f)
                original_path = backup_path[:-len(BACKUP_SUFFIX)]
                try:
                    shutil.copy2(backup_path, original_path)
                    os.remove(backup_path)
                    restored += 1
                    log(f"Restored {os.path.relpath(original_path, BASE_DIR)}", "ok")
                except Exception as e:
                    log(f"Failed: {backup_path}: {e}", "err")
    log(f"Restored {restored} file(s). Exiting.", "ok")
    sys.exit(0)


# ============================================================================
#  STEP 2: BLOG FILENAME REPAIR
# ============================================================================

def repair_blog_filenames():
    """
    Rename any non-index.html blog post file to index.html.
    Returns a dict of {old_url: new_url} for articles.json updating.
    """
    section("STEP 1 / 15 — Repairing blog filenames")
    blog_dir = os.path.join(BASE_DIR, "blog")
    if not os.path.isdir(blog_dir):
        log("blog/ folder not found, skipping", "warn")
        return {}

    renamed = {}
    for entry in sorted(os.listdir(blog_dir)):
        folder_path = os.path.join(blog_dir, entry)
        if not os.path.isdir(folder_path):
            continue

        html_files = [f for f in os.listdir(folder_path) if f.endswith(".html")]
        if "index.html" in html_files:
            log(f"blog/{entry}/index.html — OK")
            continue
        if not html_files:
            log(f"blog/{entry}/ has no HTML files", "warn")
            continue

        if len(html_files) == 1:
            old_name = html_files[0]
            old_path = os.path.join(folder_path, old_name)
            new_path = os.path.join(folder_path, "index.html")
            try:
                if not DRY_RUN:
                    os.rename(old_path, new_path)
                old_url = f"/blog/{entry}/{old_name}"
                new_url = f"/blog/{entry}/"
                renamed[old_url] = new_url
                log(f"Renamed blog/{entry}/{old_name} → blog/{entry}/index.html", "repair")
            except Exception as e:
                log(f"Could not rename blog/{entry}/{old_name}: {e}", "err")
        else:
            log(f"blog/{entry}/ has multiple HTML files: {html_files}", "warn")

    if not renamed:
        log("All blog filenames are already correct", "ok")
    return renamed


# ============================================================================
#  STEP 3: ORPHANED FILE DETECTION
# ============================================================================

def repair_orphaned_files():
    """Detect orphaned HTML files directly in blog/ root."""
    section("STEP 2 / 15 — Checking for orphaned files")
    blog_dir = os.path.join(BASE_DIR, "blog")
    if not os.path.isdir(blog_dir):
        return
    for f in os.listdir(blog_dir):
        full = os.path.join(blog_dir, f)
        if os.path.isfile(full) and f.endswith(".html") and f != "index.html":
            log(f"Orphaned file: blog/{f}", "warn")
            log(f"   Move it to blog/{slugify(f[:-5])}/index.html manually", "info")


# ============================================================================
#  STEP 4: ARTICLES.JSON REPAIR
# ============================================================================

def load_articles():
    """Load articles.json with graceful fallback."""
    path = os.path.join(BASE_DIR, "articles.json")
    if not os.path.exists(path):
        log("articles.json not found — creating empty list", "warn")
        if not DRY_RUN:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
        return []
    try:
        with open(path, encoding='utf-8') as f:
            articles = json.load(f)
        if not isinstance(articles, list):
            raise ValueError("articles.json must be a list")
        return articles
    except json.JSONDecodeError as e:
        log(f"articles.json is invalid JSON: {e}", "err")
        log("Please fix the JSON syntax and re-run.", "info")
        sys.exit(1)


def repair_articles_json(renamed):
    """Update articles.json URLs to match file locations."""
    section("STEP 3 / 15 — Repairing articles.json URLs")
    articles = load_articles()
    changed = 0
    for article in articles:
        old_url = article.get("url", "")
        # Fix /blog/foo/bar.html → /blog/foo/
        match = re.match(r'^(/blog/([^/]+))/[^/]+\.html$', old_url)
        if match:
            new_url = match.group(1) + "/"
            article["url"] = new_url
            log(f"Fixed URL: {old_url} → {new_url}", "repair")
            changed += 1
        # Apply any renamed folder names from the previous step
        elif old_url in renamed:
            article["url"] = renamed[old_url]
            log(f"Applied rename: {old_url} → {article['url']}", "repair")
            changed += 1

    if changed:
        write_file("articles.json", json.dumps(articles, indent=2, ensure_ascii=False), backup=False)
        log(f"Updated {changed} URL(s) in articles.json", "ok")
    else:
        log("All URLs in articles.json are correct", "ok")
    return articles


# ============================================================================
#  STEP 5: ARTICLE VALIDATION
# ============================================================================

def validate_articles(articles):
    """Ensure every article has a matching file on disk."""
    section("STEP 4 / 15 — Validating article files")
    missing = []
    for article in articles:
        url = article.get("url", "")
        title = article.get("title", "(untitled)")
        if url.endswith("/"):
            rel = url.lstrip("/") + "index.html"
        else:
            rel = url.lstrip("/")
        if not file_exists(rel):
            missing.append((title, url, rel))

    if missing:
        log(f"Found {len(missing)} article(s) with missing files:", "warn")
        for title, url, rel in missing:
            log(f"   • \"{title[:60]}\"", "warn")
            log(f"     URL: {url}", "info")
            log(f"     Expected: {rel}", "info")
    else:
        log(f"All {len(articles)} article URLs are valid", "ok")
    return missing


def validate_article_schema(articles):
    """Ensure every article has required fields."""
    section("STEP 5 / 15 — Validating article schema")
    required = ["title", "url", "date"]
    issues = 0
    for i, article in enumerate(articles):
        for field in required:
            if field not in article or not article[field]:
                log(f"Article #{i} missing required field: {field}", "warn")
                issues += 1
    if not issues:
        log(f"All {len(articles)} articles have required fields", "ok")
    return issues


# ============================================================================
#  STEP 6: FAVICON INJECTION
# ============================================================================

def has_favicons(html):
    """Check if HTML already has favicon links."""
    return 'rel="icon"' in html


def inject_favicons(html):
    """Add favicon links to <head> if missing."""
    if has_favicons(html):
        return html
    if '</head>' in html:
        return html.replace('</head>', FAVICON_LINKS + '\n</head>', 1)
    return html


def inject_favicons_everywhere():
    """Walk the repo and add favicons to every HTML file."""
    section("STEP 6 / 15 — Injecting favicons into all HTML files")
    updated = 0
    skipped = 0
    failed = 0

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS and not d.startswith('.')]
        for filename in files:
            if not filename.endswith('.html'):
                continue
            STATS["html_files_scanned"] += 1
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, BASE_DIR)
            try:
                with open(filepath, encoding='utf-8') as f:
                    html = f.read()
                new_html = inject_favicons(html)
                if new_html != html:
                    write_file(rel_path, new_html)
                    updated += 1
                    STATS["favicons_added"] += 1
                    log(f"Added favicons: {rel_path}", "ok")
                else:
                    skipped += 1
            except Exception as e:
                failed += 1
                log(f"Failed: {rel_path}: {e}", "err")

    log(f"Favicons added: {updated} | Already present: {skipped} | Failed: {failed}", "ok")


# ============================================================================
#  STEP 7: API FETCHERS
# ============================================================================

def http_get_json(url, timeout=20):
    """Fetch JSON from a URL with graceful error handling."""
    req = urllib.request.Request(url, headers={
        "User-Agent": f"{SITE_NAME}-builder",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        log(f"HTTP {e.code}: {url}", "warn")
    except urllib.error.URLError as e:
        log(f"Network error: {url}: {e.reason}", "warn")
    except Exception as e:
        log(f"Error: {url}: {e}", "warn")
    return None


def fetch_github_repos():
    """Fetch all public repos from GitHub."""
    log(f"Fetching GitHub repos for {GITHUB_USER}...")
    url = f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&sort=updated"
    repos = http_get_json(url)
    if not repos:
        return []

    results = []
    for r in repos:
        if r.get("fork"):
            continue
        if r["name"] in SKIP_REPOS:
            continue

        tags = list(r.get("topics") or [])
        if r.get("language") and r["language"] not in tags:
            tags.insert(0, r["language"])

        results.append({
            "source": "github",
            "id": r["name"],
            "name": r["name"],
            "title": r["name"].replace("-", " ").replace("_", " ").title(),
            "description": r.get("description") or "",
            "url": r["html_url"],
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "updated": r.get("updated_at", ""),
            "created": r.get("created_at", ""),
            "tags": tags[:6],
            "language": r.get("language") or "",
            "homepage": r.get("homepage") or "",
        })

    log(f"Fetched {len(results)} GitHub repos", "ok")
    return results


def fetch_hf_models():
    """Fetch all public models from Hugging Face."""
    log(f"Fetching Hugging Face models for {HF_USER}...")
    url = f"https://huggingface.co/api/models?author={HF_USER}&limit=100&full=true"
    models = http_get_json(url)
    if not models:
        return []

    results = []
    for m in models:
        model_id = m.get("modelId") or m.get("id", "")
        short = model_id.split("/")[-1] if "/" in model_id else model_id

        tags = []
        if m.get("pipeline_tag"):
            tags.append(m["pipeline_tag"])
        skip_tags = {"transformers", "pytorch", "safetensors",
                     "license:apache-2.0", "license:mit", "text-generation"}
        for t in (m.get("tags") or []):
            if t not in tags and t not in skip_tags:
                tags.append(t)

        results.append({
            "source": "hf_model",
            "id": short,
            "name": short,
            "title": short.replace("-", " ").replace("_", " ").title(),
            "description": (m.get("cardData", {}) or {}).get("short_description", "") or "",
            "url": f"https://huggingface.co/{model_id}",
            "downloads": m.get("downloads", 0),
            "likes": m.get("likes", 0),
            "updated": m.get("lastModified", ""),
            "created": m.get("createdAt", ""),
            "tags": tags[:6],
        })

    log(f"Fetched {len(results)} HF models", "ok")
    return results


def fetch_hf_datasets():
    """Fetch all public datasets from Hugging Face."""
    log(f"Fetching Hugging Face datasets for {HF_USER}...")
    url = f"https://huggingface.co/api/datasets?author={HF_USER}&limit=100&full=true"
    datasets = http_get_json(url)
    if not datasets:
        return []

    results = []
    for d in datasets:
        ds_id = d.get("id", "")
        short = ds_id.split("/")[-1] if "/" in ds_id else ds_id

        results.append({
            "source": "hf_dataset",
            "id": short,
            "name": short,
            "title": short.replace("-", " ").replace("_", " ").title(),
            "description": (d.get("cardData", {}) or {}).get("short_description", "") or "",
            "url": f"https://huggingface.co/datasets/{ds_id}",
            "downloads": d.get("downloads", 0),
            "likes": d.get("likes", 0),
            "updated": d.get("lastModified", ""),
            "created": d.get("createdAt", ""),
            "tags": (d.get("tags") or [])[:6],
        })

    log(f"Fetched {len(results)} HF datasets", "ok")
    return results


# ============================================================================
#  STEP 8: SCORE AND RANK PROJECTS
# ============================================================================

def score_project(p):
    """
    Score a project for ranking. Higher is better + newer.
    """
    score = 0.0
    score += p.get("stars", 0) * 10
    score += p.get("forks", 0) * 5
    score += p.get("downloads", 0) / 100.0
    score += p.get("likes", 0) * 5

    days = days_since(parse_iso(p.get("updated")))
    if days < 30:
        score += 30
    elif days < 90:
        score += 15
    elif days < 365:
        score += 5

    return score


def rank_all_projects():
    """Fetch, override, score, and rank all projects."""
    section("STEP 7 / 15 — Ranking projects")

    if NO_FETCH:
        log("Skipping API fetches (--no-fetch flag)", "warn")
        return []

    all_items = []
    all_items.extend(fetch_github_repos())
    all_items.extend(fetch_hf_models())
    all_items.extend(fetch_hf_datasets())
    STATS["projects_fetched"] = len(all_items)

    # Apply curated overrides
    for item in all_items:
        override = CURATED.get(item["id"])
        if override:
            for k, v in override.items():
                item[k] = v
            item["curated"] = True

    # Score
    for item in all_items:
        item["_score"] = score_project(item)

    # Sort: featured first, then by score desc, then by name
    all_items.sort(key=lambda x: (
        not x.get("featured", False),
        -x["_score"],
        x.get("name", "")
    ))

    # Add display dates
    for item in all_items:
        dt = parse_iso(item.get("updated")) or parse_iso(item.get("created"))
        if dt:
            item["date"] = dt.strftime("%Y-%m-%d")
            item["dateDisplay"] = dt.strftime("%B %Y")
        else:
            item["date"] = "2024-01-01"
            item["dateDisplay"] = "2024"

    log(f"Total ranked projects: {len(all_items)}", "ok")
    if VERBOSE:
        for i, p in enumerate(all_items[:10], 1):
            log(f"   #{i} [{p['source']}] {p['title']} (score: {p['_score']:.1f})")

    return all_items


# ============================================================================
#  STEP 9: RENDER FUNCTIONS
# ============================================================================

def get_project_metrics(p):
    """Return metrics (curated or derived from API data)."""
    if p.get("metrics"):
        return p["metrics"]
    if p["source"] == "github":
        return [
            {"value": str(p.get("stars", 0)), "label": "Stars"},
            {"value": str(p.get("forks", 0)), "label": "Forks"},
            {"value": p.get("language", "—"), "label": "Language"},
        ]
    elif p["source"] in ("hf_model", "hf_dataset"):
        return [
            {"value": f"{p.get('downloads', 0):,}", "label": "Downloads"},
            {"value": str(p.get("likes", 0)), "label": "Likes"},
            {"value": "HF", "label": "Hosted on"},
        ]
    return []


def get_project_actions(p):
    """Return action links for a project."""
    actions = [{"url": p["url"], "label": "View project ↗", "primary": True}]
    if p.get("homepage"):
        actions.append({"url": p["homepage"], "label": "Live demo ↗", "primary": False})
    return actions


def render_homepage_projects(projects):
    """Render the top-N projects for the homepage."""
    top = projects[:MAX_PROJECTS_HOMEPAGE]
    cards = []
    source_badges = {
        "github": "GitHub",
        "hf_model": "Hugging Face",
        "hf_dataset": "HF Dataset",
    }

    for i, p in enumerate(top, start=1):
        num = f"{i:02d}"
        metrics = get_project_metrics(p)
        metrics_html = "".join(
            f'<div class="metric"><span class="metric-value">{m["value"]}</span>'
            f'<span class="metric-label">{m["label"]}</span></div>'
            for m in metrics
        )
        tags_html = "".join(f'<span class="project-tag">{t}</span>' for t in p.get("tags", []))
        actions = get_project_actions(p)
        actions_html = "".join(
            f'<a class="project-link {"primary" if a.get("primary") else ""}" '
            f'href="{a["url"]}" target="_blank" rel="noopener noreferrer">{a["label"]}</a>'
            for a in actions
        )
        desc = p.get("description") or "Source and details on GitHub / Hugging Face."
        type_str = p.get("type", source_badges[p["source"]])

        cards.append(f'''          <article id="{p['id']}" class="featured-project">
            <div class="grid gap-8 sm:grid-cols-[auto_1fr]">
              <div class="project-number" aria-hidden="true">{num}</div>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-ink/70">{type_str}</p>
                <h3 class="mt-3 font-serif text-3xl font-bold sm:text-4xl">{p["title"]}</h3>
                <p class="mt-5 max-w-[70ch] leading-relaxed text-ink/70">{desc}</p>
                <div class="metric-grid mt-8">{metrics_html}</div>
                <div class="project-tags">{tags_html}</div>
                <div class="project-actions">{actions_html}</div>
              </div>
            </div>
          </article>
''')

    return '<div class="mt-14 space-y-6">\n' + "\n".join(cards) + '</div>'


def render_paginated_projects(projects):
    """Render the full paginated project list with client-side JS."""
    data = []
    for p in projects:
        data.append({
            "id": p["id"],
            "title": p["title"],
            "type": p.get("type", p["source"]),
            "description": p.get("description") or "",
            "dateDisplay": p.get("dateDisplay", ""),
            "metrics": get_project_metrics(p),
            "tags": p.get("tags", []),
            "actions": get_project_actions(p),
            "note": p.get("note", ""),
        })

    projects_json = json.dumps(data, ensure_ascii=False)

    return f'''<div class="projects-paginated" id="projects-paginated"></div>
<div class="projects-pagination" id="projects-pagination" role="navigation" aria-label="Project pages"></div>

<style>
.projects-paginated {{ display: grid; gap: 22px; }}
.projects-pagination {{
  display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;
  margin-top: 40px; padding-top: 24px; border-top: 1px solid rgba(237,237,237,0.09);
}}
.projects-pagination button {{
  min-width: 44px; min-height: 44px; padding: 0 14px;
  border: 1px solid rgba(237,237,237,0.13);
  border-radius: 12px; background: transparent; color: #ededed;
  font: inherit; font-size: 0.85rem; font-weight: 600; cursor: pointer;
  transition: all 180ms ease;
}}
.projects-pagination button:hover:not(:disabled):not(.active) {{
  border-color: #7db4f0; color: #7db4f0;
}}
.projects-pagination button.active {{
  background: #7db4f0; color: #14181f; border-color: #7db4f0;
}}
.projects-pagination button:disabled {{ opacity: 0.35; cursor: not-allowed; }}
</style>

<script>
(function() {{
  const projects = {projects_json};
  const perPage = {PROJECTS_PER_PAGE};
  let currentPage = 1;
  const totalPages = Math.max(1, Math.ceil(projects.length / perPage));
  const container = document.getElementById('projects-paginated');
  const pagination = document.getElementById('projects-pagination');
  if (!container || !pagination) return;

  function esc(s) {{
    return String(s).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c]);
  }}

  function renderProjects(page) {{
    const start = (page - 1) * perPage;
    const items = projects.slice(start, start + perPage);
    let html = '';
    items.forEach((p, i) => {{
      const num = String(start + i + 1).padStart(2, '0');
      const metricsHtml = (p.metrics || []).map(m =>
        `<div class="metric"><strong>${{esc(m.value)}}</strong><span>${{esc(m.label)}}</span></div>`
      ).join('');
      const tagsHtml = (p.tags || []).map(t => `<span class="tag">${{esc(t)}}</span>`).join('');
      const actionsHtml = (p.actions || []).map(a =>
        `<a class="action ${{a.primary ? 'primary' : ''}}" href="${{esc(a.url)}}" target="_blank" rel="noopener noreferrer">${{esc(a.label)}}</a>`
      ).join('');
      const noteHtml = p.note ? `<p class="note">${{esc(p.note)}}</p>` : '';
      html += `<article class="project" id="${{esc(p.id)}}">
        <div class="num" aria-hidden="true">${{num}}</div>
        <div>
          <p class="type">${{esc(p.type)}}</p>
          <h2>${{esc(p.title)}}</h2>
          <p class="desc">${{esc(p.description)}}</p>
          <div class="metrics">${{metricsHtml}}</div>
          <div class="tags">${{tagsHtml}}</div>
          <div class="actions">${{actionsHtml}}</div>
          ${{noteHtml}}
        </div>
      </article>`;
    }});
    container.innerHTML = html;
  }}

  function renderPagination() {{
    let html = '';
    html += `<button ${{currentPage === 1 ? 'disabled' : ''}} data-page="${{currentPage - 1}}">←</button>`;
    for (let i = 1; i <= totalPages; i++) {{
      html += `<button class="${{i === currentPage ? 'active' : ''}}" data-page="${{i}}">${{i}}</button>`;
    }}
    html += `<button ${{currentPage === totalPages ? 'disabled' : ''}} data-page="${{currentPage + 1}}">→</button>`;
    pagination.innerHTML = html;
    pagination.querySelectorAll('button[data-page]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const p = parseInt(btn.dataset.page, 10);
        if (p >= 1 && p <= totalPages && p !== currentPage) {{
          currentPage = p;
          renderProjects(currentPage);
          renderPagination();
          document.getElementById('selected-projects')?.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
      }});
    }});
  }}

  renderProjects(currentPage);
  renderPagination();
}})();
</script>
'''


def render_homepage_blogs(articles):
    """Render the top-N articles for the homepage hero section."""
    sorted_articles = sorted(articles, key=lambda x: x.get('date', ''), reverse=True)
    top = sorted_articles[:MAX_ARTICLES_HOMEPAGE]
    cards = []

    for a in top:
        tags = "".join(
            f'\n              <span class="writing-post-tag">{t}</span>'
            for t in a.get("tags", [])
        )
        cards.append(f'''        <a class="writing-post-card" href="{a["url"]}" aria-label="Read {a["title"]}">
          <div>
            <div class="writing-post-meta">{a.get("dateDisplay", a["date"])} · {a.get("readTime", "")}</div>
            <h3 class="writing-post-title">{a["title"]}</h3>
            <p class="writing-post-description">{a["description"]}</p>
            <div class="writing-post-tags" aria-label="Article topics">{tags}
            </div>
          </div>
          <span class="writing-post-arrow" aria-hidden="true">→</span>
        </a>''')

    return "\n\n".join(cards)


def render_blog_index(articles):
    """Render the full article list for the blog archive section."""
    sorted_articles = sorted(articles, key=lambda x: x.get('date', ''), reverse=True)
    cards = []

    for a in sorted_articles:
        tags = "".join(
            f'\n                  <span class="blog-post-tag">{t}</span>'
            for t in a.get("tags", [])
        )
        cards.append(f'''          <article>
            <a class="blog-post" href="{a["url"]}" aria-label="Read {a["title"]}">
              <div class="blog-post-meta">
                <time datetime="{a["date"]}">{a.get("dateDisplay", a["date"])}</time><br />
                {a.get("readTime", "")}
              </div>
              <div>
                <h3 class="blog-post-title">{a["title"]}</h3>
                <p class="blog-post-description">{a["description"]}</p>
                <div class="blog-post-tags" aria-label="Article topics">{tags}
                </div>
              </div>
              <span class="blog-post-arrow" aria-hidden="true">→</span>
            </a>
          </article>''')

    return "\n\n".join(cards)


# ============================================================================
#  STEP 10: FIX BLOG LAYOUT (THE CORE FIX)
#  This is the function that actually solves the layout problem.
# ============================================================================

def remove_stale_blog_blocks_from_hero(html):
    """
    Remove any stale injected blog-list-container blocks that were placed
    in the WRONG location (right after the 'Writing.' h1 title, instead of
    inside the archive section).
    """
    removed_total = 0

    # Strategy 1: Remove entire <div class="blog-list-container">...</div> blocks
    # using proper nested-div matching
    html, n = strip_blocks_by_pattern(
        html,
        r'<div\s+class="blog-list-container"',
        label="blog-list-container",
    )
    removed_total += n

    # Strategy 2: Remove any orphaned <div class="blog-card" style="...">...</div>
    # blocks that somehow escaped their container
    orphaned = find_all_blocks(html, r'<div\s+class="blog-card"[^>]*style=')
    if orphaned:
        for start, end in reversed(orphaned):
            html = html[:start] + html[end:]
        log(f"Removed {len(orphaned)} orphaned blog-card(s)", "repair")
        removed_total += len(orphaned)

    # Strategy 3: Remove empty <div class="projects-list-container"></div>
    html, n = strip_blocks_by_pattern(
        html,
        r'<div\s+class="projects-list-container">',
        label="projects-list-container",
    )
    removed_total += n

    return html, removed_total


def fix_blog_layout(html):
    """
    Ensure blog/index.html has exactly one archive section with the correct
    markers, and that the hero section is clean (no cards).
    """
    log("Analyzing blog/index.html structure...", "scan")

    # Step 1: Remove any stale injected content
    html, removed = remove_stale_blog_blocks_from_hero(html)
    if removed:
        log(f"Cleaned {removed} stale block(s) from blog page", "repair")
        STATS["layout_repairs"] += 1

    # Step 2: Count archive sections
    archive_blocks = find_all_blocks(html, r'<section\s+class="blog-archive"')
    archive_count = len(archive_blocks)

    if archive_count == 0:
        log("No blog-archive section found — rebuilding", "repair")
        html = _insert_archive_section(html)
        STATS["layout_repairs"] += 1
    elif archive_count > 1:
        log(f"Found {archive_count} duplicate archive sections — removing extras", "repair")
        # Keep the first, remove the rest
        for start, end in reversed(archive_blocks[1:]):
            html = html[:start] + html[end:]
        STATS["layout_repairs"] += 1
    else:
        log("Exactly one blog-archive section present", "ok")

    # Step 3: Ensure markers exist inside the archive
    if '<!-- AUTO:BLOG_ARTICLES:START -->' not in html or '<!-- AUTO:BLOG_ARTICLES:END -->' not in html:
        log("AUTO:BLOG_ARTICLES markers missing — adding them", "repair")
        html = _ensure_markers_in_archive(html)
        STATS["layout_repairs"] += 1
    else:
        log("AUTO:BLOG_ARTICLES markers present", "ok")

    # Step 4: Ensure markers are inside the archive, not somewhere else
    # Find the archive section and verify the markers are within it
    archive_blocks = find_all_blocks(html, r'<section\s+class="blog-archive"')
    if archive_blocks:
        archive_start, archive_end = archive_blocks[0]
        archive_content = html[archive_start:archive_end]
        if '<!-- AUTO:BLOG_ARTICLES:START -->' not in archive_content:
            log("Markers are outside the archive — relocating", "repair")
            # Remove markers from wherever they are
            html = re.sub(r'<!-- AUTO:BLOG_ARTICLES:START -->', '', html)
            html = re.sub(r'<!-- AUTO:BLOG_ARTICLES:END -->', '', html)
            # Re-add inside the archive
            html = _ensure_markers_in_archive(html)
            STATS["layout_repairs"] += 1

    # Step 5: Verify hero section is clean
    hero_blocks = find_all_blocks(html, r'<section\s+class="blog-hero"')
    if hero_blocks:
        hero_start, hero_end = hero_blocks[0]
        hero_content = html[hero_start:hero_end]
        if 'class="blog-card"' in hero_content or 'class="blog-list-container"' in hero_content:
            log("Hero section still contains cards — cleaning", "repair")
            html = remove_stale_blog_blocks_from_hero(html)[0]
            STATS["layout_repairs"] += 1
        else:
            log("Hero section is clean", "ok")

    return html


def _insert_archive_section(html):
    """Insert the canonical blog archive section before </main>."""
    if '</main>' in html:
        html = html.replace('</main>', BLOG_ARCHIVE_TEMPLATE + '  </main>', 1)
    elif '</body>' in html:
        html = html.replace('</body>', BLOG_ARCHIVE_TEMPLATE + '</body>', 1)
    return html


def _ensure_markers_in_archive(html):
    """Ensure markers exist inside .blog-post-list within the archive section."""
    archive_blocks = find_all_blocks(html, r'<section\s+class="blog-archive"')
    if not archive_blocks:
        return html

    archive_start, archive_end = archive_blocks[0]
    archive_content = html[archive_start:archive_end]

    if '<!-- AUTO:BLOG_ARTICLES:START -->' in archive_content:
        return html

    # Look for <div class="blog-post-list"> inside the archive and inject markers
    list_pattern = re.compile(r'(<div\s+class="blog-post-list">)', re.IGNORECASE)
    match = list_pattern.search(archive_content)
    if not match:
        return html

    insert_pos = archive_start + match.end()
    markers = '\n          <!-- AUTO:BLOG_ARTICLES:START -->\n          <!-- AUTO:BLOG_ARTICLES:END -->'
    return html[:insert_pos] + markers + html[insert_pos:]


# ============================================================================
#  STEP 11: INJECTION
# ============================================================================

def verify_markers(html, marker_name, filepath):
    """Return True if the AUTO markers exist in the HTML."""
    start = f'<!-- {marker_name}:START -->'
    end = f'<!-- {marker_name}:END -->'
    if start not in html or end not in html:
        log(f"{filepath}: {marker_name} markers missing", "warn")
        return False
    return True


def inject_homepage_projects(html, projects):
    """Inject the top-N projects into index.html."""
    rendered = render_homepage_projects(projects)
    pattern = r'(<div class="mt-14 space-y-6">).*?(</div>\s*<div class="mt-16">)'
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, f'{rendered}\n\n        \\2', html, flags=re.DOTALL)
        log("Injected top projects into homepage", "ok")
    else:
        log("Homepage project container not found", "warn")
    return html


def inject_projects_page(html, projects):
    """Inject paginated projects into /projects/."""
    rendered = render_paginated_projects(projects)
    pattern = r'(<div class="projects" id="project-list">).*?(</div>\s*(?:<p class="projects-empty"|</section>))'
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, f'\\1\n{rendered}\n      \\2', html, flags=re.DOTALL)
        log("Injected paginated projects", "ok")
    else:
        log("Projects page container not found", "warn")

    # Clean up old filter tools + filter script
    html = re.sub(r'<div class="project-tools"[^>]*>.*?</div>\s*(?=<div class="projects")', '', html, flags=re.DOTALL)
    html = re.sub(
        r'<script>\s*\(\(\)\s*=>\s*\{\s*const filterPanel = document\.getElementById\("project-filters"\).*?</script>',
        '', html, flags=re.DOTALL
    )
    html = re.sub(r'<p class="projects-empty"[^>]*>.*?</p>', '', html, flags=re.DOTALL)
    return html


def inject_homepage_blogs(html, articles):
    """Inject top-N articles into homepage."""
    if not verify_markers(html, "AUTO:HOME_ARTICLES", "index.html"):
        return html
    rendered = render_homepage_blogs(articles)
    pattern = r'(<!-- AUTO:HOME_ARTICLES:START -->).*?(<!-- AUTO:HOME_ARTICLES:END -->)'
    html = re.sub(pattern, f'\\1\n{rendered}\n        <!-- AUTO:HOME_ARTICLES:END -->', html, flags=re.DOTALL)
    log("Injected top articles into homepage", "ok")
    return html


def inject_blog_index(html, articles):
    """Inject full article list into blog archive section."""
    if not verify_markers(html, "AUTO:BLOG_ARTICLES", "blog/index.html"):
        return html
    rendered = render_blog_index(articles)
    pattern = r'(<!-- AUTO:BLOG_ARTICLES:START -->).*?(<!-- AUTO:BLOG_ARTICLES:END -->)'
    html = re.sub(pattern, f'\\1\n{rendered}\n<!-- AUTO:BLOG_ARTICLES:END -->', html, flags=re.DOTALL)
    log(f"Injected {len(articles)} article(s) into blog archive", "ok")
    return html


# ============================================================================
#  STEP 12: SITEMAP AND ROBOTS.TXT
# ============================================================================

def generate_sitemap(articles):
    """Generate sitemap.xml."""
    section("STEP 12 / 15 — Generating sitemap.xml")
    urls = [
        {"loc": f"{SITE_URL}/", "priority": "1.0"},
        {"loc": f"{SITE_URL}/projects/", "priority": "0.9"},
        {"loc": f"{SITE_URL}/blog/", "priority": "0.8"},
    ]
    for a in articles:
        urls.append({
            "loc": f"{SITE_URL}{a['url']}",
            "priority": "0.6",
        })

    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for u in urls:
        xml_parts.append('  <url>')
        xml_parts.append(f'    <loc>{u["loc"]}</loc>')
        xml_parts.append(f'    <priority>{u["priority"]}</priority>')
        xml_parts.append('  </url>')
    xml_parts.append('</urlset>')

    write_file("sitemap.xml", "\n".join(xml_parts), backup=False)
    log(f"Generated sitemap.xml with {len(urls)} URLs", "ok")


def generate_robots_txt():
    """Generate robots.txt."""
    section("STEP 13 / 15 — Generating robots.txt")
    content = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    write_file("robots.txt", content, backup=False)
    log("Generated robots.txt", "ok")


# ============================================================================
#  STEP 13: INTERNAL LINK VALIDATION
# ============================================================================

def validate_internal_links(html_files):
    """Check that all internal links point to existing files."""
    section("STEP 14 / 15 — Validating internal links")
    broken = []

    for rel_path in html_files:
        try:
            html = read_file(rel_path)
        except Exception:
            continue

        links = re.findall(r'href="([^"]+)"', html)
        for link in links:
            if link.startswith(('http://', 'https://', '//', '#', 'mailto:', 'tel:')):
                continue
            clean_link = link.split('?')[0].split('#')[0]
            if not clean_link:
                continue

            file_dir = os.path.dirname(os.path.join(BASE_DIR, rel_path))
            if clean_link.startswith('/'):
                target = os.path.join(BASE_DIR, clean_link.lstrip('/'))
            else:
                target = os.path.normpath(os.path.join(file_dir, clean_link))

            if os.path.isdir(target):
                target = os.path.join(target, "index.html")

            if not os.path.exists(target):
                if '.' in os.path.basename(clean_link) or clean_link.endswith('/'):
                    broken.append((rel_path, link))

    if broken:
        log(f"Found {len(broken)} potentially broken internal link(s):", "warn")
        for src, link in broken[:20]:
            log(f"   {src} → {link}", "warn")
        if len(broken) > 20:
            log(f"   ... and {len(broken) - 20} more", "warn")
    else:
        log("No broken internal links detected", "ok")

    return broken


# ============================================================================
#  STEP 14: BACKUP CLEANUP
# ============================================================================

def cleanup_old_backups():
    """Remove .build-backup files older than 30 days."""
    section("STEP 15 / 15 — Cleaning up old backups")
    removed = 0
    now = datetime.now().timestamp()
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS and not d.startswith('.')]
        for f in files:
            if f.endswith(BACKUP_SUFFIX):
                path = os.path.join(root, f)
                age_days = (now - os.path.getmtime(path)) / 86400
                if age_days > 30:
                    try:
                        os.remove(path)
                        removed += 1
                    except Exception:
                        pass
    if removed:
        log(f"Removed {removed} old backup(s)", "ok")
    else:
        log("No old backups to remove", "ok")


# ============================================================================
#  STEP 15: POST-BUILD VERIFICATION
# ============================================================================

def verify_blog_layout(html):
    """Verify the blog layout is correct after modification."""
    issues = []

    # Check hero section
    hero_blocks = find_all_blocks(html, r'<section\s+class="blog-hero"')
    if hero_blocks:
        hero_start, hero_end = hero_blocks[0]
        hero_content = html[hero_start:hero_end]
        if 'class="blog-card"' in hero_content:
            issues.append("Hero section still contains blog-card elements")
        if 'class="blog-list-container"' in hero_content:
            issues.append("Hero section still contains blog-list-container")

    # Check archive section
    archive_blocks = find_all_blocks(html, r'<section\s+class="blog-archive"')
    if not archive_blocks:
        issues.append("No blog-archive section found")
    elif len(archive_blocks) > 1:
        issues.append(f"Multiple blog-archive sections found ({len(archive_blocks)})")
    else:
        archive_start, archive_end = archive_blocks[0]
        archive_content = html[archive_start:archive_end]
        if '<!-- AUTO:BLOG_ARTICLES:START -->' not in archive_content:
            issues.append("Archive section missing AUTO:BLOG_ARTICLES:START marker")
        if '<!-- AUTO:BLOG_ARTICLES:END -->' not in archive_content:
            issues.append("Archive section missing AUTO:BLOG_ARTICLES:END marker")

    return issues


# ============================================================================
#  MAIN
# ============================================================================

def main():
    """Main entry point."""
    print()
    print("█" * 70)
    print(f"  {SITE_NAME} — Complete Build System v3.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if DRY_RUN:
        print("  ⚠️  DRY RUN MODE — no files will be written")
    if NO_FETCH:
        print("  ⚠️  NO-FETCH MODE — skipping API calls")
    if FIX_LAYOUT_ONLY:
        print("  🔧 FIX-LAYOUT MODE — only blog/index.html will be repaired")
    print("█" * 70)

    # Handle rollback
    if ROLLBACK:
        rollback_all()

    # Handle fix-layout-only mode
    if FIX_LAYOUT_ONLY:
        section("FIX-LAYOUT MODE")
        blog_path = "blog/index.html"
        if not file_exists(blog_path):
            log(f"{blog_path} not found", "err")
            sys.exit(1)
        html = read_file(blog_path)
        html = fix_blog_layout(html)
        write_file(blog_path, html)

        # Verify
        html = read_file(blog_path)
        issues = verify_blog_layout(html)
        if issues:
            log("Remaining issues:", "warn")
            for issue in issues:
                log(f"   • {issue}", "warn")
        else:
            log("Blog layout verified: no issues", "ok")

        print()
        log("Fix-layout complete. Exiting.", "ok")
        sys.exit(0)

    # STEP 1: Repair blog filenames
    renamed = repair_blog_filenames()

    # STEP 2: Check for orphaned files
    repair_orphaned_files()

    # STEP 3: Repair articles.json
    articles = repair_articles_json(renamed)
    STATS["articles_processed"] = len(articles)

    # STEP 4: Validate article links
    missing = validate_articles(articles)

    # STEP 5: Validate article schema
    validate_article_schema(articles)

    if VALIDATE_ONLY:
        section("VALIDATE-ONLY MODE — stopping here")
        log(f"Articles: {len(articles)}", "ok")
        log(f"Missing files: {len(missing)}", "ok")
        print_stats()
        sys.exit(0)

    # STEP 6: Inject favicons everywhere
    inject_favicons_everywhere()

    # STEP 7: Fetch and rank projects
    projects = rank_all_projects()

    # STEP 8: Process index.html
    section("STEP 8 / 15 — Processing index.html")
    html = read_file("index.html")

    # Clean stale content from homepage (using nested-div-aware matching)
    html, n = strip_blocks_by_pattern(
        html,
        r'<div\s+class="blog-list-container"',
        label="blog-list-container (homepage)",
    )
    html, n2 = strip_blocks_by_pattern(
        html,
        r'<div\s+class="projects-list-container">',
        label="projects-list-container (homepage)",
    )

    html = inject_homepage_projects(html, projects)
    html = inject_homepage_blogs(html, articles)
    write_file("index.html", html)
    log("index.html processed", "ok")

    # STEP 9: Process projects/index.html
    section("STEP 9 / 15 — Processing projects/index.html")
    html = read_file("projects/index.html")
    html = inject_projects_page(html, projects)
    write_file("projects/index.html", html)
    log("projects/index.html processed", "ok")

    # STEP 10: Process blog/index.html (with layout fix)
    section("STEP 10 / 15 — Processing blog/index.html")
    html = read_file("blog/index.html")
    html = fix_blog_layout(html)
    html = inject_blog_index(html, articles)
    write_file("blog/index.html", html)
    log("blog/index.html processed", "ok")

    # POST: Verify blog layout
    subsection("Verifying blog layout")
    html = read_file("blog/index.html")
    issues = verify_blog_layout(html)
    if issues:
        log("Remaining issues:", "warn")
        for issue in issues:
            log(f"   • {issue}", "warn")
    else:
        log("Blog layout verified: no issues", "ok")

    # STEP 12: Generate sitemap
    generate_sitemap(articles)

    # STEP 13: Generate robots.txt
    generate_robots_txt()

    # STEP 14: Validate internal links
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS and not d.startswith('.')]
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.relpath(os.path.join(root, f), BASE_DIR))
    validate_internal_links(html_files)

    # STEP 15: Clean up old backups
    cleanup_old_backups()

    # Final report
    print()
    print("█" * 70)
    print("  ✅ BUILD COMPLETE")
    print("█" * 70)
    print(f"  Articles:      {len(articles)}")
    print(f"  Projects:      {len(projects)}")
    print(f"  HTML files:    {len(html_files)}")
    if missing:
        print(f"  ⚠️  Missing:    {len(missing)} article file(s)")
    print_stats()
    print("  Next steps:")
    print("    1. Review the changes (git diff)")
    print("    2. Commit and push")
    print("    3. Wait ~1 min for GitHub Pages to deploy")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)