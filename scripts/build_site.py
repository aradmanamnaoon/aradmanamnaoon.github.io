#!/usr/bin/env python3
"""
============================================================================
 ARADMANAMNAOON — Complete Site Build System v4.0
============================================================================

 A self-healing script that manages the entire website build process,
 including detection and repair of broken HTML from previous script runs.

 WHAT'S NEW IN v4.0
 ------------------
 *  Orphaned </div> tag cleanup (fixes the "Writing." hero layout bug)
 *  Duplicate archive section detection and removal
 *  Marker deduplication across the entire file
 *  Post-build HTML structure validation
 *  Full preprocessing: analyze → plan → apply → verify
 *  Never breaks existing content

 FEATURES
 --------
 1.  Orphaned div cleanup
 2.  Duplicate section removal
 3.  Blog filename standardization
 4.  Blog archive section reconstruction
 5.  articles.json URL repair and validation
 6.  Article file existence validation
 7.  Favicon injection into every HTML file
 8.  Live project fetching from GitHub + HF APIs
 9.  Project scoring and ranking
 10. Homepage top-3 project rendering
 11. Paginated full project list
 12. Homepage top-3 article rendering
 13. Full blog archive rendering
 14. sitemap.xml generation
 15. robots.txt generation
 16. Internal link validation
 17. Auto-backup of every modified file
 18. Multiple CLI modes
 19. Old backup cleanup
 20. Comprehensive error handling

 USAGE
 -----
     python scripts/build_site.py
     python scripts/build_site.py --dry-run
     python scripts/build_site.py --validate
     python scripts/build_site.py --rollback
     python scripts/build_site.py --fix-blog
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
#  CONFIGURATION
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
FIX_BLOG_ONLY = "--fix-blog" in sys.argv

SKIP_REPOS = {"aradmanamnaoon.github.io", ".github"}

SKIP_FOLDERS = {
    ".git", "node_modules", "scripts", "dist",
    "assets", ".github", ".vscode", ".devcontainer",
    "__pycache__", ".pytest_cache"
}

BACKUP_SUFFIX = ".build-backup"

# ============================================================================
#  CURATED PROJECT OVERRIDES
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

FAVICON_LINKS = '''    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">'''

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
#  LOGGING
# ============================================================================

STATS = {
    "files_written": 0,
    "backups_created": 0,
    "orphaned_divs_removed": 0,
    "duplicate_sections_removed": 0,
    "favicons_added": 0,
    "articles_processed": 0,
    "projects_fetched": 0,
}


def log(msg, level="info"):
    prefixes = {
        "info": "   ",
        "step": "\n▶",
        "ok": "   ✓",
        "warn": "   ⚠️ ",
        "err": "   ❌",
        "repair": "   🔧",
        "new": "   ➕",
        "scan": "   🔎",
    }
    print(f"{prefixes.get(level, '   ')} {msg}")


def section(title):
    print()
    print("=" * 72)
    print(f"  {title}")
    print("=" * 72)


def print_stats():
    print()
    print("─" * 72)
    print("  Build statistics")
    print("─" * 72)
    print(f"  Files written:              {STATS['files_written']}")
    print(f"  Backups created:            {STATS['backups_created']}")
    print(f"  Orphaned </div> removed:    {STATS['orphaned_divs_removed']}")
    print(f"  Duplicate sections removed: {STATS['duplicate_sections_removed']}")
    print(f"  Favicons added:             {STATS['favicons_added']}")
    print(f"  Articles processed:         {STATS['articles_processed']}")
    print(f"  Projects fetched:           {STATS['projects_fetched']}")
    print("─" * 72)


# ============================================================================
#  FILE I/O
# ============================================================================

def file_exists(rel_path):
    return os.path.exists(os.path.join(BASE_DIR, rel_path))


def read_file(rel_path):
    with open(os.path.join(BASE_DIR, rel_path), encoding='utf-8') as f:
        return f.read()


def write_file(rel_path, content, backup=True):
    full = os.path.join(BASE_DIR, rel_path)
    if DRY_RUN:
        log(f"[DRY RUN] Would write {rel_path}")
        return
    if backup and os.path.exists(full):
        try:
            shutil.copy2(full, full + BACKUP_SUFFIX)
            STATS["backups_created"] += 1
        except Exception:
            pass
    os.makedirs(os.path.dirname(full) or BASE_DIR, exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    STATS["files_written"] += 1


# ============================================================================
#  DATE / SLUG
# ============================================================================

def parse_iso(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def days_since(dt):
    if dt is None:
        return 9999
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).days


# ============================================================================
#  HTML STRUCTURE UTILITIES
# ============================================================================

def find_matching_closing_div(html, start_pos):
    """
    Given the index of an opening '<div' tag, return the index just after
    the matching '</div>'. Handles arbitrarily deep nesting.
    """
    if start_pos < 0 or start_pos >= len(html):
        return -1

    depth = 0
    i = start_pos
    n = len(html)

    while i < n:
        if html.startswith('<div', i):
            if i + 4 >= n or html[i + 4] in ' >\t\n\r/':
                depth += 1
                i += 4
                continue
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
    and end with their matching closing tag.

    Returns a list of (start_index, end_index) tuples.
    """
    blocks = []
    pattern = re.compile(opening_pattern)
    pos = 0

    while True:
        match = pattern.search(html, pos)
        if not match:
            break

        start = match.start()
        div_pos = html.find('<div', start)
        if div_pos == -1 or div_pos > match.end():
            pos = match.end()
            continue

        end = find_matching_closing_div(html, div_pos)
        if end == -1:
            pos = match.end()
            continue

        blocks.append((start, end))
        pos = end

    return blocks


def find_all_sections(html, class_name):
    """
    Find all <section class="..."> blocks. Handles both single and
    multi-class attributes, and both `class="..."` and `class='...'`.
    """
    # Match `<section` followed anywhere within the tag by `class="... CLASS ..."`
    pattern = re.compile(
        r'<section\b[^>]*?\bclass="[^"]*\b' + re.escape(class_name) + r'\b[^"]*"[^>]*>',
        re.IGNORECASE
    )
    blocks = []
    pos = 0
    while True:
        m = pattern.search(html, pos)
        if not m:
            break
        start = m.start()
        # Find the matching </section>
        depth = 1
        i = m.end()
        while i < len(html) and depth > 0:
            if html.startswith('<section', i):
                # Check next char to make sure it's a section tag
                after = i + 8
                if after < len(html) and html[after] in ' >\t\n\r':
                    depth += 1
            elif html.startswith('</section>', i):
                depth -= 1
                if depth == 0:
                    end = i + len('</section>')
                    blocks.append((start, end))
                    pos = end
                    break
            i += 1
        else:
            break
    return blocks


def count_unbalanced_divs(fragment):
    """
    Return (opens, closes) count of <div> and </div> in a fragment.
    """
    opens = len(re.findall(r'<div\b[^>]*>', fragment))
    closes = len(re.findall(r'</div>', fragment))
    return opens, closes


def remove_orphaned_divs_in_hero(html):
    """
    Detect and remove runs of orphaned </div> tags in the blog hero section.

    Specifically targets the pattern where `<h1 class="blog-title">...</h1>`
    is immediately followed by a run of `</div>` tags that don't close
    any open div (orphaned fragments from previous script runs).
    """
    # Locate the hero section
    hero_blocks = find_all_sections(html, "blog-hero")
    if not hero_blocks:
        return html, 0

    hero_start, hero_end = hero_blocks[0]
    hero_content = html[hero_start:hero_end]

    # Detect: after the h1.blog-title closing tag, there are N orphaned </div> tags
    # before the <p class="blog-intro"> tag
    h1_close_pattern = re.compile(
        r'(</h1>)\s*((?:</div>\s*)+)\s*(<p class="blog-intro")',
        re.DOTALL
    )
    match = h1_close_pattern.search(hero_content)
    if not match:
        return html, 0

    orphan_run = match.group(2)
    orphan_count = orphan_run.count('</div>')

    # Replace the orphaned run with a single newline
    fixed_hero_content = h1_close_pattern.sub(r'\1\n\n        \3', hero_content, count=1)

    fixed_html = html[:hero_start] + fixed_hero_content + html[hero_end:]
    return fixed_html, orphan_count


def count_div_balance(html):
    """Return the net div balance (opens - closes)."""
    opens = len(re.findall(r'<div\b[^>]*>', html))
    closes = len(re.findall(r'</div>', html))
    return opens - closes


# ============================================================================
#  BLOG FILENAME REPAIR
# ============================================================================

def repair_blog_filenames():
    section("STEP 1 / 14 — Repairing blog filenames")
    blog_dir = os.path.join(BASE_DIR, "blog")
    if not os.path.isdir(blog_dir):
        log("blog/ folder not found", "warn")
        return {}

    renamed = {}
    for entry in sorted(os.listdir(blog_dir)):
        folder = os.path.join(blog_dir, entry)
        if not os.path.isdir(folder):
            continue
        htmls = [f for f in os.listdir(folder) if f.endswith(".html")]
        if "index.html" in htmls:
            log(f"blog/{entry}/index.html — OK")
            continue
        if not htmls:
            continue
        if len(htmls) == 1:
            old = htmls[0]
            try:
                if not DRY_RUN:
                    os.rename(os.path.join(folder, old),
                              os.path.join(folder, "index.html"))
                old_url = f"/blog/{entry}/{old}"
                new_url = f"/blog/{entry}/"
                renamed[old_url] = new_url
                log(f"Renamed blog/{entry}/{old} → index.html", "repair")
            except Exception as e:
                log(f"Rename failed: {e}", "err")
    if not renamed:
        log("All blog filenames are correct", "ok")
    return renamed


# ============================================================================
#  ARTICLES.JSON
# ============================================================================

def load_articles():
    path = os.path.join(BASE_DIR, "articles.json")
    if not os.path.exists(path):
        if not DRY_RUN:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
        return []
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as e:
        log(f"articles.json invalid: {e}", "err")
        sys.exit(1)


def repair_articles_json(renamed):
    section("STEP 2 / 14 — Repairing articles.json")
    articles = load_articles()
    changed = 0
    for a in articles:
        old = a.get("url", "")
        m = re.match(r'^(/blog/([^/]+))/[^/]+\.html$', old)
        if m:
            a["url"] = m.group(1) + "/"
            log(f"URL: {old} → {a['url']}", "repair")
            changed += 1
        elif old in renamed:
            a["url"] = renamed[old]
            log(f"Rename: {old} → {a['url']}", "repair")
            changed += 1
    if changed:
        write_file("articles.json", json.dumps(articles, indent=2, ensure_ascii=False), backup=False)
        log(f"Updated {changed} URL(s)", "ok")
    else:
        log("All URLs correct", "ok")
    return articles


def validate_articles(articles):
    section("STEP 3 / 14 — Validating article files")
    missing = []
    for a in articles:
        url = a.get("url", "")
        if url.endswith("/"):
            rel = url.lstrip("/") + "index.html"
        else:
            rel = url.lstrip("/")
        if not file_exists(rel):
            missing.append((a.get("title", "?"), url, rel))
    if missing:
        log(f"{len(missing)} article(s) missing files:", "warn")
        for title, url, rel in missing:
            log(f"   • {title[:60]}", "warn")
    else:
        log(f"All {len(articles)} article URLs valid", "ok")
    return missing


# ============================================================================
#  FAVICON INJECTION
# ============================================================================

def inject_favicons(html):
    if 'rel="icon"' in html:
        return html
    if '</head>' in html:
        return html.replace('</head>', FAVICON_LINKS + '\n</head>', 1)
    return html


def inject_favicons_everywhere():
    section("STEP 4 / 14 — Injecting favicons into all HTML files")
    updated = 0
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS and not d.startswith('.')]
        for f in files:
            if not f.endswith('.html'):
                continue
            fp = os.path.join(root, f)
            rp = os.path.relpath(fp, BASE_DIR)
            try:
                with open(fp, encoding='utf-8') as fh:
                    html = fh.read()
                new = inject_favicons(html)
                if new != html:
                    write_file(rp, new)
                    updated += 1
                    STATS["favicons_added"] += 1
                    log(f"Added favicons: {rp}", "ok")
            except Exception as e:
                log(f"Failed {rp}: {e}", "err")
    log(f"Favicons added: {updated}", "ok")


# ============================================================================
#  API FETCHERS
# ============================================================================

def http_get_json(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": f"{SITE_NAME}-builder",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        log(f"Failed {url}: {e}", "warn")
        return None


def fetch_github_repos():
    log(f"Fetching GitHub repos for {GITHUB_USER}...")
    repos = http_get_json(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&sort=updated")
    if not repos:
        return []
    results = []
    for r in repos:
        if r.get("fork") or r["name"] in SKIP_REPOS:
            continue
        tags = list(r.get("topics") or [])
        if r.get("language") and r["language"] not in tags:
            tags.insert(0, r["language"])
        results.append({
            "source": "github", "id": r["name"], "name": r["name"],
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
    log(f"Fetching HF models for {HF_USER}...")
    models = http_get_json(f"https://huggingface.co/api/models?author={HF_USER}&limit=100&full=true")
    if not models:
        return []
    results = []
    for m in models:
        mid = m.get("modelId") or m.get("id", "")
        short = mid.split("/")[-1] if "/" in mid else mid
        tags = []
        if m.get("pipeline_tag"):
            tags.append(m["pipeline_tag"])
        skip = {"transformers", "pytorch", "safetensors",
                "license:apache-2.0", "license:mit", "text-generation"}
        for t in (m.get("tags") or []):
            if t not in tags and t not in skip:
                tags.append(t)
        results.append({
            "source": "hf_model", "id": short, "name": short,
            "title": short.replace("-", " ").replace("_", " ").title(),
            "description": (m.get("cardData", {}) or {}).get("short_description", "") or "",
            "url": f"https://huggingface.co/{mid}",
            "downloads": m.get("downloads", 0),
            "likes": m.get("likes", 0),
            "updated": m.get("lastModified", ""),
            "created": m.get("createdAt", ""),
            "tags": tags[:6],
        })
    log(f"Fetched {len(results)} HF models", "ok")
    return results


def fetch_hf_datasets():
    log(f"Fetching HF datasets for {HF_USER}...")
    datasets = http_get_json(f"https://huggingface.co/api/datasets?author={HF_USER}&limit=100&full=true")
    if not datasets:
        return []
    results = []
    for d in datasets:
        did = d.get("id", "")
        short = did.split("/")[-1] if "/" in did else did
        results.append({
            "source": "hf_dataset", "id": short, "name": short,
            "title": short.replace("-", " ").replace("_", " ").title(),
            "description": (d.get("cardData", {}) or {}).get("short_description", "") or "",
            "url": f"https://huggingface.co/datasets/{did}",
            "downloads": d.get("downloads", 0),
            "likes": d.get("likes", 0),
            "updated": d.get("lastModified", ""),
            "created": d.get("createdAt", ""),
            "tags": (d.get("tags") or [])[:6],
        })
    log(f"Fetched {len(results)} HF datasets", "ok")
    return results


# ============================================================================
#  SCORING / RANKING
# ============================================================================

def score_project(p):
    s = 0.0
    s += p.get("stars", 0) * 10
    s += p.get("forks", 0) * 5
    s += p.get("downloads", 0) / 100.0
    s += p.get("likes", 0) * 5
    d = days_since(parse_iso(p.get("updated")))
    if d < 30:
        s += 30
    elif d < 90:
        s += 15
    elif d < 365:
        s += 5
    return s


def rank_all_projects():
    section("STEP 5 / 14 — Fetching and ranking projects")
    if NO_FETCH:
        log("Skipping API fetch (--no-fetch)", "warn")
        return []

    items = fetch_github_repos() + fetch_hf_models() + fetch_hf_datasets()
    STATS["projects_fetched"] = len(items)

    for it in items:
        ov = CURATED.get(it["id"])
        if ov:
            for k, v in ov.items():
                it[k] = v
            it["curated"] = True

    for it in items:
        it["_score"] = score_project(it)

    items.sort(key=lambda x: (
        not x.get("featured", False),
        -x["_score"],
        x.get("name", "")
    ))

    for it in items:
        dt = parse_iso(it.get("updated")) or parse_iso(it.get("created"))
        if dt:
            it["date"] = dt.strftime("%Y-%m-%d")
            it["dateDisplay"] = dt.strftime("%B %Y")
        else:
            it["date"] = "2024-01-01"
            it["dateDisplay"] = "2024"

    log(f"Ranked {len(items)} projects", "ok")
    if VERBOSE:
        for i, p in enumerate(items[:10], 1):
            log(f"   #{i} [{p['source']}] {p['title']} ({p['_score']:.1f})")
    return items


# ============================================================================
#  RENDER — PROJECTS
# ============================================================================

def get_metrics(p):
    if p.get("metrics"):
        return p["metrics"]
    if p["source"] == "github":
        return [
            {"value": str(p.get("stars", 0)), "label": "Stars"},
            {"value": str(p.get("forks", 0)), "label": "Forks"},
            {"value": p.get("language", "—"), "label": "Language"},
        ]
    if p["source"] in ("hf_model", "hf_dataset"):
        return [
            {"value": f"{p.get('downloads', 0):,}", "label": "Downloads"},
            {"value": str(p.get("likes", 0)), "label": "Likes"},
            {"value": "HF", "label": "Hosted on"},
        ]
    return []


def get_actions(p):
    actions = [{"url": p["url"], "label": "View project ↗", "primary": True}]
    if p.get("homepage"):
        actions.append({"url": p["homepage"], "label": "Live demo ↗", "primary": False})
    return actions


def render_homepage_projects(projects):
    top = projects[:MAX_PROJECTS_HOMEPAGE]
    cards = []
    badges = {"github": "GitHub", "hf_model": "Hugging Face", "hf_dataset": "HF Dataset"}
    for i, p in enumerate(top, start=1):
        num = f"{i:02d}"
        metrics = get_metrics(p)
        m_html = "".join(
            f'<div class="metric"><span class="metric-value">{m["value"]}</span>'
            f'<span class="metric-label">{m["label"]}</span></div>'
            for m in metrics
        )
        t_html = "".join(f'<span class="project-tag">{t}</span>' for t in p.get("tags", []))
        actions = get_actions(p)
        a_html = "".join(
            f'<a class="project-link {"primary" if a.get("primary") else ""}" '
            f'href="{a["url"]}" target="_blank" rel="noopener noreferrer">{a["label"]}</a>'
            for a in actions
        )
        desc = p.get("description") or "Source and details on GitHub / Hugging Face."
        type_str = p.get("type", badges[p["source"]])
        cards.append(f'''          <article id="{p['id']}" class="featured-project">
            <div class="grid gap-8 sm:grid-cols-[auto_1fr]">
              <div class="project-number" aria-hidden="true">{num}</div>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-ink/70">{type_str}</p>
                <h3 class="mt-3 font-serif text-3xl font-bold sm:text-4xl">{p["title"]}</h3>
                <p class="mt-5 max-w-[70ch] leading-relaxed text-ink/70">{desc}</p>
                <div class="metric-grid mt-8">{m_html}</div>
                <div class="project-tags">{t_html}</div>
                <div class="project-actions">{a_html}</div>
              </div>
            </div>
          </article>
''')
    return '<div class="mt-14 space-y-6">\n' + "\n".join(cards) + '</div>'


def render_paginated_projects(projects):
    data = []
    for p in projects:
        data.append({
            "id": p["id"], "title": p["title"],
            "type": p.get("type", p["source"]),
            "description": p.get("description") or "",
            "dateDisplay": p.get("dateDisplay", ""),
            "metrics": get_metrics(p),
            "tags": p.get("tags", []),
            "actions": get_actions(p),
            "note": p.get("note", ""),
        })
    pj = json.dumps(data, ensure_ascii=False)
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
.projects-pagination button:hover:not(:disabled):not(.active) {{ border-color: #7db4f0; color: #7db4f0; }}
.projects-pagination button.active {{ background: #7db4f0; color: #14181f; border-color: #7db4f0; }}
.projects-pagination button:disabled {{ opacity: 0.35; cursor: not-allowed; }}
</style>

<script>
(function() {{
  const projects = {pj};
  const perPage = {PROJECTS_PER_PAGE};
  let currentPage = 1;
  const totalPages = Math.max(1, Math.ceil(projects.length / perPage));
  const container = document.getElementById('projects-paginated');
  const pagination = document.getElementById('projects-pagination');
  if (!container || !pagination) return;
  function esc(s) {{ return String(s).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c]); }}
  function renderProjects(page) {{
    const start = (page - 1) * perPage;
    const items = projects.slice(start, start + perPage);
    let html = '';
    items.forEach((p, i) => {{
      const num = String(start + i + 1).padStart(2, '0');
      const mh = (p.metrics || []).map(m => `<div class="metric"><strong>${{esc(m.value)}}</strong><span>${{esc(m.label)}}</span></div>`).join('');
      const th = (p.tags || []).map(t => `<span class="tag">${{esc(t)}}</span>`).join('');
      const ah = (p.actions || []).map(a => `<a class="action ${{a.primary ? 'primary' : ''}}" href="${{esc(a.url)}}" target="_blank" rel="noopener noreferrer">${{esc(a.label)}}</a>`).join('');
      const nh = p.note ? `<p class="note">${{esc(p.note)}}</p>` : '';
      html += `<article class="project" id="${{esc(p.id)}}"><div class="num" aria-hidden="true">${{num}}</div><div><p class="type">${{esc(p.type)}}</p><h2>${{esc(p.title)}}</h2><p class="desc">${{esc(p.description)}}</p><div class="metrics">${{mh}}</div><div class="tags">${{th}}</div><div class="actions">${{ah}}</div>${{nh}}</div></article>`;
    }});
    container.innerHTML = html;
  }}
  function renderPagination() {{
    let html = '';
    html += `<button ${{currentPage === 1 ? 'disabled' : ''}} data-page="${{currentPage - 1}}">←</button>`;
    for (let i = 1; i <= totalPages; i++) html += `<button class="${{i === currentPage ? 'active' : ''}}" data-page="${{i}}">${{i}}</button>`;
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


# ============================================================================
#  RENDER — ARTICLES
# ============================================================================

def render_homepage_blogs(articles):
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
#  BLOG LAYOUT FIX (CORE)
# ============================================================================

def fix_blog_layout(html):
    """
    Fix all known blog/index.html layout problems:
    1. Remove orphaned </div> runs in the hero section
    2. Remove duplicate blog-archive sections (keep only the first)
    3. Deduplicate AUTO:BLOG_ARTICLES markers
    4. Rebuild the archive section if it's missing
    5. Ensure markers are inside the archive's .blog-post-list
    """
    log("Analyzing blog/index.html structure...", "scan")

    original = html

    # ---- Fix 1: orphaned </div> in the hero section ----
    html, n_orphans = remove_orphaned_divs_in_hero(html)
    if n_orphans:
        log(f"Removed {n_orphans} orphaned </div> tag(s) from the hero section", "repair")
        STATS["orphaned_divs_removed"] += n_orphans

    # ---- Fix 2: Duplicate archive sections ----
    archive_blocks = find_all_sections(html, "blog-archive")
    if len(archive_blocks) > 1:
        log(f"Found {len(archive_blocks)} blog-archive sections — keeping only the first", "repair")
        # Remove from the end backwards to keep indices valid
        for start, end in reversed(archive_blocks[1:]):
            html = html[:start] + html[end:]
        STATS["duplicate_sections_removed"] += len(archive_blocks) - 1

    # ---- Fix 3: deduplicate AUTO:BLOG_ARTICLES markers ----
    # Keep only the first START and first END marker
    start_marker = '<!-- AUTO:BLOG_ARTICLES:START -->'
    end_marker = '<!-- AUTO:BLOG_ARTICLES:END -->'
    start_count = html.count(start_marker)
    end_count = html.count(end_marker)
    if start_count > 1 or end_count > 1:
        log(f"Found {start_count} START / {end_count} END markers — deduplicating", "repair")
        # Remove all start markers first
        html = html.replace(start_marker, '')
        html = html.replace(end_marker, '')
        # Find the archive and reinsert exactly one pair inside .blog-post-list
        archive_blocks = find_all_sections(html, "blog-archive")
        if archive_blocks:
            archive_start, archive_end = archive_blocks[0]
            archive_content = html[archive_start:archive_end]
            # Find .blog-post-list inside the archive
            list_match = re.search(r'<div\s+class="blog-post-list">', archive_content)
            if list_match:
                insert_pos = archive_start + list_match.end()
                markers = f'\n          {start_marker}\n          {end_marker}'
                html = html[:insert_pos] + markers + html[insert_pos:]
                log("Reinserted clean marker pair inside archive", "ok")

    # ---- Fix 4: Archive section missing entirely ----
    archive_blocks = find_all_sections(html, "blog-archive")
    if not archive_blocks:
        log("No blog-archive section — rebuilding from template", "repair")
        if '</main>' in html:
            html = html.replace('</main>', BLOG_ARCHIVE_TEMPLATE + '  </main>', 1)
        else:
            html = html.replace('</body>', BLOG_ARCHIVE_TEMPLATE + '</body>', 1)

    # ---- Fix 5: Verify div balance ----
    balance = count_div_balance(html)
    if balance != 0:
        log(f"Div balance is off by {balance} — check for remaining orphans", "warn")

    if html == original:
        log("Blog layout already clean", "ok")
    return html


def remove_stale_injected_content(html):
    """Remove old inline-styled blog cards."""
    original = html
    html = re.sub(
        r'<div class="blog-card"\s+style="[^"]*"[^>]*>.*?</div>\s*'
        r'(?=<div class="blog-card"|<p class="blog-intro"|<a class="writing-link"|</div>|</section>|<!--)',
        '', html, flags=re.DOTALL
    )
    html = re.sub(r'<div class="blog-list-container">\s*</div>\s*', '', html)
    html = re.sub(r'<div class="projects-list-container">\s*</div>\s*', '', html)
    if len(html) != len(original):
        log(f"Removed {len(original) - len(html)} chars of stale content", "repair")
    return html


# ============================================================================
#  INJECTION
# ============================================================================

def inject_homepage_projects(html, projects):
    rendered = render_homepage_projects(projects)
    pattern = r'(<div class="mt-14 space-y-6">).*?(</div>\s*<div class="mt-16">)'
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, f'{rendered}\n\n        \\2', html, flags=re.DOTALL)
        log("Injected top projects into homepage", "ok")
    else:
        log("Homepage project container not found", "warn")
    return html


def inject_projects_page(html, projects):
    rendered = render_paginated_projects(projects)
    pattern = r'(<div class="projects" id="project-list">).*?(</div>\s*(?:<p class="projects-empty"|</section>))'
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, f'\\1\n{rendered}\n      \\2', html, flags=re.DOTALL)
        log("Injected paginated projects", "ok")
    else:
        log("Projects page container not found", "warn")
    html = re.sub(r'<div class="project-tools"[^>]*>.*?</div>\s*(?=<div class="projects")', '', html, flags=re.DOTALL)
    html = re.sub(
        r'<script>\s*\(\(\)\s*=>\s*\{\s*const filterPanel = document\.getElementById\("project-filters"\).*?</script>',
        '', html, flags=re.DOTALL
    )
    html = re.sub(r'<p class="projects-empty"[^>]*>.*?</p>', '', html, flags=re.DOTALL)
    return html


def inject_homepage_blogs(html, articles):
    if '<!-- AUTO:HOME_ARTICLES:START -->' not in html:
        log("index.html: AUTO:HOME_ARTICLES markers missing — skipping", "warn")
        return html
    rendered = render_homepage_blogs(articles)
    pattern = r'(<!-- AUTO:HOME_ARTICLES:START -->).*?(<!-- AUTO:HOME_ARTICLES:END -->)'
    html = re.sub(pattern, f'\\1\n{rendered}\n        <!-- AUTO:HOME_ARTICLES:END -->', html, flags=re.DOTALL)
    log("Injected top articles into homepage", "ok")
    return html


def inject_blog_index(html, articles):
    if '<!-- AUTO:BLOG_ARTICLES:START -->' not in html:
        log("blog/index.html: AUTO:BLOG_ARTICLES markers missing — skipping", "warn")
        return html
    rendered = render_blog_index(articles)
    pattern = r'(<!-- AUTO:BLOG_ARTICLES:START -->).*?(<!-- AUTO:BLOG_ARTICLES:END -->)'
    html = re.sub(pattern, f'\\1\n{rendered}\n          <!-- AUTO:BLOG_ARTICLES:END -->', html, flags=re.DOTALL)
    log(f"Injected {len(articles)} article(s) into blog", "ok")
    return html


# ============================================================================
#  SITEMAP / ROBOTS
# ============================================================================

def generate_sitemap(articles):
    section("STEP 10 / 14 — Generating sitemap.xml")
    urls = [
        {"loc": f"{SITE_URL}/", "priority": "1.0"},
        {"loc": f"{SITE_URL}/projects/", "priority": "0.9"},
        {"loc": f"{SITE_URL}/blog/", "priority": "0.8"},
    ]
    for a in articles:
        urls.append({"loc": f"{SITE_URL}{a['url']}", "priority": "0.6"})
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        xml.append(f'  <url><loc>{u["loc"]}</loc><priority>{u["priority"]}</priority></url>')
    xml.append('</urlset>')
    write_file("sitemap.xml", "\n".join(xml), backup=False)
    log(f"sitemap.xml ({len(urls)} URLs)", "ok")


def generate_robots_txt():
    section("STEP 11 / 14 — Generating robots.txt")
    write_file("robots.txt", f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
""", backup=False)
    log("robots.txt generated", "ok")


# ============================================================================
#  VALIDATION
# ============================================================================

def validate_internal_links(html_files):
    section("STEP 12 / 14 — Validating internal links")
    broken = []
    for rp in html_files:
        try:
            html = read_file(rp)
        except Exception:
            continue
        for link in re.findall(r'href="([^"]+)"', html):
            if link.startswith(('http://', 'https://', '//', '#', 'mailto:', 'tel:')):
                continue
            cl = link.split('?')[0].split('#')[0]
            if not cl:
                continue
            fd = os.path.dirname(os.path.join(BASE_DIR, rp))
            if cl.startswith('/'):
                target = os.path.join(BASE_DIR, cl.lstrip('/'))
            else:
                target = os.path.normpath(os.path.join(fd, cl))
            if os.path.isdir(target):
                target = os.path.join(target, "index.html")
            if not os.path.exists(target):
                if '.' in os.path.basename(cl) or cl.endswith('/'):
                    broken.append((rp, link))
    if broken:
        log(f"{len(broken)} broken link(s):", "warn")
        for s, l in broken[:20]:
            log(f"   {s} → {l}", "warn")
    else:
        log("No broken internal links", "ok")
    return broken


def verify_blog_structure(html):
    """Post-build: verify blog page structure is correct."""
    section("STEP 13 / 14 — Verifying blog structure")
    issues = []

    # 1. Check div balance
    balance = count_div_balance(html)
    if balance != 0:
        issues.append(f"Div imbalance: {balance} (positive = too many opens)")

    # 2. Check archive count
    archives = find_all_sections(html, "blog-archive")
    if len(archives) == 0:
        issues.append("No blog-archive section found")
    elif len(archives) > 1:
        issues.append(f"{len(archives)} blog-archive sections found (should be 1)")

    # 3. Check markers
    start_count = html.count('<!-- AUTO:BLOG_ARTICLES:START -->')
    end_count = html.count('<!-- AUTO:BLOG_ARTICLES:END -->')
    if start_count != 1:
        issues.append(f"{start_count} AUTO:BLOG_ARTICLES:START markers (should be 1)")
    if end_count != 1:
        issues.append(f"{end_count} AUTO:BLOG_ARTICLES:END markers (should be 1)")

    # 4. Check no orphaned divs after h1.blog-title
    h1_close_pattern = re.compile(
        r'</h1>\s*(?:</div>\s*){2,}\s*<p class="blog-intro"',
        re.DOTALL
    )
    if h1_close_pattern.search(html):
        issues.append("Orphaned </div> tags still present after blog hero title")

    # 5. Check hero doesn't contain blog-cards
    hero_blocks = find_all_sections(html, "blog-hero")
    if hero_blocks:
        hero_content = html[hero_blocks[0][0]:hero_blocks[0][1]]
        if 'class="blog-post"' in hero_content:
            issues.append("Hero section contains blog-post elements")

    if issues:
        log("Blog structure issues:", "warn")
        for i in issues:
            log(f"   • {i}", "warn")
    else:
        log("Blog structure verified — no issues", "ok")
    return issues


# ============================================================================
#  BACKUP CLEANUP
# ============================================================================

def cleanup_old_backups():
    section("STEP 14 / 14 — Cleaning up old backups")
    removed = 0
    now = datetime.now().timestamp()
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS and not d.startswith('.')]
        for f in files:
            if f.endswith(BACKUP_SUFFIX):
                p = os.path.join(root, f)
                if (now - os.path.getmtime(p)) / 86400 > 30:
                    try:
                        os.remove(p)
                        removed += 1
                    except Exception:
                        pass
    log(f"Removed {removed} old backup(s)", "ok" if removed else "info")


# ============================================================================
#  ROLLBACK
# ============================================================================

def rollback_all():
    section("ROLLBACK")
    restored = 0
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS and not d.startswith('.')]
        for f in files:
            if f.endswith(BACKUP_SUFFIX):
                bp = os.path.join(root, f)
                op = bp[:-len(BACKUP_SUFFIX)]
                try:
                    shutil.copy2(bp, op)
                    os.remove(bp)
                    restored += 1
                    log(f"Restored {os.path.relpath(op, BASE_DIR)}", "ok")
                except Exception as e:
                    log(f"Failed: {e}", "err")
    log(f"Restored {restored} file(s)", "ok")
    sys.exit(0)


# ============================================================================
#  MAIN
# ============================================================================

def main():
    print()
    print("█" * 72)
    print(f"  {SITE_NAME} — Complete Build System v4.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if DRY_RUN:
        print("  ⚠️  DRY RUN MODE")
    if NO_FETCH:
        print("  ⚠️  NO-FETCH MODE")
    if FIX_BLOG_ONLY:
        print("  🔧 FIX-BLOG MODE")
    print("█" * 72)

    if ROLLBACK:
        rollback_all()

    if FIX_BLOG_ONLY:
        section("FIX-BLOG MODE")
        if not file_exists("blog/index.html"):
            log("blog/index.html not found", "err")
            sys.exit(1)
        html = read_file("blog/index.html")
        html = fix_blog_layout(html)
        write_file("blog/index.html", html)
        html = read_file("blog/index.html")
        verify_blog_structure(html)
        log("Fix-blog complete", "ok")
        sys.exit(0)

    # STEP 1-3: prep
    renamed = repair_blog_filenames()
    articles = repair_articles_json(renamed)
    STATS["articles_processed"] = len(articles)
    missing = validate_articles(articles)

    if VALIDATE_ONLY:
        section("VALIDATE ONLY")
        log(f"Articles: {len(articles)}", "ok")
        log(f"Missing: {len(missing)}", "ok")
        sys.exit(0)

    # STEP 4
    inject_favicons_everywhere()

    # STEP 5
    projects = rank_all_projects()

    # STEP 6: index.html
    section("STEP 6 / 14 — Processing index.html")
    html = read_file("index.html")
    html = remove_stale_injected_content(html)
    html = inject_homepage_projects(html, projects)
    html = inject_homepage_blogs(html, articles)
    write_file("index.html", html)
    log("index.html written", "ok")

    # STEP 7: projects/index.html
    section("STEP 7 / 14 — Processing projects/index.html")
    html = read_file("projects/index.html")
    html = inject_projects_page(html, projects)
    write_file("projects/index.html", html)
    log("projects/index.html written", "ok")

    # STEP 8: blog/index.html — THE FIX
    section("STEP 8 / 14 — Processing blog/index.html")
    html = read_file("blog/index.html")
    html = remove_stale_injected_content(html)
    html = fix_blog_layout(html)          # <-- the real fix
    html = inject_blog_index(html, articles)
    write_file("blog/index.html", html)
    log("blog/index.html written", "ok")

    # STEP 9: verify
    html = read_file("blog/index.html")
    verify_blog_structure(html)

    # STEP 10: sitemap
    generate_sitemap(articles)

    # STEP 11: robots
    generate_robots_txt()

    # STEP 12: link check
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS and not d.startswith('.')]
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.relpath(os.path.join(root, f), BASE_DIR))
    validate_internal_links(html_files)

    # STEP 14: cleanup
    cleanup_old_backups()

    # Report
    print()
    print("█" * 72)
    print("  ✅ BUILD COMPLETE")
    print("█" * 72)
    print(f"  Articles:   {len(articles)}")
    print(f"  Projects:   {len(projects)}")
    print(f"  HTML files: {len(html_files)}")
    if missing:
        print(f"  ⚠️  Missing: {len(missing)} article file(s)")
    print_stats()
    print("  Next steps:")
    print("    1. git diff   (review changes)")
    print("    2. git add . && git commit -m '...' && git push")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)