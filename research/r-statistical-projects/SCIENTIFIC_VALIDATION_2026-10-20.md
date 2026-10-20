# PsychNeuro Statistical Atlas — scientific recheck (20 October 2026)

These five projects have **genuine real-data exploratory R executions** and publication-style portfolio pages, but are **not yet independently validated scientific studies**. All new artifacts are derived aggregates or public item metadata; no respondent-level records are pushed.

| Project | Input | Verification and sensitivity |
|---|---|---|
| MindHealth Observatory | CDC NHANES 2017–2018 XPT, n=5,068 complete eligible | PHQ-9 cutoffs 5/10/15: weighted screen-positive fractions 0.24723 / 0.08531 / 0.02809 under WTMEC2YR, SDMVSTRA, SDMVPSU |
| Psychemetrics Atlas | Original Harvard Dataverse SAPA RData, 23,679 respondent rows; published 696-item keys/dictionary | Five signed IPIP-50 scales: zero respondents with all 10 items in each; ≥5-item response counts 307–535; minimum pairwise overlap 289–523. **No standard complete-case reliability inferred.** |
| SchoolMind Global | OECD PISA 2022, with all 80 Fay-BRR replicate student weights | Independent re-estimation of DEU, FIN and SWE BELONG country means and SE agrees with saved results to within 1e-10 |
| ReplicationScope | Many Labs 2 processed effect summaries | Five highest-I² contrasts independently refitted; 50 deterministic leave-one-lab-out refits performed |
| Neurobehavior Inference Lab | OpenNeuro ds000030, 80-subject SCAP event subset | RT window sensitivity: Load log-RT coefficient 0.04270, 0.04138, 0.03919 across three windows; fitted models nonsingular |

### Original uploaded SAPA archive and provenance

Uploaded ZIP SHA-256: `34eccd6b5c0e5deb621789fe0dd1549df7d8a00a918a3a6b99de4fd3f4e6180c`. Verified original user archive includes RData, tab-format respondent data, `superKey696.csv`, `ItemInfo696.csv`, `ItemLists.csv` and demographic codebook. The signing key SHA-256 `8d19b6a23c7f42b91cf5bc0895e2c63790510ba9355a2c69d19703c6f791bc49` and item dictionary SHA-256 `ce280ebf42cd77f3db1955a3027051a74d017ca61da02adf5dbbab11545b1732` match upstream published copies byte for byte. To perform R execution, the original publisher's Dataverse API RData (file ID 11016302, SHA-256 `803daa08fa07659352f882be365902d2b85d99d1f8b403f5f7dacfda401f7bed`) was independently downloaded. The downloaded original RData is *not byte-identical* to the supplied RData and record-level equivalence has not been demonstrated. Its observed matrix is 23,679 × 719; the previously published IRW table has 23,678 respondent IDs. The count discrepancy remains an explicit investigation target.

The original item dictionary is CP1252 encoded. The new R analysis explicitly converts it to Unicode before mapping original item text. Results are persisted in `psychemetrics-atlas/results/original_sapa_*`; the corresponding SVG uses the portfolio's charcoal and blue palette.

### Reproduce the cross-checks

Run the following commands from `research/r-statistical-projects` with local, official downloaded data:

```bash
cd psychemetrics-atlas
Rscript R/test_original_sapa_audit.R
Rscript R/original_sapa_audit.R original.RData superKey696.csv ItemInfo696.csv results
cd ..
Rscript R/empirical_release_checks.R /data/NHANES /data/ManyLabs2.csv /data/OpenNeuro_80SCAP /data/PISA_country_csv_gz
```

Outputs in `validation/`: survey cutoff sensitivity; PISA three-country independent Fay-BRR recheck; five-contrast/50-deletion meta-analysis sensitivity; SCAP three-window model sensitivity; execution matrix. Exact input provenance for the other four studies remains in `EXECUTION_EVIDENCE.md`.

### Unmet scientific release gates

Cross-cycle/nonresponse NHANES assessment; SAPA full scored-trait model reliability under planned missingness and individual alignment of original and IRW representations; PISA measurement invariance and external replication across all 78 economies; Many Labs effect-size/variance source audit and raw-data reconstruction; OpenNeuro preregistration/full-cohort validation; independent numerical review, package lockfiles and rendered Quarto report review. The original 109-file development staging archive has **not** been merged wholesale because its modules were never executed as a suite.

**The research programs are substantially implemented, but cannot honestly be called five finished, validated research publications.**
