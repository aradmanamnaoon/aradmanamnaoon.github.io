# SAPA keyed-item coverage audit. No respondent-level data are committed.
# Usage: Rscript R/original_sapa_audit.R source.RData superKey696.csv ItemInfo696.csv results
if (!requireNamespace("ggplot2",quietly=TRUE)) stop("Install ggplot2")
scales <- c("IPIP50Agree","IPIP50Consc","IPIP50Extra","IPIP50Intel","IPIP50EmoSt")
labels <- c("Agreeableness","Conscientiousness","Extraversion","Intellect / openness","Emotional stability")
validate_key <- function(k) {
  stopifnot(!anyDuplicated(rownames(k)),all(scales %in% colnames(k)))
  for (s in scales) if (anyNA(k[[s]]) || !all(k[[s]] %in% -1:1) ||
    sum(k[[s]] != 0) != 10) stop(paste("Invalid keyed scale",s))
  TRUE
}
keyed <- function(x,weights) {
  x <- as.matrix(data.frame(lapply(x,function(z) as.numeric(as.character(z)))))
  if (any(!is.na(x) & !(x %in% 1:6))) stop("Unexpected response category")
  for (i in seq_along(weights)) if(weights[i]==-1) x[,i] <- 7-x[,i]
  x
}
audit_one <- function(dat,key,scale,label) {
  k <- key[[scale]]; names(k) <- rownames(key)
  signs <- k[k != 0]; items <- names(signs)
  if (!all(items %in% names(dat))) stop("Missing item columns")
  x <- keyed(dat[,items,drop=FALSE],signs)
  colnames(x) <- items
  n_observed <- rowSums(!is.na(x))
  overlaps <- crossprod(!is.na(x))
  ij <- which(upper.tri(overlaps),arr.ind=TRUE)
  cors <- cor(x,use="pairwise.complete.obs")
  pair <- data.frame(scale=scale,item_a=items[ij[,1]],item_b=items[ij[,2]],
        paired_n=as.integer(overlaps[ij]),keyed_pearson_r=as.numeric(cors[ij]))
  if(any(pair$paired_n < 30) || any(!is.finite(pair$keyed_pearson_r)))
    stop("Insufficient paired responses for descriptive correlations")
  eig <- eigen(cors,symmetric=TRUE)$values
  flow <- data.frame(scale=scale,label=label,original_n=nrow(dat),item_count=length(items),
      n_at_least_1=sum(n_observed>=1),n_at_least_3=sum(n_observed>=3),
      n_at_least_5=sum(n_observed>=5),n_at_least_8=sum(n_observed>=8),
      n_all_10=sum(n_observed==10),pair_min=min(pair$paired_n),
      pair_median=median(pair$paired_n),mean_keyed_r=mean(pair$keyed_pearson_r),
      fraction_positive_pairs=mean(pair$keyed_pearson_r>0),
      correlation_largest_eigen=max(eig),
      negative_eigenvalues=sum(eig<(-1e-6)))
  keys <- data.frame(scale=scale,item=items,sign=as.integer(signs),
                     nonmissing=as.integer(colSums(!is.na(x))))
  list(flow=flow,pairs=pair,keys=keys)
}
run_audit <- function(input,keyfile,infofile,out) {
  e <- new.env(parent=emptyenv()); objects <- load(input,envir=e)
  if(length(objects)!=1) stop("Expected one SAPA RData object")
  dat <- e[[objects[[1]]]]
  if(!is.data.frame(dat) || nrow(dat)<20000) stop("Unexpected original SAPA source")
  key <- read.csv(keyfile,row.names=1,check.names=FALSE)
  info <- read.csv(text=iconv(readLines(infofile,encoding="bytes",warn=FALSE),from="CP1252",to="UTF-8"),row.names=1,check.names=FALSE)
  validate_key(key)
  if(!setequal(rownames(key),rownames(info))) stop("Key and dictionary disagree")
  z <- Map(function(s,l) audit_one(dat,key,s,l),scales,labels)
  flow <- do.call(rbind,lapply(z,function(v)v$flow))
  pairs <- do.call(rbind,lapply(z,function(v)v$pairs))
  keys <- do.call(rbind,lapply(z,function(v)v$keys))
  keys$original_item_text <- info[keys$item,"Item"]
  if(anyNA(keys$original_item_text)) stop("Unmapped item descriptions")
  dir.create(out,recursive=TRUE,showWarnings=FALSE)
  write.csv(flow,file.path(out,"original_sapa_keyed_coverage.csv"),row.names=FALSE)
  write.csv(pairs,file.path(out,"original_sapa_keyed_pairs.csv"),row.names=FALSE)
  write.csv(keys,file.path(out,"original_sapa_item_key_audit.csv"),row.names=FALSE)
  p <- ggplot2::ggplot(flow,ggplot2::aes(x=reorder(label,n_at_least_5),y=n_at_least_5)) +
    ggplot2::geom_col(fill="#7db4f0",width=.62) + ggplot2::coord_flip() +
    ggplot2::geom_text(ggplot2::aes(label=n_at_least_5),hjust=-.18,
                       color="#ededed",size=4) +
    ggplot2::scale_y_continuous(expand=ggplot2::expansion(mult=c(0,.24))) +
    ggplot2::labs(title="SAPA personality items: planned missingness",
       subtitle="Observed respondents with at least 5 of 10 keyed items per IPIP-50 scale",
       x=NULL,y="Respondents",caption="Original public SAPA · descriptive feasibility, not a reliability estimate") +
    ggplot2::theme_minimal(base_size=12) +
    ggplot2::theme(plot.background=ggplot2::element_rect(fill="#14181f",color=NA),
        panel.background=ggplot2::element_rect(fill="#14181f",color=NA),
        text=ggplot2::element_text(color="#ededed"),
        axis.text=ggplot2::element_text(color="#ededed"),
        panel.grid.major.y=ggplot2::element_blank(),
        panel.grid.minor=ggplot2::element_blank(),
        plot.subtitle=ggplot2::element_text(color="#a6b2c1"),
        plot.caption=ggplot2::element_text(color="#a6b2c1"))
  ggplot2::ggsave(file.path(out,"original_sapa_keyed_coverage.svg"),p,
                  width=10,height=5,units="in",device="svg")
  writeLines(c(paste("Rows:",nrow(dat),"Columns:",ncol(dat)),
               capture.output(sessionInfo())),
             file.path(out,"original_sapa_R_session.txt"))
  flow
}
if (sys.nframe()==0L) {
  a <- commandArgs(trailingOnly=TRUE)
  if(length(a)!=4) stop("Usage: Rscript R/original_sapa_audit.R original.RData superKey696.csv ItemInfo696.csv results")
  print(run_audit(a[1],a[2],a[3],a[4]),row.names=FALSE)
}

