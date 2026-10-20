# SchoolMind Global

**School belonging, bullying and uncertainty in international comparisons**

> **Research in progress — NOT EXECUTED.** No numerical findings, statistical figures, sample sizes or validated model diagnostics are available for this project. Do not cite it as a completed study.

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
