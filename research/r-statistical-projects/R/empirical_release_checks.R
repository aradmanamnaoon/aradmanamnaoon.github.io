# Cross-project empirical checks and prespecified sensitivity reports.
# Usage: Rscript R/empirical_release_checks.R NHANES_DIRECTORY MANY_LABS_CSV SCAP_DIRECTORY PISA_COUNTRY_DIRECTORY
suppressPackageStartupMessages({library(haven);library(survey);library(metafor);library(lme4)})
args<-commandArgs(trailingOnly=TRUE)
if(length(args)!=4)stop("Expected four local source paths")
root <- getwd()
out <- file.path(root,"validation")
dir.create(out,recursive=TRUE,showWarnings=FALSE)
assert <- function(ok,msg) if(!isTRUE(ok))stop(msg,call.=FALSE)
report<-list()
# MindHealth — independent PHQ threshold sensitivity under masked stratified cluster design.
dem<-haven::read_xpt(file.path(args[1],"DEMO_J.xpt"))
dpq<-haven::read_xpt(file.path(args[1],"DPQ_J.xpt"))
items<-sprintf("DPQ0%d0",1:9)
assert(all(c(items,"SEQN")%in%names(dpq)),"NHANES DPQ schema mismatch")
d<-merge(dem,dpq[,c("SEQN",items)],by="SEQN")
matrix<-as.matrix(d[,items])
elig<-d$RIDAGEYR>=18 & is.finite(d$WTMEC2YR) & d$WTMEC2YR>0 &
  complete.cases(d[,c("SDMVSTRA","SDMVPSU")]) &
  apply(matrix,1,function(row)all(!is.na(row)&row%in%0:3))
x<-d[which(elig),];x$phq<-rowSums(x[,items])
assert(nrow(x)==5068L,"NHANES original analytic population changed")
des<-survey::svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~WTMEC2YR,nest=TRUE,data=x)
nh<-do.call(rbind,lapply(c(5,10,15),function(t){
  z<-survey::svymean(~I(as.numeric(phq>=t)),des)
  data.frame(threshold=t,unweighted_n=nrow(x),screen_positive=unname(coef(z)),
     se=unname(SE(z)),ci_low=unname(coef(z)-1.96*SE(z)),
     ci_high=unname(coef(z)+1.96*SE(z)))
}))
assert(abs(nh$screen_positive[nh$threshold==10]-0.0853096351)<1e-7,"PHQ threshold 10 mismatch")
write.csv(nh,file.path(out,"nhanes_screening_threshold_sensitivity.csv"),row.names=FALSE)
report[["MindHealth"]] <- "NHANES XPT: 5068 respondents, survey design, three thresholds checked"
# PISA — independently re-estimate examples using ALL replicate weights and compare versioned outputs.
pisa_expected<-read.csv("schoolmind-global/results/belonging_by_economy.csv")
reps<-paste0("W_FSTURWT",1:80)
pisa_checks<-do.call(rbind,lapply(c("DEU","FIN","SWE"),function(country){
  p<-file.path(args[4],paste0(country,".csv.gz"))
  assert(file.exists(p),paste("Missing genuine country file",country))
  a<-read.csv(gzfile(p),check.names=FALSE)
  assert(identical(names(a),c("CNT","BELONG","W_FSTUWT",reps)),"PISA schema mismatch")
  good<-is.finite(a$BELONG)&is.finite(a$W_FSTUWT)&a$W_FSTUWT>0&
    rowSums(is.finite(as.matrix(a[,reps])))==80
  a<-a[good,]; assert(nrow(a)>50,"Too few PISA observations")
  b<-survey::svrepdesign(data=a,weights=~W_FSTUWT,
     repweights=as.matrix(a[,reps]),type="Fay",rho=.5,combined.weights=TRUE)
  m<-survey::svymean(~BELONG,b)
  ref<-pisa_expected[pisa_expected$CNT==country,,drop=FALSE]
  assert(nrow(ref)==1 && nrow(a)==ref$n,"PISA sample flow disagreement")
  assert(abs(unname(coef(m))-ref$weighted_mean)<1e-10,"PISA mean disagrees")
  assert(abs(unname(SE(m))-ref$se)<1e-10,"PISA replicate SE disagrees")
  data.frame(country=country,n=nrow(a),weighted_mean=unname(coef(m)),
    replicate_se=unname(SE(m)),matches_archived_result=TRUE)
}))
write.csv(pisa_checks,file.path(out,"pisa_fay_brr_independent_recheck.csv"),row.names=FALSE)
report[["SchoolMind"]] <- "Three PISA countries rechecked directly from 80 Fay-BRR replicate columns"
# ReplicationScope — REPRODUCE published contrast summary and leave-one-lab-out influence.
raw<-read.csv(args[2],check.names=FALSE)
raw<-raw[is.finite(raw$ESCI.r)&abs(raw$ESCI.r)<1&
  is.finite(raw$ESCI.var.r)&raw$ESCI.var.r>0&
  !is.na(raw$analysis.name)&!is.na(raw$study.source),]
raw$z<-atanh(raw$ESCI.r);raw$vz<-raw$ESCI.var.r/(1-raw$ESCI.r^2)^2
old<-read.csv("replicationscope/results/within_contrast_meta.csv")
target<-head(old$analysis[order(-old$I2)],5)
loo<-do.call(rbind,lapply(target,function(contrast){
  c<-raw[raw$analysis.name==contrast,,drop=FALSE]
  if(anyDuplicated(c$study.source))stop("Duplicate lab labels")
  original<-metafor::rma.uni(yi=c$z,vi=c$vz,method="REML")
  ref<-old[old$analysis==contrast,,drop=FALSE]
  assert(nrow(ref)==1 && abs(tanh(as.numeric(original$b))-ref$estimate_r)<1e-8,
      paste("Meta result mismatch",contrast))
  # deterministic leave-one-lab-out for 10 highest-influence candidate rows
  order_i<-order(abs(c$z-mean(c$z)),decreasing=TRUE)
  indexes<-head(order_i,10)
  fits<-vapply(indexes,function(i){
    x<-metafor::rma.uni(yi=c$z[-i],vi=c$vz[-i],method="REML")
    tanh(as.numeric(x$b))
  },numeric(1))
  data.frame(analysis=contrast,labs=nrow(c),baseline_r=tanh(as.numeric(original$b)),
       leave_one_out_min_r=min(fits),leave_one_out_max_r=max(fits),
       excluded_labs_tested=length(indexes))
}))
write.csv(loo,file.path(out,"manylabs_leave_one_out_sensitivity.csv"),row.names=FALSE)
report[["ReplicationScope"]] <- "Five highest-I2 contrasts checked with ten laboratory-deletion fits each"
# Neurobehavior — same participant cohort, alternate correct-trial RT windows.
source("neurobehavior-inference-lab/R/analysis.R",local=TRUE)
all_trials<-load_scap(args[3])
assert(length(unique(all_trials$participant))==80L,"The SCAP source cohort changed")
neuro<-do.call(rbind,lapply(list(c(.15,3),c(.2,2.5),c(.3,2)),function(w){
  f<-fit_scap(all_trials,rt_min=w[1],rt_max=w[2])
  data.frame(rt_lower=w[1],rt_upper=w[2],participants=length(unique(all_trials$participant)),
    n_trials=f$n_trials,n_rt=f$n_rt,
    log_rt_load=unname(fixef(f$rt)["Load"]),
    log_rt_load_se=summary(f$rt)$coefficients["Load","Std. Error"],
    accuracy_load=unname(fixef(f$accuracy)["Load"]),
    singular_rt=f$singular_rt,singular_accuracy=f$singular_accuracy)
}))
write.csv(neuro,file.path(out,"scap_rt_window_sensitivity.csv"),row.names=FALSE)
report[["Neurobehavior"]] <- "80-participant SCAP mixed models, three RT windows, singularity indicators"
write.csv(data.frame(project=names(report),observed_check=unname(unlist(report))),
          file.path(out,"execution_matrix.csv"),row.names=FALSE)
print(read.csv(file.path(out,"execution_matrix.csv")),row.names=FALSE)

