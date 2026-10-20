# SchoolMind Global

> **Execution update (2026-10-20):** The official OECD PISA 2022 student file has been downloaded and checked, and country-level Fay-BRR R analyses have been executed for 78 economies. Results remain exploratory and independently unvalidated. See [execution evidence](../EXECUTION_EVIDENCE.md) and [R output tables](./results/). The original 109-file staging archive is not fully integrated.


**School belonging, bullying and uncertainty in international comparisons**

> **Research in progress — PARTIALLY EXECUTED.** This is an actual, exploratory survey-weighted R analysis of student-level data, not a completed or independently replicated journal study.

**Question.** Do apparent national differences in school belonging survive measurement and complex-sampling uncertainty?

**Source.** OECD PISA 2022 student file: https://www.oecd.org/en/data/datasets/pisa-2022-database.html

**Primary estimand.** Country/economy-specific survey-weighted mean of the published BELONG index

## Proposed analysis
1. Validate the BELONG, bullying and ESCS indicators against the PISA codebook.
2. Use the final student weight and 80 Fay-BRR replicates for uncertainty.
3. Distinguish country-level descriptions from individual-level socioeconomic associations.
4. Evaluate scaling comparability, response quality and exclusions before interpreting rankings.

## Research limitations
PISA is observational. International measurement comparability and nonresponse restrictions require careful review. Conventional lme4 random intercepts are exploratory, not equivalent to complex-design inference; cognitive plausible-value rules should not be transferred to BELONG.

## Reproducibility status
This directory contains the public methods and a bounded initial R analysis implementation for scientific review. The complete five-project staging archive was produced separately; no R execution, R unit test, Quarto build or resolved renv dependency snapshot has been observed. Run scientific quality gates before publication of results.

[Research case study](https://aradmanamnaoon.github.io/projects/schoolmind-global/) · [Data source](https://www.oecd.org/en/data/datasets/pisa-2022-database.html) · [Protocol](./docs/protocol.md)

## Observed real-data pipeline

The official student SPSS ZIP is approximately 682 MB and expands to a 2.1 GB SAV file. A reproducible, memory-bounded workflow avoids loading all 613,744 student records into one R model:

```bash
python3 scripts/download_pisa_2022.py
unzip -o data/raw/STU_QQQ_SPSS.zip -d data/raw/
python3 scripts/extract_pisa_country.py
Rscript R/run_pisa2022.R data/derived/country_csv_gz
```

Dependencies: Python 3.11+, `pyreadstat`, pandas; R 4.3+, `survey` and its dependencies. Files under `data/` are untracked. The final file is validated against the exact SHA-256 in the source script, and outputs are in `results/`.

Observed run: **613,744 source rows across 80 country/economy codes; 561,339 valid rows analyzed across 78 systems**. ISR and KSV failed the analysis completeness threshold (under 50 valid observations). Full lists, intervals and missingness are in the output CSVs. Source interpretation must consider national-response adjudication, metric invariance, survey administration differences and multiplicity.
