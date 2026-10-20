library(survey)
args <- commandArgs(trailingOnly=TRUE)
root <- if(length(args)==1L) args[[1]] else 'data/derived/country_csv_gz'
if(!dir.exists(root)) stop('Country CSV inputs not found: ',root)
files <- sort(list.files(root,pattern='^[A-Z0-9]+[.]csv[.]gz$',full.names=TRUE))
rep_cols <- paste0('W_FSTURWT',1:80)
results <- list();flows <- list();errors <- list()
for(i in seq_along(files)) {
  f <- files[[i]]; economy <- sub('[.]csv[.]gz$','',basename(f))
  tryCatch({
    d <- utils::read.csv(gzfile(f),check.names=FALSE)
    if (!identical(names(d),c('CNT','BELONG','W_FSTUWT',rep_cols))) stop('Schema mismatch')
    raw_n <- nrow(d)
    eligible <- is.finite(d$BELONG) & is.finite(d$W_FSTUWT) & d$W_FSTUWT > 0 &
       rowSums(is.finite(as.matrix(d[,rep_cols])))==80L
    d <- d[eligible,]
    if(nrow(d)<50) stop('Too few complete observations')
    if(any(as.matrix(d[,rep_cols])<0)) stop('Negative replicate weights')
    design <- survey::svrepdesign(data=d,weights=~W_FSTUWT,
       repweights=as.matrix(d[,rep_cols]),type='Fay',rho=0.5,combined.weights=TRUE)
    a <- survey::svymean(~BELONG,design,na.rm=TRUE)
    ci <- stats::confint(a)
    results[[economy]] <- data.frame(CNT=economy,n=nrow(d),weighted_mean=unname(coef(a)),se=unname(SE(a)),ci_low=ci[[1]],ci_high=ci[[2]])
    flows[[economy]] <- data.frame(CNT=economy,raw_n=raw_n,complete_n=nrow(d),missing_n=raw_n-nrow(d))
  },error=function(e){errors[[economy]] <<- conditionMessage(e)})
  if(i%%20==0) cat('PROCESSED',i,'OF',length(files),'\n')
}
folder <- 'results'
dir.create(folder,recursive=TRUE,showWarnings=FALSE)
out<-do.call(rbind,results);rownames(out)<-NULL
f<-do.call(rbind,flows);rownames(f)<-NULL
utils::write.csv(out,file.path(folder,'belonging_by_economy.csv'),row.names=FALSE)
utils::write.csv(f,file.path(folder,'sample_flow.csv'),row.names=FALSE)
if(length(errors)) utils::write.csv(data.frame(CNT=names(errors),error=unlist(errors)),file.path(folder,'errors.csv'),row.names=FALSE)
cat('SUCCESS_COUNTRIES',nrow(out),'ERRORS',length(errors),'RAW_ROWS',sum(f$raw_n),'ANALYZED_ROWS',sum(f$complete_n),'\n')
writeLines(c(R.version.string,capture.output(utils::sessionInfo())), file.path(folder,'session_info.txt'))
print(out[out$CNT %in% c('DEU','SWE','FIN','USA','GBR'),])
