# Executable analysis candidate — mindhealth-observatory

This R script is **not yet run or numerically validated**. It is an initial auditable method implementation, not the complete planned pipeline. Read the protocol and input codebook first.

```sh
Rscript R/analysis.R DEMO_J.XPT DPQ_J.XPT
```

Output is written into `results/` **only when executed**. Do not interpret results until survey-design, effect metric, selection, missingness and reproducibility checks pass. The complete staged research suite (with additional modules, Quarto and tests) was prepared separately and remains pending integration after real R validation.
