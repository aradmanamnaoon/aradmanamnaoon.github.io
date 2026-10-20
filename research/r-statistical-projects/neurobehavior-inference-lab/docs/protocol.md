# Protocol — Neurobehavior Inference Lab

**Status: proposed analysis, unexecuted.**

## Target question
How do working-memory load and delay relate to speed and accuracy within repeated behavioral task trials?

## Data
OpenNeuro ds000030 (UCLA CNP) (https://openneuro.org/datasets/ds000030)

## Primary estimand
Within-participant associations of SCAP working-memory load/delay with log response time and accuracy

## Protocol
Use phenotype/participants.tsv and *_task-scap_events.tsv from a pinned ds000030 release. Do not fetch NIfTI volumes for this analysis. Validate coded Load, Delay, ResponseAccuracy and ReactionTime. Accuracy is Bernoulli; log-RT among correct trials with predeclared RT window 0.15–3 seconds. Model log-RT as a function of Load, Delay and a participant random intercept; fit binomial mixed model for correctness. Report participant counts, trial counts, exclusion rates, convergence, singular fits and sensitivity to alternative RT limits. Do not interpret task behavior as clinical diagnosis or neuroimaging evidence.

## Required release gates
- Verify specific dataset license, data version and raw input SHA-256 checksums.
- Validate codebook mapping, exclusions, analytic denominator and missing data rules.
- Execute R package installation, statistical unit tests and the complete pipeline.
- Review design-based or clustered variance, model diagnostics and sensitivity analysis.
- Create numerical results and figures from authentic data only; include provenance and uncertainty.
- Render, review and archive the Quarto report and R session information.

## Limitations
No fMRI analysis, psychiatric diagnosis, reliability validation or causal claim is established. The trial exclusion window and task timing definitions need independent validation. Models and R tests have not been run.
