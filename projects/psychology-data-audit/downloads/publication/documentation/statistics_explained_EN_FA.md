# Statistical Methods Explained — English & فارسی

**Dataset:** `raw.sav` · **Analysis date:** 2026-10-12 · **Status:** exploratory, **not cleared for confirmatory inference**.

> **Critical context:** 119 of 120 aligned fire/non pairs match on all 76 questionnaire items. There are only 86 distinct full questionnaire-response patterns in 240 rows. Scores in the source may not be consistently computed. The tests below explain what is computable, not what has been proven about two independently sampled populations.
>
> **نکتهٔ اساسی:** پاسخ‌های ۷۶ سؤال پرسشنامه در ۱۱۹ مورد از ۱۲۰ جفت ردیف متناظر دو گروه یکسان است. در کل ۲۴۰ ردیف، فقط ۸۶ الگوی پاسخ متمایز وجود دارد. بنابراین اعداد استنباطی صرفاً محاسبات تشخیصی هستند، نه اثبات تفاوت واقعی دو جمعیت مستقل.

---

# Part I — English: explaining the reasoning behind every analysis

## 1. Exploratory analysis versus a hypothesis test
**What:** Exploration maps structure, unexpected patterns, inconsistencies and possible hypotheses. Confirmatory testing evaluates hypotheses specified before looking at outcomes.
**Why here:** No substantive research question or validated questionnaire scoring instructions were supplied. Data anomalies also prevent defensible population inference.
**Interpretation:** Findings are hypotheses and audit results; they are *not* definitive evidence about `fire` or `non`.
**Use / avoid:** Explore first when the research target is unclear. Do not retrospectively market exploratory discoveries as preregistered tests.

## 2. Measurement levels and response categories
**What:** Nominal variables are categories without order (`GROUP`, `MARRIAGE`); ordinal variables have order (`AGE`, `EDUCATIO`, the A/EM/H questionnaire items); metric/scale variables have meaningful numerical distances (`AGEE`, provisionally stored questionnaire scores). `D1–D15` are nominal binary responses coded 1/2.
**Why:** Test choice and chart types depend on data type. SPSS marks many Likert items as `scale`, but conceptually a single five-category response is ordinal.
**Interpretation:** A higher item code is more agreement or endorsement only according to its supplied labels; it does not prove greater mental health or a higher construct without a scoring key.
**Use / avoid:** Treat multi-item validated scale scores as approximately continuous when justified. Do not run a t-test on a marital-status code or call a yes/no response a continuous outcome.

## 3. Missing values, invalid values, and structural duplicates
**What:** A blank observation differs from a filled cell containing an impossible code. A duplicate *questionnaire profile* means identical answers, not necessarily the same person. Pseudoreplication means rows treated as separate observations may not be independent.
**Why:** There are no system-missing cells, but 31 death-anxiety item values across five rows are outside the documented 1–2 codes. Exactly matching questionnaire profiles appear on 239 rows; 119 matched cross-group pairs appear in aligned rows.
**Interpretation:** No missing cells **does not imply** valid data. The overlap makes effective independent sample size unknown.
**Use / avoid:** Identify and adjudicate questionable rows using source documentation. Do not automatically delete repeated patterns or assume they are different people; ask whether rows represent repeated measurement, matching, cloning, or an export mistake.

## 4. Item scoring, reverse coding, and construct validity
**What:** A *raw sum* simply adds codes. A *validated score* follows the questionnaire's published scoring rules, including reversed items, omitted items and subscale definitions. Reverse-coding for a five-point item is commonly `6 - x`, but only for items designated as reverse-coded by its actual manual.
**Why:** Stored `TOTALA` differs from the direct A1–A13 sum in 84 rows, `TOTALEM` in 32 and `MZQ` in 26. In contrast, the raw A-sum difference between groups is about 0.08, compared with 4.63 for stored `TOTALA`.
**Interpretation:** This disagreement is a warning, *not proof* that stored scores are wrong; manuals could explain valid differences.
**Use / avoid:** Use published keys when provided. Do not invent reverse-item lists or treat raw sum scores as validated psychological measures.

## 5. Skewness and distribution shape
**What:** Skewness measures asymmetry: positive tails to the right; negative tails to the left.
**Why:** Shape and ceiling/floor effects affect suitable summaries, models and plots. `TOTALA` across all rows has skewness around −0.39.
**Interpretation:** A modest skewness value alone does not make normal assumptions valid; the repeated-row structure matters more.
**Use / avoid:** Examine histograms and residuals when continuous scores will be modeled. Do not discard otherwise sensible linear models because of a small departure from a perfect bell curve.

## 6. Outliers and the IQR rule
**What:** A value below Q1 − 1.5×IQR or above Q3 + 1.5×IQR is flagged as a potential outlier.
**Why:** Across all rows `TOTALA` has 10 potential IQR outliers. These are *review flags*, not confirmed mistakes.
**Interpretation:** An extreme participant can be genuine. A data-entry issue requires verification against the source.
**Use / avoid:** Investigate whether an extreme value is plausible; do not remove it solely to make a p-value smaller.

## 7. Shapiro–Wilk normality test
**What:** Tests how strongly the observed distribution deviates from a normal distribution.
**Why:** Used on stored score distributions and linear-model residuals as a diagnostic. For full-sample `TOTALA`, p≈0.00058.
**Interpretation:** A small p-value suggests a detectable deviation from perfect normality. It does *not* prove a statistical comparison is unusable or tell us if an effect is scientifically important.
**Use / avoid:** Use alongside Q–Q plots and substantive checks. Normality of *regression residuals*, not necessarily raw outcome variables, is most relevant to classical OLS inference.

## 8. Independence of observations
**What:** The statistical model assumes that the information contributed by one observation does not merely repeat information contributed by another, absent explicit modeling of clustering/pairs.
**Why:** This is the decisive failure here: 119/120 matched pairs share identical raw questionnaire answers.
**Interpretation:** Ordinary independent-sample p-values, standard errors and intervals may be severely misleading, even when other assumptions look satisfactory.
**Use / avoid:** Establish unique respondent identifiers, and determine whether records are independent, paired, clustered or repeated. Robust variance alone does not repair unknown sample provenance.

## 9. Welch independent-samples t-test versus Mann–Whitney U
**What:** Welch's test estimates the difference in two population means without assuming equal variances. Mann–Whitney works with ranks and detects differences in distributions, not automatically median differences.
**Why:** Exactly two dataset groups; stored continuous-like scores can be contrasted diagnostically. `TOTALA` means are 40.45 (`fire`) and 35.83 (`non`); the Welch diagnostic mean difference is 4.63.
**Interpretation:** A provisional 95% Welch interval is roughly 3.04–6.21 and a calculated p≈2.75×10⁻⁸. **Neither interval nor p-value can be used for inference because independence is not established.** Mann–Whitney does not fix duplication either.
**Use / avoid:** Use Welch for two *independent* groups with a reasonably meaningful numeric outcome. Use Mann–Whitney for rank/distribution comparisons when relevant; use paired tests only if the matching is verified as a real study design.

## 10. Brown–Forsythe / Levene variance test and homoscedasticity
**What:** Compares spread between groups. Brown–Forsythe uses deviations from the group median and is more robust to non-normal observations than classical Levene centered on the mean.
**Why:** For `TOTALA`, p≈0.013 suggests different variability in the two stored-score groups, reinforcing the choice of Welch over pooled-variance t.
**Interpretation:** Different spreads can coexist with similar or different means; this is *not* a test of the group mean difference.
**Use / avoid:** Check before equal-variance procedures. Do not switch to pooled-variance t merely because a Levene p-value is non-significant.

## 11. p-value and the distinction between evidence and size
**What:** Conditional on the statistical model and the null hypothesis, a p-value measures how unusual a result at least as extreme would be. It is not the probability the hypothesis is true.
**Why:** Diagnostic tests generate p-values and illustrate their vulnerability to broken assumptions.
**Interpretation:** “p<0.05” does not establish practical importance, absence of bias, independent sampling, or causation. Here the small `TOTALA` p-value is especially unsafe because its item responses nearly coincide across groups.
**Use / avoid:** Combine p-values with design validity, effect size, intervals, multiplicity correction and subject-matter context.

## 12. Confidence interval (CI) and bootstrap uncertainty
**What:** A confidence interval describes a procedure that covers a fixed population parameter at its stated frequency under the model assumptions. A bootstrap repeatedly resamples records to approximate uncertainty.
**Why:** Welch differences, Hedges g, correlations and Cronbach α are presented with intervals.
**Interpretation:** A “95% CI” is **not** a 95% probability that the fixed population value lies within this specific range. Bootstrap intervals are also inappropriate for unmodeled dependence.
**Use / avoid:** Use if sampling structure and estimand are clearly defined; do not interpret intervals as validated just because they were computable.

## 13. Standardized difference: Cohen's d and Hedges' g
**What:** Both divide a mean difference by a within-group SD; Hedges g applies a small-sample bias correction.
**Why:** The stored `TOTALA` comparison yields g≈0.74, but the raw A-item sums differ by only ~0.08 points.
**Interpretation:** g≈0.74 is the size *of the stored-score contrast*, not evidence of a real psychological difference. Generic “small/medium/large” labels require context and are not universal thresholds.
**Use / avoid:** Compare numeric outcome contrasts across scales when groups are genuinely independent and scoring is valid. Not for categorical labels.

## 14. Rank-biserial correlation
**What:** Describes the direction and size of a two-group rank separation, often derived from Mann–Whitney U.
**Why:** Reported with Mann–Whitney as a descriptive counterpart to Hedges g; `TOTALA` rank-biserial≈0.39.
**Interpretation:** Positive means larger ranks are more common in the first group; it is not a probability of causation and here is diagnostic only.
**Use / avoid:** Suitable for rank-based two-group contrasts, not a substitute for checking independence.

## 15. Chi-square versus Fisher's exact / permutation test; Cramér's V
**What:** Pearson's chi-square contrasts observed versus expected category counts. Fisher's exact is useful for sparse small contingency tables (especially 2×2). A permutation/Monte Carlo test can approximate an exact conditional-style reference distribution for wider tables. Cramér's V expresses association strength from 0 to 1.
**Why:** `AGE`, `MARRIAGE` and `EDUCATIO` group distributions were tabulated. Education has sparse cells (1 doctorate in each group), so asymptotic chi-square assumptions may fail.
**Interpretation:** Group age-band and education counts are *exactly identical*; this is notable for the audit, not reassuring evidence of comparability given the duplicated response patterns.
**Use / avoid:** Use for independent categorical counts; neither Fisher nor permutation repairs duplicated or paired rows.

## 16. Pearson versus Spearman correlation
**What:** Pearson r measures approximately linear co-variation of numeric variables. Spearman ρ measures monotonic ordering relationships using ranks.
**Why:** Multiple stored scale scores were screened with both. Within 86 unique response patterns, Spearman ρ≈0.922 between `TOTALEM` and `SOCIALSK`.
**Interpretation:** Strong co-movement here may be partly mechanical because `SOCIALSK` is an emotional subscale and `TOTALEM` may overlap in scoring content. It is **not** independent validation or proof of a causal relationship.
**Use / avoid:** Use Pearson for linear numerical relationships with appropriate diagnostics; Spearman for monotonic or ordinal relationships. Avoid correlating a total and its own components as if they were independent constructs.

## 17. Multiple testing and Benjamini–Hochberg (BH) correction
**What:** Examining many hypotheses inflates chances of at least one apparently small p-value. BH adjusts for expected false-discovery proportion within a specified family of comparisons, unlike Bonferroni which controls familywise error more conservatively.
**Why:** Seven stored-score group contrasts and 21 score-score correlation pairs were computed as separate exploratory families.
**Interpretation:** An adjusted q-value is *not* a cure for low-quality records, confounding, score problems or dependent sampling.
**Use / avoid:** Define a family of tests before applying corrections; avoid fishing for whichever outcome happens to pass a threshold.

## 18. Cronbach's alpha and corrected item–total correlation
**What:** Alpha measures consistency of a set of coded items under restrictive assumptions; corrected item–total correlation tests whether one item aligns with the sum of the *other* items.
**Why:** Raw-item α≈0.328 for A (13 items), 0.926 for EM (33), and 0.660 for H (15), with bootstrap intervals. The A result is especially low.
**Interpretation:** Unverified item direction and duplicated records mean these values are preliminary diagnostics, not a claim that an instrument has good or bad reliability in the true population. A high α does not establish validity or unidimensionality.
**Use / avoid:** Recalculate after obtaining instrument manuals and identifying any reverse-coded items. Don't interpret raw-item α as final psychometric evidence.

## 19. Linear regression: OLS, coefficients, intercept, residuals
**What:** Ordinary least squares predicts a continuous-like outcome using a weighted sum of explanatory variables; coefficients represent adjusted expected differences conditional on others in the model.
**Why:** Diagnostic models related each stored score to group, exact age, marital status and educational bands. Adjusted `TOTALA` group coefficient≈4.80 (HC3 95% CI 3.22–6.39).
**Interpretation:** Adjusting recorded demographics does not solve duplicated respondent profiles or inconsistent scoring. Observational regression cannot establish causality.
**Use / avoid:** Appropriate for a reasonably continuous validated outcome with independent or properly modeled observations; otherwise treat coefficients as descriptive only.

## 20. Heteroscedasticity, HC3, residual shape, linearity and influence
**What:** Heteroscedasticity means residual variance changes across fitted values/predictors. Breusch–Pagan screens this. HC3 standard errors are less sensitive to unequal variances. Residual Q–Q plots inspect shape; residual-versus-fitted plots assess pattern/linearity; Cook's distance flags influential rows.
**Why:** Several stored-score regressions have small Breusch–Pagan p-values, and HC3 was used for reported regression intervals.
**Interpretation:** HC3 can address a variance-model problem but **cannot make pseudo-independent records independent**. Cook's distance is a case review flag, not automatic grounds for deletion.
**Use / avoid:** Apply appropriate variance estimators to an otherwise valid model; if data are clustered, establish legitimate cluster IDs and a matched/cluster model.

## 21. Multicollinearity and VIF
**What:** Predictor overlap inflates coefficient uncertainty. VIF summarizes variance inflation; generalized VIF can handle multi-df categorical predictors.
**Why:** Diagnostic group/age/education/marital regression predictors had maximum adjusted VIF around 1.63.
**Interpretation:** No severe collinearity signal in *these covariates*, but the sample-provenance failure remains.
**Use / avoid:** Use VIF for regression predictors. Do not use VIF as a test of data authenticity or causal identifiability.

## 22. R², adjusted R², AIC and BIC
**What:** R² is the observed variance proportion explained by fitted regression; adjusted R² penalizes added predictors. AIC and BIC compare likelihood-based candidate models on the **same outcome and data**, with penalties for complexity; smaller usually preferred among comparable candidates.
**Why:** Included to transparently describe models; none validates the dataset. For one exploratory unique-profile model, R²≈0.054 and adjusted R²≈0.031.
**Interpretation:** A large R² is neither accuracy on new people nor proof of causality. Do not compare AIC for models of different response variables or altered samples.
**Use / avoid:** Use on well-specified candidate models with genuine sampling assumptions; favor held-out predictive evaluation when prediction is the actual goal.

## 23. One-way ANOVA versus Kruskal–Wallis and post-hoc tests
**What:** ANOVA tests average differences among 3+ group levels; Welch ANOVA relaxes variance equality. Kruskal–Wallis compares rank distributions across 3+ groups. Post-hoc methods (Tukey, Games–Howell, Dunn) identify pairs, with multiplicity control.
**Why not a headline analysis:** `GROUP` has only two levels, so Welch t is the natural diagnostic comparison. Education has five levels but severe imbalance and questionable independence.
**Use / avoid:** Use for suitable multi-group research questions only after establishing real independent cases and valid outcomes.

## 24. Linear versus logistic regression, odds ratios and classification
**What:** Linear regression models a numeric response. Logistic regression models log-odds of a binary response; exponentiated coefficients yield odds ratios (OR), not risk ratios. An OR of 2 means doubled odds at fixed covariates, **not** twice the probability.
**Why not a headline analysis:** No predesignated binary outcome, and raw `D1–D15` contain invalid codes. Treating `GROUP` as an outcome would manufacture a prediction task unsupported by proven sample structure.
**Use / avoid:** Use logistic modeling only with a legitimate binary endpoint, enough events, design-valid records and calibration checks. Do not infer discrimination ability from replicated examples or in-sample fit.

## 25. Effect interpretation, confounding and ecological/causal claims
**What:** Statistical association means variables co-vary, not one causes the other. Confounding involves a third variable related to both exposure and outcome; observational adjustments cannot guarantee it is resolved.
**Why:** Group membership is only coded `fire`/`non` with no study protocol explaining recruitment or meaning.
**Interpretation:** There is no basis to say that either group *causes* stronger tolerance, emotional regulation, mentalization or death anxiety.
**Use / avoid:** First obtain sampling design, intended outcomes and questionnaires, then formulate defensible confirmatory estimands.

## 26. Research-design decision sequence
1. Verify what `fire`/`non` represent and whether respondents were independent, paired, or repeated measures.
2. Reconcile aligned identical item responses with source questionnaires and the original SPSS export.
3. Obtain the full item wording, reverse-scoring keys and subscale rules.
4. Audit and correct D-item codes using source records, without guessing.
5. Establish a unique respondent ID; consider ethics and confidentiality requirements.
6. Prespecify primary and secondary outcomes, effect sizes and multiplicity procedure.
7. Recompute all score totals and rerun the chosen design-valid tests.
8. Only then write confirmatory conclusions or publish a result-bearing dashboard.

---

# بخش دوم — توضیح فارسی مفاهیم و آزمون‌ها

## ۱. تحلیل اکتشافی و آزمون فرضیه
**چیست؟** تحلیل اکتشافی برای شناخت ساختار داده، کشف الگوها و یافتن مشکلات است. تحلیل تأییدی به پرسش‌هایی می‌پردازد که پیش از مشاهدهٔ نتایج مشخص شده‌اند.
**چرا اینجا؟** سؤال پژوهشی، دستورالعمل نمره‌گذاری و طرح نمونه‌گیری ارائه نشده است.
**تفسیر:** نتایج این فایل «سرنخ و یافتهٔ ممیزی» هستند؛ تفاوت قطعی دو جمعیت را نشان نمی‌دهند.
**زمان استفاده / منع استفاده:** برای داده‌های تازه مناسب است؛ اما نباید نتیجهٔ کشف‌شده را به‌صورت فرضیهٔ از پیش تعیین‌شده ارائه کرد.

## ۲. نوع متغیر و مقیاس اندازه‌گیری
**چیست؟** اسمی: دسته‌هایی بدون ترتیب (`GROUP`, `MARRIAGE`)؛ ترتیبی: دسته‌هایی دارای ترتیب (`AGE`, `EDUCATIO` و سؤال‌های لیکرت)؛ عددی/فاصله‌ای: سن دقیق (`AGEE`) و نمره‌های تجمیعی، اگر صحت محاسبهٔ آن‌ها تأیید شود. پاسخ‌های `D1–D15` دوحالتی‌اند.
**چرا؟** انتخاب آزمون تابع نوع متغیر است. «Scale» بودن سؤال لیکرت در تنظیمات SPSS به‌تنهایی آن را پیوسته نمی‌کند.
**تفسیر:** عدد بزرگ‌تر در سؤال الزاماً به معنی وضعیت روان‌شناختی بهتر نیست؛ جهت سؤال و کلید نمره‌گذاری تعیین‌کننده است.
**زمان استفاده / منع استفاده:** نمرهٔ تجمیعی معتبر ممکن است عددی مدل‌سازی شود؛ وضعیت تأهل را نمی‌توان به‌عنوان مقدار پیوسته وارد آزمون میانگین کرد.

## ۳. دادهٔ گمشده، کد نامعتبر و تکرار پاسخ‌ها
**چیست؟** خانهٔ خالی با کد عددی نامعتبر فرق دارد. تکرار کل پاسخنامه به‌تنهایی ثابت نمی‌کند دو ردیف متعلق به یک شخص هستند؛ اما استقلال را زیر سؤال می‌برد.
**چرا؟** خانهٔ خالی سیستم وجود ندارد؛ بااین‌حال ۳۱ مقدار خارج از کدهای ۱ و ۲ در پنج ردیف سؤال‌های اضطراب مرگ دیده شده است. ۲۳۹ ردیف الگوی تکراری دارند.
**تفسیر:** کامل بودن فایل به معنی سالم بودن آن نیست.
**زمان استفاده / منع استفاده:** باید فرم‌های اصلی بررسی شوند؛ حذف خودکار داده‌های تکراری یا تلقی آن‌ها به‌عنوان اشخاص مستقل اشتباه است.

## ۴. جمع حسابی، نمرهٔ معتبر و نمره‌گذاری معکوس
**چیست؟** جمع حسابی، حاصل جمع سادهٔ پاسخ‌هاست؛ ولی نمرهٔ واقعی پرسشنامه ممکن است به معکوس‌کردن بعضی سؤال‌ها نیاز داشته باشد.
**چرا؟** `TOTALA` در ۸۴ ردیف، `TOTALEM` در ۳۲ و `MZQ` در ۲۶ ردیف با جمع سادهٔ سؤال‌ها متفاوت‌اند.
**تفسیر:** این اختلاف الزاماً خطا نیست؛ شاید از کلید معکوس ناشی شود. اما اختلاف میان دو گروه در `TOTALA` برابر ۴٫۶۳ و در جمع سادهٔ `A1–A13` فقط حدود ۰٫۰۸ است؛ پس بدون دستورالعمل نمی‌توان نتیجهٔ روان‌شناختی گرفت.
**زمان استفاده / منع استفاده:** فقط فهرست رسمی سؤال‌های معکوس را به‌کار ببرید؛ معکوس‌سازی حدسی مجاز نیست.

## ۵. چولگی و شکل توزیع
**چیست؟** چولگی جهت نامتقارن بودن توزیع را نشان می‌دهد.
**چرا؟** برای تشخیص تجمع پاسخ‌ها در یک سوی مقیاس بررسی شد؛ چولگی `TOTALA` در کل داده تقریباً ۰٫۳۹− است.
**تفسیر:** چولگی نسبتاً کم تضمین‌کنندهٔ نرمال بودن یا معتبر بودن استنباط نیست.
**زمان استفاده / منع استفاده:** هنگام بررسی نمره‌های عددی مفید است؛ به‌تنهایی معیار حذف آزمون پارامتری نیست.

## ۶. مقادیر دورافتاده و روش IQR
**چیست؟** مقداری که بیرون از بازهٔ چارک اول منهای ۱٫۵ برابر فاصلهٔ بین‌چارکی یا چارک سوم به‌علاوهٔ آن قرار گیرد، «مشکوک به دورافتادگی» است.
**چرا؟** در `TOTALA` ده مقدار بالقوه دورافتاده گزارش شده است.
**تفسیر:** دورافتاده بودن مساوی غلط بودن نیست.
**زمان استفاده / منع استفاده:** برای بازبینی فرم اصلی مناسب است؛ حذف صرفاً برای بهبود معنی‌داری علمی نیست.

## ۷. آزمون نرمال بودن شاپیرو–ویلک
**چیست؟** فاصلهٔ شکل توزیع از منحنی نرمال را می‌سنجد.
**چرا؟** روی نمره‌ها و باقی‌مانده‌های مدل بررسی شد. برای `TOTALA` در کل داده p≈۰٫۰۰۰۵۸ است.
**تفسیر:** p کوچک یعنی تفاوت قابل تشخیص از نرمال؛ اما این آزمون نه اندازهٔ اثر را می‌سنجد و نه مشکل ردیف‌های تکراری را رفع می‌کند.
**زمان استفاده / منع استفاده:** همراه نمودار Q–Q و بررسی باقی‌مانده‌ها مفید است؛ «نرمال بودن خود متغیر وابسته» همیشه شرط اصلی رگرسیون نیست.

## ۸. استقلال مشاهده‌ها
**چیست؟** هر مشاهده باید اطلاعات مستقلی فراهم کند، مگر آن‌که جفت‌بودن یا خوشه‌ای‌بودن به‌طور صریح در مدل لحاظ شود.
**چرا؟** در ۱۱۹ جفت از ۱۲۰ ردیف متناظر دو گروه، همهٔ ۷۶ پاسخ یکسان‌اند.
**تفسیر:** این بزرگ‌ترین مانع اعتبار p-value، فاصلهٔ اطمینان و خطای معیار است.
**زمان استفاده / منع استفاده:** باید شناسهٔ معتبر فرد و طرح پژوهش مشخص شود. خطای معیار مقاوم (HC3) نمی‌تواند منشأ نامشخص نمونه را اصلاح کند.

## ۹. آزمون t ولچ در برابر من–ویتنی
**چیست؟** ولچ تفاوت میانگین دو گروه مستقل را بدون فرض برابری واریانس بررسی می‌کند. من–ویتنی مبتنی بر رتبه است و الزاماً آزمون «تفاوت میانه» نیست.
**چرا؟** متغیر گروه دو سطح دارد. میانگین `TOTALA` در `fire` برابر ۴۰٫۴۵ و در `non` برابر ۳۵٫۸۳ است.
**تفسیر:** اختلاف محاسبه‌شده ۴٫۶۳، فاصلهٔ تشخیصی ۹۵٪ برابر ۳٫۰۴ تا ۶٫۲۱ و p≈۲٫۷۵×۱۰⁻⁸ است؛ **ولی این مقادیر به دلیل نامعلوم بودن استقلال و صحت نمره، استنباط معتبر نیستند.** من–ویتنی هم این مشکل را حل نمی‌کند.
**زمان استفاده / منع استفاده:** ولچ برای دو گروه واقعاً مستقل و نمرهٔ معتبر مناسب است. در صورت تأیید جفت‌بودن واقعی باید آزمون جفتی متناسب به‌کار رود.

## ۱۰. برابری واریانس، لون و براون–فورسایت
**چیست؟** بررسی می‌کنند آیا پراکندگی در گروه‌ها نزدیک به هم است یا نه.
**چرا؟** مقدار p براون–فورسایت برای `TOTALA` حدود ۰٫۰۱۳ است، بنابراین ولچ به آزمون t با واریانس تجمیعی ترجیح داده شد.
**تفسیر:** تفاوت واریانس، لزوماً تفاوت میانگین نیست.
**زمان استفاده / منع استفاده:** برای انتخاب مدل واریانس مناسب مفید است؛ نامعنی‌دار شدن آزمون لون دلیل کافی برای تحمیل برابری واریانس نیست.

## ۱۱. مقدار p
**چیست؟** احتمال مشاهدهٔ داده‌ای با این شدت یا بیشتر، **اگر فرض صفر و مفروضات مدل درست باشند**. احتمال درست‌بودن فرض صفر نیست.
**چرا؟** آزمون‌های تشخیصی مقدار p تولید می‌کنند.
**تفسیر:** p کوچک نه اندازهٔ اهمیت نتیجه را مشخص می‌کند، نه علیت و نه کیفیت داده را. در این فایل ممکن است گمراه‌کننده باشد.
**زمان استفاده / منع استفاده:** فقط در کنار طرح مطالعه، اندازهٔ اثر، فاصلهٔ اطمینان و تصحیح آزمون‌های متعدد خوانده شود.

## ۱۲. فاصلهٔ اطمینان و بوت‌استرپ
**چیست؟** فاصلهٔ اطمینان یک روش برآورد با پوشش بلندمدت تعریف‌شده است؛ بوت‌استرپ با نمونه‌گیری مجدد عدم‌قطعیت را تقریب می‌زند.
**چرا؟** برای تفاوت گروهی، همبستگی و آلفا استفاده شد.
**تفسیر:** فاصلهٔ ۹۵٪ به معنی احتمال ۹۵٪ قرارگرفتن پارامتر ثابت در همان فاصلهٔ محاسبه‌شده نیست. تکرار پاسخ‌ها اعتبار روش را هم کاهش می‌دهد.
**زمان استفاده / منع استفاده:** وقتی واحدهای نمونه‌گیری معتبر و مستقل یا مدل‌شده باشند مناسب است.

## ۱۳. اندازهٔ اثر کوهن d و هدجز g
**چیست؟** تفاوت میانگین را برحسب انحراف معیار درون‌گروهی بیان می‌کند؛ g اصلاح کوچکی برای اریب نمونه دارد.
**چرا؟** برای `TOTALA` مقدار g≈۰٫۷۴ محاسبه شد.
**تفسیر:** این عدد اندازهٔ تفاوت **نمرهٔ ثبت‌شده** است، نه تأیید تفاوت واقعی روان‌شناختی؛ برچسب‌های کوچک/متوسط/بزرگ به زمینهٔ پژوهش بستگی دارد.
**زمان استفاده / منع استفاده:** برای نمرهٔ عددی معتبر در دو گروه مناسب است؛ برای دسته‌های اسمی مناسب نیست.

## ۱۴. ضریب همبستگی رتبه‌ای دووجهی
**چیست؟** مقدار جدایی رتبه‌ها در دو گروه را بیان می‌کند.
**چرا؟** همراه من–ویتنی گزارش شد؛ برای `TOTALA` حدود ۰٫۳۹ است.
**تفسیر:** علامت مثبت یعنی رتبه‌های بزرگ‌تر در گروه اول بیشتر دیده می‌شود؛ نتیجه در این فایل فقط توصیفی است.
**زمان استفاده / منع استفاده:** مناسب آزمون‌های رتبه‌ای با استقلال معتبر است.

## ۱۵. کای‌دو، آزمون دقیق فیشر و V کرامر
**چیست؟** کای‌دو فراوانی مشاهده‌شده و مورد انتظار را مقایسه می‌کند. فیشر برای جدول‌های کوچک/کم‌تعداد مناسب است. V کرامر اندازهٔ رابطهٔ دو متغیر دسته‌ای است.
**چرا؟** فراوانی تحصیلات، وضعیت تأهل و ردهٔ سنی دو گروه مقایسه شد. تعداد دکتری در هر گروه فقط ۱ نفر است؛ لذا تقریب‌های معمول کای‌دو در بخشی از جدول ضعیف‌اند.
**تفسیر:** توزیع تحصیلات و گروه‌های سنی دقیقاً در دو گروه یکسان است، ولی با توجه به تکرار پاسخنامه‌ها نمی‌توان آن را «همتاسازی علمی تأییدشده» نامید.
**زمان استفاده / منع استفاده:** تنها برای شمارش‌های مستقل؛ آزمون دقیق هم تکرار رکوردها را اصلاح نمی‌کند.

## ۱۶. همبستگی پیرسون و اسپیرمن
**چیست؟** پیرسون برای رابطهٔ خطی و اسپیرمن برای رابطهٔ یکنواخت بر مبنای رتبه است.
**چرا؟** برای جفت‌های نمره‌های ثبت‌شده استفاده شد. در ۸۶ الگوی متمایز، همبستگی اسپیرمن بین `TOTALEM` و `SOCIALSK` تقریباً ۰٫۹۲۲ است.
**تفسیر:** ممکن است این رابطه عمدتاً ناشی از هم‌پوشانی زیرمقیاس مهارت اجتماعی با نمرهٔ کلی باشد؛ دلیل رابطهٔ علت و معلولی نیست.
**زمان استفاده / منع استفاده:** باید از همبستگی «کل مقیاس با جزء همان مقیاس» به‌عنوان تأیید مستقل اجتناب کرد.

## ۱۷. اصلاح آزمون‌های متعدد و روش بنجامینی–هوچبرگ
**چیست؟** با افزایش تعداد آزمون‌ها احتمال نتایج ظاهراً معنادار تصادفی بیشتر می‌شود؛ BH سهم مورد انتظار کشفیات غلط را کنترل می‌کند.
**چرا؟** هفت تفاوت نمره و ۲۱ جفت همبستگی در دو خانوادهٔ جدا تصحیح شدند.
**تفسیر:** q-value اصلاح‌شده کیفیت داده، استقلال یا اعتبار نمره‌گذاری را تأمین نمی‌کند.
**زمان استفاده / منع استفاده:** برای خانوادهٔ آزمون‌ها با هدف مشخص؛ نباید بعد از شکار نتایج موفق، خانواده را دلخواه تعریف کرد.

## ۱۸. آلفای کرونباخ و همبستگی اصلاح‌شده سؤال با مجموع
**چیست؟** آلفا شاخص همسانی درونی سؤال‌هاست؛ همبستگی اصلاح‌شده نشان می‌دهد یک سؤال با مجموع دیگر سؤال‌ها چقدر همسوست.
**چرا؟** آلفای خام A≈۰٫۳۲۸، EM≈۰٫۹۲۶ و H≈۰٫۶۶۰ است.
**تفسیر:** نبود کلید سؤال‌های معکوس و تکرار پاسخ‌ها به معنی «تشخیصی بودن» این شاخص‌هاست. آلفای زیاد نه روایی را ثابت می‌کند و نه الزاماً تک‌بعدی‌بودن را.
**زمان استفاده / منع استفاده:** پس از دریافت راهنمای رسمی پرسشنامه دوباره محاسبه شود؛ فعلاً نتیجهٔ قطعی روان‌سنجی ارائه نشود.

## ۱۹. رگرسیون خطی و ضرایب آن
**چیست؟** یک نمرهٔ عددی را به‌صورت تابعی از گروه، سن و متغیرهای دیگر توضیح می‌دهد.
**چرا؟** برای کنترل توصیفی سن، تحصیلات و وضعیت تأهل، مدل OLS محاسبه شد. ضریب گروه برای `TOTALA` حدود ۴٫۸۰ و فاصلهٔ تشخیصی HC3 تقریباً ۳٫۲۲ تا ۶٫۳۹ است.
**تفسیر:** کنترل متغیرهای جمعیت‌شناختی، مشکل تکرار خام پاسخنامه را رفع نمی‌کند. رابطهٔ رگرسیونی علت و معلول نیست.
**زمان استفاده / منع استفاده:** پس از اطمینان از استقلال، صحت نمره و شکل رابطه استفاده شود.

## ۲۰. ناهمسانی واریانس، HC3، خطی‌بودن و دادهٔ اثرگذار
**چیست؟** ناهمسانی یعنی پراکندگی باقی‌مانده‌ها ثابت نیست؛ بروش–پاگان برای شناسایی آن استفاده می‌شود. HC3 خطای معیار مقاوم‌تری می‌دهد. نمودار باقی‌مانده و فاصلهٔ کوک شکل رابطه و نقاط اثرگذار را نشان می‌دهند.
**چرا؟** بخشی از رگرسیون‌ها p کوچک بروش–پاگان دارند و برای ضرایب HC3 استفاده شد.
**تفسیر:** HC3 مشکل واریانس را تا حدی پوشش می‌دهد، اما تکرار افراد/پاسخ‌ها را برطرف نمی‌کند.
**زمان استفاده / منع استفاده:** در مدل درست تعریف‌شده مناسب است؛ دادهٔ با منشأ نامعتبر با انتخاب HC3 معتبر نمی‌شود.

## ۲۱. هم‌خطی چندگانه و VIF
**چیست؟** هم‌پوشانی پیش‌بین‌ها می‌تواند عدم‌قطعیت ضرایب را بیشتر کند. VIF شدت این وضعیت را می‌سنجد.
**چرا؟** حداکثر VIF تعدیل‌شده در مدل‌های تشخیصی حدود ۱٫۶۳ بوده است.
**تفسیر:** این مقدار نشانهٔ شدیدی از هم‌خطی در متغیرهای توضیحی مشخص‌شده ندارد؛ اما نشان‌دهندهٔ استقلال مشاهدات نیست.
**زمان استفاده / منع استفاده:** برای متغیرهای پیش‌بین رگرسیون؛ نه برای تأیید اصالت داده.

## ۲۲. R²، R² تعدیل‌شده، AIC و BIC
**چیست؟** R² مقدار تغییرپذیری توضیح‌داده‌شده در دادهٔ مشاهده‌شده را نشان می‌دهد؛ نسخهٔ تعدیل‌شده بابت تعداد پیش‌بین‌ها جریمه دارد. AIC/BIC برای مقایسهٔ مدل‌هایی با یک پاسخ و دادهٔ قابل‌مقایسه به کار می‌روند.
**چرا؟** برای شفافیت تشخیص مدل گزارش شده‌اند؛ R²≈۰٫۰۵۴ در یک مدل حساسیت از الگوهای متمایز مشاهده شد.
**تفسیر:** R² بالا الزاماً پیش‌بینی خوب برای افراد جدید یا رابطهٔ علّی نیست. AIC دو مدل با متغیر وابستهٔ متفاوت را با هم مقایسه نکنید.
**زمان استفاده / منع استفاده:** برای انتخاب مدل در شرایط طراحی و برازش معتبر.

## ۲۳. ANOVA و کروسکال–والیس و آزمون‌های تعقیبی
**چیست؟** ANOVA برای تفاوت میانگین میان سه گروه یا بیشتر است؛ ولچ ANOVA برابری واریانس را لازم ندارد. کروسکال–والیس توزیع رتبه‌ها را میان چند گروه مقایسه می‌کند. آزمون‌های تعقیبی مانند توکی، گیمز–هاول و دان با اصلاح چندگانه جفت‌های متفاوت را مشخص می‌کنند.
**چرا به‌عنوان آزمون اصلی اجرا نشد؟** `GROUP` فقط دو سطح دارد؛ سطح‌های تحصیلات نیز نامتوازن و استقلال محل تردید است.
**زمان استفاده / منع استفاده:** فقط پس از تثبیت ساختار واقعی داده و تعریف پرسش پژوهشی چندگروهی.

## ۲۴. رگرسیون خطی در برابر لجستیک و نسبت شانس OR
**چیست؟** لجستیک برای پیامد دوحالتی استفاده می‌شود. نمای ضریب آن OR است؛ OR=۲ به معنی دوبرابر شدن «شانس» است نه لزوماً دوبرابر شدن احتمال.
**چرا اجرا نشد؟** متغیر پیامد دوحالتیِ معتبر و از پیش تعریف‌شده نداریم و برخی پاسخ‌های D نامعتبرند. پیش‌بینی کد گروه از داده‌های تکراری تحلیل علمی قابل اعتماد ایجاد نمی‌کند.
**زمان استفاده / منع استفاده:** برای پیامد مشخص دوحالتی، شمار رویداد کافی، بررسی کالیبراسیون و دادهٔ مستقل.

## ۲۵. رابطه، مخدوش‌گری و علیت
**چیست؟** همبستگی به معنی علت و معلول نیست؛ متغیر سوم ممکن است توضیح‌دهندهٔ رابطه باشد.
**چرا؟** معنی پژوهشی `fire` و `non` و روش نمونه‌گیری هنوز معلوم نیست.
**تفسیر:** نمی‌توان گفت تعلق به هر گروه باعث تغییر تحمل ابهام، خودگردانی هیجانی یا اضطراب مرگ می‌شود.
**زمان استفاده / منع استفاده:** برای استنباط علّی به طرح پژوهشی مناسب و کنترل مخدوش‌گرهای معنادار نیاز است.

## ۲۶. چک‌لیست پیش از ارائهٔ یافتهٔ قطعی
1. معنی دقیق گروه‌های `fire` و `non` و ماهیت مستقل/جفتی نمونه‌ها مشخص شود.
2. منبع ردیف‌های با پاسخ یکسان بررسی و مستند شود.
3. متن کامل سؤال‌ها، کلید معکوس و نحوهٔ محاسبهٔ نمره‌ها دریافت شود.
4. ۳۱ پاسخ خارج از دامنه در D با فرم اولیه تطبیق داده شود.
5. شناسهٔ یکتای پاسخ‌دهنده و ملاحظات محرمانگی تعیین شود.
6. پیامد اصلی و پیامدهای فرعی پیش از تفسیر استنباطی مشخص شوند.
7. نمره‌های درست محاسبه، آزمون مناسب طرح انتخاب و تحلیل مجدداً اجرا شود.
8. فقط پس از این مراحل، نتیجهٔ تأییدی یا داشبورد نتایج قابل انتشار تهیه شود.

---

*This document deliberately excludes tutorials on mean, median, standard deviation, frequency, and percentage. Raw numerical outputs and all 89 variables are supplied separately.*

*این سند عمداً از توضیح میانگین، میانه، انحراف معیار، فراوانی و درصد صرف‌نظر کرده است. اعداد تفصیلی و فهرست کامل ۸۹ متغیر در فایل‌های همراه ارائه شده‌اند.*
