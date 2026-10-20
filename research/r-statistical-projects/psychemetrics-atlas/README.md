# Psychemetrics Atlas

> **Execution update (2026-10-20):** An initial authentic-data R run has been observed. Scientific interpretation remains preliminary and independently unvalidated. See [execution evidence](../EXECUTION_EVIDENCE.md). Full study/reports and original 109-file staging archive are not yet integrated.


**Latent dimensions, item coverage and the limits of personality measurement**

> **Research in progress — PARTIALLY EXECUTED.** Authentic data were used for an initial exploratory R run. The observations, figures, output tables and provenance are documented, but models require independent reproduction and further scientific checks; do not cite this as a completed peer-reviewed study.

**Question.** How stable are exploratory personality item dimensions when respondents encounter only subsets of a large questionnaire?

**Source.** SAPA public personality questionnaires: https://doi.org/10.7910/DVN/SD7SVE

**Primary estimand.** Exploratory item-level factor structure under planned questionnaire missingness

## Proposed analysis
1. Audit item codebooks, scales, reverse-coding and response coverage.
2. Assess sparse pairwise overlap before estimating polychoric correlations.
3. Explore oblique factor solutions, eigenstructure and item-level sensitivity.
4. Separate unkeyed descriptive scale consistency from validated trait reliability.

## Research limitations
SAPA is a volunteer, nonprobability sample with matrix-sampled items. The scoring key and cross-group invariance are not yet verified; no validated trait scale, confirmatory factor analysis or item-response-theory result is claimed.

## Reproducibility status
This directory contains the public methods and a bounded initial R analysis implementation for scientific review. The complete five-project staging archive was produced separately; no R execution, R unit test, Quarto build or resolved renv dependency snapshot has been observed. Run scientific quality gates before publication of results.

[Research case study](https://aradmanamnaoon.github.io/projects/psychemetrics-atlas/) · [Data source](https://doi.org/10.7910/DVN/SD7SVE) · [Protocol](./docs/protocol.md)

## Observed execution artifacts

- [Run ledger and SHA-256 checksums](../EXECUTION_EVIDENCE.md)
- [Aggregate CSV outputs](./results/)
- [Exploratory project case study](https://aradmanamnaoon.github.io/projects/psychemetrics-atlas/)

The original 109-file research staging archive is available separately and is **not** yet completely integrated into this repository. The scientific release gate remains open.
