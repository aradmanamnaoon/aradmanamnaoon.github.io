"""Apply the five verified cinematic feature choices without deleting archived work.

Run explicitly when regenerating the cinematic content configuration.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEATURES = {
    "constellation": 1,
    "medical-image-segmentation": 2,
    "ai-research-assistant-platform": 3,
    "holdout-ledger": 4,
    "eu-loneliness-social-support-analysis": 5,
}


def main() -> None:
    path = ROOT / "projects.json"
    projects = json.loads(path.read_text(encoding="utf-8"))
    assert set(FEATURES) <= {project["id"] for project in projects}
    for project in projects:
        project["homepage_featured"] = project["id"] in FEATURES
        if project["id"] in FEATURES:
            project["homepage_order"] = FEATURES[project["id"]]
    survey = next(p for p in projects if p["id"] == "eu-loneliness-social-support-analysis")
    survey.update({
        "slug": "eu-loneliness-social-support-analysis",
        "homepage_description": "Exploratory analysis of European survey data on loneliness, perceived emotional support and face-to-face contact. Observational associations, not causal findings.",
        "homepage_note": "Python analysis results are author-reported; the accompanying R replication script has not been executed or validated.",
        "type": "Behavioral data science · EU survey · Observational analysis",
        "metrics": [
            {"value": "23,307", "label": "EU27 complete cases (reported)"},
            {"value": "0.610", "label": "EU27 perceived-support odds ratio (reported)"},
            {"value": "2022", "label": "survey reference year"},
        ],
        "research": {
            "context": "A secondary, exploratory analysis of the European Commission Joint Research Centre's 2022 EU Loneliness Survey, examining associations between perceived emotional support, contact and loneliness.",
            "methods": [
                "Two public JRC survey archives covering EU4 and EU27 populations",
                "Python weighted quasibinomial logistic regression with HC3 robust covariance",
                "Matched four-country sensitivity comparison and full EU27 sample",
                "An R replication script was prepared but has not been run or independently validated",
            ],
            "limitations": "Cross-sectional associations cannot establish causal effects. Complex survey design inference, independent replication and manuscript publication have not been established.",
        },
        "caseStudy": {
            "title": "Social support and loneliness across the European Union",
            "seoTitle": "EU Loneliness Survey: Social Support Analysis | Arad",
            "description": "Exploratory Python analysis of the 2022 EU Loneliness Survey examining weighted associations between emotional support and loneliness in EU4 and EU27 respondents.",
            "lede": "How does perceived emotional support relate to loneliness across European survey samples? This independent exploratory analysis compares EU4, four matched countries in EU27 and all EU27 countries.",
            "challenge": "Estimate interpretable observational associations while respecting source coding, missing responses, sample differences and the limits of cross-sectional survey evidence.",
            "approach": [
                "Used the 2022 EU Loneliness Survey published by the European Commission Joint Research Centre; the original response data remain with the publisher.",
                "Prepared Python analyses for EU4, EU27 in France, Italy, Poland and Sweden, and the full EU27 sample.",
                "Estimated weighted quasibinomial models with HC3 confidence intervals as documented in the public repository.",
                "Prepared a separate R replication script; as of the documented repository revision, it had not been executed or independently validated.",
            ],
            "results": [
                "Author-reported Python EU4 estimate: n=3,756 complete cases, perceived-support odds ratio 0.565 (HC3 95% CI 0.516–0.618).",
                "Author-reported Python matched-country EU27 estimate: n=3,679, odds ratio 0.598 (HC3 95% CI 0.555–0.645).",
                "Author-reported Python full-EU27 estimate: n=23,307, odds ratio 0.610 (HC3 95% CI 0.591–0.631).",
                "These are reference values from the Python analysis, not replicated R results or causal estimates.",
            ],
            "limitations": "The study is exploratory and cross-sectional. Weighting with HC3 robust errors does not itself establish full complex-survey inference. No causal finding, direct measure of enjoyable solitude, independently validated R replication, accepted paper or published journal article is claimed.",
            "sourceLabel": "Read the public analysis and reproduction notes",
        },
    })
    path.write_text(json.dumps(projects, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Featured projects:", [(p["id"], p["homepage_order"]) for p in projects if p["homepage_featured"]])


if __name__ == "__main__":
    main()
