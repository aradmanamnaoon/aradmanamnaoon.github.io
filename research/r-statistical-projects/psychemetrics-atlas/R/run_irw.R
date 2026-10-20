# Execute exploratory SAPA structure from the open IRW v71 long-response CSV.
# Rscript R/run_irw.R [path/to/sapa_personality_irw_v71.csv]
# The source is a transformed representation of the Harvard Dataverse SAPA survey.
needed <- c("data.table", "psych", "GPArotation", "digest")
absent <- needed[!vapply(needed, requireNamespace, logical(1), quietly=TRUE)]
if(length(absent)) stop("Required packages: ", paste(absent, collapse=", "))
source("R/analysis.R")
args <- commandArgs(trailingOnly=TRUE)
source_url <- "https://redivis.com/api/v1/tables/datapages.item_response_warehouse%3Av71_0.sapa_personality/rows?format=csv"
dir.create("data/raw",recursive=TRUE,showWarnings=FALSE)
input <- if(length(args)==1L) args[[1]] else "data/raw/sapa_personality_irw_v71.csv"
if(!file.exists(input)) {
  if(length(args)) stop("Input does not exist: ",input)
  utils::download.file(source_url,input,mode="wb",quiet=FALSE)
}
expected <- "d09b2956d28c0f99222330fdedbb8169256b15fc06195c5a6fce40295c06f292"
actual <- digest::digest(file=input,algo="sha256")
if(!identical(tolower(actual),expected)) stop("Version/hash mismatch: inspect source before proceeding")
d <- data.table::fread(input,select=c("id","item","resp"),showProgress=FALSE)
if(!identical(names(d),c("resp","item","id")) && !setequal(names(d),c("resp","item","id")))
  stop("Unexpected source data columns")
if(anyNA(d[,c("id","item","resp")]) || any(!d$resp %in% 1:6))
  stop("Invalid respondent, item or response values")
freq <- d[,.(n=.N),by=item][order(-n)]
items <- head(freq$item,12L)
x <- d[item %in% items]
if(anyDuplicated(x[,paste(id,item,sep="::")])) stop("Duplicate respondent/item records")
wide <- data.table::dcast(x,id~item,value.var="resp",fill=NA_real_)
res <- analyse_sapa(as.data.frame(wide),items,factors=3L)
overlap <- min(res$pairwise_n[upper.tri(res$pairwise_n)])
dir.create("results",recursive=TRUE,showWarnings=FALSE)
utils::write.csv(res$coverage,"results/item_coverage.csv",row.names=FALSE)
utils::write.csv(res$pairwise_n,"results/item_pair_overlap.csv")
utils::write.csv(unclass(res$exploratory_factor_fit$loadings),"results/exploratory_loadings.csv")
utils::write.csv(data.frame(rows=nrow(d),respondents=data.table::uniqueN(d$id),
  source_items=data.table::uniqueN(d$item),selected_items=length(items),
  min_pairwise_overlap=overlap,source_sha256=actual),
  "results/observed_input_summary.csv",row.names=FALSE)
writeLines(c(R.version.string,capture.output(utils::sessionInfo())),"results/session_info.txt")
message("Exploratory EFA completed; no validated personality factors or traits are claimed")
