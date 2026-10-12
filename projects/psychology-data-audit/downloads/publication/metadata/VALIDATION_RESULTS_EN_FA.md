# Verification log / گزارش کنترل کیفیت

**Review candidate only; not approved for publication. / فقط پیش‌نویس، تأیید انتشار انجام نشده است.**

## Verified / موارد بررسی‌شده

- Original SAV: **240 × 89**; item-response audit: **76** items, **86** distinct profiles, **119 of 120** aligned cross-group pairs identical, **31** invalid D cells in **5** rows, and **108** records with at least one stored-total/arithmetic discrepancy.
- The public aggregate-generation Python script was executed again on the original SAV; **five generated CSV result tables matched the packaged tables** within numerical precision.
- English and Persian DOCX files passed structural loading. PDF files were parsed successfully and contain no embedded attachments.
- Browser-preview HTML data embed is aggregate-only by design; all **8** relative download links resolve to files inside the public folder. JavaScript syntax was checked successfully with Node.js.
- Public candidate tree has **no `.sav`, `.pbix`, or row-level CSV**. All participant-level exports remain under `PRIVATE_REVIEW_ONLY/`.
- Public demographics were coarsened to avoid small doctoral cells; the minimum published group-category cell count is **7**.

## Not verified / مواردی که هنوز باید بررسی شوند

- **Not a peer-reviewed study.** SPSS scoring manuals, sampling/independence, provenance, source questionnaire forms, consent, authorship and public-data distribution permissions are unverified.
- **R is unavailable here**; `exploratory_analysis_R_UNTESTED.R` was patched for original variable names but was **not** run end-to-end.
- Browser automation was blocked by the local environment. Web preview passed static tests, **not visual/browser interaction tests**; open it in desktop/mobile browsers before publishing.
- No native `.pbix` is included. The `.dax` measures and aggregate CSVs help build a report manually.
- Diagnostic p-values, correlations and confidence intervals **must not be presented as confirmatory scientific evidence**.
- The public archive still requires formal approval: see `PUBLICATION_APPROVAL_CHECKLIST_EN_FA.md`.

## PDF page counts / تعداد صفحات

- English report: **19 pages**.
- Persian report: **23 pages**.

این بسته شامل مدارک فارسی و انگلیسی است. آمار تجمیعی بازتولید شد، اما اعتبارسنجی روش نمره‌گذاری، استقلال رکوردها و مجوز بازنشر هنوز انجام نشده است. پیش از انتقال فایل‌ها به گیت‌هاب، پوشهٔ عمومی و فایل HTML را در رایانه و مرورگر خود بررسی کنید.
