# SchoolMind Global — OECD PISA 2022 Fay-BRR descriptive estimator.
# Usage: Rscript R/analysis.R pisa2022_student.csv
if(!requireNamespace("survey",quietly=TRUE)) stop("Install survey")
estimate_belonging <- function(d) {
  replicates <- paste0("W_FSTURWT",seq_len(80))
  needed <- c("CNT","BELONG","W_FSTUWT",replicates)
  if(!all(needed %in% names(d))) stop("Missing PISA country, BELONG or 80 replicate weights")
  d <- d[!is.na(d$CNT) & !is.na(d$BELONG) &
            is.finite(d$W_FSTUWT) & d$W_FSTUWT>0,,drop=FALSE]
  if(nrow(d)==0) stop("No complete BELONG observations")
  for(col in replicates) {
    if(any(!is.finite(d[[col]]) | d[[col]]<0))
      stop("Invalid replicate weight: ",col)
  }
  design <- survey::svrepdesign(data=d,weights=~W_FSTUWT,
      repweights=d[,replicates,drop=FALSE],type="Fay",rho=0.5,
      combined.weights=TRUE)
  out <- survey::svyby(~BELONG,~CNT,design,survey::svymean,
       na.rm=TRUE,keep.names=FALSE,ci=TRUE)
  list(n=nrow(d),countries=out,design=design)
}
cli <- commandArgs(trailingOnly=TRUE)
if(sys.nframe()==0L) {
  if(length(cli)!=1) stop("Usage: Rscript R/analysis.R pisa2022_student.csv")
  d <- utils::read.csv(cli[[1]],check.names=FALSE)
  estimate <- estimate_belonging(d)
  dir.create("results",showWarnings=FALSE)
  utils::write.csv(estimate$countries,"results/economy_belonging.csv",row.names=FALSE)
  message("Requires verification against OECD Fay-BRR, scaling and participation notes.")
}
