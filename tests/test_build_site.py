from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_site", ROOT / "scripts" / "build_site.py")
assert SPEC is not None and SPEC.loader is not None
build_site = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build_site
SPEC.loader.exec_module(build_site)


class PortfolioGeneratorTests(unittest.TestCase):
    def test_flagship_projects_are_first_and_keep_the_archive(self) -> None:
        projects = build_site.load_projects(ROOT)
        ids = [project["id"] for project in projects]
        self.assertEqual(
            ids[:3],
            [
                "persian-lm-from-scratch",
                "medical-image-segmentation",
                "ai-research-assistant-platform",
            ],
        )
        self.assertEqual(len(ids), 11)

    def test_metric_renderer_escapes_untrusted_text(self) -> None:
        result = build_site.render_project_metrics(
            {"metrics": [{"value": "<script>", "label": "held-out result"}]}
        )
        self.assertIn("&lt;script&gt;", result)
        self.assertNotIn("<script>", result)

    def test_research_evidence_includes_methods_and_limits(self) -> None:
        projects = build_site.load_projects(ROOT)
        rendered = build_site.render_research_projects(projects)
        self.assertIn("0.8821", rendered)
        self.assertIn("not been clinically validated", rendered)
        self.assertIn("14.52", rendered)
        self.assertIn("103", rendered)

    def test_skills_page_comes_from_cv_knowledge_base(self) -> None:
        rendered = build_site.render_skills_directory(ROOT)
        for skill in ("Python", "SQL", "Flutter", "PyQt6", "Humanities Data Analysis"):
            self.assertIn(skill.lower(), rendered.lower())

    def test_page_markers_replace_only_generated_content(self) -> None:
        template = "before<!-- START -->old<!-- END -->after"
        rendered = build_site.inject_generated_page(
            template, "<!-- START -->", "<!-- END -->", "new"
        )
        self.assertEqual(rendered, "before<!-- START -->\nnew\n<!-- END -->after")

    def test_featured_case_studies_have_unique_seo_routes_and_evidence(self) -> None:
        projects = build_site.load_projects(ROOT)
        studies = [project for project in projects if project.get("caseStudy")]
        slugs = [project["slug"] for project in studies]
        self.assertEqual(len(studies), 3)
        self.assertEqual(len(slugs), len(set(slugs)))
        for project in studies:
            study = project["caseStudy"]
            self.assertRegex(project["slug"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertGreaterEqual(len(study["description"]), 60)
            self.assertGreaterEqual(len(study["approach"]), 3)
            self.assertGreaterEqual(len(study["results"]), 2)
            self.assertGreaterEqual(len(study["limitations"]), 50)

    def test_project_detail_template_contains_unique_metadata_and_breadcrumbs(self) -> None:
        from project_pages import render

        project = next(
            item for item in build_site.load_projects(ROOT)
            if item["id"] == "medical-image-segmentation"
        )
        page = render(project, build_site.SITE_URL)
        self.assertIsNotNone(page)
        assert page is not None
        self.assertIn("rel=\"canonical\"", page)
        self.assertIn("og:title", page)
        self.assertIn('"@type": "BreadcrumbList"', page)
        self.assertIn("0.8821", page)
        self.assertIn("not a diagnostic device", page)

    def test_project_actions_link_to_internal_case_study_and_public_source(self) -> None:
        project = next(
            item for item in build_site.load_projects(ROOT)
            if item["id"] == "persian-lm-from-scratch"
        )
        actions = build_site.project_actions(project)
        self.assertEqual(actions[0]["url"], "/projects/persian-gpt-from-scratch/")
        self.assertFalse(actions[0]["external"])
        self.assertTrue(actions[1]["external"])

    def test_utility_pages_are_noindex_and_search_remains_current(self) -> None:
        from utility_pages import render, search_entries

        projects = build_site.load_projects(ROOT)
        entries = search_entries(projects)
        urls = [item["url"] for item in entries]
        self.assertEqual(len(entries), 4 + len(projects))
        self.assertIn("/projects/3d-cardiac-mri-segmentation/", urls)
        self.assertIn("/projects/#cohortseal", urls)
        self.assertIn("/skills/", urls)
        self.assertNotIn("/404.html", urls)
        for kind in ("404", "offline", "search"):
            page = render(kind, projects)
            self.assertIn('name="robots" content="noindex, follow"', page)
            self.assertIn('action="/search/"', page)
            self.assertIn('href="/research/"', page)
            self.assertNotIn('rel="canonical"', page)

    def test_utility_routes_are_excluded_from_sitemap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_site.generate_sitemap(root, False, ["/projects/test-case/"])
            urls = [node.text for node in ET.parse(root / "sitemap.xml").iter()
                    if node.tag.endswith("loc")]
        self.assertIn(build_site.SITE_URL + "/projects/test-case/", urls)
        self.assertTrue({build_site.SITE_URL + route for route in
                         ("/404.html", "/offline.html", "/search/")}.isdisjoint(urls))


if __name__ == "__main__":
    unittest.main()
