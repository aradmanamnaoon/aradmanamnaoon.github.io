# Psychemetrics Atlas — preliminary exploratory EFA, NOT validated scale measurement.
# Usage: Rscript R/analysis.R responses.csv ITEM1 ITEM2 ITEM3 ...
if(!requireNamespace("psych",quietly=TRUE)) stop("Install psych")
analyse_sapa <- function(df, items, factors=3L) {
  if(length(items)<6L || anyDuplicated(items) || !all(items %in% names(df)))
    stop("Supply >=6 distinct valid item-column names")
  X <- as.data.frame(lapply(df[items],as.numeric))
  if(any(vapply(X,function(x) any(!is.na(x) & (x<1 | x>6)),logical(1))))
    stop("Item response outside expected 1..6 range; inspect codebook")
  coverage <- data.frame(item=items,nonmissing=vapply(X,function(x) sum(!is.na(x)),integer(1)))
  pair_n <- outer(seq_along(X), seq_along(X),
    Vectorize(function(i,j) sum(complete.cases(X[,c(i,j),drop=FALSE]))))
  rownames(pair_n) <- colnames(pair_n) <- items
  if(any(pair_n[upper.tri(pair_n)] < 30)) stop("Insufficient item coadministration")
  correlations <- psych::polychoric(X,correct=.5)
  if(min(eigen(correlations$rho,symmetric=TRUE)$values) < -1e-6)
    stop("Estimated polychoric matrix is not positive semidefinite")
  ef <- psych::fa(correlations$rho,nfactors=factors,fm="minres",
                  rotate="oblimin",n.obs=min(pair_n[upper.tri(pair_n)]))
  list(coverage=coverage,pairwise_n=pair_n,correlation=correlations$rho,
       exploratory_factor_fit=ef)
}
cli <- commandArgs(trailingOnly=TRUE)
if(sys.nframe()==0L) {
  if(length(cli)<7) stop("Usage: Rscript R/analysis.R responses.csv ITEM1 ... ITEM6")
  X <- utils::read.csv(cli[[1]],check.names=FALSE)
  model <- analyse_sapa(X,cli[-1])
  dir.create("results",showWarnings=FALSE)
  utils::write.csv(model$coverage,"results/item_coverage.csv",row.names=FALSE)
  utils::write.csv(model$pairwise_n,"results/item_pair_overlap.csv")
  utils::write.csv(unclass(model$exploratory_factor_fit$loadings),
                   "results/exploratory_loadings.csv")
  message("EFA is exploratory; verify scoring key, item overlap and factor rotation.")
}
