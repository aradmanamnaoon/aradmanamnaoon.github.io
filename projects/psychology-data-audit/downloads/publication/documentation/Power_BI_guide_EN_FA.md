# Power BI Desktop: complete bilingual dashboard build / راهنمای کامل ساخت داشبورد دو‌زبانه

**Prepared for:** `raw.sav` · **Date:** 12 October 2026

> **Study status: EXPLORATORY / NOT VERIFIED.** The SPSS data have 240 rows, but nearly the entire questionnaire content is repeated across the two groups. **The Power BI report must display the quality warnings and should not present inferential p-values as scientifically established evidence.**
>
> **وضعیت: اکتشافی / تأییدنشده.** این فایل ۲۴۰ ردیف دارد، اما پاسخ‌های پرسشنامه در بیشتر ردیف‌های دو گروه تکراری هستند. در داشبورد هشدار کیفیت داده باید همیشه دیده شود؛ مقدارهای p نباید نتیجهٔ علمی تأییدشده تلقی شوند.

The ChatGPT website **cannot directly connect to or operate your local Power BI Desktop session**. You will import the provided CSV files and build the visuals manually. Power BI Desktop is a Windows application; it supports Persian text in report titles and data fields, but Microsoft does not promise a fully right-to-left Desktop interface or automatic translation of data. The dependable solution is **two manually labeled pages per language** within one `.pbix` file.

وب‌سایت ChatGPT **اتصال مستقیم به محیط Power BI Desktop روی کامپیوتر شما ندارد**. فایل‌های CSV را خودتان وارد کرده و طبق این راهنما روی عناصر کلیک می‌کنید. متن و برچسب‌های فارسی قابل استفاده‌اند؛ ولی نباید انتظار داشت همهٔ منوهای برنامه و چیدمان نمودارها خودکار راست‌به‌چپ شوند. راه‌حل مناسب این پروژه ساخت صفحات انگلیسی و فارسی در یک فایل `.pbix` است.

## A. Deliverable map / نقشه فایل‌ها

| File / فایل | Meaning / کاربرد |
|---|---|
| `powerbi_cases_bilingual_INTERNAL.csv` | 240 case-level rows; 89 original variables plus explicitly named audit/translation fields. **Private working data / دادهٔ ردیفی، محرمانه.** |
| `powerbi_group_summary_bilingual.csv` | The seven stored totals/subscores and three raw sums per group, with English/Persian captions. **Diagnostic only / تشخیصی.** |
| `powerbi_demographics_bilingual.csv` | Group × age/education/marriage grouped counts; bilingual, suited to presentation. |
| `powerbi_data_quality_bilingual.csv` | Full audit values and Persian audit labels. |
| `powerbi_correlations_bilingual_DIAGNOSTIC.csv` | Score correlations and sensitivity sample; no validated inference. |
| `variable_dictionary_89_original_EN_FA.csv` | Original names, Persian SPSS labels, English descriptions, coding/level issues. |
| `group_differences_unreliable_diagnostic.csv` | Calculated Welch/effect-size comparisons; **never caption them as confirmed group differences.** |
| `full_reproducible_analysis.R` | Recreate the primary audit and exported CSVs from the uploaded SAV in R. |

**Sensitive-data warning / هشدار محرمانگی:** The case-level table includes age, education, marital status and original questionnaire responses. Share a published report only with approved audiences. For a public audience, prefer aggregated tables with small-cell suppression and do **not** publish the case-level semantic model unless cleared by the data controller.

---

# Part I. English instructions: from zero to an interactive report

## 1. Install and open Power BI Desktop
1. On Windows, open the **Microsoft Store** and search for **Power BI Desktop**, or visit https://www.microsoft.com/en-us/power-platform/products/power-bi/desktop . The Store version can update automatically.
2. Install, launch Power BI Desktop, and choose a blank report if prompted.
3. Locate the **Home** ribbon, **Report canvas**, **Visualizations / Build visual** controls, **Data** pane, and page tabs at the bottom. Microsoft may change pane names and placement between releases.
4. Save a blank working file: **File > Save As** → `SPSS_Psychology_Exploratory_Bilingual.pbix`.

**Why:** A PBIX contains your data model, DAX definitions, visual layout and page text. The CSV files do **not** constitute a finished dashboard by themselves.

## 2. Import the 240-case bilingual CSV as `Cases`
1. Choose **Home > Get data > Text/CSV** (or **Get data** → **Text/CSV**).
2. Navigate to `powerbi_cases_bilingual_INTERNAL.csv` and select it.
3. In the preview, check that the first row is column headings, Persian strings display correctly, and **File origin** (if shown) is `65001: Unicode (UTF-8)`.
4. Select **Transform Data**, not Load, to inspect the query.
5. In Power Query, right-click the query name → **Rename** → `Cases`.
6. Confirm that `GROUP`, `AGE`, `MARRIAGE`, `EDUCATIO`, `IS_FIRE`, `IS_REPEATED_PROFILE`, `IS_D_INVALID`, `IS_PROFILE_FIRST`, `CASE_ID`, and `QUESTIONNAIRE_PROFILE_ID` are **Whole Number** types. For `AGEE`, `TOTALA`, `TOTALEM`, `OPTIMISM`, `EVALUATI`, `SOCIALSK`, `EMOTIONA`, `MZQ`, use **Decimal Number** as appropriate.
7. Ensure all `GROUP_EN`, `GROUP_FA`, `AGE_BAND_EN`, `AGE_BAND_FA`, `EDUCATION_EN`, `EDUCATION_FA`, `MARRIAGE_EN`, `MARRIAGE_FA` columns are **Text**. If numbers in a decimal column look corrupted, select the column → **Data type > Using Locale** and choose an appropriate decimal locale.
8. Select **Home > Close & Apply**. Verify **240 rows** using a table visual or the first DAX measure below.

**Why:** Explicit types stop Power BI from treating codes and IDs as meaningful numerical averages. The source data remain unchanged; only the import interpretation changes.

### Extra bilingual files (optional but recommended)
Repeat **Home > Get data > Text/CSV** to import, rename and Load:

- `powerbi_demographics_bilingual.csv` → `Demographics`
- `powerbi_group_summary_bilingual.csv` → `GroupScores`
- `powerbi_data_quality_bilingual.csv` → `QualityChecks`
- `powerbi_correlations_bilingual_DIAGNOSTIC.csv` → `Correlations`

**Important:** These tables represent already aggregated statistics. Do not drag a row count of `GroupScores` into a card and call it a participant count. Use the `Cases` table for participant rows. Leave the imported summary tables **disconnected** unless you deliberately define and test relationships. Page-level slicers on `Cases` do not automatically filter disconnected summary tables.

## 3. Create measures (DAX) and verify them
1. In the **Data** pane, right-click the table `Cases` → **New measure**. Alternatively select **Home / Modeling > New measure**.
2. Paste **one formula at a time** from the blocks below. The text to the left of `=` is the measure name; copy the complete formula.
3. Press Enter. Repeat for each measure.
4. If you are using a system locale that requires semicolons as DAX argument separators, change the argument delimiters accordingly. Do not change the number of arguments.

```dax
Case Rows = COUNTROWS(Cases)
```

```dax
Unique Questionnaire Profiles = DISTINCTCOUNT(Cases[QUESTIONNAIRE_PROFILE_ID])
```

```dax
Repeated Profile Rows = SUM(Cases[IS_REPEATED_PROFILE])
```

```dax
Repeated Profile Rate = DIVIDE([Repeated Profile Rows], [Case Rows])
```

```dax
Out of Range D Rows = SUM(Cases[IS_D_INVALID])
```

```dax
Out of Range D Percent = DIVIDE([Out of Range D Rows], [Case Rows])
```

```dax
TOTALA Mismatch Rows = SUM(Cases[IS_TOTALA_MISMATCH_RAW])
```

```dax
Emotion Total Mismatch Rows = SUM(Cases[IS_TOTALEM_MISMATCH_RAW])
```

```dax
Mentalization Total Mismatch Rows = SUM(Cases[IS_MZQ_MISMATCH_RAW])
```

```dax
Mean Age = AVERAGE(Cases[AGEE])
```

```dax
Mean Stored TOTALA = AVERAGE(Cases[TOTALA])
```

```dax
Mean Arithmetic A Sum = AVERAGE(Cases[A_RAW_SUM])
```

```dax
Mean Stored TOTALEM = AVERAGE(Cases[TOTALEM])
```

```dax
Mean Stored MZQ = AVERAGE(Cases[MZQ])
```

```dax
Group Fire Rows = CALCULATE([Case Rows], Cases[GROUP] = 1)
```

```dax
Group Non Rows = CALCULATE([Case Rows], Cases[GROUP] = 2)
```

```dax
Group Fire Share = DIVIDE([Group Fire Rows], [Case Rows])
```

```dax
Group Mean TOTALA Difference =
    CALCULATE([Mean Stored TOTALA], REMOVEFILTERS(Cases[GROUP], Cases[GROUP_EN], Cases[GROUP_FA]), Cases[GROUP] = 1)
    - CALCULATE([Mean Stored TOTALA], REMOVEFILTERS(Cases[GROUP], Cases[GROUP_EN], Cases[GROUP_FA]), Cases[GROUP] = 2)
```

```dax
Group Mean Raw A Difference =
    CALCULATE([Mean Arithmetic A Sum], REMOVEFILTERS(Cases[GROUP], Cases[GROUP_EN], Cases[GROUP_FA]), Cases[GROUP] = 1)
    - CALCULATE([Mean Arithmetic A Sum], REMOVEFILTERS(Cases[GROUP], Cases[GROUP_EN], Cases[GROUP_FA]), Cases[GROUP] = 2)
```

**Format tips:** Under **Measure tools**, set the two rate/share measures to **Percentage** with one decimal; means to **Decimal number** with two decimals. On a totally unfiltered page the key checks are `Case Rows`=240, `Unique Questionnaire Profiles`=86, `Repeated Profile Rows`=239, `Out of Range D Rows`=5, `TOTALA Mismatch Rows`=84, and `Group Fire Share`=50%. Under slicers these will change. **No DAX formula can establish that these 240 rows are independent participants.**

## 4. Page 1 — English Executive Overview
1. At the bottom, click **+ New page**. Double-click its tab name → `01 Overview EN`.
2. Click the white canvas → find the **Format page** or **Canvas settings** area → use a 16:9 page size. Choose a light off-white canvas background (`#F8FAFC`).
3. Select **Insert > Text box**. Type `Psychology Survey — Exploratory Overview` and beneath it `DATA NOT VERIFIED | 240 rows are not 240 proven independent people`.
4. Create three **Card** visuals; drag `[Case Rows]`, `[Unique Questionnaire Profiles]`, and `[Out of Range D Rows]` (one measure per card). Make the labels explicit: `Rows`, `Unique answer patterns`, and `Rows with invalid D codes`.
5. Insert a **Clustered bar chart**. Put `GROUP_EN` in **Y-axis** and `[Case Rows]` in **X-axis / Values**. Title: `Recorded rows by group (not verified respondents)`.
6. Insert a second clustered bar chart. `EDUCATION_EN` → Y-axis; `[Case Rows]` → X-axis. Title: `Recorded educational attainment`; optionally use `GROUP_EN` in Legend.
7. Insert a **Slicer** visual, drop `GROUP_EN` into Field and set **Dropdown** or **Tiles** as desired. Add a second slicer for `AGE_BAND_EN` and a third for `EDUCATION_EN`.
8. Put a **Text box** at the top of the page with `WARNING: 119 of 120 aligned cross-group rows have identical item responses. Stored totals are not fully reconciled.`
9. Save with **Ctrl+S**.

**Meaning:** You are presenting what is *stored*, how it is distributed and what is wrong with it—not claims of real between-population differences.

## 5. Page 2 — English Score Patterns and Sensitivity
1. **New page** → `02 Scores EN`. Add a top caution banner: `ALL SCORE COMPARISONS ARE DIAGNOSTIC / NOT FOR INFERENCE`.
2. Create a **Clustered column chart** with `GROUP_EN` on X-axis and `[Mean Stored TOTALA]` on Y-axis; from visual formatting, turn on **Data labels**. Title: `Recorded TOTALA by group — unverified`.
3. Duplicate this visual (**Ctrl+C**, **Ctrl+V**) and replace the Y-axis measure with `[Mean Arithmetic A Sum]`. Title: `Raw A1–A13 sum by group — not a validated score`.
4. Place the charts **side by side**. The visually striking story is that the source total differs by about **4.63** points, while raw A sums differ by about **0.08**.
5. Add a **Scatter chart**: `TOTALA` → X-axis; `TOTALEM` → Y-axis; `CASE_ID` → **Values / Details** (depending on UI release). If Power BI aggregates points, set fields to **Don't summarize**, use `CASE_ID` for each point and enable transparency. Title: `Individual rows: score association (repeated profiles)`.
6. Make a **Table** with `GROUP_EN`, `AGEE`, `TOTALA`, `A_RAW_SUM`, `A_SUM_DISCREPANCY`, `TOTALEM`, `EM_RAW_SUM`, `D_INVALID_ITEM_COUNT` and `CASE_ID`. Hide `NUMBER` if the report is going to nonresearch audiences. Don't publish case-level rows publicly.
7. Optional line chart for **ordered age categories only**: place `AGE` on X-axis and `[Mean Stored TOTALA]` on Y-axis, then `AGE_BAND_EN` as tooltip. Sort `AGE` ascending. **This shows an ordered age-band profile, not a timeline and not longitudinal change.** A bar chart is generally easier to interpret here because the dataset contains no date/time field.
8. Add a text note: `Very strong correlations among emotional subscales may partly reflect component–total overlap; no causal interpretation.`

**GroupScores alternative:** To show all seven stored scores using bilingual score captions, use a clustered bar visual with `GroupScores[Score_EN]` for Y-axis, `GroupScores[Mean]` for X-axis and `GroupScores[Group_EN]` for legend. Because different scales have different ranges, prefer **a separate small multiple per score** or a slicer on `Score_EN` rather than one misleading mixed-unit ranking. Keep this visual disconnected from `Cases` slicers.

## 6. Page 3 — English Data Quality and Audit
1. Add page `03 Quality EN`.
2. Add **Card** visuals for `[Repeated Profile Rows]`, `[TOTALA Mismatch Rows]`, `[Emotion Total Mismatch Rows]`, `[Mentalization Total Mismatch Rows]` and `[Out of Range D Rows]`.
3. Create a **Table** from `QualityChecks[check]`, `QualityChecks[variable]`, `QualityChecks[affected]` and `QualityChecks[description]`. Set word wrap in its Format pane.
4. Add a bar chart from the `Cases` table: `D_INVALID_STATUS_EN` on Y-axis and `[Case Rows]` on X-axis. Title: `Death-anxiety response validity`.
5. Add **Text boxes** to explain: (i) 119/120 aligned questionnaire pairs identical, (ii) 31 out-of-range D item cells in five rows, (iii) 84/32/26 stored total–raw sum differences, (iv) no verified scale key. Use a contrasting neutral caution band and readable fonts.
6. Add a slicer for `GROUP_EN` to see how quality flags are distributed by dataset group. `QualityChecks` is a static table and will not respond to this `Cases` slicer; its counts are for the original unfiltered full dataset.

## 7. Interactivity: slicers, drill and filters
1. Select a slicer → in **Format** choose **Slicer settings / Options** → `Dropdown` for compactness.
2. Use **View > Sync slicers** to decide whether the same group/age selections should apply to multiple pages; sync only the EN pages or make explicit labels because FA uses separate field names.
3. Select a bar chart → **Format > Edit interactions** (often in the ribbon) → choose whether clicking bars cross-filters other charts or leaves them unchanged.
4. For hierarchy drilling, create an age/education hierarchy or put `EDUCATION_EN` and `AGE_BAND_EN` in a chart axis hierarchy; enable visual header **drill-down** and test each drill. Do not imply a temporal sequence from education or age bands.
5. In the **Filters** pane, test report/page/visual filters and note their scope. A slicer is not a substitute for access control.
6. For extra explanation, select a visual → **Format visual > General > Header icons > Help tooltip**, if this feature is available, and supply a short explanation such as `Raw score vs stored score; neither is externally validated`. A simple text box is sufficient if this differs in your version.

## 8. Design, accessibility and bilingual consistency
- **Page palette:** navy `#16324F`, cobalt `#2563EB`, teal `#0F766E`, warm caution `#9A3412`, near-white `#F8FAFC`.
- **Typography:** make title 22–28 pt, plot titles 12–15 pt, labels at least ~11 pt where space allows. Favor fonts with good Arabic/Persian glyph coverage, but test rendering on the actual machine.
- **Do not use colors alone** to identify groups; always show `fire` and `non` labels and data values. Keep the exact group names until the researcher confirms their meaning.
- Turn off excessive decimal digits, avoid 3D charts, and place the data-quality note in the same location on all pages.
- Write accessible alternative descriptions and title text; test hover and keyboard navigation.

## 9. Save and publish with safeguards
1. **File > Save As** and save your `.pbix` locally.
2. For a **private report**, choose **Home > Publish** or **File > Publish > Publish to Power BI**, sign in and select an approved workspace. Confirm its sharing permissions.
3. Be aware that the uploaded semantic model can include underlying row data, not only the visuals. To publish publicly, build a *separate* aggregate-only PBIX from `powerbi_group_summary_bilingual.csv`, `powerbi_demographics_bilingual.csv` and the non-person-level audit tables; suppress potentially identifying small cells first.
4. If publication is disallowed or not licensed, use **File > Export > PDF** or **PowerPoint** where supported for an approved private audience. Check actual available license/workspace policies; public **Publish to web** is not appropriate for confidential psychological responses.
5. After publishing, open the report link and verify Persian glyphs, warnings, slicers and data access on the service.

---

# بخش دوم. راهنمای فارسی: ساخت صفحات فارسی در همان فایل

## ۱. آماده‌سازی محیط
۱. برنامهٔ **Power BI Desktop** را روی ویندوز نصب و باز کنید (Microsoft Store یا صفحهٔ رسمی مایکروسافت).
۲. اگر منوهای برنامه انگلیسی هستند، مشکلی نیست؛ این راهنما نام دکمه‌ها را مطابق رابط انگلیسی نوشته است.
۳. از **File > Save As** فایل را با نام `SPSS_Psychology_Exploratory_Bilingual.pbix` ذخیره کنید.
۴. جدول اصلی باید قبلاً در بخش انگلیسی با نام `Cases` وارد شده باشد و دقیقاً ۲۴۰ ردیف داشته باشد.

**چرا؟** صفحات فارسی و انگلیسی از همان داده و همان فرمول‌ها استفاده می‌کنند؛ بنابراین اختلاف عددی میان دو نسخه ایجاد نمی‌شود.

## ۲. ساخت صفحهٔ «نمای کلی» فارسی
۱. روی علامت **+** پایین صفحه کلیک کنید؛ نام صفحه را `۰۴ نمای کلی FA` بگذارید.
۲. با **Insert > Text box** عنوان زیر را قرار دهید:

> **بررسی اکتشافی داده‌های روان‌شناختی**  
> **هشدار: اصالت نمره‌ها و استقلال ۲۴۰ ردیف هنوز تأیید نشده است.**

۳. سه **Card** اضافه کنید. برای نمایش عنوان فارسی از **Format visual > General > Title** استفاده کنید:

| فیلد / DAX | عنوان فارسی پیشنهادی |
|---|---|
| `[Case Rows]` | تعداد ردیف‌های ثبت‌شده |
| `[Unique Questionnaire Profiles]` | الگوهای پاسخ متمایز |
| `[Out of Range D Rows]` | ردیف‌های دارای پاسخ نامعتبر |
| `[Repeated Profile Rows]` | ردیف‌های دارای پاسخنامه تکراری |

۴. نمودار **Clustered bar chart** را انتخاب کنید؛ در محور دسته‌ها `Cases[GROUP_FA]` و در قسمت Values سنجهٔ `[Case Rows]` را بگذارید. عنوان: **تعداد ردیف‌های ثبت‌شده در هر گروه**.
۵. نمودار ستونی یا میله‌ای دیگری بسازید: `Cases[EDUCATION_FA]` در Axis، `[Case Rows]` در Values و `Cases[GROUP_FA]` در Legend. عنوان: **تحصیلات ثبت‌شده در دو گروه**.
۶. **Slicer** مربوط به گروه (`GROUP_FA`)، بازهٔ سنی (`AGE_BAND_FA`) و تحصیلات (`EDUCATION_FA`) اضافه کنید.
۷. هر نمودار را انتخاب کنید؛ به **Format visual > General > Title** بروید و متن عنوان انگلیسی خودکار را با فارسی عوض کنید. برچسب‌ها، راهنمای رنگ و tooltip را نیز کنترل کنید.
۸. یک **Text box** در بالای صفحه قرار دهید:

> **۱۱۹ مورد از ۱۲۰ جفت ردیف متناظر دو گروه، برای تمام ۷۶ سؤال پاسخ یکسان دارند. این فایل برای نتیجه‌گیری قطعی دربارهٔ تفاوت دو گروه آماده نیست.**

## ۳. ساخت صفحهٔ «نمره‌ها» فارسی
۱. **New page** → نام `۰۵ الگوی نمره‌ها FA`.
۲. **Clustered column chart** بسازید: `GROUP_FA` در X-axis و `[Mean Stored TOTALA]` در Y-axis. عنوان: **میانگین نمرهٔ ثبت‌شدهٔ تحمل ابهام (تأییدنشده)**.
۳. همین نمودار را با **Ctrl+C / Ctrl+V** کپی کنید؛ Measure را به `[Mean Arithmetic A Sum]` تغییر دهید. عنوان: **میانگین جمع سادهٔ سؤال‌های تحمل ابهام (نمره‌گذاری تأییدنشده)**.
۴. این دو نمودار را در کنار هم قرار دهید: اختلاف دو گروه در نمرهٔ ثبت‌شده ≈۴٫۶۳ و در جمع سادهٔ سؤال‌ها ≈۰٫۰۸ است. متن توضیحی **«احتمال اثر خطای ورود یا تفاوت قواعد نمره‌گذاری؛ نیازمند بررسی منبع»** اضافه کنید.
۵. نمودار **Scatter** بسازید: `TOTALA` محور افقی و `TOTALEM` محور عمودی؛ `CASE_ID` برای تفکیک نقطه‌ها. عناوین محور را **«تحمل ابهام»** و **«خودگردانی هیجانی»** بنویسید. اشاره کنید که ردیف‌ها ممکن است مستقل نباشند.
۶. برای یک جدول مقایسهٔ فارسی، از `GroupScores[Score_FA]`, `GroupScores[Group_FA]`, `GroupScores[Mean]`, `GroupScores[SD]` استفاده کنید. اگر برای همهٔ مقیاس‌ها نمودار می‌سازید، دامنهٔ متفاوت نمره‌ها را مشخص کنید.
۷. برای نمودار خطی می‌توانید `AGE` در X-axis و میانگین یکی از نمره‌ها را در Y-axis قرار دهید؛ **این نمودار روند زمانی نیست**. به‌دلیل نبود زمان در داده، نمودار میله‌ای گروه‌های سنی معمولاً روشن‌تر است.
۸. هشدار این صفحه: **«مقایسه‌ها توصیفی هستند؛ اعتبار پاسخنامه‌ها و نمره‌گذاری باید بررسی شود.»**

## ۴. ساخت صفحهٔ «کیفیت داده» فارسی
۱. **New page** → نام `۰۶ کیفیت داده FA`.
۲. سنجه‌های زیر را به Card اضافه کنید و عنوانشان را فارسی بنویسید:

- `[Repeated Profile Rows]` → **ردیف‌های با الگوی تکراری** (مقدار اصلی ۲۳۹)
- `[TOTALA Mismatch Rows]` → **اختلاف نمرهٔ تحمل ابهام با جمع ساده** (۸۴)
- `[Emotion Total Mismatch Rows]` → **اختلاف نمرهٔ هیجانی با جمع ساده** (۳۲)
- `[Mentalization Total Mismatch Rows]` → **اختلاف نمرهٔ ذهنی‌سازی با جمع ساده** (۲۶)
- `[Out of Range D Rows]` → **ردیف‌های دارای کد نامعتبر اضطراب مرگ** (۵)

۳. یک **Table** بسازید: `QualityChecks[check_fa]` و `QualityChecks[affected]` را انتخاب کنید. عنوان فارسی: **فهرست مشکلات کیفیت داده**. در تنظیمات Formatting، حالت Word wrap متن را فعال کنید.
۴. با `D_INVALID_STATUS_FA` و `[Case Rows]` نمودار میله‌ای **وضعیت اعتبار سؤال‌های اضطراب مرگ** را رسم کنید.
۵. جعبهٔ توضیحی درج کنید:

> **۳۱ پاسخ خارج از دامنه در ۵ ردیف سؤال‌های اضطراب مرگ ثبت شده است. برای نتیجه‌گیری علمی، باید پاسخ‌های اصلی، کلید نمره‌گذاری و ماهیت رابطهٔ دو گروه مشخص شود.**

۶. نام ستون‌هایی که حروف لاتین دارند (مثلاً `TOTALA`) را عوض نکنید؛ این‌ها شناسه‌های فنی هستند. عنوان‌های نمودار، اسلایسرها و متن توضیحی می‌توانند فارسی باشند.

## ۵. نمایش راست‌به‌چپ و قالب مناسب فارسی
۱. از **Insert > Text box** متن فارسی ایجاد و در تنظیمات متن گزینهٔ راست‌چین را انتخاب کنید، اگر در نسخهٔ شما وجود دارد.
۲. از فونتی مانند **Tahoma** یا فونت فارسی قابل‌پشتیبانی روی کامپیوترتان استفاده کنید؛ بعد از انتشار در وب نیز نمایش را آزمایش کنید.
۳. جایگاه عنوان‌ها، کارت‌ها و برچسب‌ها را دستی برای خوانش فارسی بچینید؛ فرض نکنید تغییر زبان سیستم چیدمان را برعکس می‌کند.
۴. فونت بدنه را تا حد امکان ۱۱ تا ۱۳ پوینت و عنوان‌ها را واضح‌تر بگذارید.
۵. رنگ ثابت گروه‌ها را در هر شش صفحه حفظ کنید. عنوان‌های فنی مانند `fire`/`non` را بدون دانستن معنایشان به گروه شغلی یا تشخیصی خاص ترجمه نکنید.
۶. برای مخاطب انگلیسی و فارسی دو مجموعه صفحه بسازید، نه دو فایل دادهٔ متفاوت. همین کار نگهداری و کنترل نسخه را آسان می‌کند.

## ۶. تعامل، فیلتر و ذخیره
۱. روی Slicer کلیک کنید و از **Format** نمایش کشویی (**Dropdown**) را انتخاب کنید.
۲. از **View > Sync slicers** در صورت نیاز همگام‌سازی اسلایسرهای هر زبان را تنظیم کنید.
۳. با **Format > Edit interactions** تعیین کنید که کلیک روی نمودار، بقیهٔ نمودارها را فیلتر کند یا نه.
۴. از **Filters** فیلترهای صفحه/نمودار/کل گزارش را آزمایش کنید.
۵. ذخیره با **Ctrl+S**. برای ارسال در سازمانِ مجاز از **Home > Publish** استفاده کنید، وارد حساب Power BI شوید و Workspace مناسب را انتخاب کنید.
۶. **هشدار محرمانگی:** انتشار عمومی دادهٔ ردیفی روان‌شناختی مناسب نیست؛ در صورت لزوم فایل PBIX جداگانه‌ای فقط بر پایهٔ جدول‌های تجمیعی بسازید و شمارش گروه‌های بسیار کوچک را پوشیده نگه دارید.

---

# Suggested bilingual six-page report layout / چیدمان پیشنهادی شش صفحه

| Page | Title | Main visuals | Mandatory caveat |
|---|---|---|---|
| 01 | Overview EN | Participant-row cards, age/education bars, slicers | Rows are not confirmed independent participants |
| 02 | Scores EN | Stored `TOTALA` versus raw A-sum, scatter, score table | Score key and group difference unverified |
| 03 | Quality EN | Duplicate cards, audit table, D-code validation | Data provenance must be reconciled |
| 04 | نمای کلی FA | کارت‌ها، نمودار تحصیلات و سن، فیلترهای فارسی | افراد مستقل تأیید نشده‌اند |
| 05 | الگوی نمره‌ها FA | مقایسهٔ نمره ثبت‌شده و جمع خام، پراکنش، جدول | قواعد نمره‌گذاری قطعی نیست |
| 06 | کیفیت داده FA | کارت خطاها، جدول ممیزی، کدهای نامعتبر | قبل از نتیجه‌گیری منبع داده بررسی شود |

**There is no valid calendar variable.** A line chart can portray ordered *age categories* but not a time trend. Do not invent annual/monthly periods.

**این فایل متغیر تاریخ ندارد.** نمودار خطی گروه‌های سنی فقط تغییر میان رده‌های سنی را نمایش می‌دهد و به معنی روند زمانی نیست.

## Source links / منابع رسمی راهنما
- Power BI Desktop installation/getting started: https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-getting-started
- Create DAX measures: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-tutorial-create-measures
- Power BI publishing: https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-upload-desktop-files
- Supported languages / RTL limitations: https://learn.microsoft.com/en-us/power-bi/fundamentals/supported-languages-countries-regions
- Hierarchy slicers: https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-slicer-hierarchy-multiple-fields
- Visual help tooltips: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-help-tooltips

*Instructions reflect Microsoft documentation available in October 2026; exact ribbons/panes can vary by Power BI Desktop version.*
