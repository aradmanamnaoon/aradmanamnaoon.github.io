#!/usr/bin/env python3
"""Build, audit, and safely maintain this static GitHub Pages site.

Responsibilities: project rendering, favicon injection, sitemap and robots
generation, link checks, backups, dry runs, and rollback. The audit engine
checks supported source, configuration, and content files under the
repository, excluding generated, dependency, and VCS directories.
`--fix-safe` applies only narrowly defined, repeatable fixes. Uncertain
findings are reported instead of rewriting arbitrary content.

No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import traceback
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

SITE_URL = "https://aradmanamnaoon.github.io"
SITE_NAME = "ARADMANAMNAOON"
GITHUB_USER = "aradmanamnaoon"
HF_USER = "aradmanamnaoon"
HERO_IMAGE_URL = f"{SITE_URL}/photo_2026-10-06_09-42-56.jpg"
HERO_IMAGE_ALT = (
    "Seyyed Arad Hosseini Moghaddam — AI Engineer and Data Scientist"
)
HERO_IMAGE_TITLE = "Seyyed Arad Hosseini Moghaddam headshot"
HERO_IMAGE_WIDTH = 853
HERO_IMAGE_HEIGHT = 1280
MAX_PROJECTS_HOMEPAGE = 3
PROJECTS_PER_PAGE = 6
FAVICON_LINKS = """    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">"""
SKIP_DIRS = {
    ".git",
    "node_modules",
    "build",
    "coverage",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    ".cache",
    "vendor",
}
TEXT_SUFFIXES = {
    ".html",
    ".htm",
    ".css",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".jsx",
    ".py",
    ".json",
    ".jsonld",
    ".xml",
    ".txt",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".sh",
    ".webmanifest",
    ".svg",
    ".gitignore",
    ".conf",
}
SECRET_PATTERNS = [
    re.compile(r"(?i)\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\b(?:ghp|github_pat|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9_-]{24,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    path: str
    line: int
    check: str
    message: str
    fix: str


class SiteError(Exception):
    """An expected repository or build error."""


def log(message: str, level: str = "info") -> None:
    prefix = {"ok": "✓", "warn": "!", "error": "ERROR", "step": "▶"}.get(
        level, " "
    )
    print(f"{prefix} {message}")


def escape_html(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def discover_root(explicit: str | None) -> Path:
    root = (
        Path(explicit).expanduser().resolve()
        if explicit
        else Path(__file__).resolve().parents[1]
    )
    markers = (
        root / "index.html",
        root / "scripts" / "build_site.py",
    )
    if not all(path.exists() for path in markers):
        raise SiteError(
            f"{root} does not look like the site root "
            "(expected index.html, scripts/build_site.py)"
        )
    return root


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def atomic_write(path: Path, content: str, dry_run: bool = False) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return False
    if dry_run:
        log(f"Would write {path}")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
    log(f"Wrote {path}", "ok")
    return True


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SiteError(f"Cannot read valid JSON from {path}: {error}") from error


def walk_files(root: Path, suffixes: set[str] | None = None) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(directory for directory in dirs if directory not in SKIP_DIRS)
        for name in sorted(files):
            path = Path(current) / name
            if (
                suffixes is None
                or path.suffix.lower() in suffixes
                or (
                    suffixes is not None
                    and name in {".gitignore", "Dockerfile"}
                    and ".gitignore" in suffixes
                )
            ):
                yield path


def html_files(root: Path) -> list[Path]:
    return list(walk_files(root, {".html", ".htm"}))


def local_url_to_path(
    root: Path, source: Path, url: str
) -> tuple[Path | None, str]:
    parsed = urllib.parse.urlsplit(url.strip())
    if url.strip().startswith("//"):
        return None, "external"
    if parsed.scheme.lower() in {"http", "https"} and parsed.netloc:
        return None, "external"
    if parsed.scheme or parsed.netloc:
        return None, "scheme"
    decoded = urllib.parse.unquote(parsed.path)
    if not decoded:
        target = source
    elif decoded.startswith("/"):
        target = root / decoded.lstrip("/")
    else:
        target = source.parent / decoded
    try:
        target = target.resolve()
        target.relative_to(root.resolve())
    except (OSError, ValueError):
        return None, "outside"
    if target.is_dir():
        target = target / "index.html"
    if not target.exists() and not target.suffix:
        html_candidate = Path(str(target) + ".html")
        if html_candidate.exists():
            target = html_candidate
    return target, "local"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.references: list[tuple[str, str, int]] = []
        self.images: list[tuple[dict[str, str | None], int]] = []
        self.headings: list[tuple[int, str, int]] = []
        self.meta: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []
        self.anchors: list[tuple[dict[str, str | None], str, int]] = []
        self.inputs: list[tuple[dict[str, str | None], int]] = []
        self._anchor: tuple[dict[str, str | None], int] | None = None
        self._anchor_text = ""
        self.forms = 0
        self._heading: tuple[int, int] | None = None
        self._heading_text = ""
        self._line = 1

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        data = dict(attrs)
        line = self.getpos()[0]
        if data.get("id"):
            self.ids.add(data["id"] or "")
        if tag in {
            "a",
            "area",
            "link",
            "script",
            "img",
            "source",
            "iframe",
            "video",
            "audio",
        }:
            for attribute in ("href", "src", "poster"):
                value = data.get(attribute)
                if value:
                    self.references.append((attribute, value, line))
            srcset = data.get("srcset")
            if srcset:
                for candidate in srcset.split(","):
                    url = candidate.strip().split()[0] if candidate.strip() else ""
                    if url:
                        self.references.append(("srcset", url, line))
        if tag == "img":
            self.images.append((data, line))
        if tag == "meta":
            self.meta.append(data)
        if tag == "link":
            self.links.append(data)
        if tag == "a":
            self._anchor = (data, line)
            self._anchor_text = ""
        if tag == "input":
            self.inputs.append((data, line))
        if tag == "form":
            self.forms += 1
        if re.fullmatch(r"h[1-6]", tag):
            self._heading = (int(tag[1]), line)
            self._heading_text = ""
        if tag not in {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        }:
            self._line = line

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if self._heading:
            self._heading_text += data
        if self._anchor:
            self._anchor_text += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._anchor:
            attrs, anchor_line = self._anchor
            self.anchors.append((attrs, self._anchor_text.strip(), anchor_line))
            self._anchor = None
            self._anchor_text = ""
        if self._heading and tag == f"h{self._heading[0]}":
            level, line = self._heading
            self.headings.append((level, self._heading_text.strip(), line))
            self._heading = None
            self._heading_text = ""


def parse_html(path: Path) -> tuple[str, PageParser]:
    source = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(source)
    parser.close()
    return source, parser


def check_finding(
    findings: list[Finding],
    severity: str,
    category: str,
    path: Path,
    root: Path,
    line: int,
    check: str,
    message: str,
    fix: str,
) -> None:
    findings.append(
        Finding(severity, category, relpath(path, root), line, check, message, fix)
    )


def meta_values(parser: PageParser, key: str, attr: str) -> list[str]:
    return [
        str(item.get("content") or "").strip()
        for item in parser.meta
        if (item.get(key) or "").lower() == attr.lower()
    ]


def validate_homepage_contract(
    path: Path,
    root: Path,
    source: str,
    parser: PageParser,
    findings: list[Finding],
) -> None:
    """Validate the visual and SEO hooks used by the current homepage."""
    if relpath(path, root) != "index.html":
        return

    def report(
        severity: str,
        category: str,
        check: str,
        message: str,
        fix: str,
        token: str,
    ) -> None:
        position = source.lower().find(token.lower())
        line = source[:position].count("\n") + 1 if position >= 0 else 1
        check_finding(
            findings,
            severity,
            category,
            path,
            root,
            line,
            check,
            message,
            fix,
        )

    hero_images = [
        (attrs, line)
        for attrs, line in parser.images
        if "hero-portrait" in (attrs.get("class") or "").split()
    ]
    if len(hero_images) != 1:
        report(
            "High",
            "Homepage / image SEO",
            "hero-image-count",
            f"Expected one .hero-portrait image; found {len(hero_images)}.",
            "Keep one visible .hero-portrait img in the hero media column.",
            "hero-portrait",
        )
    else:
        attrs, image_line = hero_images[0]
        hero_filename = "photo_2026-10-06_09-42-56.jpg"
        accepted_srcs = {
            HERO_IMAGE_URL,
            f"/{hero_filename}",
            f"./{hero_filename}",
            hero_filename,
        }
        actual_src = (attrs.get("src") or "").strip()
        if actual_src not in accepted_srcs:
            check_finding(
                findings,
                "High",
                "Homepage / image SEO",
                path,
                root,
                image_line,
                "hero-image-src",
                "The hero image src does not match the current homepage contract.",
                f'Set src="{HERO_IMAGE_URL}" or a relative form '
                f'like "/{hero_filename}" on the .hero-portrait image.',
            )

        expected = {
            "alt": HERO_IMAGE_ALT,
            "title": HERO_IMAGE_TITLE,
            "width": str(HERO_IMAGE_WIDTH),
            "height": str(HERO_IMAGE_HEIGHT),
            "loading": "eager",
            "fetchpriority": "high",
        }
        for attribute, value in expected.items():
            if (attrs.get(attribute) or "").strip() != value:
                check_finding(
                    findings,
                    "High" if attribute == "alt" else "Medium",
                    "Homepage / image SEO",
                    path,
                    root,
                    image_line,
                    f"hero-image-{attribute}",
                    f"The hero image {attribute} does not match the current homepage contract.",
                    f'Set {attribute}="{value}" on the .hero-portrait image.',
                )

    image_path = root / "photo_2026-10-06_09-42-56.jpg"
    if not image_path.is_file():
        report(
            "High",
            "Homepage / image SEO",
            "hero-image-file",
            "The repository-root headshot file is missing.",
            "Add photo_2026-10-06_09-42-56.jpg to the repository root and commit it.",
            "hero-portrait",
        )
    else:
        dimensions = image_dimensions(image_path)
        if dimensions and dimensions != (HERO_IMAGE_WIDTH, HERO_IMAGE_HEIGHT):
            report(
                "Medium",
                "Homepage / image SEO",
                "hero-image-dimensions",
                f"The root headshot is {dimensions[0]}×{dimensions[1]}, but the homepage declares {HERO_IMAGE_WIDTH}×{HERO_IMAGE_HEIGHT}.",
                "Update the hero img and matching JSON-LD dimensions to the actual image dimensions.",
                "hero-portrait",
            )

    portrait_rule = re.search(
        r"\.hero-portrait\s*\{([^}]*)\}",
        source,
        re.I | re.S,
    )
    if not portrait_rule:
        report(
            "High",
            "Homepage / layout",
            "hero-image-style",
            "The homepage has no inline .hero-portrait rule.",
            "Restore visible block sizing, circular radius, and object-fit: cover for the hero image.",
            "hero-portrait",
        )
    else:
        declarations = portrait_rule.group(1).lower()
        required_css = {
            "display": r"display\s*:\s*block\b",
            "visibility": r"visibility\s*:\s*visible\b",
            "opacity": r"opacity\s*:\s*(?:1|1\.0)\b",
            "width": r"width\s*:\s*100%(?:\s|;|$)",
            "height": r"height\s*:\s*100%(?:\s|;|$)",
            "circle": r"border-radius\s*:\s*50%(?:\s|;|$)",
            "crop": r"object-fit\s*:\s*cover\b",
        }
        for name, pattern in required_css.items():
            if not re.search(pattern, declarations):
                report(
                    "Medium",
                    "Homepage / layout",
                    f"hero-image-css-{name}",
                    f"The .hero-portrait CSS is missing its {name} visibility/layout declaration.",
                    "Keep the hero image visible, square, circular, and cropped with object-fit: cover.",
                    ".hero-portrait",
                )

    body_rule = re.search(
        r"(?m)^[ \t]*body\s*\{(?P<declarations>[^}]+)\}",
        source,
        re.I,
    )
    body_css = body_rule.group("declarations").lower() if body_rule else ""
    if not re.search(r"background-color\s*:\s*#14181f\b", body_css):
        report(
            "Medium",
            "Homepage / visual design",
            "homepage-body-surface",
            "The homepage body does not declare the shared dark surface color (#14181f).",
            "Keep the body surface at #14181f; let dist/output.css provide the dotted pseudo-element background.",
            "body {",
        )

    inline_dot_layer = re.search(
        r"(?is)body\s*::before\s*\{[^{}]*radial-gradient\s*\(",
        source,
    )
    if inline_dot_layer:
        report(
            "Medium",
            "Homepage / visual design",
            "homepage-inline-dot-override",
            "An inline body::before radial-gradient overrides the shared stylesheet's subtle dotted background.",
            "Remove the custom body::before radial-gradient block and let dist/output.css draw the background.",
            "body::before",
        )
    if not re.search(r"isolation\s*:\s*isolate\b", body_css):
        report(
            "Medium",
            "Homepage / visual design",
            "dot-grid-stacking-context",
            "The body does not isolate the negative-z-index dot layers from the root background.",
            "Add isolation: isolate to the body rule so the dot and glow layers paint above the body surface and behind content.",
            "body {",
        )

    stylesheet = root / "dist" / "output.css"
    if not stylesheet.is_file():
        report(
            "High",
            "Homepage / visual design",
            "dot-grid-stylesheet",
            "dist/output.css is missing, so its body pseudo-element dot layers cannot load.",
            "Restore the built stylesheet referenced by index.html.",
            "dist/output.css",
        )
    else:
        css = stylesheet.read_text(encoding="utf-8", errors="replace").lower()
        if not all(token in css for token in ("body:before", "body:after", "radial-gradient", "--glow-x")):
            report(
                "High",
                "Homepage / visual design",
                "dot-grid-css-layers",
                "dist/output.css is missing one or more dot-grid or cursor-glow declarations.",
                "Restore the body pseudo-element dot grid, radial mask, and --glow-x mask position in the source stylesheet, then rebuild output.css.",
                "dist/output.css",
            )

    animation_script = root / "animations.js"
    if not animation_script.is_file():
        report(
            "High",
            "Homepage / visual design",
            "dot-grid-animation-script",
            "animations.js is missing, so mouse-reactive dot variables cannot update.",
            "Restore the script referenced by the homepage.",
            "animations.js",
        )
    else:
        script = animation_script.read_text(encoding="utf-8", errors="replace")
        if not all(
            token in script
            for token in ("mousemove", "--dot-x", "--dot-y", "--glow-x", "--glow-y")
        ):
            report(
                "High",
                "Homepage / visual design",
                "dot-grid-animation-hooks",
                "animations.js is missing one or more mousemove CSS-variable hooks.",
                "Restore the mousemove handler that updates --dot-x, --dot-y, --glow-x, and --glow-y.",
                "animations.js",
            )

    schema_blocks = re.findall(
        r"<script\b(?=[^>]*type=[\"']application/ld\+json[\"'])"
        r"[^>]*>(.*?)</script\s*>",
        source,
        re.I | re.S,
    )
    schema_nodes: list[dict[str, Any]] = []
    for block in schema_blocks:
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        graph = data.get("@graph", []) if isinstance(data, dict) else []
        if isinstance(graph, list):
            schema_nodes.extend(node for node in graph if isinstance(node, dict))
        elif isinstance(data, dict):
            schema_nodes.append(data)

    person_nodes = [
        node for node in schema_nodes
        if "Person" in (
            node.get("@type")
            if isinstance(node.get("@type"), list)
            else [node.get("@type")]
        )
    ]
    if not any(
        (node.get("image", {}).get("url") if isinstance(node.get("image"), dict) else node.get("image"))
        == HERO_IMAGE_URL
        for node in person_nodes
    ):
        report(
            "Medium",
            "Homepage / structured data",
            "person-image",
            "Person JSON-LD does not reference the current headshot URL.",
            "Set the Person image property to an ImageObject for the repository-root headshot.",
            '"@type": "Person"',
        )

    webpage_nodes = [
        node for node in schema_nodes
        if any(
            value in {"WebPage", "ProfilePage"}
            for value in (
                node.get("@type")
                if isinstance(node.get("@type"), list)
                else [node.get("@type")]
            )
        )
    ]
    if not any(
        isinstance(node.get("primaryImageOfPage"), dict)
        and node["primaryImageOfPage"].get("url") == HERO_IMAGE_URL
        for node in webpage_nodes
    ):
        report(
            "Medium",
            "Homepage / structured data",
            "webpage-primary-image",
            "WebPage JSON-LD does not reference the current headshot as its primary image.",
            "Set primaryImageOfPage to an ImageObject for the repository-root headshot.",
            '"primaryImageOfPage"',
        )


def validate_html_page(
    path: Path,
    root: Path,
    findings: list[Finding],
    all_pages: dict[str, PageParser],
    check_external: bool,
) -> None:
    try:
        source, parser = parse_html(path)
    except (OSError, UnicodeError) as error:
        check_finding(
            findings,
            "High",
            "Code quality",
            path,
            root,
            1,
            "html-read",
            str(error),
            "Save the page as valid UTF-8 HTML.",
        )
        return

    title_match = re.search(r"<title\b[^>]*>(.*?)</title\s*>", source, re.I | re.S)
    title = (
        html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip())
        if title_match
        else ""
    )
    schema_pattern = re.compile(
        r"<script\b(?=[^>]*type=[\"']application/ld\+json[\"'])"
        r"[^>]*>(.*?)</script\s*>",
        re.I | re.S,
    )
    for schema_match in schema_pattern.finditer(source):
        try:
            json.loads(schema_match.group(1).strip())
        except json.JSONDecodeError as error:
            schema_line = (
                source[:schema_match.start(1)].count("\n") + error.lineno
            )
            check_finding(
                findings,
                "High",
                "SEO",
                path,
                root,
                schema_line,
                "json-ld",
                f"Invalid JSON-LD: {error.msg}.",
                "Correct the structured-data JSON syntax.",
            )

    descriptions = meta_values(parser, "name", "description")
    canonicals = [
        str(link.get("href") or "")
        for link in parser.links
        if (link.get("rel") or "").lower() == "canonical"
    ]
    og_titles = meta_values(parser, "property", "og:title")
    og_descs = meta_values(parser, "property", "og:description")
    og_urls = meta_values(parser, "property", "og:url")
    og_images = meta_values(parser, "property", "og:image")
    twitter_cards = meta_values(parser, "name", "twitter:card")
    noindex = any(
        "noindex" in (item.get("content") or "").lower()
        for item in parser.meta
        if (item.get("name") or "").lower() in {"robots", "googlebot"}
    )

    def source_line(token: str) -> int:
        position = source.lower().find(token.lower())
        return source[:position].count("\n") + 1 if position >= 0 else 1

    validate_homepage_contract(path, root, source, parser, findings)

    if not title:
        check_finding(
            findings,
            "High",
            "SEO",
            path,
            root,
            1,
            "title",
            "Missing or empty title element.",
            "Add one concise, page-specific title element.",
        )
    if len(re.findall(r"<title\b", source, re.I)) > 1:
        check_finding(
            findings,
            "Medium",
            "SEO",
            path,
            root,
            source_line("<title"),
            "duplicate-title",
            "Multiple title elements are present.",
            "Keep a single page title.",
        )
    if len(descriptions) != 1 or not descriptions[0]:
        check_finding(
            findings,
            "Medium",
            "SEO",
            path,
            root,
            1,
            "description",
            "Expected exactly one non-empty meta description.",
            "Add or consolidate the description metadata.",
        )

    if not noindex:
        if len(canonicals) != 1 or not canonicals[0]:
            check_finding(
                findings,
                "Medium",
                "SEO",
                path,
                root,
                1,
                "canonical",
                "Expected exactly one canonical URL.",
                "Add the absolute preferred URL for this page.",
            )
        elif not canonicals[0].startswith(SITE_URL + "/"):
            check_finding(
                findings,
                "High",
                "SEO",
                path,
                root,
                source_line('rel="canonical"'),
                "canonical-origin",
                f"Canonical is not on the configured site origin: {canonicals[0]}",
                "Use the matching canonical URL under SITE_URL.",
            )

        if og_images:
            image_url = urllib.parse.urlsplit(og_images[0])
            if (
                image_url.scheme == "https"
                and image_url.netloc == urllib.parse.urlsplit(SITE_URL).netloc
            ):
                image_path = root / urllib.parse.unquote(image_url.path.lstrip("/"))
                dimensions = (
                    image_dimensions(image_path) if image_path.is_file() else None
                )
                if dimensions:
                    width = meta_values(parser, "property", "og:image:width")
                    height = meta_values(parser, "property", "og:image:height")
                    if width != [str(dimensions[0])] or height != [
                        str(dimensions[1])
                    ]:
                        check_finding(
                            findings,
                            "Medium",
                            "SEO",
                            path,
                            root,
                            source_line("og:image"),
                            "og-image-dimensions",
                            "Open Graph dimensions do not match the image "
                            f"dimensions {dimensions[0]}×{dimensions[1]}.",
                            "Set og:image:width and og:image:height to the "
                            "actual image dimensions.",
                        )

        if len(og_titles) != 1 or not og_titles[0]:
            check_finding(
                findings,
                "Medium",
                "SEO",
                path,
                root,
                1,
                "og-title",
                "Missing or duplicate Open Graph title.",
                "Provide one page-specific og:title.",
            )
        if len(og_descs) != 1 or not og_descs[0]:
            check_finding(
                findings,
                "Medium",
                "SEO",
                path,
                root,
                1,
                "og-description",
                "Missing or duplicate Open Graph description.",
                "Provide one page-specific og:description.",
            )
        if len(og_urls) != 1 or not og_urls[0]:
            check_finding(
                findings,
                "Medium",
                "SEO",
                path,
                root,
                1,
                "og-url",
                "Missing or duplicate og:url.",
                "Set og:url to the page's canonical URL.",
            )
        if len(og_images) != 1 or not og_images[0]:
            check_finding(
                findings,
                "Medium",
                "SEO",
                path,
                root,
                1,
                "og-image",
                "Missing or duplicate og:image.",
                "Set one absolute, crawlable share image URL.",
            )
        if not twitter_cards:
            check_finding(
                findings,
                "Low",
                "SEO",
                path,
                root,
                1,
                "twitter-card",
                "Missing Twitter card declaration.",
                "Add twitter:card summary_large_image when a share image is available.",
            )

    if (
        path.name == "index.html"
        and path.parent.name not in {"projects"}
        and not re.search(r"property=[\"']og:image:width", source, re.I)
    ):
        check_finding(
            findings,
            "Low",
            "SEO",
            path,
            root,
            source_line("og:image"),
            "og-image-dimensions-missing",
            "Open Graph image dimensions are not declared.",
            "Add dimensions that match the image file.",
        )

    weak_anchor_text = {
        "click here",
        "here",
        "read more",
        "more",
        "learn more",
        "link",
        "this link",
    }
    for anchor_attrs, anchor_text, anchor_line in parser.anchors:
        accessible_name = (
            anchor_attrs.get("aria-label") or anchor_text
        ).strip().lower()
        if anchor_attrs.get("href") and accessible_name in weak_anchor_text:
            check_finding(
                findings,
                "Low",
                "SEO / Accessibility",
                path,
                root,
                anchor_line,
                "weak-anchor-text",
                f"Anchor text {accessible_name!r} does not describe its destination.",
                "Use concise link text that describes the destination or action.",
            )

    for attrs, image_line in parser.images:
        if "alt" not in attrs:
            check_finding(
                findings,
                "Medium",
                "Accessibility",
                path,
                root,
                image_line,
                "image-alt",
                "Image is missing an alt attribute.",
                'Add descriptive alt text, or alt="" for decorative images.',
            )

    h1s = [heading for heading in parser.headings if heading[0] == 1]
    if len(h1s) != 1:
        check_finding(
            findings,
            "Medium",
            "SEO / Accessibility",
            path,
            root,
            h1s[1][2] if len(h1s) > 1 else 1,
            "h1-count",
            f"Expected one h1; found {len(h1s)}.",
            "Keep one descriptive page-level heading.",
        )

    previous = 0
    for level, heading_text, heading_line in parser.headings:
        if previous and level > previous + 1:
            check_finding(
                findings,
                "Low",
                "Accessibility",
                path,
                root,
                heading_line,
                "heading-order",
                f"Heading level jumps from h{previous} to h{level}.",
                "Use heading levels in sequence to preserve the document outline.",
            )
        if not heading_text:
            check_finding(
                findings,
                "Medium",
                "Accessibility",
                path,
                root,
                heading_line,
                "empty-heading",
                f"Empty h{level} heading.",
                "Add heading text or remove the empty heading.",
            )
        previous = level

    if len(canonicals) > 1:
        check_finding(
            findings,
            "Medium",
            "SEO",
            path,
            root,
            source_line('rel="canonical"'),
            "duplicate-canonical",
            "More than one canonical link is present.",
            "Keep one canonical link.",
        )

    for attrs, input_line in parser.inputs:
        if (attrs.get("type") or "").lower() in {
            "hidden",
            "submit",
            "button",
            "reset",
            "image",
        }:
            continue
        input_id = attrs.get("id")
        has_label = bool(
            input_id
            and re.search(
                rf"<label\b[^>]*\bfor\s*=\s*['\"]{re.escape(input_id)}['\"]",
                source,
                re.I,
            )
        )
        has_wrapping = bool(
            input_id
            and re.search(
                rf"<label\b[^>]*>[^<]*(?:<[^>]+>[^<]*)*<input\b"
                rf"[^>]*\bid=['\"]{re.escape(input_id)}['\"]",
                source,
                re.I | re.S,
            )
        )
        if not (
            has_label
            or has_wrapping
            or attrs.get("aria-label")
            or attrs.get("aria-labelledby")
        ):
            check_finding(
                findings,
                "Medium",
                "Accessibility",
                path,
                root,
                input_line,
                "input-label",
                f"Input {input_id or '(without id)'} has no accessible label.",
                "Associate a visible label or set an accurate aria-label.",
            )

    if (
        path.name == "index.html"
        and 'id="cv-chat-input"' in source
        and not re.search(
            r"for=['\"]cv-chat-input['\"]|aria-label=['\"]|aria-labelledby=['\"]",
            source,
            re.I,
        )
    ):
        check_finding(
            findings,
            "Medium",
            "Accessibility",
            path,
            root,
            source_line("cv-chat-input"),
            "chat-label",
            "CV chat input is not programmatically labelled.",
            "Add an associated label or aria-label.",
        )

    if re.search(r"http://(?!www\.w3\.org|www\.sitemaps\.org)[^\s\"'<>]+", source, re.I):
        check_finding(
            findings,
            "Low",
            "Security",
            path,
            root,
            1,
            "http-url",
            "HTTP URL found in HTML source.",
            "Use HTTPS where the destination supports it.",
        )

    if re.search(r"<style\b", source, re.I):
        check_finding(
            findings,
            "Low",
            "Performance",
            path,
            root,
            source_line("<style"),
            "inline-css",
            "Page contains an inline style block.",
            "Move maintainable site-wide CSS into src/input.css so it can be "
            "cached and audited centrally.",
        )

    if path.name == "index.html" and re.search(
        r"<script\b[^>]*src=[\"'][^\"']*cv-chat-ui\.js", source, re.I
    ):
        check_finding(
            findings,
            "Medium",
            "Performance",
            path,
            root,
            source_line("cv-chat-ui.js"),
            "eager-chat-import",
            "The chatbot UI is loaded eagerly from the document.",
            "Load the chat module after user interaction with a cached dynamic import.",
        )

    for script_match in re.finditer(r"<script\b([^>]*)>", source, re.I):
        attributes = script_match.group(1).lower()
        before_close = source[: script_match.start()].lower()
        in_head = before_close.rfind("<head") > before_close.rfind("</head")
        if in_head and "src=" in attributes and not re.search(
            r"\b(defer|async)\b", attributes
        ):
            check_finding(
                findings,
                "Low",
                "Performance",
                path,
                root,
                source[: script_match.start()].count("\n") + 1,
                "blocking-script",
                "External script in the document head blocks parsing.",
                "Use defer/async when execution order permits, or move the script "
                "to the end of body.",
            )

    if (
        "http-equiv=\"content-security-policy\"" not in source.lower()
        and "http-equiv='content-security-policy'" not in source.lower()
    ):
        check_finding(
            findings,
            "Low",
            "Security",
            path,
            root,
            1,
            "csp-meta",
            "No document-level CSP policy is present.",
            "Add a tested CSP meta policy; GitHub Pages cannot set arbitrary "
            "response headers from repository files.",
        )

    id_matches = re.findall(r"\bid\s*=\s*['\"]([^'\"]+)['\"]", source, re.I)
    duplicates = sorted(
        {item for item in id_matches if id_matches.count(item) > 1}
    )
    for duplicate in duplicates:
        check_finding(
            findings,
            "Low",
            "Accessibility",
            path,
            root,
            source_line(f'id="{duplicate}"'),
            f"duplicate-id:{duplicate}",
            f"ID {duplicate!r} is declared more than once.",
            "Make each ID unique and update references.",
        )

    for kind, value, ref_line in parser.references:
        value = value.strip()
        if value.startswith("#"):
            fragment = urllib.parse.unquote(value[1:])
            if fragment and fragment not in parser.ids:
                check_finding(
                    findings,
                    "Medium",
                    "Links & assets",
                    path,
                    root,
                    ref_line,
                    "broken-fragment",
                    f"Fragment #{fragment} is not present on this page.",
                    "Use an existing target ID or add the intended ID.",
                )
            continue

        lowered = value.lower()
        if lowered.startswith(
            ("data:", "mailto:", "tel:", "javascript:", "blob:")
        ):
            if lowered.startswith("javascript:"):
                check_finding(
                    findings,
                    "High",
                    "Security",
                    path,
                    root,
                    ref_line,
                    "javascript-url",
                    "javascript: URL is present in a link or asset attribute.",
                    "Remove it and use a safe event handler or URL.",
                )
            continue

        target, status = local_url_to_path(root, path, value)
        if status == "external":
            if check_external and value.startswith(("https://", "http://")):
                try:
                    request = urllib.request.Request(
                        value,
                        method="HEAD",
                        headers={"User-Agent": "StaticSiteAudit/1.0"},
                    )
                    with urllib.request.urlopen(request, timeout=8) as response:
                        if response.status >= 400:
                            check_finding(
                                findings,
                                "Low",
                                "Links & assets",
                                path,
                                root,
                                ref_line,
                                "external-link",
                                f"External URL returned HTTP {response.status}: {value}",
                                "Update or remove the broken URL.",
                            )
                except Exception as error:
                    check_finding(
                        findings,
                        "Low",
                        "Links & assets",
                        path,
                        root,
                        ref_line,
                        "external-link",
                        f"External URL could not be verified ({error}): {value}",
                        "Check the destination manually.",
                    )
            continue

        if status == "outside":
            check_finding(
                findings,
                "High",
                "Security",
                path,
                root,
                ref_line,
                "path-traversal-link",
                f"Local URL escapes repository: {value}",
                "Use a repository-local URL.",
            )
            continue

        if status == "scheme":
            check_finding(
                findings,
                "High",
                "Security",
                path,
                root,
                ref_line,
                "unsafe-scheme",
                f"Unsupported URL scheme in {value!r}.",
                "Use a supported safe URL scheme.",
            )
            continue

        if target is None or not target.exists():
            check_finding(
                findings,
                "High",
                "Links & assets",
                path,
                root,
                ref_line,
                "broken-local-link",
                f"Local {kind} target does not exist: {value}",
                "Correct the path or restore the missing file.",
            )
            continue

        fragment = urllib.parse.urlsplit(value).fragment
        if fragment and target.suffix.lower() in {".html", ".htm"}:
            target_key = relpath(target, root)
            target_parser = all_pages.get(target_key)
            if (
                target_parser
                and urllib.parse.unquote(fragment) not in target_parser.ids
            ):
                check_finding(
                    findings,
                    "Medium",
                    "Links & assets",
                    path,
                    root,
                    ref_line,
                    "broken-fragment",
                    f"Fragment #{fragment} is not present in {target_key}.",
                    "Use an existing target ID or add the intended ID.",
                )


def hex_contrast(first: str, second: str) -> float | None:
    def luminance(value: str) -> float | None:
        value = value.lstrip("#")
        if len(value) == 3:
            value = "".join(character * 2 for character in value)
        if len(value) != 6:
            return None
        try:
            channels = [
                int(value[index : index + 2], 16) / 255
                for index in (0, 2, 4)
            ]
        except ValueError:
            return None
        linear = [
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return (
            0.2126 * linear[0]
            + 0.7152 * linear[1]
            + 0.0722 * linear[2]
        )

    first_luminance = luminance(first)
    second_luminance = luminance(second)
    if first_luminance is None or second_luminance is None:
        return None
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def audit_repo(root: Path, check_external: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    print(
        "Hosting note: GitHub Pages does not configure arbitrary response "
        "headers, compression, or cache headers from repository files; CSP "
        "is checked as a document meta policy."
    )

    pages = html_files(root)
    parsed_pages: dict[str, PageParser] = {}
    for page in pages:
        try:
            _, parsed = parse_html(page)
            parsed_pages[relpath(page, root)] = parsed
        except (OSError, UnicodeError):
            pass
    for page in pages:
        validate_html_page(
            page, root, findings, parsed_pages, check_external
        )

    for file_path in walk_files(root):
        relative = relpath(file_path, root)
        try:
            text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue

        patterns = [] if file_path.name == "build_site.py" else SECRET_PATTERNS
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                check_finding(
                    findings,
                    "Critical",
                    "Security",
                    file_path,
                    root,
                    text[: match.start()].count("\n") + 1,
                    "secret-pattern",
                    "Possible credential or private key in a tracked text file.",
                    "Revoke exposed credentials, remove the secret, and use "
                    "repository secrets.",
                )
                break

        todo_iterator = (
            []
            if file_path.name == "build_site.py"
            else re.finditer(r"\b(TODO|FIXME|XXX)\b", text)
        )
        for match in todo_iterator:
            check_finding(
                findings,
                "Low",
                "Code quality",
                file_path,
                root,
                text[: match.start()].count("\n") + 1,
                "todo",
                f"Unresolved {match.group(1)} marker.",
                "Resolve it or track it in the project issue system.",
            )

        if file_path.name != "build_site.py" and file_path.suffix.lower() in {
            ".js",
            ".mjs",
            ".cjs",
        }:
            for match in re.finditer(r"\bconsole\.(?:log|debug)\s*\(", text):
                check_finding(
                    findings,
                    "Low",
                    "Code quality",
                    file_path,
                    root,
                    text[: match.start()].count("\n") + 1,
                    "console-output",
                    "Console logging remains in client source.",
                    "Remove debug output or gate intentional diagnostics.",
                )

        if file_path.suffix.lower() == ".json" or file_path.name == "site.webmanifest":
            try:
                json.loads(text)
            except json.JSONDecodeError as error:
                check_finding(
                    findings,
                    "High",
                    "Configuration",
                    file_path,
                    root,
                    error.lineno,
                    "json-syntax",
                    f"Invalid JSON: {error.msg}",
                    "Correct the JSON syntax.",
                )

        if file_path.suffix.lower() == ".xml":
            try:
                ET.fromstring(text)
            except ET.ParseError as error:
                check_finding(
                    findings,
                    "High",
                    "SEO / Configuration",
                    file_path,
                    root,
                    error.position[0] if error.position else 1,
                    "xml-syntax",
                    f"Invalid XML: {error}",
                    "Correct the XML syntax.",
                )

        if (
            file_path.name != "build_site.py"
            and file_path.suffix.lower()
            in {".html", ".js", ".css", ".py", ".json", ".md", ".txt"}
        ):
            for match in re.finditer(
                r"http://(?!www\.w3\.org|www\.sitemaps\.org)"
                r"[^\s\"'<>]+",
                text,
                re.I,
            ):
                check_finding(
                    findings,
                    "Low",
                    "Security",
                    file_path,
                    root,
                    text[: match.start()].count("\n") + 1,
                    "insecure-http",
                    f"HTTP URL found: {match.group(0)}",
                    "Prefer HTTPS if supported by the destination.",
                )

    sitemap_path = root / "sitemap.xml"
    if not sitemap_path.exists():
        findings.append(
            Finding(
                "High",
                "SEO",
                "sitemap.xml",
                1,
                "sitemap-missing",
                "sitemap.xml is missing.",
                "Generate it from existing static routes.",
            )
        )
    else:
        try:
            xml_root = ET.parse(sitemap_path).getroot()
            locs = {
                node.text or ""
                for node in xml_root.iter()
                if node.tag.endswith("}loc") or node.tag == "loc"
            }
            expected = {
                f"{SITE_URL}/",
                f"{SITE_URL}/projects/",
            }
            for url in sorted(locs - expected):
                findings.append(
                    Finding(
                        "Medium",
                        "SEO",
                        "sitemap.xml",
                        1,
                        "sitemap-extra",
                        f"Sitemap includes an unregistered route: {url}",
                        "Remove stale sitemap entries.",
                    )
                )
            for url in sorted(expected - locs):
                findings.append(
                    Finding(
                        "Medium",
                        "SEO",
                        "sitemap.xml",
                        1,
                        "sitemap-omission",
                        f"Sitemap is missing route: {url}",
                        "Regenerate the sitemap.",
                    )
                )
        except (ET.ParseError, OSError):
            pass

    robots = root / "robots.txt"
    if not robots.exists():
        findings.append(
            Finding(
                "Medium",
                "SEO",
                "robots.txt",
                1,
                "robots-missing",
                "robots.txt is missing.",
                "Add crawl policy and sitemap location.",
            )
        )
    elif f"{SITE_URL}/sitemap.xml" not in robots.read_text(
        encoding="utf-8", errors="replace"
    ):
        findings.append(
            Finding(
                "Low",
                "SEO",
                "robots.txt",
                1,
                "robots-sitemap",
                "robots.txt does not reference the configured sitemap.",
                "Add the sitemap URL.",
            )
        )

    manifest_path = root / "site.webmanifest"
    if manifest_path.exists():
        try:
            manifest = read_json(manifest_path)
            for icon in manifest.get("icons", []) if isinstance(manifest, dict) else []:
                icon_src = icon.get("src") if isinstance(icon, dict) else None
                icon_path = (
                    root / str(icon_src).lstrip("/")
                    if isinstance(icon_src, str)
                    else None
                )
                if not icon_path or not icon_path.exists():
                    findings.append(
                        Finding(
                            "Medium",
                            "Links & assets",
                            "site.webmanifest",
                            1,
                            "manifest-icon",
                            f"Manifest icon is missing: {icon_src!r}.",
                            "Point the manifest to an existing icon file.",
                        )
                    )
        except SiteError:
            pass
    package_path = root / "package.json"
    lock_path = root / "package-lock.json"
    if package_path.exists() and lock_path.exists():
        try:
            package_data = read_json(package_path)
            lock_data = read_json(lock_path)
            lock_root = (
                lock_data.get("packages", {}).get("", {})
                if isinstance(lock_data, dict)
                else {}
            )
            required_scripts = {"build", "build:site", "validate", "test"}
            missing_scripts = sorted(
                required_scripts - set(package_data.get("scripts", {}))
            )
            if missing_scripts:
                findings.append(
                    Finding(
                        "Medium",
                        "Configuration",
                        "package.json",
                        1,
                        "package-scripts",
                        "Expected npm scripts are missing: "
                        + ", ".join(missing_scripts)
                        + ".",
                        "Restore build and validation entry points used by local "
                        "and CI workflows.",
                    )
                )
            if (
                package_data.get("name") != lock_root.get("name")
                or package_data.get("version") != lock_root.get("version")
            ):
                findings.append(
                    Finding(
                        "Medium",
                        "Configuration",
                        "package-lock.json",
                        1,
                        "lockfile-sync",
                        "package.json and package-lock.json root metadata differ.",
                        "Regenerate the lockfile with the repository's npm version.",
                    )
                )
            for section in ("dependencies", "devDependencies"):
                if package_data.get(section, {}) != lock_root.get(section, {}):
                    findings.append(
                        Finding(
                            "Medium",
                            "Configuration",
                            "package-lock.json",
                            1,
                            "lockfile-dependencies",
                            f"{section} differs between package.json and "
                            "package-lock.json.",
                            "Run npm install with the project's package manager "
                            "and commit the lockfile.",
                        )
                    )
        except (AttributeError, SiteError):
            pass

    git = shutil.which("git")
    if git:
        try:
            tracked_ignored = subprocess.run(
                [
                    git,
                    "-C",
                    str(root),
                    "ls-files",
                    "-ci",
                    "--exclude-standard",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.splitlines()
            for tracked_path in tracked_ignored:
                if tracked_path.endswith(".build-backup"):
                    findings.append(
                        Finding(
                            "Medium",
                            "Configuration",
                            tracked_path,
                            1,
                            "tracked-build-backup",
                            "A generated build backup is tracked despite the "
                            "ignore rule.",
                            f"Remove it from the index with: git rm -- {tracked_path}",
                        )
                    )
        except (OSError, subprocess.TimeoutExpired):
            pass

    stylesheet = root / "src" / "input.css"
    if stylesheet.exists():
        css = stylesheet.read_text(encoding="utf-8", errors="replace")
        block = re.search(
            r"\.project-link\.primary\s*\{([^}]*)\}",
            css,
            re.S,
        )
        if block:
            foreground = re.search(
                r"(?:^|;)\s*color\s*:\s*(#[0-9a-f]{3,8})\b",
                block.group(1),
                re.I,
            )
            background = re.search(
                r"(?:^|;)\s*background(?:-color)?\s*:\s*(#[0-9a-f]{3,8})\b",
                block.group(1),
                re.I,
            )
            if foreground and background:
                ratio = hex_contrast(
                    foreground.group(1),
                    background.group(1),
                )
                if ratio is not None and ratio < 4.5:
                    findings.append(
                        Finding(
                            "High",
                            "Accessibility",
                            "src/input.css",
                            css[: block.start()].count("\n") + 1,
                            "project-link-contrast",
                            "Primary project link contrast is "
                            f"{ratio:.2f}:1; 4.5:1 is the normal text target.",
                            "Choose foreground and background colors that meet "
                            "WCAG AA contrast.",
                        )
                    )

    for name in (
        "favicon.ico",
        "favicon.svg",
        "apple-touch-icon.png",
        "site.webmanifest",
        "og-image.jpg",
    ):
        if not (root / name).exists():
            findings.append(
                Finding(
                    "Medium",
                    "Links & assets",
                    name,
                    1,
                    "site-asset-missing",
                    f"Expected site asset {name} is missing.",
                    "Restore the asset or remove its references.",
                )
            )

    return findings


def format_findings(findings: list[Finding]) -> None:
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    for item in sorted(
        findings,
        key=lambda finding: (
            order.get(finding.severity, 9),
            finding.path,
            finding.line,
            finding.check,
        ),
    ):
        print(
            f"{item.severity:8} {item.category:22} "
            f"{item.path}:{item.line} [{item.check}] {item.message}"
        )
        print(f"         Fix: {item.fix}")
    print(f"\nAudit: {len(findings)} finding(s).")


def write_report(
    path: Path, findings: list[Finding], dry_run: bool = False
) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "findings": [asdict(item) for item in findings],
    }
    atomic_write(
        path,
        json.dumps(payload, indent=2, ensure_ascii=False),
        dry_run=dry_run,
    )


def backup_paths(
    root: Path, paths: list[Path], dry_run: bool
) -> Path | None:
    unique_paths = list(dict.fromkeys(paths))
    if not unique_paths or dry_run:
        return None

    backup_root = root / ".git" / "site-build-backups"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    snapshot = backup_root / stamp
    files_dir = snapshot / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for path in unique_paths:
        relative = relpath(path, root)
        existed = path.exists()
        manifest.append({"path": relative, "existed": existed})
        if existed and path.is_file():
            destination = files_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    (snapshot / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return snapshot


def rollback(root: Path) -> int:
    snapshots = sorted(
        (root / ".git" / "site-build-backups").glob("*/manifest.json")
    )
    if not snapshots:
        raise SiteError(
            "No build backup snapshot exists under .git/site-build-backups"
        )

    manifest_path = snapshots[-1]
    snapshot = manifest_path.parent
    files = read_json(manifest_path)
    restored = 0
    for entry in files:
        relative = entry["path"]
        destination = root / relative
        if not entry["existed"]:
            if destination.is_file():
                destination.unlink()
                restored += 1
            continue

        source = snapshot / "files" / relative
        if not source.is_file():
            raise SiteError(f"Backup file is missing: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        restored += 1

    log(f"Restored {restored} files from {snapshot}", "ok")
    return restored


def load_projects(root: Path) -> list[dict[str, Any]]:
    path = root / "projects.json"
    if not path.exists():
        return []
    data = read_json(path)
    if not isinstance(data, list):
        raise SiteError("projects.json must contain a JSON array")
    return data


def project_actions(project: dict[str, Any]) -> list[dict[str, Any]]:
    actions = [
        {
            "url": project["url"],
            "label": "View project ↗",
            "primary": True,
        }
    ]
    homepage = project.get("homepage")
    if safe_external_url(homepage):
        actions.append(
            {
                "url": homepage,
                "label": "Live demo ↗",
                "primary": False,
            }
        )
    return actions


def safe_external_url(url: Any) -> str | None:
    if not isinstance(url, str) or not url:
        return None
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return url


def safe_json_for_script(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def render_home_projects(projects: list[dict[str, Any]]) -> str:
    cards = []
    source_names = {
        "github": "GitHub",
        "hf_model": "Hugging Face",
        "hf_dataset": "HF Dataset",
    }
    legacy_anchors = {
        "persian-lm-from-scratch": "persian-gpt",
        "ai-research-assistant-platform": "research-assistant",
        "medical-image-segmentation": "cardiac-mri",
    }
    for index, project in enumerate(
        projects[:MAX_PROJECTS_HOMEPAGE],
        start=1,
    ):
        tags = "".join(
            f'<span class="project-tag">{escape_html(tag)}</span>'
            for tag in project.get("tags", [])
        )
        actions = "".join(
            f'<a class="project-link {"primary" if action.get("primary") else ""}" '
            f'href="{escape_html(action["url"])}" target="_blank" '
            f'rel="noopener noreferrer">{escape_html(action["label"])}</a>'
            for action in project_actions(project)
        )
        project_id = str(project.get("id") or f"project-{index}")
        alias = legacy_anchors.get(project_id, "")
        alias_markup = (
            f'<span id="{escape_html(alias)}" class="sr-only"></span>\n            '
            if alias and alias != project_id
            else ""
        )
        project_type = project.get(
            "type",
            source_names.get(str(project.get("source") or ""), "Project"),
        )
        type_label = " · ".join(
            str(value)
            for value in (project_type, *project.get("tags", [])[:2])
            if value
        )
        featured = " project-card-featured" if index == 1 else ""
        cards.append(
            f"""          <article
            id="{escape_html(project_id)}"
            class="surface-card project-card{featured}"
          >
            {alias_markup}<p class="project-number">{index:02} / {escape_html(type_label)}</p>
            <h3 class="card-title">{escape_html(project.get('title') or 'Untitled project')}</h3>
            <p class="card-copy">
              {escape_html(project.get('description') or 'Project details and source repository.')}
            </p>
            <div class="project-tags">{tags}</div>
            <div class="project-actions">{actions}</div>
          </article>"""
        )
    return "\n".join(cards)


def render_paginated_projects(projects: list[dict[str, Any]]) -> str:
    payload = []
    for project in projects:
        payload.append(
            {
                "id": project["id"],
                "title": project["title"],
                "type": project.get("type", project["source"]),
                "description": project.get("description") or "",
                "dateDisplay": project.get("dateDisplay", ""),
                "tags": project.get("tags", []),
                "actions": project_actions(project),
                "note": project.get("note", ""),
            }
        )
    data = safe_json_for_script(payload)

    template = """<div class="projects-paginated" id="projects-paginated" aria-live="polite"></div>
<nav class="projects-pagination" id="projects-pagination" role="navigation" aria-label="Project pages"></nav>
<style>
.projects-pagination {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
.projects-pagination .pag-status {
  margin: 0;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 0.02em;
}
.projects-pagination .pag-status strong {
  color: rgba(255, 255, 255, 0.85);
  font-weight: 600;
}
.projects-pagination .pag-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  flex-wrap: wrap;
}
.projects-pagination .pag-btn {
  min-width: 2.5rem;
  height: 2.5rem;
  padding: 0 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.7);
  border-radius: 0.5rem;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
}
.projects-pagination .pag-btn:hover:not(:disabled):not(.pag-active) {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.2);
}
.projects-pagination .pag-btn:active:not(:disabled) {
  transform: translateY(1px);
}
.projects-pagination .pag-btn.pag-active {
  background: #3b82f6;
  color: #ffffff;
  border-color: #3b82f6;
  font-weight: 600;
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.3);
}
.projects-pagination .pag-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.projects-pagination .pag-btn:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
.projects-pagination .pag-ellipsis {
  min-width: 2.5rem;
  height: 2.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.35);
  font-size: 0.875rem;
  user-select: none;
}
</style>
<script>
(function() {
  var projects = __DATA__;
  var perPage = __PER_PAGE__;
  var currentPage = 1;
  var totalPages = Math.max(1, Math.ceil(projects.length / perPage));
  var container = document.getElementById('projects-paginated');
  var pagination = document.getElementById('projects-pagination');
  if (!container || !pagination) return;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function(c) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }

  function renderProjects(page) {
    var start = (page - 1) * perPage;
    var items = projects.slice(start, start + perPage);
    var html = items.map(function(p, i) {
      var num = String(start + i + 1).padStart(2, '0');
      var tags = (p.tags || []).map(function(t) {
        return '<span class="tag">' + esc(t) + '</span>';
      }).join('');
      var actions = (p.actions || []).map(function(a) {
        var cls = a.primary ? 'action primary' : 'action';
        return '<a class="' + cls + '" href="' + esc(a.url) + '" target="_blank" rel="noopener noreferrer">' + esc(a.label) + '</a>';
      }).join('');
      var note = p.note ? '<p class="note">' + esc(p.note) + '</p>' : '';
      return '<article class="project" id="' + esc(p.id) + '">' +
        '<div class="num" aria-hidden="true">' + num + '</div>' +
        '<div>' +
          '<p class="type">' + esc(p.type) + '</p>' +
          '<h2>' + esc(p.title) + '</h2>' +
          '<p class="desc">' + esc(p.description) + '</p>' +
          '<div class="tags">' + tags + '</div>' +
          '<div class="actions">' + actions + '</div>' +
          note +
        '</div>' +
      '</article>';
    }).join('');
    container.innerHTML = html;
  }

  function pageNumbers(current, total) {
    if (total <= 7) {
      var all = [];
      for (var i = 1; i <= total; i++) all.push(i);
      return all;
    }
    var arr = [1];
    if (current > 3) arr.push('left');
    var lo = Math.max(2, current - 1);
    var hi = Math.min(total - 1, current + 1);
    for (var j = lo; j <= hi; j++) arr.push(j);
    if (current < total - 2) arr.push('right');
    arr.push(total);
    return arr;
  }

  function renderPagination() {
    var parts = [];

    parts.push(
      '<button type="button" class="pag-btn pag-nav" data-page="' + (currentPage - 1) + '"' +
      (currentPage === 1 ? ' disabled aria-disabled="true"' : '') +
      ' aria-label="Previous page"><span aria-hidden="true">&larr;</span></button>'
    );

    var nums = pageNumbers(currentPage, totalPages);
    nums.forEach(function(n) {
      if (typeof n === 'string') {
        parts.push('<span class="pag-ellipsis" aria-hidden="true">&hellip;</span>');
        return;
      }
      var isActive = n === currentPage;
      parts.push(
        '<button type="button" class="pag-btn' + (isActive ? ' pag-active' : '') + '"' +
        ' data-page="' + n + '"' +
        (isActive ? ' aria-current="page"' : '') +
        ' aria-label="Page ' + n + '">' + n + '</button>'
      );
    });

    parts.push(
      '<button type="button" class="pag-btn pag-nav" data-page="' + (currentPage + 1) + '"' +
      (currentPage === totalPages ? ' disabled aria-disabled="true"' : '') +
      ' aria-label="Next page"><span aria-hidden="true">&rarr;</span></button>'
    );

    var startItem = (currentPage - 1) * perPage + 1;
    var endItem = Math.min(currentPage * perPage, projects.length);

    pagination.innerHTML =
      '<p class="pag-status">Showing <strong>' + startItem + '&ndash;' + endItem + '</strong> of <strong>' + projects.length + '</strong> projects</p>' +
      '<div class="pag-controls">' + parts.join('') + '</div>';

    pagination.querySelectorAll('button[data-page]:not([disabled])').forEach(function(button) {
      button.addEventListener('click', function() {
        var page = Number.parseInt(button.dataset.page, 10);
        if (page >= 1 && page <= totalPages && page !== currentPage) {
          currentPage = page;
          renderProjects(page);
          renderPagination();
          container.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  renderProjects(currentPage);
  renderPagination();
})();
</script>"""

    return template.replace("__DATA__", data).replace("__PER_PAGE__", str(PROJECTS_PER_PAGE))


def replace_between(
    source: str,
    start: str,
    end: str,
    replacement: str,
) -> tuple[str, bool]:
    if source.count(start) != 1 or source.count(end) != 1:
        return source, False
    pattern = re.compile(
        re.escape(start) + r"(?P<content>.*?)" + re.escape(end),
        re.S,
    )
    match = pattern.search(source)
    if not match:
        return source, False
    content = match.group("content")
    indent_match = re.search(r"\n(?P<indent>[ \t]*)$", content)
    end_indent = indent_match.group("indent") if indent_match else ""
    replacement = replacement.strip("\n")
    updated = (
        source[: match.start()]
        + start
        + "\n"
        + replacement
        + "\n"
        + end_indent
        + end
        + source[match.end() :]
    )
    return updated, True


def inject_favicons(source: str) -> str:
    if re.search(
        r"<link\b[^>]*rel=['\"](?:shortcut )?icon['\"]",
        source,
        re.I,
    ):
        return source
    return re.sub(
        r"</head\s*>",
        FAVICON_LINKS + "\n</head>",
        source,
        count=1,
        flags=re.I,
    )


def inject_project_home(
    source: str, projects: list[dict[str, Any]]
) -> str:
    start_marker = "<!-- AUTO:HOME_PROJECTS:START -->"
    end_marker = "<!-- AUTO:HOME_PROJECTS:END -->"
    rendered = render_home_projects(projects)

    if source.count(start_marker) == 1 and source.count(end_marker) == 1:
        updated, ok = replace_between(
            source,
            start_marker,
            end_marker,
            rendered,
        )
        return updated if ok else source

    if source.count(start_marker) or source.count(end_marker):
        log("Homepage project markers are incomplete; skipped project injection", "warn")
        return source

    updated, replaced = replace_div_contents_by_class(
        source,
        "projects-grid",
        "\n          "
        + start_marker
        + "\n"
        + rendered
        + "\n          "
        + end_marker
        + "\n        ",
    )
    if not replaced:
        log(
            "Homepage .projects-grid container not found exactly once; skipped project injection",
            "warn",
        )
    return updated


def replace_div_contents_by_class(
    source: str,
    class_name: str,
    replacement: str,
) -> tuple[str, bool]:
    """Replace the inner HTML of exactly one div with the requested class."""
    opening_tags = []
    for match in re.finditer(r"<div\b[^>]*>", source, re.I | re.S):
        class_match = re.search(
            r"\bclass\s*=\s*(['\"])(.*?)\1",
            match.group(0),
            re.I | re.S,
        )
        if class_match and class_name in class_match.group(2).split():
            opening_tags.append(match)
    if len(opening_tags) != 1:
        return source, False

    opening = opening_tags[0]
    depth = 1
    token_pattern = re.compile(r"</?div\b[^>]*>", re.I | re.S)
    for token in token_pattern.finditer(source, opening.end()):
        if token.group(0).startswith("</"):
            depth -= 1
        else:
            depth += 1
        if depth == 0:
            return (
                source[: opening.end()]
                + replacement
                + source[token.start() :],
                True,
            )
    return source, False


def inject_projects_page(
    source: str, projects: list[dict[str, Any]]
) -> str:
    pattern = re.compile(
        r'(<div class="projects" id="project-list">).*?'
        r'(</div>\s*(?:<p class="projects-empty"|</section>))',
        re.S,
    )
    match = pattern.search(source)
    if not match:
        return source
    return pattern.sub(
        lambda found: found.group(1)
        + "\n"
        + render_paginated_projects(projects)
        + "\n      "
        + found.group(2),
        source,
        count=1,
    )


def remove_stale_injected_content(source: str) -> str:
    """Remove only known legacy injected containers."""
    source = re.sub(
        r'<div class="(?:blog-list|projects-list)-container">\s*</div>\s*',
        "",
        source,
    )
    return source


def generate_sitemap(root: Path, dry_run: bool) -> None:
    locations = [
        (f"{SITE_URL}/", "1.0"),
        (f"{SITE_URL}/projects/", "0.9"),
    ]
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    xml.extend(
        f"  <url><loc>{html.escape(url)}</loc>"
        f"<priority>{priority}</priority></url>"
        for url, priority in locations
    )
    xml.append("</urlset>")
    atomic_write(root / "sitemap.xml", "\n".join(xml), dry_run)


def generate_robots(root: Path, dry_run: bool) -> None:
    content = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    atomic_write(root / "robots.txt", content, dry_run)


def image_dimensions(path: Path) -> tuple[int, int] | None:
    """Read PNG or JPEG dimensions without external image dependencies."""
    try:
        with path.open("rb") as stream:
            header = stream.read(24)
            if header[:8] == b"\x89PNG\r\n\x1a\n" and len(header) >= 24:
                return struct.unpack(">II", header[16:24])
            if header[:2] != b"\xff\xd8":
                return None

            stream.seek(2)
            while True:
                marker_prefix = stream.read(1)
                if not marker_prefix:
                    return None
                if marker_prefix != b"\xff":
                    continue

                marker = stream.read(1)
                while marker == b"\xff":
                    marker = stream.read(1)
                if not marker or marker in {b"\xd8", b"\xd9"}:
                    continue

                length_bytes = stream.read(2)
                if len(length_bytes) != 2:
                    return None
                length = struct.unpack(">H", length_bytes)[0]

                if marker[0] in {
                    0xC0,
                    0xC1,
                    0xC2,
                    0xC3,
                    0xC5,
                    0xC6,
                    0xC7,
                    0xC9,
                    0xCA,
                    0xCB,
                    0xCD,
                    0xCE,
                    0xCF,
                }:
                    data = stream.read(5)
                    if len(data) == 5:
                        height, width = struct.unpack(">HH", data[1:5])
                        return width, height
                    return None

                stream.seek(length - 2, os.SEEK_CUR)
    except OSError:
        return None
    return None


def set_or_add_meta(
    source: str,
    key: str,
    value: str,
    property_name: str = "name",
) -> tuple[str, bool]:
    pattern = re.compile(
        r"<meta\b(?=[^>]*\b"
        + re.escape(property_name)
        + r"=[\"']"
        + re.escape(key)
        + r"[\"'])[^>]*>",
        re.I,
    )
    matches = list(pattern.finditer(source))
    if matches:
        return source, False

    tag = (
        f'<meta {property_name}="{escape_html(key)}" '
        f'content="{escape_html(value)}">'
    )
    if re.search(r"</head\s*>", source, re.I):
        updated = re.sub(
            r"</head\s*>",
            "  " + tag + "\n</head>",
            source,
            count=1,
            flags=re.I,
        )
        return updated, True
    return source, False


def update_or_add_meta(
    source: str,
    key: str,
    value: str,
    property_name: str = "name",
) -> str:
    pattern = re.compile(
        r"<meta\b(?=[^>]*\b"
        + re.escape(property_name)
        + r"=[\"']"
        + re.escape(key)
        + r"[\"'])[^>]*>",
        re.I,
    )
    match = pattern.search(source)
    if match:
        tag = re.sub(
            r"(\bcontent\s*=\s*[\"'])[^\"']*([\"'])",
            lambda content: (
                content.group(1)
                + escape_html(value)
                + content.group(2)
            ),
            match.group(0),
            count=1,
            flags=re.I,
        )
        return source[: match.start()] + tag + source[match.end() :]

    source, _ = set_or_add_meta(source, key, value, property_name)
    return source


def update_or_add_canonical(source: str, url: str) -> str:
    pattern = re.compile(
        r"<link\b(?=[^>]*\brel=[\"']canonical[\"'])[^>]*>",
        re.I,
    )
    match = pattern.search(source)
    if match:
        tag = re.sub(
            r"(\bhref\s*=\s*[\"'])[^\"']*([\"'])",
            lambda href: (
                href.group(1) + escape_html(url) + href.group(2)
            ),
            match.group(0),
            count=1,
            flags=re.I,
        )
        return source[: match.start()] + tag + source[match.end() :]

    tag = f'<link rel="canonical" href="{escape_html(url)}">'
    return re.sub(
        r"</head\s*>",
        "  " + tag + "\n</head>",
        source,
        count=1,
        flags=re.I,
    )


def repair_share_metadata(source: str, root: Path) -> str:
    """Fill absent share tags from existing page metadata and local image facts."""
    image_match = re.search(
        r"<meta\b(?=[^>]*property=[\"']og:image[\"'])"
        r"[^>]*content=[\"']([^\"']+)",
        source,
        re.I,
    )
    if not image_match:
        return source

    image_url = html.unescape(image_match.group(1))
    parsed = urllib.parse.urlsplit(image_url)
    site_host = urllib.parse.urlsplit(SITE_URL).netloc
    image_path = (
        root / urllib.parse.unquote(parsed.path.lstrip("/"))
        if parsed.netloc in {"", site_host}
        else None
    )
    dimensions = (
        image_dimensions(image_path)
        if image_path and image_path.is_file()
        else None
    )

    alt = (
        "ARADMANAMNAOON portfolio graphic with Seyyed Arad Hosseini "
        "Moghaddam, Data Scientist and AI Engineer."
    )
    title_match = re.search(
        r"<meta\b(?=[^>]*property=[\"']og:title[\"'])"
        r"[^>]*content=[\"']([^\"']+)",
        source,
        re.I,
    )
    desc_match = re.search(
        r"<meta\b(?=[^>]*property=[\"']og:description[\"'])"
        r"[^>]*content=[\"']([^\"']+)",
        source,
        re.I,
    )
    title = (
        html.unescape(title_match.group(1))
        if title_match
        else "ARADMANAMNAOON"
    )
    description = (
        html.unescape(desc_match.group(1))
        if desc_match
        else "Portfolio and technical writing by Seyyed Arad Hosseini Moghaddam."
    )

    updates = [
        ("og:image:alt", alt, "property"),
        ("twitter:card", "summary_large_image", "name"),
        ("twitter:title", title, "name"),
        ("twitter:description", description, "name"),
        ("twitter:image", image_url, "name"),
        ("twitter:image:alt", alt, "name"),
    ]
    if dimensions:
        updates.extend(
            [
                ("og:image:width", str(dimensions[0]), "property"),
                ("og:image:height", str(dimensions[1]), "property"),
            ]
        )

    for key, value, attribute in updates:
        if key in {"og:image:width", "og:image:height"}:
            pattern = re.compile(
                r"(<meta\b(?=[^>]*"
                + re.escape(attribute)
                + r"=[\"']"
                + re.escape(key)
                + r"[\"'])[^>]*content=[\"'])[^\"']*([\"'])",
                re.I,
            )
            source, count = pattern.subn(
                lambda match: (
                    match.group(1)
                    + escape_html(value)
                    + match.group(2)
                ),
                source,
                count=1,
            )
            if count:
                continue
        source, _ = set_or_add_meta(
            source,
            key,
            value,
            attribute,
        )
    return source


def repair_homepage_background(source: str) -> tuple[str, bool]:
    """Keep the homepage surface dark and defer its dot layer to output.css."""
    original = source

    inline_dot_override = re.compile(
        r"(?ims)^[ \t]*(?:/\*\s*Single blue dot layer\b.*?\*/[ \t]*\n)?"
        r"[ \t]*body\s*::before\s*\{(?=[^{}]*radial-gradient)[^{}]*\}[ \t]*\n?"
    )
    source = inline_dot_override.sub("", source, count=1)

    body_pattern = re.compile(
        r"(?m)^(?P<indent>[ \t]*)body\s*\{(?P<body>.*?)^(?P=indent)\}",
        re.I | re.S,
    )
    match = body_pattern.search(source)
    if not match:
        return source, source != original

    body = match.group("body")
    original_body = body
    indent = match.group("indent") + "  "
    declarations = {
        "position": "relative",
        "isolation": "isolate",
        "background-color": "#14181f",
        "background-image": "none",
    }
    for name, value in declarations.items():
        declaration = re.compile(
            r"(?m)^[ \t]*" + re.escape(name) + r"\s*:\s*[^;]*;"
        )
        replacement = f"{indent}{name}: {value};"
        if declaration.search(body):
            body = declaration.sub(replacement, body, count=1)
        else:
            body = body.rstrip("\n") + "\n" + replacement + "\n"

    if body != original_body:
        source = source[: match.start("body")] + body + source[match.end("body") :]
    return source, source != original


def fix_safe(
    root: Path,
    dry_run: bool,
    create_backup: bool = True,
) -> int:
    """Apply only narrow deterministic repairs with strong local evidence."""
    changes = 0
    if create_backup:
        backup_targets = [
            root / "site.webmanifest",
            root / ".gitignore",
            *html_files(root),
        ]
        backup_paths(root, backup_targets, dry_run)

    manifest_path = root / "site.webmanifest"
    if manifest_path.exists():
        try:
            manifest = read_json(manifest_path)
            dirty = False
            for icon in (
                manifest.get("icons", [])
                if isinstance(manifest, dict)
                else []
            ):
                if (
                    not isinstance(icon, dict)
                    or not isinstance(icon.get("src"), str)
                ):
                    continue
                src = icon["src"]
                candidate = root / src.lstrip("/")
                basename = Path(src).name
                root_candidate = root / basename
                if not candidate.exists() and root_candidate.exists():
                    icon["src"] = "/" + basename
                    dirty = True
            if dirty:
                changes += int(
                    atomic_write(
                        manifest_path,
                        json.dumps(manifest, indent=2, ensure_ascii=False),
                        dry_run,
                    )
                )
        except SiteError:
            pass

    for page in html_files(root):
        try:
            source = page.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue

        relative = relpath(page, root)
        if relative == "index.html":
            route = "/"
        elif relative.endswith("index.html"):
            route = "/" + relative[:-10].rstrip("/") + "/"
        else:
            route = "/" + relative
        canonical = SITE_URL + route

        updated = repair_share_metadata(source, root)
        if relative == "index.html":
            updated, background_changed = repair_homepage_background(updated)
            if background_changed:
                log("Restored the homepage surface and removed its inline dot override")
        if relative == "404.html":
            updated, _ = set_or_add_meta(
                updated,
                "description",
                "The requested page could not be found. Return to the "
                "portfolio or projects archive.",
            )

        page_parser = PageParser()
        page_parser.feed(updated)
        is_noindex = any(
            "noindex" in (item.get("content") or "").lower()
            for item in page_parser.meta
            if (item.get("name") or "").lower()
            in {"robots", "googlebot"}
        )
        if not is_noindex:
            updated = update_or_add_canonical(updated, canonical)
            updated = update_or_add_meta(
                updated,
                "og:url",
                canonical,
                "property",
            )

        if "Content-Security-Policy" not in updated and page != root / "index.html":
            try:
                root_source = (root / "index.html").read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                root_source = ""
            csp = re.search(
                r"<meta\b[^>]*http-equiv=[\"']Content-Security-Policy[\"']"
                r"[^>]*>",
                root_source,
                re.I,
            )
            if csp and re.search(r"</head\s*>", updated, re.I):
                updated = re.sub(
                    r"</head\s*>",
                    "  " + csp.group(0) + "\n</head>",
                    updated,
                    count=1,
                    flags=re.I,
                )

        if page == root / "index.html" and 'id="cv-chat-input"' in updated:
            has_associated_label = re.search(
                r"<label\b[^>]*\bfor=[\"']cv-chat-input[\"']",
                updated,
                re.I,
            )
            input_match = re.search(
                r"<input\b(?=[^>]*\bid=[\"']cv-chat-input[\"'])[^>]*>",
                updated,
                re.I,
            )
            has_aria = input_match and re.search(
                r"\baria-(?:label|labelledby)=",
                input_match.group(0),
                re.I,
            )
            if input_match and not has_associated_label and not has_aria:
                updated = (
                    updated[: input_match.start()]
                    + input_match.group(0).replace(
                        "<input",
                        '<input aria-label="Ask a question about Arad"',
                        1,
                    )
                    + updated[input_match.end() :]
                )

        if updated != source:
            changes += int(atomic_write(page, updated, dry_run))

    ignore_path = root / ".gitignore"
    if ignore_path.exists():
        ignore_source = ignore_path.read_text(encoding="utf-8")
        if "*.build-backup" not in ignore_source.splitlines():
            changes += int(
                atomic_write(
                    ignore_path,
                    ignore_source.rstrip() + "\n*.build-backup\n",
                    dry_run,
                )
            )

    for page in html_files(root):
        try:
            source = page.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        updated = inject_favicons(source)
        if updated != source:
            changes += int(atomic_write(page, updated, dry_run))

    return changes


def cleanup_old_backups(root: Path, keep_days: int = 30) -> int:
    backup_root = root / ".git" / "site-build-backups"
    if not backup_root.exists():
        return 0

    cutoff = datetime.now().timestamp() - keep_days * 86400
    removed = 0
    for snapshot in backup_root.iterdir():
        try:
            if snapshot.is_dir() and snapshot.stat().st_mtime < cutoff:
                shutil.rmtree(snapshot)
                removed += 1
        except OSError as error:
            log(f"Could not remove old backup {snapshot}: {error}", "warn")
    return removed


def build_site(root: Path, args: argparse.Namespace) -> int:
    projects = load_projects(root)
    if projects:
        log(f"Loaded {len(projects)} project(s) from projects.json")
    else:
        log("No projects.json found; project injection skipped", "warn")

    targets = [
        root / "index.html",
        root / "projects" / "index.html",
        root / "sitemap.xml",
        root / "robots.txt",
        root / "site.webmanifest",
        root / ".gitignore",
    ]
    targets.extend(html_files(root))

    snapshot = backup_paths(root, targets, args.dry_run)
    safe_changes = fix_safe(root, args.dry_run, create_backup=False)
    if safe_changes:
        log(f"Applied or proposed {safe_changes} safe repository repair(s)")

    for page in html_files(root):
        source = page.read_text(encoding="utf-8")
        updated = inject_favicons(source)
        if updated != source:
            atomic_write(page, updated, args.dry_run)

    if projects:
        home = root / "index.html"
        source = home.read_text(encoding="utf-8")
        updated = remove_stale_injected_content(source)
        updated = inject_project_home(updated, projects)
        atomic_write(home, updated, args.dry_run)

        projects_page = root / "projects" / "index.html"
        if projects_page.exists():
            projects_source = projects_page.read_text(encoding="utf-8")
            updated_page = inject_projects_page(projects_source, projects)
            atomic_write(projects_page, updated_page, args.dry_run)
        else:
            log("projects/index.html not found; skipping paginated project injection", "warn")

    generate_sitemap(root, args.dry_run)
    generate_robots(root, args.dry_run)

    if snapshot:
        log(f"Backup snapshot: {snapshot}")

    removed_backups = cleanup_old_backups(root)
    if removed_backups:
        log(
            f"Removed {removed_backups} build backup snapshot(s) "
            "older than 30 days"
        )

    findings = audit_repo(root, args.check_external)
    format_findings(findings)
    errors = [
        item for item in findings
        if item.severity in {"Critical", "High"}
    ]
    return 1 if errors else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and audit the static portfolio site."
    )
    parser.add_argument(
        "--root",
        help="Site repository root (defaults to the parent of this script).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report generated changes without writing files.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Audit the repository without writing files.",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Alias for --validate; prints future-oriented repository findings.",
    )
    parser.add_argument(
        "--fix-safe",
        action="store_true",
        help="Apply only narrow deterministic repairs, then audit.",
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Restore the latest build snapshot.",
    )
    parser.add_argument(
        "--check-external",
        action="store_true",
        help="Opt in to checking external links "
        "(network requests may be slow or blocked).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Write a JSON audit report to this path.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print additional progress output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = discover_root(args.root)

    if args.rollback:
        rollback(root)
        return 0

    if args.fix_safe:
        changed = fix_safe(root, args.dry_run)
        log(f"Safe repairs applied or proposed: {changed}")
        findings = audit_repo(root, args.check_external)
        format_findings(findings)
        if args.report:
            report_path = (
                args.report
                if args.report.is_absolute()
                else root / args.report
            )
            write_report(report_path, findings, args.dry_run)
        return (
            1
            if any(
                item.severity in {"Critical", "High"}
                for item in findings
            )
            else 0
        )

    if args.validate or args.audit:
        findings = audit_repo(root, args.check_external)
        format_findings(findings)
        if args.report:
            report_path = (
                args.report
                if args.report.is_absolute()
                else root / args.report
            )
            write_report(report_path, findings, args.dry_run)
        return (
            1
            if any(
                item.severity in {"Critical", "High"}
                for item in findings
            )
            else 0
        )

    return build_site(root, args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        raise SystemExit(130)
    except SiteError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as error:
        print(f"FATAL: {error}", file=sys.stderr)
        if "--verbose" in sys.argv:
            traceback.print_exc()
        raise SystemExit(1)
