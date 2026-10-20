# Psychology & Neuroscience Statistical Research Atlas

Five statistics-first R research projects staged for reproducible empirical execution. **Status: source implementations and analytical protocols; not executed or validated in R.** These are not published findings.

| Project | Public source | Primary method |
|---|---|---|
| [MindHealth Observatory](./mindhealth-observatory/) | [CDC NHANES 2017–2018](https://wwwn.cdc.gov/nchs/nhanes/) | Use 2-year MEC weights, masked strata and PSU identifiers for design-based estimates. |
| [Psychemetrics Atlas](./psychemetrics-atlas/) | [SAPA public personality questionnaires](https://doi.org/10.7910/DVN/SD7SVE) | Assess sparse pairwise overlap before estimating polychoric correlations. |
| [SchoolMind Global](./schoolmind-global/) | [OECD PISA 2022 student file](https://www.oecd.org/en/data/datasets/pisa-2022-database.html) | Use the final student weight and 80 Fay-BRR replicates for uncertainty. |
| [ReplicationScope](./replicationscope/) | [Many Labs 2 publicly released effect tables](https://github.com/ManyLabsOpenScience/ManyLabs2) | Keep independent psychological contrasts separate instead of pooling them indiscriminately. |
| [Neurobehavior Inference Lab](./neurobehavior-inference-lab/) | [OpenNeuro ds000030 (UCLA CNP)](https://openneuro.org/datasets/ds000030) | Validate response correctness and prespecified reaction-time windows. |

Each project has a case-study page using the portfolio's existing design, scientific question, scoped analysis, source data and limits. Original data are not vendored. Do not fabricate results or treat synthetic tests as empirical evidence. Reproducibility/CI and full dataset validation remain release gates.

## Release status

Rscript/Quarto were not available to the development session. None of the five analyses has verified run output. Before advertising results, execute authentic data acquisition, validate schemas and licenses, run R tests and full models, inspect diagnostics, record checksums and render audited reports.
