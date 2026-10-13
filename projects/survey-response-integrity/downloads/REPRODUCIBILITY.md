# Reproducibility — Digital Survey Response Integrity

All files in this folder are **public-safe aggregate derivatives**, not individual responses.

## Source and integrity

- Original upload: `datafile(4).csv` (private: not included).
- Origin: Source DOI not verified; original survey codebook not supplied.
- Observed shape: 4,771 × 289.
- Parser: pandas CSV with separator `,` and decimal `.`.
- Null cells: 0; full-row duplicates: 0.
- Dataset license: UNVERIFIED from uploaded material — obtain original rights confirmation before publishing.
- Status: exploratory; not a validated causal or clinical finding.

## Regenerate results

1. Obtain permission to process the original `datafile(4).csv`. Keep it in a **private** directory on your computer; the raw rows are never distributed here.
2. Install Python ≥3.11 and `pip install -r requirements.txt`.
3. Run the one-project analysis, writing output **outside the public project**:

   ```sh
   python analysis.py /absolute/path/to/private-csv-folder --output-dir /absolute/path/to/private-analysis-output
   ```

4. This script reads **only `datafile(4).csv`** and writes `analysis_results.json`, a **single-dataset** statistical diagnostic, to the designated private output directory. It does not export participant-level rows and does not rewrite the published charts, PDF, DOCX or `aggregate-results.csv`. Rebuilding those separately requires the full authoring pipeline.
5. A regression test comparing selected JSON fields to the existing aggregate summary was completed in the local authoring environment. **Statistical inference remains exploratory**, and the original survey instrument/metadata have not been fully verified.
6. `aggregate-results.csv` is a public summary snapshot; by itself, it cannot recover participant-level statistics such as correlations or alpha. Reproduction of those measures requires access to the original authorized data.

## Methods and decisions

- Spearman rho: pairwise available numeric data; repeated-measures analysis is not interchangeable with independent data analysis.
- Reliability: Cronbach alpha and approximate single-factor McDonald omega only on item groups where a narrow diagnostic check was defensible. Raw item direction and official score keys remain unverified.
- -9 in HA03 sensitivity analysis: assumed unavailable only in a **separate derived view**. The original input remains unchanged.
- All negative response codes in the digital survey export are counted; they were **not** silently mapped to missingness.
- Named composites were checked but never overwritten.
- No ordinary imputation or automatic participant filtering is applied.

## WITHHELD FROM PUBLIC RELEASE

- `full_data(4).csv` — contains `worker_id` and individual observations.
- `datafile(4).csv` — contains case identifiers, timestamp, and respondent-level answers.
- `Schuster et al_data(4).csv` — individual respondent responses; withheld per project-specific release policy even though an original public archive is available.
- Any source `.sav` or codebook file not supplied to this build: **not included**; do not infer permission.
- Dataset provenance for full_data and datafile is unverified; **no data-source DOI or license was invented**.

## Files safe to publish only after human review

- `report-en.pdf`, `report-en.docx`
- `aggregate-results.csv` (dataset-level aggregates)
- `variable-dictionary.csv` (field metadata; may include small-cell counts, review before release)
- `figures/*.png`, `figures/*.svg`
- `analysis.py` (dataset-specific, accepts private source directory; writes summary to a private output location)
- `requirements.txt`, `references.bib`, `REPRODUCIBILITY.md`

## Interpretation and limitations

- The exported CSV contains no literal nulls but uses blank strings and negative response codes extensively. Treating all these as valid survey answers is unsafe.
- Meaning of codes -1, -2, -3, -5, -96, -97, -98 is unverified without the survey codebook; negative-coded cells were counted, not silently recoded.
- A raking-weight variable exists, but its target population, weighting strata and intended inference are undocumented here. No population estimates claimed.
- Device-type codes and all personality scoring keys need the source instrument. The device group comparison is diagnostic only.
- The status and RQI_breakoff flags align numerically but the codebook must confirm their operational meaning.

## Source references

See `references.bib`. For data sources without verified DOI/URL, the citation is **incomplete** and publication should await metadata verification.
