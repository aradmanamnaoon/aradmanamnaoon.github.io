# Neurobehavior Inference Lab

> **Execution update (2026-10-20):** An initial authentic-data R run has been observed. Scientific interpretation remains preliminary and independently unvalidated. See [execution evidence](../EXECUTION_EVIDENCE.md). Full study/reports and original 109-file staging archive are not yet integrated.


**Working-memory load, reaction time and trial-level behavioral statistics**

> **Research in progress — PARTIALLY EXECUTED.** Authentic data were used for an initial exploratory R run. The observations, figures, output tables and provenance are documented, but models require independent reproduction and further scientific checks; do not cite this as a completed peer-reviewed study.

**Question.** How do working-memory load and delay relate to speed and accuracy within repeated behavioral task trials?

**Source.** OpenNeuro ds000030 (UCLA CNP): https://openneuro.org/datasets/ds000030

**Primary estimand.** Within-participant associations of SCAP working-memory load/delay with log response time and accuracy

## Proposed analysis
1. Read BIDS behavioral events and phenotype metadata, not MRI volumes.
2. Validate response correctness and prespecified reaction-time windows.
3. Fit participant-intercept Gaussian/log-RT and binomial mixed-effects models.
4. Quantify participant heterogeneity and rerun with alternative outlier cutoffs.

## Research limitations
No fMRI analysis, psychiatric diagnosis, reliability validation or causal claim is established. The trial exclusion window and task timing definitions need independent validation. Models and R tests have not been run.

## Reproducibility status
This directory contains the public methods and a bounded initial R analysis implementation for scientific review. The complete five-project staging archive was produced separately; no R execution, R unit test, Quarto build or resolved renv dependency snapshot has been observed. Run scientific quality gates before publication of results.

[Research case study](https://aradmanamnaoon.github.io/projects/neurobehavior-inference-lab/) · [Data source](https://openneuro.org/datasets/ds000030) · [Protocol](./docs/protocol.md)

## Observed execution artifacts

- [Run ledger and SHA-256 checksums](../EXECUTION_EVIDENCE.md)
- [Aggregate CSV outputs](./results/)
- [Exploratory project case study](https://aradmanamnaoon.github.io/projects/neurobehavior-inference-lab/)

The original 109-file research staging archive is available separately and is **not** yet completely integrated into this repository. The scientific release gate remains open.
