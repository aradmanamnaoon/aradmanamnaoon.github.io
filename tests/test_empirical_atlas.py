"""Regression checks for five real-data exploratory R projects and portfolio figures."""
import csv
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "r-statistical-projects"
IDS = ("mindhealth-observatory", "psychemetrics-atlas", "schoolmind-global",
       "replicationscope", "neurobehavior-inference-lab")

def read_csv(path):
    with (BASE / path).open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))

class ResearchValidationTests(unittest.TestCase):
    def test_all_five_studies_have_public_case_studies(self):
        registry = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))
        records = {item["id"]: item for item in registry}
        for name in IDS:
            with self.subTest(project=name):
                self.assertIn(name, records)
                self.assertEqual(records[name]["category"], "analysis")
                self.assertTrue(records[name]["caseStudy"]["limitations"])
                self.assertTrue((BASE / name / "R" / "analysis.R").is_file())
    def test_original_sapa_keyed_missingness(self):
        rows = read_csv("psychemetrics-atlas/results/original_sapa_keyed_coverage.csv")
        self.assertEqual(len(rows), 5)
        self.assertEqual({int(x["original_n"]) for x in rows}, {23679})
        for x in rows:
            self.assertEqual(int(x["item_count"]), 10)
            self.assertEqual(int(x["n_all_10"]), 0)
            self.assertGreaterEqual(int(x["pair_min"]), 250)
            self.assertLessEqual(int(x["n_at_least_8"]), int(x["n_at_least_5"]))
        mapping = read_csv("psychemetrics-atlas/results/original_sapa_item_key_audit.csv")
        self.assertEqual(len(mapping), 50)
        self.assertTrue(all(x["sign"] in ("-1", "1") for x in mapping))
    def test_pisa_country_crosschecks(self):
        rows = read_csv("validation/pisa_fay_brr_independent_recheck.csv")
        self.assertEqual({x["country"] for x in rows}, {"DEU", "FIN", "SWE"})
        for row in rows:
            self.assertGreater(int(row["n"]), 1000)
            self.assertGreater(float(row["replicate_se"]), 0)
            self.assertEqual(row["matches_archived_result"].upper(), "TRUE")
    def test_nhanes_cutoff_monotonicity(self):
        rows = read_csv("validation/nhanes_screening_threshold_sensitivity.csv")
        self.assertEqual([int(x["threshold"]) for x in rows], [5,10,15])
        probabilities = [float(x["screen_positive"]) for x in rows]
        self.assertGreater(probabilities[0], probabilities[1])
        self.assertGreater(probabilities[1], probabilities[2])
        self.assertTrue(all(0 < p < 1 for p in probabilities))
    def test_mixed_models_and_meta_sensitivity(self):
        neuro = read_csv("validation/scap_rt_window_sensitivity.csv")
        self.assertEqual(len(neuro), 3)
        self.assertEqual({int(x["participants"]) for x in neuro}, {80})
        self.assertTrue(all(x["singular_rt"].upper()=="FALSE" for x in neuro))
        self.assertTrue(all(int(x["n_rt"])<=int(x["n_trials"]) for x in neuro))
        meta = read_csv("validation/manylabs_leave_one_out_sensitivity.csv")
        self.assertEqual(len(meta), 5)
        for x in meta:
            self.assertLessEqual(float(x["leave_one_out_min_r"]), float(x["baseline_r"]))
            self.assertGreaterEqual(float(x["leave_one_out_max_r"]), float(x["baseline_r"]))
    def test_research_ui_preserves_original_renderer(self):
        code = (ROOT / "scripts" / "project_pages.py").read_text(encoding="utf-8")
        self.assertIn("case-figure-grid", code)
        registry = json.loads((ROOT / "projects.json").read_text(encoding="utf-8"))
        sapa = next(x for x in registry if x["id"] == "psychemetrics-atlas")
        self.assertTrue(any("psychemetrics-original-coverage.svg" in x["src"]
                            for x in sapa["figures"]))
        self.assertTrue((ROOT / "projects/psychemetrics-atlas/assets/figures/psychemetrics-original-coverage.svg").exists())

if __name__ == "__main__":
    unittest.main()
