from __future__ import annotations

import importlib.util
import sys
import unittest
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


if __name__ == "__main__":
    unittest.main()
