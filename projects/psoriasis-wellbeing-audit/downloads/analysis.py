#!/usr/bin/env python3
"""Research-grounded reproducible statistics. No participant-level output is written."""
from __future__ import annotations
import json, re, math, hashlib, argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import FactorAnalysis
import statsmodels.formula.api as smf
from statsmodels.stats.weightstats import DescrStatsW
_parser = argparse.ArgumentParser(description="Recalculate ONE dataset's exploratory statistics from an authorized private original.")
_parser.add_argument("private_input_dir", type=Path, help="Private directory containing the original CSV; never publish this folder")
_parser.add_argument("--output-dir", type=Path, required=True, help="Explicit PRIVATE directory for derived JSON; no files are written into the public project")
_args = _parser.parse_args()
BASE = _args.private_input_dir.expanduser().resolve()
OUT = _args.output_dir.expanduser().resolve()
OUT.mkdir(parents=True, exist_ok=True)
DATA=[('Schuster et al_data(4).csv', 'psoriasis-wellbeing-audit', 'Psoriasis & Wellbeing Study', ';', 'https://doi.org/10.23668/psycharchives.4451')]

def serial(v):
 if isinstance(v,(np.integer,)):return int(v)
 if isinstance(v,(np.floating,)):return float(v) if np.isfinite(v) else None
 if isinstance(v,(np.bool_,)):return bool(v)
 if isinstance(v,(pd.Timestamp,)):return str(v)
 return str(v) if isinstance(v,(Path,)) else v

def pear(x,y):
 z=pd.concat([pd.to_numeric(x,errors='coerce'),pd.to_numeric(y,errors='coerce')],axis=1).dropna()
 if len(z)<10 or z.iloc[:,0].std()==0 or z.iloc[:,1].std()==0:return None
 r,p=stats.spearmanr(z.iloc[:,0],z.iloc[:,1]);return {'n':len(z),'rho':round(float(r),4),'p':float(p)}

def alpha(x):
 z=x.dropna();k=z.shape[1]
 if k<2 or len(z)<10:return None
 vv=z.var(ddof=1);tot=z.sum(axis=1).var(ddof=1)
 return {'alpha':round(float(k/(k-1)*(1-float(vv.sum()/tot))),4),'n':len(z),'items':k} if tot>0 else None

def omega(x):
 z=x.dropna()
 if z.shape[0]<30:return None
 sd=z.std(ddof=1)
 if (sd<=0).any():return None
 Z=(z-z.mean())/sd
 try:
  fit=FactorAnalysis(n_components=1,random_state=42,max_iter=500).fit(Z)
  loading=fit.components_[0,:]
  if loading.sum()<0:loading=-loading
  uni=np.maximum(fit.noise_variance_,0)
  val=loading.sum()**2/(loading.sum()**2+uni.sum())
  return {'omega_one_factor_approx':round(float(val),4),'n':len(Z),'note':'Approximate one-factor omega; factor dimensionality and reverse scoring not validated'}
 except Exception:return None

def series_json(d,col):
 s=d[col]; vc=s.value_counts(dropna=False).head(14)
 return [{'label': 'missing' if pd.isna(v) else str(v),'count':int(c)} for v,c in vc.items()]

results=[]
for file,slug,title,sep,source in DATA:
 d=pd.read_csv(BASE/file,sep=sep,decimal=',' if sep==';' else '.',low_memory=False)
 raw_na=int(d.isna().sum().sum());cells=d.size
 blank=sum(int(d[c].astype(str).str.fullmatch(r'\s*',na=False).sum()) for c in d.select_dtypes('object').columns)
 neg_cols=[c for c in d.select_dtypes('number').columns if (d[c]<0).any()]
 literal_sentinels={code:int(sum((d[c]==code).sum() for c in neg_cols)) for code in [-1,-2,-3,-5,-9,-96,-97,-98]}
 dictrows=[]
 for c in d.columns:
  z=d[c]; vals=z.value_counts(dropna=False)
  typ='text/category' if pd.api.types.is_object_dtype(z) else ('integer/coded' if pd.api.types.is_integer_dtype(z) else 'numeric')
  if c in ['case_num','worker_id','HIT_id']:typ='identifier (private, excluded from public exports)'
  if c.lower().startswith(('rq','check','quality','all_','time_')):typ='quality / audit flag'
  if z.nunique(dropna=True)<15 and not c.endswith('_id') and not c=='case_num':
   labels='; '.join(f'{v}: {int(n)}' for v,n in vals.head(8).items() if not pd.isna(v))
  else:labels='not supplied; original variable name retained'
  dictrows.append({'variable':c,'type':typ,'description':c.replace('_',' ') if not re.search(r'^(O\d|AL\d|HA\d)',c) else 'Coded question; official wording not included in upload','coded_values':labels,'null_count':int(z.isna().sum()),'blank_text_count':int(z.astype(str).str.fullmatch(r'\s*').sum()) if z.dtype==object else 0,'negative_values':','.join(map(str, sorted(set(z[z<0].unique().tolist())))) if pd.api.types.is_numeric_dtype(z) else '', 'non_missing_n':int(z.notna().sum())})
 res={'source_file':file,'slug':slug,'title':title,'dataset_url':source,'rows':len(d),'columns':len(d.columns),'true_missing_pct':round(raw_na/cells*100,3),'true_missing_cells':raw_na,'blank_string_cells':blank,'duplicate_rows':int(d.duplicated().sum()),'has_missing_patterns':'For survey-style files, explicit negative sentinel codes and blanks are not included in CSV-null rates. No sentinel interpreted as missing without an explicit assumption.','sentinel_cells':literal_sentinels,'unique_id':None,'limitations':[],'notable':[],'findings':[],'correlations':[],'bars':[],'integrity':{},'analyses':{},'dictionary':dictrows, 'citations':[source], 'feature_values':{},'summary_rows':[]}
 nums=d.select_dtypes('number');res['n_numeric']=len(nums.columns);res['n_text']=len(d.columns)-len(nums.columns)
 res['null_columns_top']=[{'name':c,'pct':round(v*100,2)} for c,v in d.isna().mean().sort_values(ascending=False).head(8).items()]
 res['distributions']={c:series_json(d,c) for c in ([('gender' if 'gender' in d else ('status' if 'status' in d else 'AL07'))] + (['device_type','expcell'] if slug=='survey-response-integrity' else []))}
 if slug=='emotion-appraisal-video-audit':
  worker=d.worker_id.nunique();hits=d.HIT_id.nunique();vid=d.video_code.nunique();res['unique_id']=f'{worker} unique worker IDs; {hits} tasks (HITs); {vid} videos'
  res['feature_values']={'unique_workers':int(worker),'unique_tasks':int(hits),'unique_videos':int(vid)}
  res['integrity']={'quality_flagged':int((d.QUALITY_CRITERION==0).sum()),'all_fail':int((d.ALL_CRITERIA==0).sum()),'time_fail':int((d.TIME_CRITERION==0).sum()),'duration_over_24h':int((d.dur_in_sec>86400).sum()),'max_duration_hours':round(float(d.dur_in_sec.max()/3600),2),'task_repeats':int(len(d)-hits),'workers':int(worker)}
  # Same task appears four times: diagnosis of dependence, not row-level duplication.
  g=d.groupby('HIT_id').size();res['integrity']['hit_size_counts']={str(k):int(v) for k,v in g.value_counts().items()}
  comp=d[['worker_id','APP_pleasantness','intensity_1','age']].copy().dropna(subset=['APP_pleasantness','intensity_1']);comp['APP_pleasantness']=pd.to_numeric(comp.APP_pleasantness,errors='coerce')
  ag=comp.groupby('worker_id',as_index=False).agg({'APP_pleasantness':'mean','intensity_1':'mean','age':'mean'}).dropna()
  res['analyses']['aggregated_worker_spearman']=pear(ag.APP_pleasantness,ag.intensity_1)
  res['analyses']['all_rows_spearman_diagnostic']=pear(comp.APP_pleasantness,comp.intensity_1)
  try:
   md=smf.mixedlm('intensity_1 ~ APP_pleasantness',comp,groups=comp.worker_id).fit(reml=False,method='lbfgs',maxiter=120,disp=False)
   res['analyses']['mixed_worker_intercept']={'n_rows':len(comp),'n_workers':comp.worker_id.nunique(),'slope':round(float(md.params['APP_pleasantness']),3),'p':float(md.pvalues['APP_pleasantness']),'ci_low':round(float(md.conf_int().loc['APP_pleasantness',0]),3),'ci_high':round(float(md.conf_int().loc['APP_pleasantness',1]),3),'converged':bool(md.converged)}
  except Exception as e:res['analyses']['mixed_worker_intercept']={'error':str(e)[:160]}
  # Cluster-robust marginal comparator. The random-intercept MixedLM may have singular variance.
  try:
   ols=smf.ols('intensity_1 ~ APP_pleasantness',comp).fit(cov_type='cluster',cov_kwds={'groups':comp.worker_id})
   z=ols.conf_int().loc['APP_pleasantness']
   res['analyses']['worker_cluster_robust_ols']={'slope':round(float(ols.params['APP_pleasantness']),3),'p':float(ols.pvalues['APP_pleasantness']),'ci_low':round(float(z.iloc[0]),3),'ci_high':round(float(z.iloc[1]),3),'n_rows':len(comp),'n_workers':comp.worker_id.nunique(),'type':'Pooled marginal OLS, cluster-robust covariance by worker; not a random-effects model'}
  except Exception as e:res['analyses']['worker_cluster_robust_ols']={'error':str(e)[:160]}
  if 'md' in locals() and 'mixed_worker_intercept' in res['analyses']:
   variance=float(md.cov_re.iloc[0,0])
   res['analyses']['mixed_worker_intercept']['random_intercept_variance']=variance
   res['analyses']['mixed_worker_intercept']['warning']='Random-intercept covariance estimated at boundary/singular; inferential p values and CIs from this fit are not reliable' if variance<1e-8 else 'Check fit diagnostics and crossed HIT/video dependence'
  items=d[['FEAR1','FEAR2','FEAR3']]
  res['analyses']['fear_items_alpha_diagnostic']=alpha(items)
  res['analyses']['fear_items_omega_diagnostic']=omega(items)
  comps=[]
  for c,items in [('FEAR',['FEAR1','FEAR2','FEAR3']),('ACH',['ACH1','ACH2','ACH3']),('INT',['INT1','INT2','INT3']),('AFF',['AFF1','AFF2','AFF3'])]:
   diag=d[items].mean(axis=1); stored=d[c];z=(stored-diag).abs()
   comps.append({'score':c,'nonmissing_compared':int(z.notna().sum()),'mismatch_gt_0_01':int((z>0.01).sum()),'max_abs_diff':round(float(z.max()),4) if z.notna().any() else None})
  res['analyses']['score_checks']=comps
  res['correlations']=[('Appraisal pleasantness','Reported intensity',pear(d.APP_pleasantness,d.intensity_1)),('Age','Reported intensity',pear(d.age,d.intensity_1)),('Appraisal pleasantness','Immersion',pear(d.APP_pleasantness,d.immersion_1)),('Fear motive','Reported intensity',pear(d.FEAR,d.intensity_1))]
  res['bars']=[{'label':'QUALITY_CRITERION = 0','value':res['integrity']['quality_flagged']},{'label':'ALL_CRITERIA = 0','value':res['integrity']['all_fail']},{'label':'TIME_CRITERION = 0','value':res['integrity']['time_fail']}]
  res['integrity']['comparison_a']={'label':'QUALITY_CRITERION flagged','value':res['integrity']['quality_flagged']}
  res['integrity']['comparison_b']={'label':'ALL_CRITERIA flagged','value':res['integrity']['all_fail']}
  res['limitations']=['Worker IDs repeat across observations; treating 13,264 rows as independent people is incorrect. HITs and videos also repeat.','QUALITY_CRITERION and ALL_CRITERIA measure different combinations of checks. Their disagreement is not proof of a computation bug without the original rulebook.','Duration outliers exceed a day; preserved, not removed or truncated.','Item scoring and the provenance of coded variables have not been verified. FEAR reliability and component checks are diagnostic.','Missing responses are nonrandom across survey sections and need instrument/branching documentation.']
 elif slug=='survey-response-integrity':
  res['unique_id']=f"{d.case_num.nunique()} unique case numbers (one record per case)"
  res['integrity']={'breakoff_flagged':int((d.RQI_breakoff==1).sum()),'status_not6':int((d.status!=6).sum()),'blank_personality_scores':int((d['Extraversion_mean'].astype(str).str.strip()=='').sum()),'blank_device_dich':int((d.device_type_dich.astype(str).str.strip()=='').sum()),'negative_code_cells':int(sum((d[c]<0).sum() for c in nums.columns if c!='case_num')),'negative_code_rows':int((nums.drop(columns=['case_num'])<0).any(axis=1).sum()),'n_negative_columns':len(neg_cols)}
  # RQI_breakoff is a recorded variable, not assumed high/low quality globally.
  score_cols=['Extraversion_mean','Agreeableness_mean','Conscientionusness_mean','Neuroticism_mean','Imagination_mean']
  for c in score_cols:d[c+'_num']=pd.to_numeric(d[c],errors='coerce')
  res['analyses']['personality_summary']={c:{'n':int(d[c+'_num'].notna().sum()),'mean':round(float(d[c+'_num'].mean()),3),'sd':round(float(d[c+'_num'].std()),3)} for c in score_cols}
  pc=d[score_cols].apply(pd.to_numeric,errors='coerce'); cr=pc.corr(method='spearman');res['analyses']['personality_correlations']=cr.round(3).to_dict()
  res['correlations']=[(a.replace('_mean',''),b.replace('_mean',''),pear(pc[a],pc[b])) for a,b in [('Extraversion_mean','Neuroticism_mean'),('Agreeableness_mean','Conscientionusness_mean'),('Neuroticism_mean','Conscientionusness_mean'),('Extraversion_mean','Imagination_mean')]]
  x=pd.to_numeric(d.loc[d.device_type==0,'Extraversion_mean'],errors='coerce').dropna(); y=pd.to_numeric(d.loc[d.device_type==1,'Extraversion_mean'],errors='coerce').dropna()
  if len(x)>20 and len(y)>20:
   t=stats.ttest_ind(x,y,equal_var=False);sp=np.sqrt(((len(x)-1)*x.var(ddof=1)+(len(y)-1)*y.var(ddof=1))/(len(x)+len(y)-2))
   res['analyses']['device_group_extraversion']={'device_codes':'0 versus 1; meanings unverified','n0':len(x),'n1':len(y),'mean0':round(float(x.mean()),3),'mean1':round(float(y.mean()),3),'difference':round(float(x.mean()-y.mean()),3),'cohen_d':round(float((x.mean()-y.mean())/sp),3),'p':float(t.pvalue),'exploratory':True}
  # compare reverse-coded O1 for non-sentinel values only; transparent assumed range 1-6.
  valid=d.O1.between(1,6);res['analyses']['reverse_code_diagnostic']={'n':int(valid.sum()),'matches_7_minus_O1':int((d.loc[valid,'O1_R']==7-d.loc[valid,'O1']).sum())}
  res['bars']=[{'label':'Records with explicit blank personality score','value':res['integrity']['blank_personality_scores']},{'label':'RQI_breakoff = 1','value':res['integrity']['breakoff_flagged']},{'label':'Rows with negative codes','value':res['integrity']['negative_code_rows']}]
  res['integrity']['comparison_a']={'label':'CSV null cells','value':raw_na}
  res['integrity']['comparison_b']={'label':'Negative-coded cells','value':res['integrity']['negative_code_cells']}
  res['limitations']=['The exported CSV contains no literal nulls but uses blank strings and negative response codes extensively. Treating all these as valid survey answers is unsafe.','Meaning of codes -1, -2, -3, -5, -96, -97, -98 is unverified without the survey codebook; negative-coded cells were counted, not silently recoded.','A raking-weight variable exists, but its target population, weighting strata and intended inference are undocumented here. No population estimates claimed.','Device-type codes and all personality scoring keys need the source instrument. The device group comparison is diagnostic only.','The status and RQI_breakoff flags align numerically but the codebook must confirm their operational meaning.']
 else:
  res['unique_id']='One row per survey record; no independently verified participant identifier or repeat index'
  code_cols=[c for c in d.columns if c.startswith('HA03_')]
  sentinel_mask=(d[code_cols]==-9)
  sentinel_count=int(sentinel_mask.sum().sum());sentinel_rows=int(sentinel_mask.any(axis=1).sum())
  res['integrity']={'minus9_cells':int(sum((d[c]==-9).sum() for c in d.columns)),'minus9_rows':int((d==-9).any(axis=1).sum()),'ha03_minus9_cells':sentinel_count,'ha03_minus9_rows':sentinel_rows,'age_min':int(d.AL06_01.min()),'age_max':int(d.AL06_01.max())}
  # Assumption for *sensitivity only*: -9 means special missing and 1-5 ranges for HA03. No mutation to raw.
  ha=d[code_cols].where((d[code_cols]>=1)&(d[code_cols]<=5))
  res['analyses']['ha03_raw_item_alpha_diagnostic']=alpha(ha)
  res['analyses']['ha03_raw_item_omega_diagnostic']=omega(ha)
  res['analyses']['ha03_complete_cases']=int(ha.dropna().shape[0]);res['analyses']['ha03_raw_composite']={'n':len(ha.dropna()),'mean':round(float(ha.dropna().mean(axis=1).mean()),3),'description':'Unkeyed average of 12 item codes; NOT a validated clinical score'}
  res['correlations']=[('Age (AL06_01)','HA03 unkeyed item mean',pear(d.AL06_01,ha.mean(axis=1))),('Age (AL06_01)','HA04',pear(d.AL06_01,d.HA04.where(d.HA04>=0))),('AL09_01','HA04',pear(d.AL09_01,d.HA04.where(d.HA04>=0))),('HA02_01','HA03 unkeyed item mean',pear(d.HA02_01.where(d.HA02_01>=0),ha.mean(axis=1)))]
  # Age groups: no claimed phenotype labels, threshold explicit
  young=ha.mean(axis=1).loc[d.AL06_01<40].dropna();old=ha.mean(axis=1).loc[d.AL06_01>=40].dropna()
  if len(young)>20 and len(old)>20:
   test=stats.ttest_ind(young,old,equal_var=False);pooled=np.sqrt(((len(young)-1)*young.var()+(len(old)-1)*old.var())/(len(young)+len(old)-2))
   res['analyses']['age_group_raw_HA03']={'group1':'Age <40','group2':'Age >=40','n1':len(young),'n2':len(old),'mean1':round(float(young.mean()),3),'mean2':round(float(old.mean()),3),'cohen_d':round(float((young.mean()-old.mean())/pooled),3),'p':float(test.pvalue),'exploratory':True}
  res['bars']=[{'label':'Literal CSV missing cells','value':raw_na},{'label':'Cells coded -9','value':res['integrity']['minus9_cells']},{'label':'Rows containing -9','value':res['integrity']['minus9_rows']}]
  res['integrity']['comparison_a']={'label':'CSV null cells','value':raw_na}
  res['integrity']['comparison_b']={'label':'Cells explicitly coded -9','value':res['integrity']['minus9_cells']}
  res['limitations']=['The study dataset is published with a separate codebook, but the codebook was not part of the uploaded files and the original variable labels are not embedded in CSV.','The -9 code appears in multiple questions; the sensitivity calculation assumes it denotes an unavailable response, but the original CSV remains unchanged.','HA03 reliability is computed on raw directions and complete cases; its score semantics and reverse coding are not established. No clinical diagnosis or outcome score is inferred.','The survey has no participant identifier or repeated-measures index; one row per respondent is assumed, not externally verified.','Observational cross-sectional results cannot support causal claims.']
  res['citations']+=['https://doi.org/10.1007/s11136-021-02991-2']
 # True 4-variable symmetric Spearman matrix, pairwise-complete values, never fabricated.
 if slug=='emotion-appraisal-video-audit':
  matrix_variables=[('Age','age'),('Appraisal','APP_pleasantness'),('Intensity','intensity_1'),('Immersion','immersion_1')]
  frame=d
 elif slug=='survey-response-integrity':
  matrix_variables=[('Extraversion','Extraversion_mean'),('Agreeableness','Agreeableness_mean'),('Neuroticism','Neuroticism_mean'),('Imagination','Imagination_mean')]
  frame=d
 else:
  matrix_variables=[('Age','AL06_01'),('HA04','HA04'),('AL09','AL09_01'),('HA02','HA02_01')]
  frame=d
 matrix_columns={label:pd.to_numeric(frame[col],errors='coerce') for label,col in matrix_variables}
 if slug=='psoriasis-wellbeing-audit':
  # Sensitivity-only -9 interpretation, original data is not modified.
  matrix_columns={name:series.where(series!=-9) for name,series in matrix_columns.items()}
 matrix_values=[]
 for label_a,_ in matrix_variables:
  cells_for_row=[]
  for label_b,_ in matrix_variables:
   if label_a==label_b:
    z=matrix_columns[label_a].dropna()
    obj={'rho':1.,'n':int(len(z))} if len(z)>0 else None
   else:obj=pear(matrix_columns[label_a],matrix_columns[label_b])
   cells_for_row.append(obj)
  matrix_values.append(cells_for_row)
 res['heatmap']={'labels':[x[0] for x in matrix_variables],'cells':matrix_values,'method':'Pairwise-complete Spearman; observational and exploratory. -9 excluded in Schuster sensitivity view only.'}
 res['notable']=[f'{len(d):,} recorded rows, {len(d.columns)} fields; {res["true_missing_pct"]:.2f}% literal missing cells.',f'{res["duplicate_rows"]} whole-row duplicates; structure: {res["unique_id"]}.']
 res['summary_rows']=[{'metric':'Records','value':len(d)},{'metric':'Variables','value':len(d.columns)},{'metric':'Literal missing (%)','value':res['true_missing_pct']},{'metric':'Whole-row duplicates','value':res['duplicate_rows']}]
 results.append(res)
 print('DONE',slug,'rows',len(d),'missing',res['true_missing_pct'],'integrity',res['integrity'],'analyses',str(res['analyses'])[:550],flush=True)
(OUT/'analysis_results.json').write_text(json.dumps(results,indent=2,default=serial,ensure_ascii=False))
print('WROTE',OUT/'analysis_results.json')
