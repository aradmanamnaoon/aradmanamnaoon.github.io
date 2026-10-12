#!/usr/bin/env python3
"""Reproduce safe-to-review aggregate tables directly from the original SPSS file.

This intentionally does NOT export individual responses by default. The source SAV
must be obtained from its lawful custodian with permission for research processing.

Run: python code/reproduce_public_aggregates.py <path-to-SAV> <output-directory>
Dependencies: numpy, pandas; parse_sav.py is bundled for this specific SPSS format.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from parse_sav import Parser

A = [f'A{i}' for i in range(1, 14)]
EM = [f'EM{i}' for i in range(1, 34)]
H = [f'H{i}' for i in range(1, 16)]
D = [f'D{i}' for i in range(1, 16)]
ITEMS = A + EM + H + D
SCALES = ['TOTALA', 'TOTALEM', 'MZQ', 'OPTIMISM', 'EVALUATI', 'SOCIALSK', 'EMOTIONA']
SCORE_LABELS = {
    'TOTALA': ('Stored ambiguity-tolerance total', 'نمرهٔ ثبت‌شدهٔ تحمل ابهام'),
    'TOTALEM': ('Stored emotional self-regulation total', 'نمرهٔ ثبت‌شدهٔ خودتنظیمی هیجانی'),
    'MZQ': ('Stored mentalization total', 'نمرهٔ ثبت‌شدهٔ ذهنی‌سازی'),
    'OPTIMISM': ('Stored optimism-related score', 'نمرهٔ ثبت‌شدهٔ خوش‌بینی'),
    'EVALUATI': ('Stored emotional evaluation score', 'نمرهٔ ثبت‌شدهٔ ارزیابی هیجانی'),
    'SOCIALSK': ('Stored social-skills score', 'نمرهٔ ثبت‌شدهٔ مهارت‌های اجتماعی'),
    'EMOTIONA': ('Stored emotional application score', 'نمرهٔ ثبت‌شدهٔ به‌کارگیری هیجان'),
    'A_RAW_SUM': ('Arithmetic sum of A1–A13 (unvalidated)', 'جمع خام سؤال‌های A1–A13 (تأییدنشده)'),
    'EM_RAW_SUM': ('Arithmetic sum of EM1–EM33 (unvalidated)', 'جمع خام سؤال‌های EM1–EM33 (تأییدنشده)'),
    'H_RAW_SUM': ('Arithmetic sum of H1–H15 (unvalidated)', 'جمع خام سؤال‌های H1–H15 (تأییدنشده)'),
}
GROUP_EN = {1.0: 'fire', 2.0: 'non'}
GROUP_FA = {1.0: 'گروه fire', 2.0: 'گروه non'}
AGE_EN = {1:'Under 30',2:'30–39',3:'40–49',4:'50–60'}
AGE_FA = {1:'کمتر از ۳۰',2:'۳۰ تا ۳۹',3:'۴۰ تا ۴۹',4:'۵۰ تا ۶۰'}
EDU_EN = {1:'Diploma',2:'Associate',3:'Bachelor',4:'Postgraduate',5:'Postgraduate'}
EDU_FA = {1:'دیپلم',2:'کاردانی',3:'کارشناسی',4:'تحصیلات تکمیلی',5:'تحصیلات تکمیلی'}
MAR_EN = {1:'Single',2:'Married',3:'Other'}
MAR_FA = {1:'مجرد',2:'متأهل',3:'سایر'}


def save_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding='utf-8-sig', float_format='%.9g')


def build(input_sav: Path, output: Path) -> dict:
    if not input_sav.is_file(): raise FileNotFoundError(input_sav)
    output.mkdir(parents=True, exist_ok=True)
    df, meta = Parser(input_sav).parse()
    if (df.shape != (240,89) or not all(c in df for c in ITEMS + SCALES)):
        raise ValueError('Unexpected input schema: audit against original file before publishing.')
    df = df.copy()
    for name,cols in [('A_RAW_SUM',A),('EM_RAW_SUM',EM),('H_RAW_SUM',H)]:
        df[name]=df[cols].sum(axis=1, min_count=len(cols))
    patterns = df[ITEMS].apply(tuple,axis=1)
    duplicates = patterns.duplicated(keep=False)
    n_profiles = int(patterns.nunique())
    invalid = ~(df[D].isin([1,2]) | df[D].isna())
    mismatch = {score: int((df[score] != df[key]).sum()) for score,key in [('TOTALA','A_RAW_SUM'),('TOTALEM','EM_RAW_SUM'),('MZQ','H_RAW_SUM')]}
    discrepancy = (df['TOTALA'] != df['A_RAW_SUM']) | (df['TOTALEM'] != df['EM_RAW_SUM']) | (df['MZQ'] != df['H_RAW_SUM'])
    grouped = {i: df[df.GROUP == i].reset_index(drop=True) for i in [1.,2.]}
    pair_matches = int((grouped[1.][ITEMS].to_numpy() == grouped[2.][ITEMS].to_numpy()).all(axis=1).sum())
    metrics = {
      'source_sha256': hashlib.sha256(input_sav.read_bytes()).hexdigest(),
      'source_file': input_sav.name,
      'record_count': len(df), 'original_variable_count': len(meta['variables']),
      'group_fire': int((df.GROUP==1).sum()), 'group_non': int((df.GROUP==2).sum()),
      'questionnaire_item_count': len(ITEMS), 'unique_questionnaire_patterns': n_profiles,
      'records_in_repeated_patterns': int(duplicates.sum()),
      'excess_pattern_instances': len(df)-n_profiles,
      'matched_item_profiles_across_aligned_groups': pair_matches,
      'invalid_death_anxiety_item_cells': int(invalid.to_numpy().sum()),
      'records_with_invalid_death_items': int(invalid.any(axis=1).sum()),
      'stored_total_vs_raw_arithmetic_disagreement': mismatch,
      'records_with_any_arithmetic_disagreement': int(discrepancy.sum()),
      'comparison_reliability': 'UNSUPPORTED: group independence and scoring keys unverified',
      'analysis_type':'exploratory data audit, not a confirmatory inferential study',
    }
    (output/'quality_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    metric_labels={
      'record_count':('Recorded rows','تعداد ردیف‌ها'),
      'original_variable_count':('Original variables','تعداد متغیرهای اصلی'),
      'group_fire':('Rows in fire','تعداد ردیف‌های گروه fire'),
      'group_non':('Rows in non','تعداد ردیف‌های گروه non'),
      'questionnaire_item_count':('Questionnaire items','تعداد سؤال‌های پرسشنامه'),
      'unique_questionnaire_patterns':('Unique complete item response patterns','الگوهای متمایز پاسخ به سؤال‌ها'),
      'records_in_repeated_patterns':('Records belonging to repeated response patterns','رکوردهای دارای الگوی پاسخ تکراری'),
      'excess_pattern_instances':('Additional occurrences beyond unique patterns','تکرارهای مازاد بر الگوهای متمایز'),
      'matched_item_profiles_across_aligned_groups':('Aligned cross-group complete item matches','تطابق کامل سؤال‌های جفت‌های متناظر دو گروه'),
      'invalid_death_anxiety_item_cells':('Invalid D-item answer cells','تعداد پاسخ‌های نامعتبر پرسشنامه اضطراب مرگ'),
      'records_with_invalid_death_items':('Records with invalid D answers','رکوردهای دارای پاسخ نامعتبر اضطراب مرگ'),
      'records_with_any_arithmetic_disagreement':('Recorded totals disagreeing with direct sums (any construct)','رکوردهای دارای مغایرت با جمع خام سؤال‌ها'),
    }
    qrows=[]
    for name,(en,fa) in metric_labels.items():
      qrows.append(dict(metric=name,label_en=en,label_fa=fa,value=metrics[name],evidence='file-level diagnostic; does not establish participant independence'))
    for k,(en,fa) in {'TOTALA':('A-total disagreement','مغایرت مجموع تحمل ابهام'), 'TOTALEM':('EM-total disagreement','مغایرت مجموع تنظیم هیجان'), 'MZQ':('H-total disagreement','مغایرت مجموع ذهنی‌سازی')}.items():
      qrows.append(dict(metric='mismatch_'+k,label_en=en,label_fa=fa,value=mismatch[k],evidence='unvalidated direct item sums; reverse scoring unknown'))
    save_csv(pd.DataFrame(qrows),output/'quality_metrics_bilingual.csv')
    dem=[]
    for grp,part in [('all',df),('fire',grouped[1.]),('non',grouped[2.])]:
      for variable,codes,names_en,names_fa in [('Age group',part.AGE,AGE_EN,AGE_FA),('Education (postgraduate combined)',part.EDUCATIO,EDU_EN,EDU_FA),('Marital status',part.MARRIAGE,MAR_EN,MAR_FA)]:
        labels = codes.map(names_en)
        for value, count in labels.value_counts().items():
          fa = dict(zip(names_en.values(),names_fa.values()))[value]
          if grp != 'all' and count < 5:
            raise ValueError('A public subgroup has fewer than five members: adjust coarsening before publication')
          dem.append(dict(group_en=grp,group_fa={'all':'همه', 'fire':'گروه fire','non':'گروه non'}[grp],dimension_en=variable,dimension_fa={'Age group':'گروه سنی','Education (postgraduate combined)':'تحصیلات (تجمیع تحصیلات تکمیلی)','Marital status':'وضعیت تأهل'}[variable],category_en=value,category_fa=fa,n=int(count),percent=round(100*count/len(part),2)))
    save_csv(pd.DataFrame(dem),output/'demographics_bilingual_aggregated.csv')
    means=[]
    for grp,part in [('all',df),('fire',grouped[1.]),('non',grouped[2.])]:
      for variable,(en,fa) in SCORE_LABELS.items():
        s=part[variable].dropna()
        means.append(dict(group_en=grp,group_fa={'all':'همه','fire':'گروه fire','non':'گروه non'}[grp],variable=variable,measure_en=en,measure_fa=fa,n=len(s),mean=round(s.mean(),6),sd=round(s.std(ddof=1),6),median=round(s.median(),6),min=s.min(),max=s.max(),interpretation_en='Unvalidated stored score or arithmetic sum; descriptive only',interpretation_fa='نمره ثبت‌شده یا مجموع خام تأییدنشده؛ صرفاً توصیفی'))
    save_csv(pd.DataFrame(means),output/'score_summary_bilingual_aggregated.csv')
    dictionary=[]
    for v in meta['variables']:
      n=v['name']
      labels=v.get('value_labels',{})
      dictionary.append(dict(variable=n,label_fa=v.get('label') or '',spss_measurement_level={1:'nominal',2:'ordinal',3:'scale'}.get(v.get('measurement_level'),'unknown'),n_missing=int(df[n].isna().sum()),n_unique=int(df[n].nunique(dropna=True)),observed_min=df[n].min(),observed_max=df[n].max(),value_labels='; '.join(f'{x}={y}' for x,y in labels.items()),notes_en='Original SPSS metadata. Questionnaire reverse scoring unverified.'))
    save_csv(pd.DataFrame(dictionary),output/'original_variable_dictionary_89.csv')
    multiplicities = patterns.value_counts().value_counts().sort_index()
    save_csv(pd.DataFrame([{'repetitions_per_pattern':int(rep),'number_of_patterns':int(n),'rows_in_category':int(rep*n)} for rep,n in multiplicities.items()]),output/'response_pattern_multiplicity_aggregated.csv')
    assert metrics['unique_questionnaire_patterns']==86
    assert metrics['records_in_repeated_patterns']==239
    assert metrics['matched_item_profiles_across_aligned_groups']==119
    assert metrics['invalid_death_anxiety_item_cells']==31
    assert metrics['records_with_invalid_death_items']==5
    assert metrics['records_with_any_arithmetic_disagreement']==108
    assert sum(mismatch.values()) ==142
    assert len(meta['variables'])==89
    return metrics


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sav',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    result=build(args.sav,args.output)
    print('PASS: source dataset audited, public aggregate exports created.')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','source_file')},indent=2))

if __name__=='__main__':main()
