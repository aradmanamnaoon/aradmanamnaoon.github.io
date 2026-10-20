# PISA 2022 source access — resolved with range download

**20 October 2026:** The earlier student-data download blocker was resolved using HTTP byte-range downloads from the [official OECD PISA 2022 SPSS file](https://webfs.oecd.org/pisa2022/STU_QQQ_SPSS.zip).

- Downloaded archive: 682,364,259 bytes, SHA-256 `24ee020cd6315d8aca52e07fd9aaef21cbf4f9e5b21601734b4ee6d0928a0905`.
- ZIP check: passed. Student SAV member: `CY08MSP_STU_QQQ.SAV` (2,096,666,903 bytes).
- Student records: 613,744, country/economy values: 80.
- Pipeline: Python `pyreadstat` streamed the exact fields, creating per-economy compressed intermediate files; R `survey::svrepdesign(type="Fay", rho=0.5)` calculated the national descriptive means and replicate-weight uncertainty.
- Successfully analyzed: 78 economies, 561,339 complete `BELONG` observations. ISR and KSV yielded too few complete observations.

**Scientific limitations:** These are exploratory survey-weighted descriptive estimates, not independently replicated PISA publication tables. No individual-level source data or country-intermediate files were added to GitHub. Review participation/adjudication, nonresponse, measurement comparability, and the Fay-BRR specification against OECD technical documentation before treating any comparison as confirmatory.
