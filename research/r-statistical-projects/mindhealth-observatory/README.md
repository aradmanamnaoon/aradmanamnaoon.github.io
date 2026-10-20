# MindHealth Observatory

**Depression screening, population inequality and survey-weighted inference**

> **Research in progress — NOT EXECUTED.** No numerical findings, statistical figures, sample sizes or validated model diagnostics are available for this project. Do not cite it as a completed study.

**Question.** How does the prevalence of elevated depressive symptoms differ across socioeconomic and demographic strata once the NHANES sample design is respected?

**Source.** CDC NHANES 2017–2018: https://wwwn.cdc.gov/nchs/nhanes/

**Primary estimand.** Survey-weighted PHQ-9 screening prevalence among eligible US adults (18+) with complete item responses

## Proposed analysis
1. Validate all nine PHQ-9 symptoms and survey eligibility before scoring.
2. Use 2-year MEC weights, masked strata and PSU identifiers for design-based estimates.
3. Estimate weighted prevalence, survey-weighted GLMs, design-aware confidence intervals and nonlinear income sensitivity.
4. Audit complete-case selection and report all weights, denominators and exclusion rules.

## Research limitations
Cross-sectional survey estimates are associations, not evidence of causality. PHQ-9 screening is not clinical diagnosis. Multiple imputation and cross-cycle comparisons are not implemented in the staged source.

## Reproducibility status
This directory contains the public methods and a bounded initial R analysis implementation for scientific review. The complete five-project staging archive was produced separately; no R execution, R unit test, Quarto build or resolved renv dependency snapshot has been observed. Run scientific quality gates before publication of results.

[Research case study](https://aradmanamnaoon.github.io/projects/mindhealth-observatory/) · [Data source](https://wwwn.cdc.gov/nchs/nhanes/) · [Protocol](./docs/protocol.md)
