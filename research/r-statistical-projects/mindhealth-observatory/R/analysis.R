# MindHealth Observatory — executable candidate, NOT empirically validated.
# Usage: Rscript R/analysis.R DEMO_J.XPT DPQ_J.XPT
required <- c("haven", "survey", "ggplot2")
missing <- required[!vapply(required, requireNamespace, logical(1), quietly=TRUE)]
if(length(missing)) stop("Install R packages: ", paste(missing, collapse=", "))
estimate <- function(demographics, depression) {
  items <- sprintf("DPQ0%d0", 1:9)
  required_demo <- c("SEQN", "RIDAGEYR", "RIAGENDR", "INDFMPIR", "WTMEC2YR", "SDMVSTRA", "SDMVPSU")
  if(!all(required_demo %in% names(demographics))) stop("NHANES DEMO schema mismatch")
  if(!all(c("SEQN",items) %in% names(depression))) stop("NHANES DPQ schema mismatch")
  if(anyDuplicated(demographics$SEQN) || anyDuplicated(depression$SEQN)) stop("Duplicate SEQN")
  dat <- merge(demographics[,required_demo], depression[,c("SEQN",items)], by="SEQN")
  mat <- as.matrix(dat[,items])
  eligible <- dat$RIDAGEYR >= 18 & is.finite(dat$WTMEC2YR) &
    dat$WTMEC2YR > 0 & complete.cases(dat[,c("SDMVSTRA","SDMVPSU")])
  valid <- apply(mat,1, function(row) all(!is.na(row) & row %in% 0:3))
  dat <- dat[which(eligible & valid),,drop=FALSE]
  if(nrow(dat)<10) stop("Insufficient eligible complete PHQ respondents")
  dat$phq_score <- rowSums(dat[,items])
  dat$phq10 <- as.numeric(dat$phq_score >= 10)
  design <- survey::svydesign(ids=~SDMVPSU,strata=~SDMVSTRA,weights=~WTMEC2YR,
                              nest=TRUE,data=dat)
  overall <- survey::svymean(~phq10,design,na.rm=TRUE)
  by_sex <- survey::svyby(~phq10,~RIAGENDR,design,survey::svymean,
                          na.rm=TRUE,keep.names=FALSE)
  model <- survey::svyglm(phq10 ~ RIDAGEYR + factor(RIAGENDR) + INDFMPIR,
                           design=design,family=quasibinomial())
  list(n=nrow(dat),weighted_prevalence=overall,
       by_sex=by_sex,model=model,missing_pir=sum(is.na(dat$INDFMPIR)))
}
cli <- commandArgs(trailingOnly=TRUE)
if(sys.nframe()==0L) {
  if(length(cli)!=2) stop("Usage: Rscript R/analysis.R DEMO_J.XPT DPQ_J.XPT")
  result <- estimate(haven::read_xpt(cli[[1]]),haven::read_xpt(cli[[2]]))
  dir.create("results",showWarnings=FALSE)
  utils::write.csv(data.frame(n=result$n,prevalence=coef(result$weighted_prevalence),
     se=survey::SE(result$weighted_prevalence)), "results/summary.csv", row.names=FALSE)
  utils::write.csv(as.data.frame(result$by_sex), "results/by_sex.csv", row.names=FALSE)
  utils::write.csv(summary(result$model)$coefficients,"results/model.csv")
  message("Outputs created for REVIEW; inspect survey design and analytic exclusions.")
}
