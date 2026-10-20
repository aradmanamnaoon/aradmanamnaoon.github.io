# ReplicationScope — Many Labs 2 processed effect summary, NOT raw-trial replication.
# Usage: Rscript R/analysis.R Data_Figure_NOweird.csv
if(!requireNamespace("metafor",quietly=TRUE)) stop("Install metafor")
analyse_effects <- function(d,minimum_labs=3L) {
  fields <- c("analysis.name","study.source","ESCI.r","ESCI.var.r")
  if(!all(fields %in% names(d))) stop("Missing Many Labs 2 processed effect fields")
  d <- d[is.finite(d$ESCI.r) & abs(d$ESCI.r)<1 &
           is.finite(d$ESCI.var.r) & d$ESCI.var.r>0 &
           !is.na(d$analysis.name) & !is.na(d$study.source),]
  d$key <- paste(d$analysis.name,d$study.source,sep="::")
  if(anyDuplicated(d$key)) stop("Nonindependent or repeated lab-by-contrast estimate; inspect mapping")
  d$z <- atanh(d$ESCI.r)
  d$vz <- d$ESCI.var.r/(1-d$ESCI.r^2)^2
  groups <- split(d,d$analysis.name)
  fits <- lapply(groups,function(g) {
    if(nrow(g)<minimum_labs) return(NULL)
    fit <- metafor::rma.uni(yi=g$z,vi=g$vz,method="REML")
    ci <- stats::confint(fit)
    pi <- tryCatch(stats::predict(fit), error=function(e) NULL)
    data.frame(analysis=g$analysis.name[[1]],labs=nrow(g),
       estimate_r=tanh(as.numeric(fit$b)),ci_low_r=tanh(fit$ci.lb),
       ci_high_r=tanh(fit$ci.ub),tau2=fit$tau2,I2=fit$I2,
       prediction_low_r=if(is.null(pi)) NA_real_ else tanh(pi$pi.lb),
       prediction_high_r=if(is.null(pi)) NA_real_ else tanh(pi$pi.ub))
  })
  out <- do.call(rbind,Filter(Negate(is.null),fits))
  if(is.null(out)) stop("No contrasts with enough laboratory estimates")
  out
}
cli <- commandArgs(trailingOnly=TRUE)
if(sys.nframe()==0L) {
  if(length(cli)!=1) stop("Usage: Rscript R/analysis.R Data_Figure_NOweird.csv")
  results <- analyse_effects(utils::read.csv(cli[[1]],check.names=FALSE))
  dir.create("results",showWarnings=FALSE)
  utils::write.csv(results,"results/within_contrast_meta.csv",row.names=FALSE)
  message("Verify effect direction, filtering and ESCI variance meaning before interpretation.")
}
