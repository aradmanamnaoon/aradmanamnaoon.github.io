"""Regression checks for the cinematic static deployment.

Tests the rendered public files, the five verified featured projects, SEO,
fallbacks, mobile media, and the disabled resume feature.
"""
from __future__ import annotations

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
FEATURES = [
    ("constellation", "constellation"),
    ("medical-image-segmentation", "3d-cardiac-mri-segmentation"),
    ("ai-research-assistant-platform", "multi-agent-ai-research-assistant"),
    ("holdout-ledger", "holdout-ledger"),
    ("eu-loneliness-social-support-analysis", "eu-loneliness-social-support-analysis"),
]


class PublicHtml(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str]]] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        parsed = {key: value or "" for key, value in attrs}
        self.elements.append((tag, parsed))
        if parsed.get("id"):
            self.ids.append(parsed["id"])


def parse(path: Path) -> PublicHtml:
    parser = PublicHtml()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


class CinematicPublicSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.home = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.parser = parse(ROOT / "index.html")
        cls.projects = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))

    def test_featured_order_and_older_work_preserved(self) -> None:
        featured = sorted(
            (project for project in self.projects if project.get("homepage_featured")),
            key=lambda p: p["homepage_order"],
        )
        self.assertEqual([p["id"] for p in featured], [item[0] for item in FEATURES])
        self.assertGreaterEqual(len(self.projects), 26)
        self.assertEqual(self.home.count('class="project-plane"'), 5)
        for project_id, slug in FEATURES:
            with self.subTest(project=project_id):
                self.assertTrue((ROOT / "projects" / slug / "index.html").is_file())
                self.assertIn(f'id="{project_id}" class="project-plane"', self.home)
                self.assertIn(f'href="/projects/{slug}/"', self.home)
        self.assertTrue((ROOT / "projects" / "persian-gpt-from-scratch" / "index.html").is_file())
        self.assertTrue((ROOT / "projects" / "researchweave" / "index.html").is_file())

    def test_single_real_portrait_and_scientific_scope(self) -> None:
        portrait = [
            attrs for tag, attrs in self.parser.elements
            if tag == "img" and "photo_2026-10-06_09-42-56.jpg" in attrs.get("src", "")
        ]
        self.assertEqual(len(portrait), 1)
        self.assertTrue((ROOT / portrait[0]["src"].lstrip("/")).is_file())
        for name in ("neuro-imaging", "neuro-informatics", "neuro-genomics", "neuro-pharmacology"):
            self.assertIn(name, self.parser.ids)
        self.assertIn("developing scientific interests", self.home)
        self.assertIn("AI engineer and data scientist", self.home)
        self.assertIn("not claims of completed brain research", self.home)

    def test_disabled_resume_is_invisible_on_every_public_page(self) -> None:
        config = (ROOT / "assets" / "js" / "site-config.js").read_text(encoding="utf-8")
        self.assertRegex(config, r"showCV:\s*false")
        self.assertRegex(config, r"resumeUrl:\s*null")
        self.assertFalse((ROOT / "Profile.pdf").exists())
        for html_file in ROOT.rglob("*.html"):
            if "node_modules" in html_file.parts or ".git" in html_file.parts:
                continue
            parsed = parse(html_file)
            visible_links = [
                attrs for tag, attrs in parsed.elements
                if tag == "a" and re.search(r"(?:Profile\.pdf|/resume|/cv/)", attrs.get("href", ""), re.I)
            ]
            self.assertFalse(visible_links, f"Public CV link in {html_file}")

    def test_primary_navigation_and_section_landmarks(self) -> None:
        self.assertEqual(self.home.count("<h1"), 1)
        for target in ("main", "home", "identity", "intersection", "worlds", "toolchain", "work", "contact", "about", "research-collaboration"):
            self.assertIn(target, self.parser.ids)
        for target in ("identity", "worlds", "toolchain", "work", "contact"):
            self.assertIn(f'href="#{target}"', self.home)
        self.assertIn('aria-controls="site-nav"', self.home)
        self.assertIn('aria-expanded="false"', self.home)
        self.assertIn('href="#main"', self.home)

    def test_seo_and_archive_routes(self) -> None:
        self.assertIn('<link rel="canonical" href="https://aradmanamnaoon.github.io/">', self.home)
        self.assertIn('"@type":"Person"', self.home)
        self.assertIn('"@type":"WebPage"', self.home)
        self.assertIn('property="og:image"', self.home)
        self.assertIn('name="twitter:card"', self.home)
        self.assertIn('http-equiv="Content-Security-Policy"', self.home)
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for _, slug in FEATURES:
            self.assertIn(f"/projects/{slug}/", sitemap)
        self.assertIn("Sitemap:", (ROOT / "robots.txt").read_text(encoding="utf-8"))

    def test_loading_motion_and_system_fallbacks(self) -> None:
        js = (ROOT / "assets" / "js" / "cinematic.js").read_text(encoding="utf-8")
        css = (ROOT / "assets" / "css" / "cinematic.css").read_text(encoding="utf-8")
        self.assertIn("ScrollTrigger", js)
        self.assertIn('prefers-reduced-motion: reduce', js)
        self.assertIn("loader-failsafe", css)
        self.assertIn("@media(max-width:480px)", css)
        self.assertIn("@media(prefers-reduced-motion:reduce)", css)
        self.assertIn("IntersectionObserver", js)
        for name in ("404.html", "offline.html"):
            page = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("cinematic-states.css", page)
            self.assertIn('name="robots" content="noindex', page)
            self.assertIn('href="/projects/"', page)
            self.assertIn("Content-Security-Policy", page)
        for asset in ("favicon.ico", "favicon.svg", "apple-touch-icon.png", "site.webmanifest"):
            self.assertTrue((ROOT / asset).is_file(), asset)

    def test_all_local_urls_in_home_resolve(self) -> None:
        for tag, attrs in self.parser.elements:
            for field in ("href", "src", "poster"):
                url = attrs.get(field, "")
                if not url.startswith("/") or url.startswith("//"):
                    continue
                path = urlsplit(url).path
                resolved = ROOT / unquote(path).lstrip("/")
                if path == "/":
                    resolved = ROOT / "index.html"
                elif resolved.is_dir():
                    resolved /= "index.html"
                with self.subTest(tag=tag, url=url):
                    self.assertTrue(resolved.is_file(), f"Missing local asset: {url}")

    def test_media_optimized_and_scoped(self) -> None:
        media = ROOT / "assets" / "cinematic"
        for filename in ("hero-desktop.mp4", "hero-mobile.mp4"):
            size = (media / filename).stat().st_size
            self.assertLess(size, 4 * 1024 * 1024, filename)
            self.assertIn(filename, self.home)
        for name in ("constellation", "cardiac", "research", "holdout", "loneliness"):
            file = media / f"{name}.webp"
            self.assertTrue(file.exists())
            self.assertLess(file.stat().st_size, 300_000)
        self.assertNotIn(".glb", self.home)

    def test_case_studies_preserve_scientific_qualifications(self) -> None:
        phrases = {
            "constellation": ["experimental", "production"],
            "3d-cardiac-mri-segmentation": ["0.8821", "clinical"],
            "multi-agent-ai-research-assistant": ["offline", "quality"],
            "holdout-ledger": ["synthetic", "leakage"],
            "eu-loneliness-social-support-analysis": ["0.610", "cross-sectional", "not", "replication"],
        }
        for slug, expected in phrases.items():
            html = (ROOT / "projects" / slug / "index.html").read_text(encoding="utf-8").lower()
            for phrase in expected:
                with self.subTest(project=slug, phrase=phrase):
                    self.assertIn(phrase.lower(), html)


if __name__ == "__main__":
    unittest.main()
