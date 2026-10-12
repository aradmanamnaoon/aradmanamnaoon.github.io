# Methods and limitations / روش‌ها و محدودیت‌ها

## English

- Source: IBM SPSS system file, standard compressed numeric records; exact source bytes are preserved in **private review**.
- Parser: bundled lightweight reader for this particular SPSS format, checked against the original 240 × 89 import. Prefer `haven` or `pyreadstat` for other file types. This parser does not claim universal SAV compatibility.
- No missing numeric data were inferred or imputed; original SPSS labels were retained in the data dictionary. Value-label rules for `D1–D15` require codes 1/2, and their violations were counted, not silently fixed.
- Raw arithmetic sums of A, EM and H items were compared with stored totals only for *audit purposes*, not to prescribe the correct scale score.
- Pattern repetition: counted exactly identical vectors of 76 questionnaire responses; comparison across groups used row order in each group, which is **not proof of an original pairing design**.
- Public categories are coarsened: Master's and doctorate combined as "Postgraduate". Public exports contain aggregate counts, score moments and diagnostic metrics, not row-level data.
- Naive comparisons, correlations, regressions, bootstrapped intervals, and reliability estimates in companion results are marked *exploratory diagnostic / not valid population inference* because person-level independence and scoring are not verified.
- No preregistration, original question, random sampling description, follow-up, validated instrument editions or threshold definitions were supplied.
- Prior report PDFs are authored summaries, not an independent second replication of the Python audit. R script variable-name handling is fixed but its runtime has not been verified.

## فارسی

- منبع یک فایل SPSS شامل ۲۴۰ ردیف و ۸۹ متغیر است؛ نسخهٔ اصلی فقط در بخش خصوصی قرار دارد.
- برای بازتولید آمار تجمیعی، کد پایتون همراه با خوانش اختصاصی قالب فایل ارائه شده است.
- پاسخ‌های دارای کد نامعتبر اصلاح نشده‌اند؛ فقط شناسایی و شمارش شده‌اند.
- جمع سادهٔ سؤال‌ها فقط برای کنترل کیفیت به کار رفته و به معنی نمرهٔ معتبر پرسشنامه نیست.
- تطابق ۷۶ سؤال در دو گروه، مستقل نبودن یا جفت‌بودن نمونه را قطعی نمی‌کند، اما نیازمند بررسی جدی است.
- داده‌های عمومی فقط تجمیعی هستند و در دستهٔ تحصیلات، ارشد و دکتری به «تحصیلات تکمیلی» تبدیل شده‌اند.
- آزمون‌های استنباطی و مقدارهای p به دلیل نامشخص بودن استقلال نمونه‌ها و نمره‌گذاری صرفاً تشخیصی هستند.
- اجرای واقعی اسکریپت R در این محیط انجام نشده است و پیش از استناد علمی باید آزموده شود.
