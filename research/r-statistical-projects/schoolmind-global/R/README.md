# Executable analysis candidate — schoolmind-global

This R script is **not yet run or numerically validated**. It is an initial auditable method implementation, not the complete planned pipeline. Read the protocol and input codebook first.

```sh
Rscript R/analysis.R pisa2022_student.csv
```

Output is written into `results/` **only when executed**. Do not interpret results until survey-design, effect metric, selection, missingness and reproducibility checks pass. The complete staged research suite (with additional modules, Quarto and tests) was prepared separately and remains pending integration after real R validation.
