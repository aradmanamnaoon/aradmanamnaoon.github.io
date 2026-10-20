# Protocol — SchoolMind Global

**Status: proposed analysis, unexecuted.**

## Target question
Do apparent national differences in school belonging survive measurement and complex-sampling uncertainty?

## Data
OECD PISA 2022 student file (https://www.oecd.org/en/data/datasets/pisa-2022-database.html)

## Primary estimand
Country/economy-specific survey-weighted mean of the published BELONG index

## Protocol
Target: published BELONG index for PISA 2022 student respondents with relevant questionnaire data. Use final student weight W_FSTUWT plus all 80 W_FSTURWT replicates under Fay BRR rho=0.5 and the OECD specifications. Report weighted mean, replicate-based SE and interval for every supported economy, with response-rate restrictions and missingness. ESCS/bullying associations can use design-aware country-adjusted models. Country rankings and overlap of CIs are not multiplicity-adjusted rank inferences. Do not average cognitive plausible values when analyzing the BELONG index.

## Required release gates
- Verify specific dataset license, data version and raw input SHA-256 checksums.
- Validate codebook mapping, exclusions, analytic denominator and missing data rules.
- Execute R package installation, statistical unit tests and the complete pipeline.
- Review design-based or clustered variance, model diagnostics and sensitivity analysis.
- Create numerical results and figures from authentic data only; include provenance and uncertainty.
- Render, review and archive the Quarto report and R session information.

## Limitations
PISA is observational. International measurement comparability and nonresponse restrictions require careful review. Conventional lme4 random intercepts are exploratory, not equivalent to complex-design inference; cognitive plausible-value rules should not be transferred to BELONG.
