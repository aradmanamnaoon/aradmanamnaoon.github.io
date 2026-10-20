# Preliminary R replication — TWO datasets only

**R runtime and packages required.** Outputs will overwrite files in a local `results/` directory; run from a clean working directory and archive checksums.

```sh
Rscript research/r-statistical-projects/replicationscope/R/analysis.R \
  /path/to/Data_Figure_NOweird.csv
Rscript research/r-statistical-projects/neurobehavior-inference-lab/R/analysis.R \
  /path/to/ds000030
```

Input for the meta-analysis must match SHA-256
`1d01187bcb50a67ba43d9651c122002a9f2036a4c8c23e7107763aceb9225820`.
This pins a byte-level snapshot, not a validated scientific estimand.

SCAP data source:
https://github.com/OpenNeuroDatasets/ds000030
Task events only; no MRI required.

The output files `results/within_contrast_meta.csv`, `results/rt_coefficients.csv` and `results/accuracy_coefficients.csv` are preliminary, unreviewed computation artifacts. Obtain full cohort and design-specific analyses before interpreting effects. Do not confuse a successful exit code with valid inference.
