"""Generate small utility pages and an explicit, local search index."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Callable


BASE = "https://aradmanamnaoon.github.io"


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def search_entries(projects: list[dict[str, Any]]) -> list[dict[str, str]]:
    entries = [
        {"title": "Home — Seyyed Arad Hosseini Moghaddam", "url": "/", "summary": "AI engineer and data scientist working in medical imaging, machine learning, Persian NLP, and quantitative humanities research.", "terms": "portfolio contact CV graduate research"},
        {"title": "Projects and research directions", "url": "/projects/", "summary": "Medical imaging, language models, humanities data science, research evidence, and broader software projects.", "terms": "projects research graduate machine learning AI RAG Flutter statistics humanities"},
        {"title": "Skills and tools", "url": "/skills/", "summary": "Full inventory of AI, medical imaging, statistics, data science, NLP, RAG, and software skills.", "terms": "skills PyTorch MONAI Python SQL Flutter Hugging Face"},
    ]
    for project in projects:
        study = project.get("caseStudy") or {}
        route = (f"/projects/{project['slug']}/"
                 if study and project.get("slug")
                 else f"/projects/#{project['id']}")
        entries.append({
            "title": str(project.get("title") or study.get("title") or "Project"),
            "url": route,
            "summary": str(study.get("description") or project.get("description") or ""),
            "terms": " ".join(str(tag) for tag in project.get("tags", [])),
        })
    return entries


def render(kind: str, projects: list[dict[str, Any]]) -> str:
    if kind == "404":
        title, eyebrow, heading = "Page not found | Arad", "404 · Page not found", "This route does not exist."
        intro = "The link may have changed, or the address may contain a typo. Search the portfolio or go directly to the projects and research directions."
        action = '<a class="utility-action primary" href="/">Back to home</a>'
        extra = ""
    elif kind == "offline":
        title, eyebrow, heading = "Offline | Arad", "Connection unavailable", "You are offline."
        intro = "The page could not be loaded right now. Pages you previously viewed may still open from this device's cache. Try again when your connection returns."
        action = '<button class="utility-action primary" type="button" data-retry>Try again</button>'
        extra = ""
    elif kind == "search":
        title, eyebrow, heading = "Search the portfolio | Arad", "Portfolio search", "Find a project or skill."
        intro = "Search medical AI, Persian NLP, agentic systems, data science, and the complete skills inventory. Results stay on this site."
        action = ""
        extra = '<section class="utility-results" aria-labelledby="results-title"><h2 id="results-title">Results</h2><p id="search-status" role="status" aria-live="polite">Enter a term to search the portfolio.</p><div id="search-results"></div></section>'
    else:
        raise ValueError(f"Unknown utility page: {kind}")

    links = "".join(
        f'<a href="{esc(item["url"])}">{esc(item["title"])}</a>'
        for item in search_entries(projects)[1:] if "#" not in item["url"]
    )
    search_script = '<script src="/assets/js/search.js" defer></script>' if kind == "search" else ""
    page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(intro)}" />
  <meta name="robots" content="noindex, follow" />
  <meta name="theme-color" content="#14181f" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; base-uri 'none'; object-src 'none'; form-action 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; worker-src 'self'" />
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="stylesheet" href="/dist/output.css" />
  <link rel="stylesheet" href="/assets/css/ux.css" />
  <link rel="stylesheet" href="/assets/css/motion.css" />
</head>
<body class="utility-page">
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="utility-header"><a class="utility-brand" href="/">ARADMANAMNAOON</a><a href="/projects/">Projects</a></header>
  <main id="main" class="utility-main">
    <p class="utility-eyebrow">{esc(eyebrow)}</p>
    <h1>{esc(heading)}</h1>
    <p class="utility-intro">{esc(intro)}</p>
    <form class="utility-search" action="/search/" method="get" role="search">
      <label for="site-search">Search the portfolio</label>
      <div class="utility-search-row"><input id="site-search" type="search" name="q" maxlength="120" autocomplete="off" placeholder="Try cardiac MRI or Persian NLP" /><button type="submit">Search</button></div>
    </form>
    <div class="utility-actions">{action}<a class="utility-action" href="/projects/#research-directions">Research directions</a><a class="utility-action" href="/skills/">All skills</a></div>
    {extra}
    <section class="utility-directory" aria-labelledby="directory-title"><h2 id="directory-title">Explore the portfolio</h2><div>{links}</div></section>
  </main>
  <footer class="utility-footer">Seyyed Arad Hosseini Moghaddam · AI engineering and data science</footer>
  <script src="/assets/js/site-ui.js" defer></script>
  <script src="/animations.js" defer></script>
  {search_script}
</body>
</html>'''
    return "\n".join(line.rstrip() for line in page.split("\n"))


def generate(root: Path, projects: list[dict[str, Any]], dry_run: bool,
             atomic_write: Callable[[Path, str, bool], bool]) -> None:
    for kind, path in (("404", root / "404.html"),
                       ("offline", root / "offline.html"),
                       ("search", root / "search" / "index.html")):
        atomic_write(path, render(kind, projects), dry_run)
    content = json.dumps(search_entries(projects), ensure_ascii=False, indent=2) + "\n"
    atomic_write(root / "search-index.json", content, dry_run)
