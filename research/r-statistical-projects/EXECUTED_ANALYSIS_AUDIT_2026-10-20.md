# Empirical execution log — 20 October 2026

**Classification: preliminary real-data execution, NOT validated research findings.** Analyses were run with R 4.5.0 in an isolated execution environment. No clinical, policy or causal claim is warranted. Prior public case-study status labels remain conservative.

## ReplicationScope — completed initial computational run

- Data: ManyLabsOpenScience/ManyLabs2, `OSFdata/!!RawData/Data_Figure_NOweird.csv`.
- SHA-256 of downloaded CSV: `1d01187bcb50a67ba43d9651c122002a9f2036a4c8c23e7107763aceb9225820`.
- Input: 1,593 processed effect rows, 301 columns, 28 unique analysis labels and 115 unique study.source values.
- Current `R/analysis.R` executed without a runtime error and emitted 26 within-contrast REML models (minimum 41 laboratory records among fitted contrasts).
- Numerical results should **not** be treated as verified because `ESCI.var.r` is delta-transformed to Fisher-z variance without a full independent cross-check against the upstream source definitions, and cross-study dependence/contrast direction filters remain under review.
- No independent reconstruction of original experiment-level statistics from raw trial-level datasets was performed.

## Neurobehavior Inference Lab — completed initial computational run

- Data: OpenNeuro `ds000030` SCAP task event TSV files.
- Ten participant identifiers sampled from the original dataset: `10159, 10171, 10189, 10206, 10217, 10225, 10227, 10228, 10235, 10249`.
- A single source participant file `sub-10159_task-scap_events.tsv` had SHA-256 `1971b171038dfabadaadd37520813047f56192d6613fe660edf5cc9c58f0c832`.
- Existing R analysis script ran and generated log-reaction-time and accuracy mixed-model coefficient tables. The fit used an unbalanced ten-participant subset; coefficient stability, converged solutions, exclusion rates, task coding and external validity have **not** been approved.
- Example *unchecked computational output* for the log-RT model: Load coefficient +0.03992584, SE 0.00668551; this number is **not** a scientific conclusion.
- No fMRI, imaging or full-cohort analysis has been executed.

## MindHealth Observatory — BLOCKED

- Attempted downloads at the NHANES 2017–18 `DEMO_J.XPT` and `DPQ_J.XPT` URLs yielded HTML rather than XPT data (both responses 20,905 bytes).
- The R `haven::read_xpt` parser correctly rejected the returned HTML. No NHANES estimates were computed. A working official public-use file endpoint, sample-design audit and fresh run are required.

## Psychemetrics Atlas and SchoolMind Global — NOT RUN

- No verified SAPA item-response file or PISA student microdata were loaded into R. No latent-factor or school-belonging inferential result exists.
- These remain source-only research implementations pending verified data schemas, sample design and execution.

## Website and software validation

- The repository's existing HTML case-study generator and 5 project routes were verified at the previous integration.
- The current empirical execution does **not** fulfill the full 109-file archive integration or 10,000 substantive lines requirement.
- Earlier portfolio checks: 25 Python tests and 59 Node tests passed; the browser audit passed on retry. These are not R statistical validation tests.

## Release gates

1. Confirm distributional permissions and pin immutable source revisions and input hashes.
2. Run all 5 scientific pipelines end-to-end using verified source data.
3. Review estimation targets, missingness, selection, weights, model convergence and sensitivity.
4. Add independent numerical fixtures for R outputs and actual research plots.
5. Only then replace the conservative public 'not yet validated' labels.
