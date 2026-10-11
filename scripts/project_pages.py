"""Render long-form, evidence-led project pages from projects.json."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Callable


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def render(project: dict[str, Any], site_url: str) -> str | None:
    study = project.get("caseStudy")
    slug = str(project.get("slug") or "").strip("/")
    if not isinstance(study, dict) or not slug:
        return None

    route = f"/projects/{slug}/"
    canonical = site_url.rstrip("/") + route
    title = str(study.get("title") or project.get("title") or "Project case study")
    seo_title = str(study.get("seoTitle") or title)
    description = str(study.get("description") or project.get("description") or "")
    lede = str(study.get("lede") or project.get("description") or "")
    source_url = str(project.get("url") or "")
    source_label = str(study.get("sourceLabel") or "View the source project")
    metrics = project.get("metrics", [])
    metric_html = "".join(
        f'<div class="metric"><strong>{esc(metric.get("value"))}</strong>'
        f'<span>{esc(metric.get("label"))}</span></div>'
        for metric in metrics if isinstance(metric, dict)
    )

    def list_items(name: str) -> str:
        values = study.get(name, [])
        if not isinstance(values, list):
            return ""
        return "".join(f"<li>{esc(value)}</li>" for value in values if isinstance(value, str))

    work_schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": canonical,
        "inLanguage": "en",
        "isPartOf": {"@type": "WebSite", "url": site_url.rstrip("/") + "/", "name": "ARADMANAMNAOON"},
        "mainEntity": {
            "@type": "CreativeWork",
            "name": str(project.get("title") or title),
            "description": description,
            "url": source_url,
            "creator": {
                "@type": "Person",
                "@id": site_url.rstrip("/") + "/#person",
                "name": "Seyyed Arad Hosseini Moghaddam",
            },
        },
    }
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url.rstrip("/") + "/"},
            {"@type": "ListItem", "position": 2, "name": "Projects", "item": site_url.rstrip("/") + "/projects/"},
            {"@type": "ListItem", "position": 3, "name": str(project.get("title") or title), "item": canonical},
        ],
    }
    schema = "\n".join(
        '<script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
        + "\n</script>"
        for data in (work_schema, breadcrumb_schema)
    )

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(seo_title)}</title>
  <meta name="description" content="{esc(description)}" />
  <meta name="author" content="Seyyed Arad Hosseini Moghaddam" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta name="theme-color" content="#14181f" />
  <link rel="canonical" href="{esc(canonical)}" />
  <link rel="alternate" hreflang="en" href="{esc(canonical)}" />
  <link rel="alternate" hreflang="x-default" href="{esc(canonical)}" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="ARADMANAMNAOON" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:url" content="{esc(canonical)}" />
  <meta property="og:image" content="{esc(site_url.rstrip('/') + '/og-image.jpg')}" />
  <meta property="og:image:width" content="1890" />
  <meta property="og:image:height" content="848" />
  <meta property="og:image:alt" content="Portfolio case study: {esc(title)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />
  <meta name="twitter:image" content="{esc(site_url.rstrip('/') + '/og-image.jpg')}" />
  <meta name="twitter:image:alt" content="Portfolio case study: {esc(title)}" />
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,500;1,600;1,700;1,800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/dist/output.css" />
  <link rel="stylesheet" href="/assets/css/ux.css" />
  <link rel="stylesheet" href="/assets/css/motion.css?v=20261011-motion-exp-v8" />
  {schema}
  <link rel="stylesheet" href="/assets/css/interaction-hub.css?v=20261011-theme-v5" />
  <link rel="stylesheet" href="/assets/css/page-extras.css?v=20261011-interactive-v1" />
</head>
<body class="project-case-study">
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="shell site-header">
    <nav class="nav" aria-label="Primary navigation"><a class="brand" href="/">ARADMANAMNAOON</a><div class="nav-links"><a href="/projects/">Projects</a><a href="/skills/">Skills</a></div></nav>
    <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/projects/">Projects</a><span aria-hidden="true">/</span><span aria-current="page">{esc(project.get('title') or title)}</span></nav>
  </header>
  <main id="main" class="shell">
    <header class="hero"><p class="eyebrow">Project case study · {esc(project.get('type', 'Research project'))}</p><h1>{esc(title)}</h1><p class="lede">{esc(lede)}</p><div class="hero-actions"><a class="action primary" href="{esc(source_url)}" target="_blank" rel="noopener noreferrer">{esc(source_label)} ↗</a><a class="action" href="/projects/#research-directions">Research directions</a></div></header>
    <section aria-label="Reported project metrics" class="metrics">{metric_html}</section>
    <div class="case-grid">
      <section class="case-section" data-reveal="true" aria-labelledby="challenge-heading"><p class="eyebrow">01 · Context</p><h2 id="challenge-heading">Research question</h2><p>{esc(study.get('challenge', ''))}</p></section>
      <section class="case-section" data-reveal="true" aria-labelledby="approach-heading"><p class="eyebrow">02 · Methods</p><h2 id="approach-heading">Approach</h2><ul>{list_items('approach')}</ul></section>
      <section class="case-section" data-reveal="true" aria-labelledby="results-heading"><p class="eyebrow">03 · Evaluation</p><h2 id="results-heading">Reported results</h2><ul>{list_items('results')}</ul></section>
      <section class="case-section limitations" data-reveal="true" aria-labelledby="limitations-heading"><p class="eyebrow">04 · Scope</p><h2 id="limitations-heading">Limitations</h2><p>{esc(study.get('limitations', ''))}</p></section>
    </div>
    <nav class="related" aria-label="Related pages"><strong>Explore more:</strong> <a href="/projects/">All projects</a><a href="/projects/#research-directions">Research directions</a><a href="/skills/">Skills and tools</a></nav>
  </main>
  <footer class="shell">Seyyed Arad Hosseini Moghaddam · Medical AI, machine learning, and data science portfolio.</footer>
  <script src="/animations.js?v=20261011-motion-exp-v7" defer></script>
  <script src="/assets/js/brand-icons.js?v=20261011-brands-v7" defer></script>
  <script src="/assets/js/site-ui.js" defer></script>
  <script src="/assets/js/interaction-hub.js?v=20261011-theme-v5" defer></script>
  <script src="/assets/js/page-extras.js?v=20261011-interactive-v1" defer></script>
</body>
</html>'''


def generate(root: Path, projects: list[dict[str, Any]], site_url: str,
             dry_run: bool, atomic_write: Callable[[Path, str, bool], bool]) -> list[str]:
    routes: list[str] = []
    for project in projects:
        page = render(project, site_url)
        slug = str(project.get("slug") or "").strip("/")
        if not page or not slug:
            continue
        atomic_write(root / "projects" / slug / "index.html", page, dry_run)
        routes.append(f"/projects/{slug}/")
    return routes
