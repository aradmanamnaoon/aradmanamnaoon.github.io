import os
import re
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ============================================================
#  CONFIGURATION
# ============================================================
BASE_DIR = os.getcwd()
SITE_URL = "https://aradmanamnaoon.github.io"

GITHUB_USER = "aradmanamnaoon"
HF_USER = "aradmanamnaoon"

MAX_PROJECTS_HOMEPAGE = 3
MAX_ARTICLES_HOMEPAGE = 3
PROJECTS_PER_PAGE = 6

SKIP_REPOS = {"aradmanamnaoon.github.io", ".github", "aradmanamnaoon"}

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

# ============================================================
#  FAVICON
# ============================================================
FAVICON_LINKS = '''    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">'''

def inject_favicons(html):
    if 'rel="icon"' in html:
        return html
    if '</head>' in html:
        return html.replace('</head>', FAVICON_LINKS + '\n</head>')
    return html

# ============================================================
#  REPAIR BROKEN SECTIONS (one-time fix for previously injected junk)
# ============================================================
def repair_broken_sections(html, file_type):
    """
    Removes unstyled injected content from previous script runs and 
    re-establishes clean markers so future injections work correctly.
    
    file_type: 'homepage' | 'blog_index' | 'projects_index'
    """
    original_len = len(html)
    
    # --- 1. Remove OLD unstyled blog-list-container blocks (with inline styles) ---
    html = re.sub(
        r'<div class="blog-list-container">\s*<div class="blog-card"[^>]*style=[^>]*>.*?</div>\s*</div>\s*',
        '', html, flags=re.DOTALL
    )
    
    # --- 2. Remove OLD unstyled blog cards WITHOUT a container ---
    # (the screenshot shows cards floating directly in the section, unstyled)
    # Match <div class="blog-card" style="..."> ... </div> blocks
    html = re.sub(
        r'<div class="blog-card"\s+style="[^"]*"[^>]*>.*?</div>\s*(?=<div class="blog-card"|<p class="blog-intro"|<a class="writing-link"|</div>|</section>|<!--)',
        '', html, flags=re.DOTALL
    )
    
    # --- 3. Remove duplicate markers (if script ran twice) ---
    for marker in ['AUTO:HOME_ARTICLES', 'AUTO:BLOG_ARTICLES']:
        # Keep only the first pair
        pattern = rf'<!-- {marker}:START -->.*?<!-- {marker}:END -->\s*'
        matches = list(re.finditer(pattern, html, re.DOTALL))
        if len(matches) > 1:
            # Keep the first, remove the rest
            for m in reversed(matches[1:]):
                html = html[:m.start()] + html[m.end():]
    
    # --- 4. Restore clean marker pairs if missing ---
    if file_type == 'homepage':
        # Ensure marker pair exists inside .writing-post-list
        if '<!-- AUTO:HOME_ARTICLES:START -->' not in html:
            # Look for <div class="writing-post-list"> and inject markers inside
            pattern = r'(<div class="writing-post-list">)\s*(.*?)\s*(</div>\s*</section>)'
            def add_markers(m):
                return f'{m.group(1)}\n        <!-- AUTO:HOME_ARTICLES:START -->\n        <!-- AUTO:HOME_ARTICLES:END -->\n        {m.group(3)}'
            html = re.sub(pattern, add_markers, html, count=1, flags=re.DOTALL)
    
    elif file_type == 'blog_index':
        if '<!-- AUTO:BLOG_ARTICLES:START -->' not in html:
            # Insert markers inside .blog-post-list
            pattern = r'(<div class="blog-post-list">)\s*(.*?)\s*(</div>\s*</section>)'
            def add_markers(m):
                return f'{m.group(1)}\n          <!-- AUTO:BLOG_ARTICLES:START -->\n          <!-- AUTO:BLOG_ARTICLES:END -->\n        {m.group(3)}'
            html = re.sub(pattern, add_markers, html, count=1, flags=re.DOTALL)
    
    # --- 5. Remove orphaned empty blog-list-container divs ---
    html = re.sub(r'<div class="blog-list-container">\s*</div>\s*', '', html)
    html = re.sub(r'<div class="projects-list-container">\s*</div>\s*', '', html)
    
    if len(html) != original_len:
        print(f"   🔧 Repaired: removed {original_len - len(html)} chars of stale content")
    
    return html

# ============================================================
#  API FETCHERS
# ============================================================
def fetch_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "aradmanamnaoon-site-builder",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"   ⚠️  Failed {url}: {e}")
    return None

def fetch_github_repos():
    print("🌐 Fetching GitHub repos...")
    repos = fetch_json(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&sort=updated")
    if not repos: return []
    results = []
    for r in repos:
        if r.get("fork") or r["name"] in SKIP_REPOS: continue
        tags = r.get("topics", []) or []
        if r.get("language") and r["language"] not in tags:
            tags.insert(0, r["language"])
        results.append({
            "source": "github", "id": r["name"], "name": r["name"],
            "title": r["name"].replace("-", " ").replace("_", " ").title(),
            "description": r.get("description") or "",
            "url": r["html_url"], "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0), "updated": r.get("updated_at", ""),
            "created": r.get("created_at", ""), "tags": tags[:6],
            "language": r.get("language") or "", "homepage": r.get("homepage") or "",
        })
    print(f"   → {len(results)} repos fetched")
    return results

def fetch_hf_models():
    print("🌐 Fetching Hugging Face models...")
    models = fetch_json(f"https://huggingface.co/api/models?author={HF_USER}&limit=100&full=true")
    if not models: return []
    results = []
    for m in models:
        model_id = m.get("modelId") or m.get("id", "")
        short_name = model_id.split("/")[-1] if "/" in model_id else model_id
        tags = []
        if m.get("pipeline_tag"): tags.append(m["pipeline_tag"])
        for t in (m.get("tags") or []):
            if t not in tags and t not in ("transformers", "pytorch", "safetensors", "license:apache-2.0", "license:mit"):
                tags.append(t)
        results.append({
            "source": "hf_model", "id": short_name, "name": short_name,
            "title": short_name.replace("-", " ").replace("_", " ").title(),
            "description": (m.get("cardData", {}) or {}).get("short_description", "") or "",
            "url": f"https://huggingface.co/{model_id}",
            "downloads": m.get("downloads", 0), "likes": m.get("likes", 0),
            "updated": m.get("lastModified", ""), "created": m.get("createdAt", ""),
            "tags": tags[:6],
        })
    print(f"   → {len(results)} models fetched")
    return results

def fetch_hf_datasets():
    print("🌐 Fetching Hugging Face datasets...")
    datasets = fetch_json(f"https://huggingface.co/api/datasets?author={HF_USER}&limit=100&full=true")
    if not datasets: return []
    results = []
    for d in datasets:
        ds_id = d.get("id", "")
        short_name = ds_id.split("/")[-1] if "/" in ds_id else ds_id
        results.append({
            "source": "hf_dataset", "id": short_name, "name": short_name,
            "title": short_name.replace("-", " ").replace("_", " ").title(),
            "description": (d.get("cardData", {}) or {}).get("short_description", "") or "",
            "url": f"https://huggingface.co/datasets/{ds_id}",
            "downloads": d.get("downloads", 0), "likes": d.get("likes", 0),
            "updated": d.get("lastModified", ""), "created": d.get("createdAt", ""),
            "tags": (d.get("tags") or [])[:6],
        })
    print(f"   → {len(results)} datasets fetched")
    return results

# ============================================================
#  SCORING & RANKING
# ============================================================
def parse_iso(dt_str):
    if not dt_str: return None
    try: return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception: return None

def days_since(dt):
    if dt is None: return 9999
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).days

def score_project(p):
    score = p.get("stars", 0) * 10 + p.get("forks", 0) * 5
    score += p.get("downloads", 0) / 100.0 + p.get("likes", 0) * 5
    days = days_since(parse_iso(p.get("updated")))
    if days < 30: score += 30
    elif days < 90: score += 15
    elif days < 365: score += 5
    return score

def rank_all_projects():
    all_items = fetch_github_repos() + fetch_hf_models() + fetch_hf_datasets()
    for item in all_items:
        override = CURATED.get(item["id"])
        if override:
            for k, v in override.items(): item[k] = v
            item["curated"] = True
    for item in all_items:
        item["_score"] = score_project(item)
    all_items.sort(key=lambda x: (not x.get("featured", False), -x["_score"], x.get("name", "")))
    for item in all_items:
        dt = parse_iso(item.get("updated")) or parse_iso(item.get("created"))
        item["date"] = dt.strftime("%Y-%m-%d") if dt else "2024-01-01"
        item["dateDisplay"] = dt.strftime("%B %Y") if dt else "2024"
    return all_items

# ============================================================
#  RENDER FUNCTIONS
# ============================================================
def render_homepage_projects(projects):
    top = projects[:MAX_PROJECTS_HOMEPAGE]
    cards = []
    for i, p in enumerate(top, start=1):
        num = f"{i:02d}"
        metrics = p.get("metrics", [])
        if not metrics:
            if p["source"] == "github":
                metrics = [
                    {"value": str(p.get("stars", 0)), "label": "Stars"},
                    {"value": str(p.get("forks", 0)), "label": "Forks"},
                    {"value": p.get("language", "—"), "label": "Language"},
                ]
            elif p["source"] in ("hf_model", "hf_dataset"):
                metrics = [
                    {"value": f"{p.get('downloads', 0):,}", "label": "Downloads"},
                    {"value": str(p.get("likes", 0)), "label": "Likes"},
                    {"value": "HF", "label": "Hosted on"},
                ]
        metrics_html = "".join(
            f'<div class="metric"><span class="metric-value">{m["value"]}</span>'
            f'<span class="metric-label">{m["label"]}</span></div>'
            for m in metrics
        )
        tags_html = "".join(f'<span class="project-tag">{t}</span>' for t in p.get("tags", []))
        actions = [{"url": p["url"], "label": "View project ↗", "primary": True}]
        if p.get("homepage"):
            actions.append({"url": p["homepage"], "label": "Live demo ↗", "primary": False})
        actions_html = "".join(
            f'<a class="project-link {"primary" if a.get("primary") else ""}" href="{a["url"]}" '
            f'target="_blank" rel="noopener noreferrer">{a["label"]}</a>'
            for a in actions
        )
        desc = p.get("description") or "Source and details on GitHub / Hugging Face."
        source_badge = {"github": "GitHub", "hf_model": "Hugging Face", "hf_dataset": "HF Dataset"}[p["source"]]
        cards.append(f'''          <article id="{p['id']}" class="featured-project">
            <div class="grid gap-8 sm:grid-cols-[auto_1fr]">
              <div class="project-number" aria-hidden="true">{num}</div>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-ink/70">{p.get("type", source_badge)}</p>
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
    data = []
    for p in projects:
        metrics = p.get("metrics", [])
        if not metrics:
            if p["source"] == "github":
                metrics = [
                    {"value": str(p.get("stars", 0)), "label": "Stars"},
                    {"value": str(p.get("forks", 0)), "label": "Forks"},
                    {"value": p.get("language", "—"), "label": "Language"},
                ]
            elif p["source"] in ("hf_model", "hf_dataset"):
                metrics = [
                    {"value": f"{p.get('downloads', 0):,}", "label": "Downloads"},
                    {"value": str(p.get("likes", 0)), "label": "Likes"},
                    {"value": "HF", "label": "Hosted on"},
                ]
        actions = [{"url": p["url"], "label": "View project ↗", "primary": True}]
        if p.get("homepage"):
            actions.append({"url": p["homepage"], "label": "Live demo ↗", "primary": False})
        data.append({
            "id": p["id"], "title": p["title"], "type": p.get("type", p["source"]),
            "description": p.get("description") or "", "dateDisplay": p.get("dateDisplay", ""),
            "metrics": metrics, "tags": p.get("tags", []), "actions": actions,
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
  function esc(s) {{ return String(s).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[c]); }}
  function renderProjects(page) {{
    const start = (page - 1) * perPage;
    const items = projects.slice(start, start + perPage);
    let html = '';
    items.forEach((p, i) => {{
      const num = String(start + i + 1).padStart(2, '0');
      const metricsHtml = (p.metrics || []).map(m => `<div class="metric"><strong>${{esc(m.value)}}</strong><span>${{esc(m.label)}}</span></div>`).join('');
      const tagsHtml = (p.tags || []).map(t => `<span class="tag">${{esc(t)}}</span>`).join('');
      const actionsHtml = (p.actions || []).map(a => `<a class="action ${{a.primary ? 'primary' : ''}}" href="${{esc(a.url)}}" target="_blank" rel="noopener noreferrer">${{esc(a.label)}}</a>`).join('');
      const noteHtml = p.note ? `<p class="note">${{esc(p.note)}}</p>` : '';
      html += `<article class="project" id="${{esc(p.id)}}"><div class="num" aria-hidden="true">${{num}}</div><div><p class="type">${{esc(p.type)}}</p><h2>${{esc(p.title)}}</h2><p class="desc">${{esc(p.description)}}</p><div class="metrics">${{metricsHtml}}</div><div class="tags">${{tagsHtml}}</div><div class="actions">${{actionsHtml}}</div>${{noteHtml}}</div></article>`;
    }});
    container.innerHTML = html;
  }}
  function renderPagination() {{
    let html = '';
    html += `<button ${{currentPage === 1 ? 'disabled' : ''}} data-page="${{currentPage - 1}}" aria-label="Previous">←</button>`;
    for (let i = 1; i <= totalPages; i++) html += `<button class="${{i === currentPage ? 'active' : ''}}" data-page="${{i}}">${{i}}</button>`;
    html += `<button ${{currentPage === totalPages ? 'disabled' : ''}} data-page="${{currentPage + 1}}" aria-label="Next">→</button>`;
    pagination.innerHTML = html;
    pagination.querySelectorAll('button[data-page]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const p = parseInt(btn.dataset.page, 10);
        if (p >= 1 && p <= totalPages && p !== currentPage) {{
          currentPage = p;
          renderProjects(currentPage);
          renderPagination();
          document.getElementById('selected-projects').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
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
    sorted_articles = sorted(articles, key=lambda x: x.get('date', ''), reverse=True)[:MAX_ARTICLES_HOMEPAGE]
    cards = []
    for a in sorted_articles:
        tags = "".join(f'\n              <span class="writing-post-tag">{t}</span>' for t in a.get("tags", []))
        cards.append(f'''        <a class="writing-post-card" href="{a["url"]}" aria-label="Read {a["title"]}">
          <div><div class="writing-post-meta">{a.get("dateDisplay", a["date"])} · {a.get("readTime", "")}</div>
            <h3 class="writing-post-title">{a["title"]}</h3>
            <p class="writing-post-description">{a["description"]}</p>
            <div class="writing-post-tags" aria-label="Article topics">{tags}
            </div>
          </div><span class="writing-post-arrow" aria-hidden="true">→</span>
        </a>''')
    return "\n\n".join(cards)

def render_blog_index(articles):
    sorted_articles = sorted(articles, key=lambda x: x.get('date', ''), reverse=True)
    cards = []
    for a in sorted_articles:
        tags = "".join(f'\n                  <span class="blog-post-tag">{t}</span>' for t in a.get("tags", []))
        cards.append(f'''          <article><a class="blog-post" href="{a["url"]}" aria-label="Read {a["title"]}">
              <div class="blog-post-meta"><time datetime="{a["date"]}">{a.get("dateDisplay", a["date"])}</time><br />{a.get("readTime", "")}</div>
              <div><h3 class="blog-post-title">{a["title"]}</h3><p class="blog-post-description">{a["description"]}</p>
                <div class="blog-post-tags" aria-label="Article topics">{tags}
                </div></div>
              <span class="blog-post-arrow" aria-hidden="true">→</span></a></article>''')
    return "\n\n".join(cards)

# ============================================================
#  INJECTION
# ============================================================
def inject_homepage_projects(html, projects):
    rendered = render_homepage_projects(projects)
    pattern = r'(<div class="mt-14 space-y-6">).*?(</div>\s*<div class="mt-16">)'
    if re.search(pattern, html, re.DOTALL):
        return re.sub(pattern, f'{rendered}\n\n        \\2', html, flags=re.DOTALL)
    return html

def inject_projects_page(html, projects):
    rendered = render_paginated_projects(projects)
    pattern = r'(<div class="projects" id="project-list">).*?(</div>\s*(?:<p class="projects-empty"|</section>))'
    if not re.search(pattern, html, re.DOTALL):
        print("   ⚠️  projects/index.html: project-list container not found — skipping")
        return html
    new_html = re.sub(pattern, f'\\1\n{rendered}\n      \\2', html, flags=re.DOTALL)
    # Remove old filter tools panel
    new_html = re.sub(r'<div class="project-tools"[^>]*>.*?</div>\s*(?=<div class="projects")', '', new_html, flags=re.DOTALL)
    # Remove old filter script
    new_html = re.sub(
        r'<script>\s*\(\(\)\s*=>\s*\{\s*const filterPanel = document\.getElementById\("project-filters"\).*?</script>',
        '', new_html, flags=re.DOTALL
    )
    new_html = re.sub(r'<p class="projects-empty"[^>]*>.*?</p>', '', new_html, flags=re.DOTALL)
    return new_html

def inject_homepage_blogs(html, articles):
    rendered = render_homepage_blogs(articles)
    pattern = r'(<!-- AUTO:HOME_ARTICLES:START -->).*?(<!-- AUTO:HOME_ARTICLES:END -->)'
    if not re.search(pattern, html, re.DOTALL):
        print("   ⚠️  index.html: AUTO:HOME_ARTICLES markers not found — skipping")
        return html
    return re.sub(pattern, f'\\1\n{rendered}\n        <!-- AUTO:HOME_ARTICLES:END -->', html, flags=re.DOTALL)

def inject_blog_index(html, articles):
    rendered = render_blog_index(articles)
    pattern = r'(<!-- AUTO:BLOG_ARTICLES:START -->).*?(<!-- AUTO:BLOG_ARTICLES:END -->)'
    if not re.search(pattern, html, re.DOTALL):
        print("   ⚠️  blog/index.html: AUTO:BLOG_ARTICLES markers not found — skipping")
        return html
    return re.sub(pattern, f'\\1\n{rendered}\n<!-- AUTO:BLOG_ARTICLES:END -->', html, flags=re.DOTALL)

# ============================================================
#  SITEMAP
# ============================================================
def generate_sitemap(articles):
    urls = [
        f"<url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>",
        f"<url><loc>{SITE_URL}/projects/</loc><priority>0.9</priority></url>",
        f"<url><loc>{SITE_URL}/blog/</loc><priority>0.8</priority></url>"
    ]
    for a in articles:
        urls.append(f"<url><loc>{SITE_URL}{a['url']}</loc><priority>0.6</priority></url>")
    content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + '\n</urlset>'
    with open("sitemap.xml", 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ sitemap.xml ({len(urls)} URLs)")

# ============================================================
#  MAIN
# ============================================================
def main():
    print("=" * 60)
    
    projects = rank_all_projects()
    print(f"\n📊 Ranked {len(projects)} total projects\n")
    
    articles_json = os.path.join(BASE_DIR, "articles.json")
    if os.path.exists(articles_json):
        with open(articles_json, encoding='utf-8') as f:
            articles = json.load(f)
        print(f"📝 Loaded {len(articles)} articles\n")
    else:
        articles = []
    
    # ---- index.html ----
    print("📄 Processing index.html")
    with open("index.html", encoding='utf-8') as f:
        html = f.read()
    html = inject_favicons(html)
    html = repair_broken_sections(html, 'homepage')
    html = inject_homepage_projects(html, projects)
    html = inject_homepage_blogs(html, articles)
    with open("index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    # ---- projects/index.html ----
    print("📄 Processing projects/index.html")
    with open("projects/index.html", encoding='utf-8') as f:
        html = f.read()
    html = inject_favicons(html)
    html = repair_broken_sections(html, 'projects_index')
    html = inject_projects_page(html, projects)
    with open("projects/index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    # ---- blog/index.html ----
    print("📄 Processing blog/index.html")
    with open("blog/index.html", encoding='utf-8') as f:
        html = f.read()
    html = inject_favicons(html)
    html = repair_broken_sections(html, 'blog_index')
    html = inject_blog_index(html, articles)
    with open("blog/index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    print()
    generate_sitemap(articles)
    print("\n✅ Done!")

if __name__ == "__main__":
    main()