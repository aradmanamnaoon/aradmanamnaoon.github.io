# Protocol — ReplicationScope

**Status: proposed analysis, unexecuted.**

## Target question
How much variation in each replicated psychological effect is attributable to laboratory differences rather than sampling error?

## Data
Many Labs 2 publicly released effect tables (https://github.com/ManyLabsOpenScience/ManyLabs2)

## Primary estimand
Within-contrast between-laboratory heterogeneity of replication effect estimates

## Protocol
Unit of analysis is a laboratory-level estimate within a single Many Labs 2 psychological contrast. Audit identifiers and effect direction before pooling. Transform eligible r to Fisher z and confirm that the variance columns correspond to the expected effect metric; invalid variances must be rejected. Fit separate REML random-effects meta-analyses only with sufficient independent laboratories. Back-transform pooled z to r, report CIs, tau², I² and prediction intervals. Holm-adjust exploratory across-contrast tests. Leave-one-lab-out and influence checks are required. Publication-bias tests are not assumed to be meaningful in a coordinated replication.

## Required release gates
- Verify specific dataset license, data version and raw input SHA-256 checksums.
- Validate codebook mapping, exclusions, analytic denominator and missing data rules.
- Execute R package installation, statistical unit tests and the complete pipeline.
- Review design-based or clustered variance, model diagnostics and sensitivity analysis.
- Create numerical results and figures from authentic data only; include provenance and uncertainty.
- Render, review and archive the Quarto report and R session information.

## Limitations
This uses upstream processed effect summaries, not independently reconstructed raw experiments. Study-level dependence and filter selections require verification. A non-significant replication is not evidence that a true effect is zero.
