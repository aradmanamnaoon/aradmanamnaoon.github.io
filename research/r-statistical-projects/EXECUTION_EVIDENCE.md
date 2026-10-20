# Four observed R executions — 20 October 2026

**Scope: exploratory, independently unvalidated.** These results were computed in a temporary Debian-based R 4.5.0 environment on authentic public data. The research archive has not been fully re-executed, and these outputs do not constitute finished, peer-reviewed studies.

## Dataset provenance

| Project | Exact source | Bytes | SHA-256 |
|---|---|---:|---|
| MindHealth DEMO_J | [CDC 2017–18 DEMO_J](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm) | 3,412,720 | `c0b46e0345ea19404928656277c8b0d10b0cca348a9b2fe4fc3c67e8b7ee73ec` |
| MindHealth DPQ_J | [CDC 2017–18 DPQ_J](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DPQ_J.htm) | 489,280 | `1c075f332e79736bd2360b41b0c10ed526883417e0b5996c407b1c564b01ca24` |
| ReplicationScope | [Many Labs 2 processed effects](https://github.com/ManyLabsOpenScience/ManyLabs2/blob/acef63fc397b8dce7f0b00f863bcea78d324bea8/OSFdata/!!RawData/Data_Figure_NOweird.csv) | 4,492,596 | `1d01187bcb50a67ba43d9651c122002a9f2036a4c8c23e7107763aceb9225820` |
| Psychemetrics Atlas | [IRW SAPA personality v71.0 CSV](https://itemresponsewarehouse.org/tables/sapa_personality/) | 32,788,744 | `d09b2956d28c0f99222330fdedbb8169256b15fc06195c5a6fce40295c06f292` |
| Neurobehavior | [OpenNeuro ds000030 participants.tsv](https://github.com/OpenNeuroDatasets/ds000030/blob/4070b6eea231517bfeff42527a46d9d166ac4e13/participants.tsv) | 16,387 | `d39a9697085f209ca7d72ad05792ec4689d99d28d62d3f2c1344bed3627ac4df` |

Neurobehavior source cohort: **80 SCAP event TSV files** from the first 80 lexically ordered event-file paths in GitHub tree `OpenNeuroDatasets/ds000030` at commit `4070b6eea231517bfeff42527a46d9d166ac4e13`; individual filenames and checksums were not deposited, so exact cohort provenance is incomplete. No MRI volumes downloaded.

## Observed results

### 1. MindHealth Observatory

- Source files: CDC DEMO_J + DPQ_J for NHANES 2017–2018; PHQ items DPQ010–DPQ090.
- Eligible complete-item adults with positive MEC weights: **5,068**; coded-sex counts 2,478 and 2,590.
- Survey weighted PHQ-9 ≥10 prevalence: **0.0853096351** (SE **0.0051824036**, normal 95% CI **0.07515231–0.09546696**).
- Survey design: SDMVPSU nested in SDMVSTRA; WTMEC2YR.
- Preliminary adjusted logistic coefficients: female-coded indicator `+0.4144` log-odds; income-to-poverty ratio `-0.2998` log-odds. These are *associations*, not causal effects.
- **Limitations:** complete-case PHQ screening, 2017–2018 cycle only; income complete for 4,438 rows, model-specific n differs from prevalence n. No full missing-data sensitivity analysis.

### 2. Psychemetrics Atlas

- IRW SAPA v71 derived from Condon & Revelle's Harvard Dataverse release (DOI 10.7910/DVN/SD7SVE); cite both the dataset and transformation.
- 2,039,803 long-format item-response records, 23,678 respondent IDs, 696 items.
- 12 highest-coverage items selected *exploratorily*. Per-item coverage ~6,000; minimum pairwise overlap 1,300.
- Polychoric 3-factor minres EFA ran using `psych`; loadings are unidentified as substantive trait scales without verified item keying and rotated-factor stability.
- **Limitations:** volunteer sampling; planned missingness; no validated scale reliability, CFA, measurement invariance, or independently checked item-codebook mapping.

### 3. ReplicationScope

- 1,593 rows, 28 contrast identifiers; 1,474 non-missing effect/variance pairs. 26 eligible contrasts fitted with `metafor::rma.uni(method="REML")`.
- Between 41 and 66 laboratory rows used per fitted contrast.
- Input source is upstream **processed effect summaries**, not raw trial-level experimental reproduction. Fisher z and delta-method variance transformation used; upstream variance/direction semantics require audit.
- **Limitations:** observational comparison of laboratory-level effect summaries is not causal, and significance failure is not evidence of zero effect.

### 4. Neurobehavior Inference Lab

- OpenNeuro ds000030 public SCAP event data: 80 participants sampled, 3,840 recorded event rows; 3,740 rows with coded correct/incorrect response; 3,241 correct response rows.
- `glmer(correct ~ Load + Delay + (1|participant), family=binomial)`, coefficient for Load `-0.215705` (log odds/encoded unit). `lmer(log(ReactionTime) ~ Load + Delay + (1|participant))`, coefficient for Load `+0.0427034` (log seconds/encoded unit).
- Neither model was singular and neither emitted an lme4 convergence message.
- **Limitations:** subsample of the published dataset; model-selection and exclusion choices not preregistered; these are exploratory task associations, not MRI findings or clinical diagnosis.

### 5. SchoolMind Global — BLOCKED

The official OECD PISA 2022 student-questionnaire SPSS ZIP was identified at `https://webfs.oecd.org/pisa2022/STU_QQQ_SPSS.zip` (682,364,259 bytes). Download timed out in the controlled execution environment. No genuine student records, coefficients or figures were generated. The existing R script is **not** an observed empirical run.

## Actual run environment

- R 4.5.0
- `survey` 4.4.2, `haven` 2.5.4, `metafor` 4.8.0, `psych` 2.4.12, `lme4` 1.1.37, `data.table` 1.17.0, `ggplot2` 3.5.1, `GPArotation` 2024.3.1.
- Executed the published preliminary `R/analysis.R` scripts for NHANES, Many Labs 2 and OpenNeuro; SAPA used a documented long-to-wide IRW adapter now saved as `psychemetrics-atlas/R/run_irw.R`.
- Full original 109-file research archive, dependency lockfile, Quarto report rendering, independent validation and all sensitivity analyses remain release gates.

## R-generated figures and aggregate outputs

Four exploratory visualizations are linked from the standard case-study renderer under `projects/<slug>/assets/figures/`. Ten aggregate CSV files are versioned under the corresponding `research/r-statistical-projects/<slug>/results/` directories. They contain no respondent-level records. These figures and summaries are reproducible from the documented public data and initial scripts, subject to the stated limitations.
