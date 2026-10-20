"""Regression tests for the five unexecuted R statistical research case studies."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from project_pages import render


PROJECT_SLUGS = (
    "mindhealth-observatory",
    "psychemetrics-atlas",
    "schoolmind-global",
    "replicationscope",
    "neurobehavior-inference-lab",
)


class StatisticalProjectIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads((ROOT / "projects.json").read_text("utf-8"))
        cls.by_id = {project["id"]: project for project in cls.registry}

    def test_five_unique_registry_ids(self) -> None:
        self.assertEqual(len(self.registry), len(self.by_id))
        for slug in PROJECT_SLUGS:
            with self.subTest(slug=slug):
                self.assertIn(slug, self.by_id)

    def test_preserves_homepage_features(self) -> None:
        old_featured = {
            item["id"] for item in self.registry
            if item.get("homepage_featured")
        }
        self.assertFalse(old_featured.intersection(PROJECT_SLUGS))

    def test_use_existing_generator_and_statistical_category(self) -> None:
        for slug in PROJECT_SLUGS:
            with self.subTest(slug=slug):
                p = self.by_id[slug]
                self.assertEqual(p["slug"], slug)
                self.assertEqual(p["category"], "analysis")
                self.assertEqual(p["source"], "github")
                self.assertIsNone(p.get("customPage"))
                self.assertIn("Not run", {m["value"] for m in p["metrics"]})
                html = render(p, "https://aradmanamnaoon.github.io")
                self.assertIn("/assets/css/interaction-hub.css", html)
                self.assertIn('class="case-grid"', html)
                self.assertIn(f"/projects/{slug}/", html)
                self.assertIn("No verified sample sizes", html)

    def test_sources_protocols_and_analysis_are_present(self) -> None:
        root = ROOT / "research" / "r-statistical-projects"
        for slug in PROJECT_SLUGS:
            with self.subTest(slug=slug):
                p = root / slug
                for child in ("README.md", "docs/protocol.md", "R/analysis.R"):
                    self.assertTrue((p / child).is_file(), str(p / child))
                self.assertIn(
                    "NOT EXECUTED",
                    (p / "R" / "analysis.R").read_text("utf-8").upper(),
                )


if __name__ == "__main__":
    unittest.main()
