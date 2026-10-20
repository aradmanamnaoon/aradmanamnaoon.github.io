# Protocol — Psychemetrics Atlas

**Status: proposed analysis, unexecuted.**

## Target question
How stable are exploratory personality item dimensions when respondents encounter only subsets of a large questionnaire?

## Data
SAPA public personality questionnaires (https://doi.org/10.7910/DVN/SD7SVE)

## Primary estimand
Exploratory item-level factor structure under planned questionnaire missingness

## Protocol
Exploratory, not confirmatory, factor work on public SAPA temperament items. Check item-to-dictionary mapping and category validity. Quantify missing-by-design structure, item participation, pairwise complete overlap and matrix positive semidefiniteness before polychoric EFA. Summarize loadings as exploratory only. Never present raw alpha of an unkeyed item set as reliability of an established trait. Volunteer sampling limits population generalization. CFA, graded IRT, omega of correctly keyed scales and measurement invariance remain unimplemented.

## Required release gates
- Verify specific dataset license, data version and raw input SHA-256 checksums.
- Validate codebook mapping, exclusions, analytic denominator and missing data rules.
- Execute R package installation, statistical unit tests and the complete pipeline.
- Review design-based or clustered variance, model diagnostics and sensitivity analysis.
- Create numerical results and figures from authentic data only; include provenance and uncertainty.
- Render, review and archive the Quarto report and R session information.

## Limitations
SAPA is a volunteer, nonprobability sample with matrix-sampled items. The scoring key and cross-group invariance are not yet verified; no validated trait scale, confirmatory factor analysis or item-response-theory result is claimed.
