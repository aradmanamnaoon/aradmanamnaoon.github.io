# ReplicationScope

**Experimental replicability, effect-size heterogeneity and meta-analytic uncertainty**

> **Research in progress — NOT EXECUTED.** No numerical findings, statistical figures, sample sizes or validated model diagnostics are available for this project. Do not cite it as a completed study.

**Question.** How much variation in each replicated psychological effect is attributable to laboratory differences rather than sampling error?

**Source.** Many Labs 2 publicly released effect tables: https://github.com/ManyLabsOpenScience/ManyLabs2

**Primary estimand.** Within-contrast between-laboratory heterogeneity of replication effect estimates

## Proposed analysis
1. Audit effect direction, estimates, variance semantics and laboratory labels.
2. Keep independent psychological contrasts separate instead of pooling them indiscriminately.
3. Use Fisher-z transforms and restricted maximum-likelihood random-effects models.
4. Inspect tau², I², prediction intervals, influence and leave-one-laboratory-out stability.

## Research limitations
This uses upstream processed effect summaries, not independently reconstructed raw experiments. Study-level dependence and filter selections require verification. A non-significant replication is not evidence that a true effect is zero.

## Reproducibility status
This directory contains the public methods and a bounded initial R analysis implementation for scientific review. The complete five-project staging archive was produced separately; no R execution, R unit test, Quarto build or resolved renv dependency snapshot has been observed. Run scientific quality gates before publication of results.

[Research case study](https://aradmanamnaoon.github.io/projects/replicationscope/) · [Data source](https://github.com/ManyLabsOpenScience/ManyLabs2) · [Protocol](./docs/protocol.md)
