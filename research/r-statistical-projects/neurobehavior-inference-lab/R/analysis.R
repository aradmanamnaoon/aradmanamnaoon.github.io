# Neurobehavior Inference Lab — SCAP event-level mixed models, UNEXECUTED.
# Usage: Rscript R/analysis.R /path/to/ds000030
if(!requireNamespace("lme4",quietly=TRUE)) stop("Install lme4")
load_scap <- function(root) {
  if(!dir.exists(root)) stop("Missing ds000030 directory")
  paths <- list.files(root,pattern="task-scap_events[.]tsv$",recursive=TRUE,full.names=TRUE)
  if(!length(paths)) stop("No SCAP task event files found")
  rows <- lapply(paths,function(path) {
    d <- utils::read.delim(path,check.names=FALSE)
    fields <- c("Load","Delay","ReactionTime","ResponseAccuracy")
    if(!all(fields %in% names(d))) stop("Schema error in ",path)
    d$participant <- sub(".*(sub-[A-Za-z0-9]+).*","\\1",path)
    d
  })
  do.call(rbind,rows)
}
fit_scap <- function(d,rt_min=0.15,rt_max=3) {
  d$Load <- suppressWarnings(as.numeric(d$Load))
  d$Delay <- suppressWarnings(as.numeric(d$Delay))
  d$ReactionTime <- suppressWarnings(as.numeric(d$ReactionTime))
  d$correct <- ifelse(d$ResponseAccuracy=="CORRECT",1,
                      ifelse(d$ResponseAccuracy=="INCORRECT",0,NA_real_))
  d <- d[is.finite(d$Load) & is.finite(d$Delay) & !is.na(d$correct),,drop=FALSE]
  if(length(unique(d$participant))<3) stop("Too few independent participants")
  accuracy <- lme4::glmer(correct~Load+Delay+(1|participant),data=d,
       family=binomial,control=lme4::glmerControl(optimizer="bobyqa"))
  r <- d[d$correct==1 & is.finite(d$ReactionTime) &
           d$ReactionTime>=rt_min & d$ReactionTime<=rt_max,,drop=FALSE]
  if(nrow(r)<10) stop("Insufficient RT records after preregistered exclusions")
  rt <- lme4::lmer(log(ReactionTime)~Load+Delay+(1|participant),data=r)
  list(accuracy=accuracy,rt=rt,n_trials=nrow(d),n_rt=nrow(r),
       singular_accuracy=lme4::isSingular(accuracy),
       singular_rt=lme4::isSingular(rt))
}
cli <- commandArgs(trailingOnly=TRUE)
if(sys.nframe()==0L) {
  if(length(cli)!=1) stop("Usage: Rscript R/analysis.R path/to/ds000030")
  fits <- fit_scap(load_scap(cli[[1]]))
  dir.create("results",showWarnings=FALSE)
  utils::write.csv(as.data.frame(summary(fits$rt)$coefficients),
                   "results/rt_coefficients.csv")
  utils::write.csv(as.data.frame(summary(fits$accuracy)$coefficients),
                   "results/accuracy_coefficients.csv")
  message("Check convergence, singularity and trial exclusion; no diagnosis or imaging inference.")
}
