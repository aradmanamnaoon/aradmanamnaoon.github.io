# Power BI dashboard from public aggregate tables (English / فارسی)

Unlike the earlier *private case-level CSV*, this publication package intentionally provides aggregate tables. **Do not use individual-level DAX formulas that refer to `Cases[CASE_ID]`; that table is not in the public package.**

1. Power BI Desktop → Home → Get data → Text/CSV. Import `results/demographics_bilingual_aggregated.csv` as `Demographics`; `results/score_summary_bilingual_aggregated.csv` as `ScoreSummary`; and `results/quality_metrics_bilingual.csv` as `Quality`. Set UTF-8 / Comma, then Transform Data.
2. Verify types: `Demographics[n]` Whole Number; `Demographics[percent]` Decimal; `ScoreSummary[mean]` Decimal; `ScoreSummary[n]` Whole Number; `Quality[value]` Whole Number. No relationships are required: these are independent *summary tables*.
3. Add one English page and one Persian page each for Overview, Scales and Data Quality. For an overview bar chart use `Demographics[category_en]` and `SUM(Demographics[n])`, with `Demographics[dimension_en]` filtered to **one dimension**, e.g. Age group, and group filtered to `all`.
4. For Persian change axis to `category_fa`, title to «توزیع گروه‌های سنی», and page direction using right-aligned text boxes. Use `group_fa` for labels, but avoid filtering `all` and group-specific aggregate entries together.
5. For scales: X axis `ScoreSummary[group_en]`, Y `AVERAGE(ScoreSummary[mean])` and filter `variable` to **one named scale only** such as `TOTALA` (do not average across unlike scales). Add text: "Unvalidated stored score / صرفاً نمره ثبت‌شدهٔ تأییدنشده".
6. For QA cards: filter `Quality[metric]` to a single metric and use `SUM(Quality[value])`. Example `unique_questionnaire_patterns` is 86; `matched_item_profiles_across_aligned_groups` is 119.
7. Add visible warnings to every page: independence, scoring keys, and original-data permissions remain unresolved. Never graph unverified group p-values as if confirmatory.
8. Save locally as `.pbix`; a native Power BI file is **not** generated in this package.

**فارسی:** سه فایل CSV تجمیعی را وارد کنید؛ برای هر نمودار فقط یک بُعد جمعیت‌شناختی یا یک مقیاس روان‌شناختی انتخاب کنید. در کارت‌های کیفیت داده، متغیر `metric` را به یک مقدار محدود کنید. متن هشدار اعتبار داده را در تمام صفحات درج کنید. پاسخ‌های فردی در نسخهٔ عمومی نیستند.
