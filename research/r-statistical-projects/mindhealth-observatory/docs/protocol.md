# Protocol — MindHealth Observatory

**Status: proposed analysis, unexecuted.**

## Target question
How does the prevalence of elevated depressive symptoms differ across socioeconomic and demographic strata once the NHANES sample design is respected?

## Data
CDC NHANES 2017–2018 (https://wwwn.cdc.gov/nchs/nhanes/)

## Primary estimand
Survey-weighted PHQ-9 screening prevalence among eligible US adults (18+) with complete item responses

## Protocol
Population: civilian noninstitutionalized US adults aged 18+ participating in the 2017–18 MEC examination. Primary estimand: proportion with PHQ-9 ≥ 10 among complete PHQ respondents, estimated with WTMEC2YR weights, SDMVSTRA and SDMVPSU. Item nonresponse is not scored as zero. Report raw n, weighted prevalence and design-based confidence intervals. Fit age/sex/PIR adjusted survey-weighted quasibinomial logit; nonlinear income and interaction sensitivity. Audit singleton strata. Never interpret screening thresholds as a diagnosis or cross-sectional regression as causal.

## Required release gates
- Verify specific dataset license, data version and raw input SHA-256 checksums.
- Validate codebook mapping, exclusions, analytic denominator and missing data rules.
- Execute R package installation, statistical unit tests and the complete pipeline.
- Review design-based or clustered variance, model diagnostics and sensitivity analysis.
- Create numerical results and figures from authentic data only; include provenance and uncertainty.
- Render, review and archive the Quarto report and R session information.

## Limitations
Cross-sectional survey estimates are associations, not evidence of causality. PHQ-9 screening is not clinical diagnosis. Multiple imputation and cross-cycle comparisons are not implemented in the staged source.
