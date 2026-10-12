# Psychological survey data — what the file actually shows

*Public-facing explanatory report (English). Updated 12 October 2026.*

## Purpose and boundaries

No research question, sampling protocol, or instrument manuals were supplied. Accordingly, this is **exploratory statistical description and a data-integrity audit**, not a hypothesis-confirming scientific comparison. The word *participant* can be misleading until unique-person identifiers are verified: technically, the file contains **240 recorded rows**.

## What was measured?

The original SPSS file has **89 variables**: `GROUP`, `NUMBER`, `AGE`, `AGEE`, `MARRIAGE`, `EDUCATIO`; 76 item responses (`A1–A13`, `EM1–EM33`, `H1–H15`, `D1–D15`); seven recorded summary/subscale values (`TOTALA`, `TOTALEM`, `OPTIMISM`, `EVALUATI`, `SOCIALSK`, `EMOTIONA`, `MZQ`). The `GROUP` value labels are literally `fire` (120 rows) and `non` (120 rows), but their research meaning is not established.

**A (13 items):** ambiguity tolerance — attitudes toward uncertain or ambiguous situations. **EM (33 items):** emotional self-regulation — reported emotional management. **H (15 items):** mentalization — interpreting thoughts and feelings. **D (15 items):** death-anxiety answers, recorded as binary codes 1/2. The four other reported emotional domains relate to optimism, appraisal/evaluation, social skills, and application of emotion. These are construct *labels* found in the source, not confirmation that a specific questionnaire edition or validated scoring algorithm was used.

`AGEE` is exact age (22–58 observed); `AGE` is a grouped age category, and `EDUCATIO` and `MARRIAGE` are coded demographics. `NUMBER` looks like a row/person number and is not a globally trusted person identifier. A bilingual 89-field dictionary, with original Persian SPSS labels and response codes, is included.

## Descriptive portrait of the recorded rows

- The two groups each have **120** recorded rows. Their meaning and independence are unknown.
- Original age groups contain **20 under 30**, **124 aged 30–39**, **82 aged 40–49**, and **14 aged 50–60** records, using coded categories from the SPSS metadata. The mean exact age in the provided derived CSV is approximately **39.41 years**.
- Recorded education has **126 bachelor's**, **52 associate**, **30 diploma**, **30 master's**, and **2 doctorate** entries. The **public grouped export merges master's and doctorate into 32 postgraduate records**, reducing small-cell disclosure.
- **189 records are coded married** and **51 single**.

These describe rows within this file, not population prevalence.

## Seven findings that change how results should be read

**1. Response duplication dominates the file.** There are only **86 distinct complete 76-item answer patterns** across 240 rows. A total of **239 rows** belong to patterns also found in other rows. This does not prove duplicate people: repeated answers can occur naturally, but the volume demands source-form verification.

**2. The groups are nearly identical in item responses.** At corresponding positions in the `fire` and `non` groups, **119 of 120 pairs** have precisely the same answers on all 76 questionnaire items. Without a documented paired design or merge history, treating them as independent samples is unjustified.

**3. Stored ambiguity totals appear to separate the groups, but arithmetic answers do not.** `TOTALA` averages **40.45** (`fire`) vs **35.825** (`non`), an apparent **+4.625** difference. The direct arithmetic sum of A1–A13 differs by only **+0.075** in group means. The direct sum is *not necessarily the correct psychological scale* because reverse coding and weighting are unknown. This discrepancy demands a scoring audit before substantive interpretation.

**4. Some stored totals disagree with direct item sums.** Counts are **84 rows** for `TOTALA`, **32** for `TOTALEM`, **26** for `MZQ`, with **108 rows** having at least one discrepancy. This does not automatically prove a scoring error; a scoring key may specify reversed or weighted items. It does prove that the stored totals should not be assumed to equal naive sums.

**5. There are invalid death-anxiety response codes.** The documented D-item labels use codes **1 and 2**, yet **31 response cells in five records** use other values. A defensible death-anxiety composite cannot be calculated until the affected source records are verified.

**6. Internal-consistency estimates are provisional.** Raw-item Cronbach's alpha is approximately **0.328** (A items), **0.926** (EM items), and **0.660** (H items). These are uncorrected raw-item diagnostics, not validated questionnaire reliabilities, and repeated records distort uncertainty estimates.

**7. Statistical tests in the full report are diagnostic, not confirmatory.** The report provides correlations, regression diagnostics, group comparisons, effect sizes and intervals as sensitivity analyses. Their p-values and confidence intervals are **not defensible independent-sample population inferences** until participant identity, group design, data integrity and scoring are resolved.

## What should readers conclude?

The strongest supported finding is **about the structure and quality of this dataset**, rather than a claim that one psychological group has better functioning than another. At present, it is appropriate to describe frequencies, inspect scores, visualize records and explain why further scientific validation is required. It is **not appropriate to claim that `fire` versus `non` causes or even establishes valid psychological differences**.

## What would make this study publishable as substantive research?

The custodians should establish what the groups represent and how they were sampled, retrieve the actual source questionnaires, document reverse scoring and missing-value rules, inspect matching rows against original surveys, explain the intended analysis design, resolve code errors, and repeat all statistics using verified person-level units. Only then should inferential interpretation be updated.

## Reader guide to the files

Start with `reports/SPSS_Statistical_Report_English.pdf`. Use `results/score_summary_bilingual_aggregated.csv` for descriptive charting, `results/quality_metrics_bilingual.csv` for QA statistics, the bilingual glossary for terminology, and `web_preview/index.html` for the interactive aggregate-only preview. Files with `UNRELIABLE`, `UNVALIDATED`, or `DIAGNOSTIC` in their names must be displayed with those qualifiers.
