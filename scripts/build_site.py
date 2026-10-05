#!/usr/bin/env python3
"""
============================================================================
 ARADMANAMNAOON — Complete Site Build System
============================================================================

 A single script that manages the entire website build process.

 WHAT THIS SCRIPT DOES
 ---------------------
 1.  Organizes and repairs the repository file structure
 2.  Standardizes blog post filenames to index.html
 3.  Validates and repairs articles.json
 4.  Injects favicons into every HTML file
 5.  Fetches projects live from GitHub + Hugging Face APIs
 6.  Ranks and scores projects by quality + recency
 7.  Renders top projects on the homepage
 8.  Renders paginated full project list on /projects/
 9.  Renders top articles on the homepage
 10. Renders full article list on /blog/
 11. Generates sitemap.xml
 12. Generates robots.txt
 13. Validates internal links
 14. Backs up files before modification
 15. Reports any issues found

 WHAT YOU DO MANUALLY
 --------------------
 - Write blog posts (as blog/<slug>/index.html)
 - Add one entry per post to articles.json
 - Run this script
 - Commit and push

 USAGE
 -----
     cd /workspaces/aradmanamnaoon.github.io
     python scripts/build_site.py

 OPTIONS
 -------
     --dry-run       Show what would change without writing
     --no-fetch      Skip API calls (use only cached/local data)
     --verbose       Print more detail
     --rollback      Restore all .backup files and exit
     --validate      Only validate the site, don't rebuild

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
from html import escape as html_escape

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

# Command line flags
DRY_RUN = "--dry-run" in sys.argv
NO_FETCH = "--no-fetch" in sys.argv
VERBOSE = "--verbose" in sys.argv
ROLLBACK = "--rollback" in sys.argv
VALIDATE_ONLY = "--validate" in sys.argv

# Repos to exclude from project listing
SKIP_REPOS = {"aradmanamnaoon.github.io", ".github", "aradmanamnaoon"}

# Folders to skip when walking the repo
SKIP_FOLDERS = {
    ".git", "node_modules", "scripts", "dist",
    "assets", ".github", ".vscode", ".devcontainer",
    "__pycache__", ".pytest_cache"
}

# Backup suffix for files modified by this script
BACKUP_SUFFIX = ".build-backup"

# Files that are never modified
PROTECTED_FILES = {
    "articles.json",
    "sitemap.xml",
    "robots.txt",
    "CNAME",
    ".nojekyll",
}

# ============================================================================
#  CURATED PROJECT OVERRIDES
#  This lets you polish specific projects with better titles, descriptions,
#  metrics, and tags than what the APIs provide.
#  Keys are the exact repo/model short name.
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
#  UTILITIES
# ============================================================================

def log(msg, level="info"):
    """Print a formatted log message."""
    prefixes = {
        "info": "   ",
        "step": "\n▶",
        "ok": "   ✓",
        "warn": "   ⚠️ ",
        "err": "   ❌",
        "repair": "   🔧",
    }
    prefix = prefixes.get(level, "   ")
    print(f"{prefix} {msg}")


def section(title):
    """Print a section divider."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def file_exists(rel_path):
    """Check if a file exists relative to BASE_DIR."""
    return os.path.exists(os.path.join(BASE_DIR, rel_path))


def read_file(rel_path):
    """Read a file relative to BASE_DIR."""
    with open(os.path.join(BASE_DIR, rel_path), encoding='utf-8') as f:
        return f.read()


def write_file(rel_path, content, backup=True):
    """Write a file, optionally backing up the original."""
    full_path = os.path.join(BASE_DIR, rel_path)
    if DRY_RUN:
        log(f"[DRY RUN] Would write {rel_path}")
        return
    
    # Backup
    if backup and os.path.exists(full_path):
        backup_path = full_path + BACKUP_SUFFIX
        try:
            shutil.copy2(full_path, backup_path)
        except Exception:
            pass
    
    os.makedirs(os.path.dirname(full_path) or BASE_DIR, exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)


def parse_iso(dt_str):
    """Parse an ISO 8601 datetime string."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def days_since(dt):
    """Calculate days since a datetime."""
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
#  STEP 2: FILE ORGANIZATION AND REPAIR
# ============================================================================

def repair_blog_filenames():
    """
    Rename any non-index.html blog post file to index.html.
    Returns a dict of {old_url: new_url} for articles.json updating.
    """
    section("STEP 1 / 12 — Repairing blog filenames")
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


def repair_orphaned_files():
    """
    Detect common problems:
    - HTML files at blog/ root that should be in a folder
    - Duplicate content files
    - Missing index.html in blog post folders
    """
    section("STEP 2 / 12 — Checking for orphaned files")
    blog_dir = os.path.join(BASE_DIR, "blog")
    if not os.path.isdir(blog_dir):
        return
    
    # HTML files directly in blog/ (other than index.html)
    for f in os.listdir(blog_dir):
        full = os.path.join(blog_dir, f)
        if os.path.isfile(full) and f.endswith(".html") and f != "index.html":
            log(f"Orphaned file: blog/{f}", "warn")
            log(f"   Move it to blog/{slugify(f[:-5])}/index.html manually", "info")


# ============================================================================
#  STEP 3: ARTICLES.JSON VALIDATION AND REPAIR
# ============================================================================

def load_articles():
    """Load articles.json with fallback to empty list."""
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
    """Update articles.json with the renamed URLs."""
    section("STEP 3 / 12 — Repairing articles.json URLs")
    articles = load_articles()
    changed = 0
    for article in articles:
        old_url = article.get("url", "")
        # Auto-fix .html URLs to clean folder URLs
        match = re.match(r'^(/blog/([^/]+))/[^/]+\.html$', old_url)
        if match:
            new_url = match.group(1) + "/"
            article["url"] = new_url
            log(f"Fixed URL: {old_url} → {new_url}", "repair")
            changed += 1
        # Apply renamed map from earlier step
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


def validate_articles(articles):
    """Ensure every article has a matching file on disk."""
    section("STEP 4 / 12 — Validating article links")
    missing = []
    for article in articles:
        url = article.get("url", "")
        title = article.get("title", "(untitled)")
        # Convert /blog/foo/ → blog/foo/index.html
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
    section("STEP 5 / 12 — Validating article schema")
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
    section("STEP 6 / 12 — Injecting favicons")
    updated = 0
    skipped = 0
    failed = 0
    
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS and not d.startswith('.')]
        for filename in files:
            if not filename.endswith('.html'):
                continue
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, BASE_DIR)
            try:
                with open(filepath, encoding='utf-8') as f:
                    html = f.read()
                new_html = inject_favicons(html)
                if new_html != html:
                    write_file(rel_path, new_html)
                    updated += 1
                    log(f"Added favicons: {rel_path}", "ok")
                else:
                    skipped += 1
            except Exception as e:
                failed += 1
                log(f"Failed: {rel_path}: {e}", "err")
    
    log(f"Favicons added: {updated} | Already present: {skipped} | Failed: {failed}", "ok")


# ============================================================================
#  STEP 7: FETCH PROJECTS FROM APIS
# ============================================================================

def http_get_json(url, timeout=20):
    """Fetch JSON from a URL with error handling."""
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
    Score a project for ranking.
    Higher = better + newer.
    """
    score = 0.0
    score += p.get("stars", 0) * 10
    score += p.get("forks", 0) * 5
    score += p.get("downloads", 0) / 100.0
    score += p.get("likes", 0) * 5
    
    # Recency boost
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
    section("STEP 7 / 12 — Ranking projects")
    
    if NO_FETCH:
        log("Skipping API fetches (--no-fetch flag)", "warn")
        return []
    
    all_items = []
    all_items.extend(fetch_github_repos())
    all_items.extend(fetch_hf_models())
    all_items.extend(fetch_hf_datasets())
    
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
    
    # Sort: featured first, then by score descending, then name
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
#  STEP 9: RENDER HTML
# ============================================================================

def get_project_metrics(p):
    """Get metrics for a project, using curated data if available."""
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
    """Get action links for a project."""
    actions = [{"url": p["url"], "label": "View project ↗", "primary": True}]
    if p.get("homepage"):
        actions.append({"url": p["homepage"], "label": "Live demo ↗", "primary": False})
    return actions


def render_homepage_projects(projects):
    """Render top projects for homepage."""
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
    """Render paginated project list with client-side JS."""
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
    """Render top articles for homepage."""
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
    """Render full article list for blog page."""
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
#  STEP 10: INJECT RENDERED CONTENT
# ============================================================================

def verify_markers(html, marker_name, filepath):
    """Return True if the AUTO markers exist in HTML."""
    start = f'<!-- {marker_name}:START -->'
    end = f'<!-- {marker_name}:END -->'
    if start not in html or end not in html:
        log(f"{filepath}: {marker_name} markers missing", "warn")
        return False
    return True


def inject_homepage_projects(html, projects):
    """Inject top projects into index.html."""
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
    
    # Clean up old filter tools and old filter script
    html = re.sub(r'<div class="project-tools"[^>]*>.*?</div>\s*(?=<div class="projects")', '', html, flags=re.DOTALL)
    html = re.sub(
        r'<script>\s*\(\(\)\s*=>\s*\{\s*const filterPanel = document\.getElementById\("project-filters"\).*?</script>',
        '', html, flags=re.DOTALL
    )
    html = re.sub(r'<p class="projects-empty"[^>]*>.*?</p>', '', html, flags=re.DOTALL)
    return html


def inject_homepage_blogs(html, articles):
    """Inject top articles into homepage."""
    if not verify_markers(html, "AUTO:HOME_ARTICLES", "index.html"):
        return html
    rendered = render_homepage_blogs(articles)
    pattern = r'(<!-- AUTO:HOME_ARTICLES:START -->).*?(<!-- AUTO:HOME_ARTICLES:END -->)'
    html = re.sub(pattern, f'\\1\n{rendered}\n        <!-- AUTO:HOME_ARTICLES:END -->', html, flags=re.DOTALL)
    log("Injected top articles into homepage", "ok")
    return html


def inject_blog_index(html, articles):
    """Inject full article list into blog/index.html."""
    if not verify_markers(html, "AUTO:BLOG_ARTICLES", "blog/index.html"):
        return html
    rendered = render_blog_index(articles)
    pattern = r'(<!-- AUTO:BLOG_ARTICLES:START -->).*?(<!-- AUTO:BLOG_ARTICLES:END -->)'
    html = re.sub(pattern, f'\\1\n{rendered}\n<!-- AUTO:BLOG_ARTICLES:END -->', html, flags=re.DOTALL)
    log("Injected article list into blog page", "ok")
    return html


def remove_stale_injected_content(html):
    """Remove stale injected content from previous buggy script runs."""
    original = html
    # Remove old inline-styled blog cards
    html = re.sub(
        r'<div class="blog-card"\s+style="[^"]*"[^>]*>.*?</div>\s*'
        r'(?=<div class="blog-card"|<p class="blog-intro"|<a class="writing-link"|</div>|</section>|<!--)',
        '', html, flags=re.DOTALL
    )
    # Remove empty placeholder wrappers
    html = re.sub(r'<div class="blog-list-container">\s*</div>\s*', '', html)
    html = re.sub(r'<div class="projects-list-container">\s*</div>\s*', '', html)
    if len(html) != len(original):
        log(f"Removed {len(original) - len(html)} chars of stale content", "repair")
    return html


# ============================================================================
#  STEP 11: GENERATE SITEMAP AND ROBOTS.TXT
# ============================================================================

def generate_sitemap(articles):
    """Generate sitemap.xml with all pages."""
    section("STEP 10 / 12 — Generating sitemap.xml")
    
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
        xml_parts.append(f'  <url>')
        xml_parts.append(f'    <loc>{u["loc"]}</loc>')
        xml_parts.append(f'    <priority>{u["priority"]}</priority>')
        xml_parts.append(f'  </url>')
    xml_parts.append('</urlset>')
    
    content = "\n".join(xml_parts)
    write_file("sitemap.xml", content, backup=False)
    log(f"Generated sitemap.xml with {len(urls)} URLs", "ok")


def generate_robots_txt():
    """Generate robots.txt."""
    section("STEP 11 / 12 — Generating robots.txt")
    content = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    write_file("robots.txt", content, backup=False)
    log("Generated robots.txt", "ok")


# ============================================================================
#  STEP 12: LINK VALIDATION
# ============================================================================

def validate_internal_links(html_files):
    """
    Check that all internal links point to files that exist.
    """
    section("STEP 12 / 12 — Validating internal links")
    broken = []
    
    for rel_path in html_files:
        try:
            html = read_file(rel_path)
        except Exception:
            continue
        
        # Find all href="..." that don't start with http, //, #, mailto, tel
        links = re.findall(r'href="([^"]+)"', html)
        for link in links:
            if link.startswith(('http://', 'https://', '//', '#', 'mailto:', 'tel:')):
                continue
            # Skip query strings and fragments
            clean_link = link.split('?')[0].split('#')[0]
            if not clean_link:
                continue
            
            # Resolve the link relative to the file's directory
            file_dir = os.path.dirname(os.path.join(BASE_DIR, rel_path))
            if clean_link.startswith('/'):
                target = os.path.join(BASE_DIR, clean_link.lstrip('/'))
            else:
                target = os.path.normpath(os.path.join(file_dir, clean_link))
            
            # If it points to a directory, check for index.html
            if os.path.isdir(target):
                target = os.path.join(target, "index.html")
            
            if not os.path.exists(target):
                # Only report if it looks like it should be a real file
                if '.' in os.path.basename(clean_link) or clean_link.endswith('/'):
                    broken.append((rel_path, link))
    
    if broken:
        log(f"Found {len(broken)} potentially broken internal link(s):", "warn")
        for src, link in broken[:20]:  # Cap output
            log(f"   {src} → {link}", "warn")
        if len(broken) > 20:
            log(f"   ... and {len(broken) - 20} more", "warn")
    else:
        log("No broken internal links detected", "ok")
    
    return broken


# ============================================================================
#  CLEANUP OLD BACKUPS
# ============================================================================

def cleanup_old_backups():
    """Remove .build-backup files older than 30 days."""
    section("Cleaning up old backups")
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
#  MAIN
# ============================================================================

def main():
    print()
    print("█" * 70)
    print(f"  {SITE_NAME} — Complete Build System")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if DRY_RUN:
        print("  ⚠️  DRY RUN MODE — no files will be written")
    if NO_FETCH:
        print("  ⚠️  NO-FETCH MODE — skipping API calls")
    print("█" * 70)
    
    if ROLLBACK:
        rollback_all()
    
    # ---- STEP 1: Repair blog filenames ----
    renamed = repair_blog_filenames()
    
    # ---- STEP 2: Check for orphaned files ----
    repair_orphaned_files()
    
    # ---- STEP 3: Repair articles.json ----
    articles = repair_articles_json(renamed)
    
    # ---- STEP 4: Validate article links ----
    missing = validate_articles(articles)
    
    # ---- STEP 5: Validate article schema ----
    validate_article_schema(articles)
    
    if VALIDATE_ONLY:
        section("VALIDATE-ONLY MODE — stopping here")
        log(f"Articles: {len(articles)}", "ok")
        log(f"Missing files: {len(missing)}", "ok")
        sys.exit(0)
    
    # ---- STEP 6: Inject favicons everywhere ----
    inject_favicons_everywhere()
    
    # ---- STEP 7: Fetch and rank projects ----
    projects = rank_all_projects()
    
    # ---- STEP 8-9: Process pages ----
    section("STEP 8 / 12 — Processing index.html")
    html = read_file("index.html")
    html = remove_stale_injected_content(html)
    html = inject_homepage_projects(html, projects)
    html = inject_homepage_blogs(html, articles)
    write_file("index.html", html)
    log("index.html processed", "ok")
    
    section("STEP 9 / 12 — Processing projects/index.html")
    html = read_file("projects/index.html")
    html = inject_projects_page(html, projects)
    write_file("projects/index.html", html)
    log("projects/index.html processed", "ok")
    
    section("STEP 9 / 12 — Processing blog/index.html")
    html = read_file("blog/index.html")
    html = remove_stale_injected_content(html)
    html = inject_blog_index(html, articles)
    write_file("blog/index.html", html)
    log("blog/index.html processed", "ok")
    
    # ---- STEP 10: Sitemap ----
    generate_sitemap(articles)
    
    # ---- STEP 11: robots.txt ----
    generate_robots_txt()
    
    # ---- STEP 12: Validate internal links ----
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS and not d.startswith('.')]
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.relpath(os.path.join(root, f), BASE_DIR))
    validate_internal_links(html_files)
    
    # ---- Cleanup old backups ----
    cleanup_old_backups()
    
    # ---- Final report ----
    print()
    print("█" * 70)
    print("  ✅ BUILD COMPLETE")
    print("█" * 70)
    print(f"  Articles:      {len(articles)}")
    print(f"  Projects:      {len(projects)}")
    print(f"  HTML files:    {len(html_files)}")
    if missing:
        print(f"  ⚠️  Missing:    {len(missing)} article file(s)")
    print()
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