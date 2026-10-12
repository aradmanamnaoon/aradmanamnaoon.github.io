#!/usr/bin/env Rscript
# SPSS PSYCHOLOGICAL DATA — full reproducible exploratory audit, diagnostics, and exports
# Input:  "raw.sav" (or pass its path as the first command-line argument).
# Run:    Rscript full_reproducible_analysis.R "raw.sav" "r_results"
# R >=4.2; no variables are anonymized or silently dropped.
# IMPORTANT: A=13, EM=33, H=15, D=15 items. No questionnaire scoring manuals provided.
# IMPORTANT: Nearly all records duplicate another complete questionnaire response profile.
# Consequently, p-values from group-comparison models are NOT valid inferential evidence.

options(stringsAsFactors = FALSE)
args <- commandArgs(trailingOnly = TRUE)
input <- if (length(args) >= 1) args[1] else "raw.sav"
out_dir <- if (length(args) >= 2) args[2] else "r_results"
if (!file.exists(input)) stop("SPSS input file not found: ", input)
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
packages <- c("haven", "ggplot2", "sandwich", "lmtest", "car")
missing_packages <- packages[!vapply(packages, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages)) {
  message("Install with: install.packages(c(", paste(sprintf('"%s"', missing_packages), collapse=", "), "))")
  stop("Missing required R packages. Install them once, then run again.")
}
set.seed(20261012)

# 1. Read the SAV; retain exact short variable names, data codes and value labels.
spss <- haven::read_sav(input, user_na = TRUE)
# Canonicalize names while preserving the original value and variable labels.
# Original file uses lower/mixed-case field names and four longer English names.
names(spss) <- toupper(names(spss))
canonical_aliases <- c(
  EDUCATION   = "EDUCATIO",
  EVALUATION  = "EVALUATI",
  SOCIALSKILLS = "SOCIALSK",
  EMOTIONAP   = "EMOTIONA"
)
for (old_name in names(canonical_aliases)) {
  names(spss)[names(spss) == old_name] <- canonical_aliases[[old_name]]
}
if (anyDuplicated(names(spss))) {
  stop("Variable name collision after SPSS name normalization")
}
raw <- as.data.frame(lapply(spss, as.numeric), check.names = FALSE)
names(raw) <- names(spss)
A <- paste0("A", 1:13)
EM <- paste0("EM", 1:33)
H <- paste0("H", 1:15)
D <- paste0("D", 1:15)
ITEMS <- c(A, EM, H, D)
SCORES <- c("TOTALA", "TOTALEM", "OPTIMISM", "EVALUATI", "SOCIALSK", "EMOTIONA", "MZQ")
required <- c("GROUP", "NUMBER", "AGE", "AGEE", "MARRIAGE", "EDUCATIO", ITEMS, SCORES)
missing_required <- setdiff(required, names(raw))
if (length(missing_required)) {
  stop("Required SPSS variables missing after normalization: ",
       paste(missing_required, collapse = ", "))
}

stopifnot(nrow(raw) == 240L, ncol(raw) == 89L, all(raw$GROUP %in% c(1,2)))

# 2. Labels, category validation, IDs, exact questionnaire-profile duplication.
data <- raw
data$CASE_ID <- seq_len(nrow(data))  # always unique; NUMBER repeats between groups

data$GROUP_LABEL <- factor(data$GROUP, levels=c(1,2), labels=c("fire","non"))
data$AGE_LABEL <- factor(data$AGE, levels=1:4,
  labels=c("Under 30","30-39","40-49","50-59"), ordered=TRUE)
data$MARRIAGE_LABEL <- factor(data$MARRIAGE, levels=1:3,
  labels=c("single","married","divorced"))
data$EDUCATION_LABEL <- factor(data$EDUCATIO, levels=1:5,
  labels=c("Diploma","Associate","Bachelor","Master","Doctorate"), ordered=TRUE)
data$EDUC_BAND <- factor(ifelse(data$EDUCATIO >= 4, "Postgraduate",
  c("Diploma","Associate","Bachelor")[pmin(data$EDUCATIO,3)]),
  levels=c("Bachelor","Associate","Diploma","Postgraduate"))
profile_key <- do.call(paste, c(as.list(raw[,ITEMS,drop=FALSE]), sep="|"))
data$QUESTIONNAIRE_PROFILE_ID <- match(profile_key,unique(profile_key))
data$PROFILE_REPEAT_COUNT <- as.integer(table(data$QUESTIONNAIRE_PROFILE_ID)[
  as.character(data$QUESTIONNAIRE_PROFILE_ID)])
data$PROFILE_IS_REPEATED <- as.integer(data$PROFILE_REPEAT_COUNT > 1)
for (i in 1:15) {
  col <- D[i]
  invalid <- !is.na(raw[[col]]) & !(raw[[col]] %in% c(1,2))
  data[[col]][invalid] <- NA_real_   # do NOT overwrite raw saved separately
}
data$D_INVALID_COUNT <- rowSums(sapply(D, function(n) {
  !is.na(raw[[n]]) & !(raw[[n]] %in% c(1,2))
}))
data$FLAG_ANY_D_INVALID <- as.integer(data$D_INVALID_COUNT > 0)

for (z in list(c("A","TOTALA"), c("EM","TOTALEM"), c("H","MZQ"))) {
  prefix <- z[1]; total <- z[2]
  items <- switch(prefix, A=A, EM=EM, H=H)
  raw_sum <- rowSums(raw[,items,drop=FALSE],na.rm=FALSE)
  data[[paste0(prefix,"_ITEM_SUM_RAW")]] <- raw_sum
  data[[paste0("FLAG_",total,"_DISAGREE")]] <- as.integer(raw_sum != raw[[total]])
  data[[paste0(total,"_MINUS_RAW_SUM")]] <- raw[[total]] - raw_sum
}
# Original scores are preserved, but are NOT labeled 'corrected'.
write.csv(raw,file.path(out_dir,"raw_numeric.csv"),row.names=FALSE,fileEncoding="UTF-8")
write.csv(data,file.path(out_dir,"cleaned_powerbi.csv"),row.names=FALSE,na="",fileEncoding="UTF-8")

# 3. Variable dictionary: exact Persian SPSS labels and response-category mappings.
classification <- function(n) {
 if (n == "NUMBER") return("identifier (not globally unique)")
 if (n == "GROUP") return("nominal/binary")
 if (n %in% c("AGE","EDUCATIO")) return("ordinal")
 if (n == "MARRIAGE") return("nominal")
 if (n == "AGEE" || n %in% SCORES) return("scale")
 if (n %in% D) return("binary response item")
 if (n %in% c(A,EM,H)) return("ordinal Likert item")
 return("unspecified")
}
plain <- c(GROUP="Group (fire versus non; semantics unknown)",
 NUMBER="Original case number; not unique across groups",AGE="Age band",
 MARRIAGE="Marital status",AGEE="Exact age in years",EDUCATIO="Education",
 TOTALA="Ambiguity tolerance score (stored)",
 TOTALEM="Emotional self-regulation score (stored)",
 OPTIMISM="Optimism subscale (stored)",EVALUATI="Emotional appraisal (stored)",
 SOCIALSK="Social skills (stored)",EMOTIONA="Use of emotions (stored)",
 MZQ="Mentalization score (stored)")
variable_dictionary <- do.call(rbind,lapply(names(raw),function(n) {
  lab <- attr(spss[[n]],"label")
  codes <- attr(spss[[n]],"labels")
  codes_text <- if(is.null(codes)) "" else paste(paste0(as.numeric(codes),"=",names(codes)),collapse="; ")
  English <- if(n %in% names(plain)) plain[n] else if(n %in% A) "Ambiguity-tolerance questionnaire item" else if(n %in% EM) "Emotional-self-regulation questionnaire item" else if(n %in% H) "Mentalization questionnaire item" else "Death-anxiety questionnaire item"
  issues <- c()
  if(n %in% D && any(!raw[[n]] %in% c(1,2))) issues <- c(issues,"Unlabelled invalid response codes")
  if(n %in% SCORES) issues <- c(issues,"Stored score; original scoring rules not supplied")
  if(n %in% c(A,EM,H,D)) issues <- c(issues,"Actual individual question text not contained in SAV labels")
  if(n == "NUMBER") issues <- c(issues,"Repeated case numbers")
  data.frame(variable=n,spss_label_persian=if(length(lab)) lab else "",
   plain_english=as.character(English),substantive_type=classification(n),
   value_labels=codes_text,distinct_values=length(unique(raw[[n]][!is.na(raw[[n]])])),
   missing_system=sum(is.na(raw[[n]])), min=min(raw[[n]],na.rm=TRUE),
   max=max(raw[[n]],na.rm=TRUE),issue=paste(issues,collapse="; "))
}))
write.csv(variable_dictionary,file.path(out_dir,"variable_dictionary.csv"),row.names=FALSE,fileEncoding="UTF-8")

# 4. Full audit: category violations, exact profile matches and 120+120 row structure.
stopifnot(sum(raw$GROUP==1)==120, sum(raw$GROUP==2)==120)
fire <- raw[raw$GROUP==1,,drop=FALSE]
non  <- raw[raw$GROUP==2,,drop=FALSE]
stopifnot(nrow(fire)==nrow(non))
pair_audit <- data.frame(row_in_each_group=1:120,
 fire_number=fire$NUMBER,non_number=non$NUMBER,
 identical_76_items=vapply(1:120,function(i) identical(unname(unlist(fire[i,ITEMS])),unname(unlist(non[i,ITEMS]))), logical(1)),
 identical_AGE=fire$AGE==non$AGE,
 identical_EDUCATIO=fire$EDUCATIO==non$EDUCATIO,
 identical_MARRIAGE=fire$MARRIAGE==non$MARRIAGE)
for (s in SCORES) pair_audit[[paste0(s,"_fire_minus_non")]] <- fire[[s]]-non[[s]]
write.csv(pair_audit,file.path(out_dir,"cross_group_pair_audit.csv"),row.names=FALSE)
audit <- data.frame(metric=c("rows","raw_columns","groups_fire","groups_non",
 "system_missing_cells","entire_row_duplicates_including_group_and_number",
 "unique_questionnaire_profiles","rows_belonging_to_repeated_profiles",
 "identical_76_item_pairs_in_aligned_group_rows","unique_original_case_numbers",
 "out_of_range_D_cells","rows_with_bad_D_values","TOTALA_vs_raw_sum_disagreements",
 "TOTALEM_vs_raw_sum_disagreements","MZQ_vs_raw_sum_disagreements"),
 value=c(nrow(raw),ncol(raw),sum(raw$GROUP==1),sum(raw$GROUP==2),
 sum(is.na(raw)),sum(duplicated(raw)),length(unique(profile_key)),sum(data$PROFILE_IS_REPEATED),
 sum(pair_audit$identical_76_items),length(unique(raw$NUMBER)),sum(data$D_INVALID_COUNT),
 sum(data$FLAG_ANY_D_INVALID),sum(data$FLAG_TOTALA_DISAGREE),
 sum(data$FLAG_TOTALEM_DISAGREE),sum(data$FLAG_MZQ_DISAGREE)))
write.csv(audit,file.path(out_dir,"audit_summary.csv"),row.names=FALSE)
write.csv(data[,c("CASE_ID","GROUP","NUMBER","QUESTIONNAIRE_PROFILE_ID",
 "PROFILE_REPEAT_COUNT","PROFILE_IS_REPEATED","FLAG_ANY_D_INVALID","D_INVALID_COUNT",
 "FLAG_TOTALA_DISAGREE","FLAG_TOTALEM_DISAGREE","FLAG_MZQ_DISAGREE")],
 file.path(out_dir,"case_level_quality_flags.csv"),row.names=FALSE)

# 5. Frequencies (coded respondent answers; not seven competing tests per item).
frequencies <- do.call(rbind,lapply(c("GROUP","AGE","MARRIAGE","EDUCATIO",ITEMS), function(n) {
 vals <- sort(unique(raw[[n]])); t <- table(raw[[n]])
 data.frame(variable=n,code=as.numeric(names(t)),n=as.integer(t),pct=100*as.integer(t)/nrow(raw))
}))
write.csv(frequencies,file.path(out_dir,"frequencies_all_categorical_items.csv"),row.names=FALSE)

# 6. Score summary with normality checks, skewness, outlier counts.
skew <- function(v) {
 v <- v[is.finite(v)]; n <- length(v); if(n<3||sd(v)==0) return(NA_real_)
 n/((n-1)*(n-2))*sum(((v-mean(v))/sd(v))^3)
}
desc <- function(v) {
 q <- quantile(v,c(.25,.75),na.rm=TRUE); b <- 1.5*(q[2]-q[1]);
 data.frame(n=sum(!is.na(v)),mean=mean(v,na.rm=TRUE),sd=sd(v,na.rm=TRUE),
 median=median(v,na.rm=TRUE),min=min(v,na.rm=TRUE),max=max(v,na.rm=TRUE),
 skewness=skew(v),iqr_outliers=sum(v<q[1]-b|v>q[2]+b,na.rm=TRUE),
 shapiro_p=if(length(v)>=3 && length(v)<=5000) shapiro.test(v)$p.value else NA_real_)
}
score_descriptives <- do.call(rbind,lapply(SCORES,function(s) {
 do.call(rbind,lapply(c("all","fire","non"),function(k) {
 v <- if(k=="all") raw[[s]] else raw[raw$GROUP==if(k=="fire") 1 else 2,s]
 data.frame(score=s,group=k,desc(v))
 }))
}))
write.csv(score_descriptives,file.path(out_dir,"score_descriptives.csv"),row.names=FALSE)
descriptive_all <- do.call(rbind,lapply(names(raw),function(s) {
 data.frame(variable=s,desc(raw[[s]]))
}))
write.csv(descriptive_all,file.path(out_dir,"descriptive_all_variables.csv"),row.names=FALSE)

# 7. Internal consistency on RAW item coding only (not validated scoring).
cronbach_alpha <- function(x) {
 x <- as.matrix(x); k <- ncol(x); total <- rowSums(x)
 if(k<=1 || var(total)==0) return(NA_real_)
 k/(k-1)*(1-sum(apply(x,2,var))/var(total))
}
alpha_rows <- list(); item_rows <- list()
for (name in c("A","EM","H")) {
 cols <- switch(name,A=A,EM=EM,H=H); x <- raw[,cols,drop=FALSE]
 bs <- replicate(400,cronbach_alpha(x[sample(nrow(x),replace=TRUE),,drop=FALSE]))
 ci <- quantile(bs,c(.025,.975),na.rm=TRUE)
 alpha_rows[[name]] <- data.frame(construct=name,n_items=ncol(x),alpha_raw=cronbach_alpha(x),
  ci_low=ci[1],ci_high=ci[2],note="Raw coding only; unknown reverse-key directions; repeated records")
 for (s in cols) item_rows[[s]] <- data.frame(construct=name,item=s,
  corrected_item_total_r=cor(raw[[s]],rowSums(x)-raw[[s]]),
  alpha_if_deleted=cronbach_alpha(x[,setdiff(cols,s),drop=FALSE]))
}
write.csv(do.call(rbind,alpha_rows),file.path(out_dir,"reliability_raw_provisional.csv"),row.names=FALSE)
write.csv(do.call(rbind,item_rows),file.path(out_dir,"item_reliability_diagnostics.csv"),row.names=FALSE)

# 8. Diagnostic independent-sample contrasts: calculation shown despite broken independence.
hedges_g <- function(x,y) {
 nx<-length(x); ny<-length(y)
 sp <- sqrt(((nx-1)*var(x)+(ny-1)*var(y))/(nx+ny-2))
 (mean(x)-mean(y))/sp*(1-3/(4*(nx+ny)-9))
}
welch_row <- function(s) {
 x <- data[data$GROUP==1,s]; y <- data[data$GROUP==2,s]
 tt <- t.test(x,y,var.equal=FALSE)
 # 600-iteration bootstrap CI for standardized difference is descriptive only.
 bs <- replicate(600,hedges_g(sample(x,replace=TRUE),sample(y,replace=TRUE)))
 u <- suppressWarnings(wilcox.test(x,y,exact=FALSE))
 # rank-biserial correlation uses U statistic, not W directly; ties use average ranks.
 nx <- length(x);ny <- length(y)
 ranks <- rank(c(x,y),ties.method="average")
 U <- sum(ranks[seq_along(x)]) - nx*(nx+1)/2
 data.frame(score=s,fire_mean=mean(x),non_mean=mean(y),
  mean_difference_fire_minus_non=mean(x)-mean(y),
  welch_t=unname(tt$statistic),welch_df=unname(tt$parameter),welch_p=tt$p.value,
  diff_ci_low=tt$conf.int[1],diff_ci_high=tt$conf.int[2],hedges_g=hedges_g(x,y),
  g_boot_ci_low=quantile(bs,.025),g_boot_ci_high=quantile(bs,.975),
  brown_forsythe_p=car::leveneTest(c(x,y), factor(rep(c("fire","non"),c(nx,ny))),center=median)[1,"Pr(>F)"],
  shapiro_fire_p=shapiro.test(x)$p.value,shapiro_non_p=shapiro.test(y)$p.value,
  mann_whitney_p=u$p.value,rank_biserial=(2*U/(nx*ny)-1))
}
contrasts <- do.call(rbind,lapply(c(SCORES,"A_ITEM_SUM_RAW","EM_ITEM_SUM_RAW","H_ITEM_SUM_RAW"),welch_row))
contrasts$welch_BH_q <- NA_real_
idx <- which(contrasts$score %in% SCORES)
contrasts$welch_BH_q[idx] <- p.adjust(contrasts$welch_p[idx],"BH")
contrasts$interpretation <- "DIAGNOSTIC ONLY; extreme overlap/duplication breaks independent-case inference"
write.csv(contrasts,file.path(out_dir,"group_differences_unreliable_diagnostic.csv"),row.names=FALSE)

# 9. Group-demographic association diagnostics (independence is violated).
demo_tests <- do.call(rbind,lapply(c("AGE","MARRIAGE","EDUCATIO"),function(s){
 tab <- table(raw$GROUP,raw[[s]])
 chi <- suppressWarnings(chisq.test(tab,correct=FALSE))
 n <- sum(tab);v <- sqrt(as.numeric(chi$statistic)/(n*min(dim(tab)-1)))
 p <- if(any(chi$expected<5)) suppressWarnings(chisq.test(tab,simulate.p.value=TRUE,B=4999)$p.value) else chi$p.value
 data.frame(variable=s,chi2=unname(chi$statistic),p=p,dof=unname(chi$parameter),
 cramers_v=v,min_expected=min(chi$expected),p_method=if(any(chi$expected<5)) "permutation under independent rows" else "asymptotic chi-square")
}))
write.csv(demo_tests,file.path(out_dir,"demographic_group_associations_diagnostic.csv"),row.names=FALSE)

# 10. Exploratory correlations with both 240 rows and 1 row per unique 76-item pattern.
# Neither automatically recovers true independent respondents; unique-case reduction is sensitivity only.
cor_rows <- list()
for (sample_name in c("full_240","unique_profiles")) {
 ix <- if (sample_name=="full_240") seq_len(nrow(data)) else !duplicated(data$QUESTIONNAIRE_PROFILE_ID)
 sub <- data[ix,,drop=FALSE]
 pairs <- combn(SCORES,2,simplify=FALSE)
 for (k in seq_along(pairs)) {
  pair <- pairs[[k]];x<-sub[[pair[1]]];y<-sub[[pair[2]]]
  rho <- suppressWarnings(cor.test(x,y,method="spearman",exact=FALSE))
  pearson <- cor.test(x,y,method="pearson")
  # Fisher transform interval for Pearson r, bootstrap for Spearman rho.
  n<-length(x);z<-atanh(unname(pearson$estimate));ci<-tanh(z+c(-1,1)*qnorm(.975)/sqrt(n-3))
  boot <- replicate(300,{j<-sample.int(n,n,replace=TRUE);cor(x[j],y[j],method="spearman")})
  cor_rows[[paste0(sample_name,"_",k)]] <- data.frame(sample=sample_name,x=pair[1],y=pair[2],n=n,
   spearman_rho=unname(rho$estimate),spearman_p=rho$p.value,
   spearman_ci_low=quantile(boot,.025),spearman_ci_high=quantile(boot,.975),
   pearson_r=unname(pearson$estimate),pearson_p=pearson$p.value,
   pearson_fisher_ci_low=ci[1],pearson_fisher_ci_high=ci[2])
 }
}
correlations <- do.call(rbind,cor_rows)
correlations$spearman_BH_q <- ave(correlations$spearman_p,correlations$sample,
 FUN=function(p) p.adjust(p,"BH"))
write.csv(correlations,file.path(out_dir,"score_correlations_exploratory.csv"),row.names=FALSE)

# 11. HC3 OLS regressions for education/marriage/age-adjusted DESCRIPTIVE diagnostics.
model_results <- list(); diagnostics <- list()
for (s in SCORES) {
 dd <- data; dd$FIRE <- as.integer(dd$GROUP==1)
 dd$MARRIAGE_F <- as.integer(dd$MARRIAGE==2)
 fit <- lm(reformulate(c("FIRE","AGEE","MARRIAGE_F","EDUC_BAND"),response=s),data=dd)
 vv <- sandwich::vcovHC(fit,type="HC3"); cc <- coef(fit); ss <- sqrt(diag(vv));
 residual_p <- shapiro.test(resid(fit))$p.value
 bp_p <- lmtest::bptest(fit)$p.value
 vif_obj <- car::vif(fit)
 max_vif <- if(is.matrix(vif_obj)) max(vif_obj[,"GVIF"]^(1/(2*vif_obj[,"Df"]))) else max(vif_obj)
 diagnostics[[s]] <- data.frame(score=s,n=nobs(fit),r2=summary(fit)$r.squared,
  adjusted_r2=summary(fit)$adj.r.squared,AIC=AIC(fit),BIC=BIC(fit),
  residual_shapiro_p=residual_p,breusch_pagan_p=bp_p,max_vif=max_vif)
 for (term in c("FIRE","AGEE","MARRIAGE_F")) {
  val <- cc[term];se <- ss[term];p <- 2*pnorm(-abs(val/se))
  model_results[[paste(s,term)]] <- data.frame(score=s,term=term,coef=unname(val),
   se_HC3=unname(se),ci_low=unname(val-1.96*se),ci_high=unname(val+1.96*se),
   p=unname(p),r2=summary(fit)$r.squared,adjusted_r2=summary(fit)$adj.r.squared,
   AIC=AIC(fit),BIC=BIC(fit),residual_shapiro_p=residual_p,
   breusch_pagan_p=bp_p,max_vif=max_vif)
 }
}
models <- do.call(rbind,model_results)
models$group_term_BH_q <- NA_real_
sel <- models$term == "FIRE";models$group_term_BH_q[sel] <- p.adjust(models$p[sel],method="BH")
models$interpretation <- "Diagnostic only: robust SE does not cure replicated cases"
write.csv(models,file.path(out_dir,"adjusted_regressions_unreliable_diagnostic.csv"),row.names=FALSE)
write.csv(do.call(rbind,diagnostics),file.path(out_dir,"model_diagnostics.csv"),row.names=FALSE)

# 12. Reproducible figures: all titles explicitly warn against inferential use.
p <- ggplot2::ggplot(data,ggplot2::aes(x=GROUP_LABEL,y=TOTALA,fill=GROUP_LABEL))+
 ggplot2::geom_boxplot(width=.55,alpha=.65,outlier.size=1)+
 ggplot2::labs(title="Stored ambiguity-tolerance score by dataset group (UNVERIFIED)",
 subtitle="119/120 aligned pairs have identical original questionnaire responses",
 x="SPSS group code",y="Stored TOTALA score")+ggplot2::theme_minimal()+
 ggplot2::theme(legend.position="none")
ggplot2::ggsave(file.path(out_dir,"stored_TOTALA_group.png"),p,width=8,height=5,dpi=180)
p <- ggplot2::ggplot(data,ggplot2::aes(x=GROUP_LABEL,y=A_ITEM_SUM_RAW,fill=GROUP_LABEL))+
 ggplot2::geom_boxplot(width=.55,alpha=.65,outlier.size=1)+
 ggplot2::labs(title="Simple arithmetic sum of A1–A13 (NOT a validated scale score)",
 x="SPSS group code",y="Unreversed/raw item sum")+ggplot2::theme_minimal()+
 ggplot2::theme(legend.position="none")
ggplot2::ggsave(file.path(out_dir,"raw_A_item_sum_group.png"),p,width=8,height=5,dpi=180)
m <- cor(data[,SCORES],method="spearman",use="pairwise.complete.obs")
cor_plot <- as.data.frame(as.table(m));names(cor_plot) <- c("Var1","Var2","rho")
p <- ggplot2::ggplot(cor_plot,ggplot2::aes(x=Var1,y=Var2,fill=rho))+
 ggplot2::geom_tile(color="white")+
 ggplot2::geom_text(ggplot2::aes(label=sprintf("%.2f",rho)),size=3)+
 ggplot2::scale_fill_gradient2(low="#2563eb",mid="#ffffff",high="#dc2626",midpoint=0,limits=c(-1,1))+
 ggplot2::labs(title="Exploratory score correlations — repeated records present",x="",y="")+
 ggplot2::theme_minimal()+ggplot2::theme(axis.text.x=ggplot2::element_text(angle=45,hjust=1))
ggplot2::ggsave(file.path(out_dir,"score_correlation_heatmap.png"),p,width=9,height=7,dpi=180)
plot_profiles <- as.data.frame(table(data$PROFILE_REPEAT_COUNT))
names(plot_profiles) <- c("repeats","num_rows")
p <- ggplot2::ggplot(plot_profiles,ggplot2::aes(x=repeats,y=num_rows))+
 ggplot2::geom_col(fill="#475569")+
 ggplot2::labs(title="How many rows share an identical 76-item questionnaire profile?",
 x="Times a profile repeats",y="Rows associated with repeat count")+ggplot2::theme_minimal()
ggplot2::ggsave(file.path(out_dir,"questionnaire_duplication.png"),p,width=8,height=5,dpi=180)

# 13. Bilingual Power BI case export — readable English + Persian dimension captions.
# This file retains case-level rows; protect it and never publish it publicly by default.
data$GROUP_EN <- ifelse(data$GROUP==1,"fire","non")
data$GROUP_FA <- ifelse(data$GROUP==1,"گروه fire","گروه non")
data$AGE_BAND_EN <- c("Under 30","30–40 (SPSS code)","40–50 (SPSS code)","50–60 (SPSS code)")[data$AGE]
data$AGE_BAND_FA <- c("کمتر از ۳۰ سال","۳۰ تا ۴۰ سال","۴۰ تا ۵۰ سال","۵۰ تا ۶۰ سال")[data$AGE]
data$MARRIAGE_EN <- c("Single","Married","Divorced")[data$MARRIAGE]
data$MARRIAGE_FA <- c("مجرد","متأهل","مطلقه")[data$MARRIAGE]
data$EDUCATION_EN <- c("High-school diploma","Associate degree","Bachelor degree","Master degree","Doctorate")[data$EDUCATIO]
data$EDUCATION_FA <- c("دیپلم","فوق‌دیپلم","کارشناسی","کارشناسی ارشد","دکتری")[data$EDUCATIO]
data$IS_FIRE <- as.integer(data$GROUP==1)
data$IS_REPEATED_PROFILE <- as.integer(data$PROFILE_REPEAT_COUNT>1)
data$IS_D_INVALID <- data$FLAG_ANY_D_INVALID
data$IS_TOTALA_MISMATCH_RAW <- data$FLAG_TOTALA_DISAGREE
data$IS_TOTALEM_MISMATCH_RAW <- data$FLAG_TOTALEM_DISAGREE
data$IS_MZQ_MISMATCH_RAW <- data$FLAG_MZQ_DISAGREE
data$IS_PROFILE_FIRST <- as.integer(!duplicated(data$QUESTIONNAIRE_PROFILE_ID))
# Aliases matching the original bilingual Power BI export and DAX field names.
data$A_RAW_SUM <- data$A_ITEM_SUM_RAW
data$EM_RAW_SUM <- data$EM_ITEM_SUM_RAW
data$H_RAW_SUM <- data$H_ITEM_SUM_RAW
data$A_SUM_DISCREPANCY <- data$TOTALA_MINUS_RAW_SUM
data$EM_SUM_DISCREPANCY <- data$TOTALEM_MINUS_RAW_SUM
data$H_SUM_DISCREPANCY <- data$MZQ_MINUS_RAW_SUM
data$D_INVALID_ITEM_COUNT <- data$D_INVALID_COUNT
data$PROFILE_MULTIPLICITY <- data$PROFILE_REPEAT_COUNT
data$IS_FIRST_PROFILE_OCCURRENCE <- data$IS_PROFILE_FIRST
# Original D codes are preserved separately; use validated D columns for careful item analysis.
for (c in D) data[[paste0(c,"_VALIDATED")]] <- data[[c]]
for (c in D) data[[c]] <- raw[[c]]
# D1:D15 original columns contain raw data for audit; Dn_VALIDATED invalid items are NA.
data$D_INVALID_STATUS_EN <- ifelse(data$IS_D_INVALID==1,"Out-of-range responses","All D responses valid")
data$D_INVALID_STATUS_FA <- ifelse(data$IS_D_INVALID==1,"پاسخ نامعتبر در سؤال‌های اضطراب مرگ","پاسخ‌های اضطراب مرگ معتبر")
write.csv(data,file.path(out_dir,"powerbi_cases_bilingual_INTERNAL.csv"),row.names=FALSE,
          fileEncoding="UTF-8",na="")
score_names_en <- c("Stored ambiguity-tolerance score","Stored emotion self-regulation score",
 "Stored mentalization score","Optimism","Emotional appraisal","Social skills",
 "Emotion utilization","Arithmetic A sum (not validated)","Arithmetic EM sum (not validated)",
 "Arithmetic H sum (not validated)")
score_names_fa <- c("نمره ثبت‌شده تحمل ابهام","نمره ثبت‌شده خودگردانی هیجانی",
 "نمره ثبت‌شده ذهنی‌سازی","خوش‌بینی","ارزیابی هیجانات","مهارت اجتماعی",
 "کاربرد هیجانات","جمع حسابی A (تأییدنشده)","جمع حسابی EM (تأییدنشده)",
 "جمع حسابی H (تأییدنشده)")
score_codes <- c(SCORES,"A_ITEM_SUM_RAW","EM_ITEM_SUM_RAW","H_ITEM_SUM_RAW")
summary_rows <- list()
for (i in seq_along(score_codes)) for (g in c(1,2)) {
 x <- data[data$GROUP==g,score_codes[i]]
 summary_rows[[length(summary_rows)+1]] <- data.frame(
  Score_code=score_codes[i], Score_EN=score_names_en[i], Score_FA=score_names_fa[i],
  Group_EN=if(g==1) "fire" else "non",Group_FA=if(g==1) "گروه fire" else "گروه non",
  N=sum(!is.na(x)),Mean=mean(x,na.rm=TRUE),SD=sd(x,na.rm=TRUE),
  Median=median(x,na.rm=TRUE),Minimum=min(x,na.rm=TRUE),Maximum=max(x,na.rm=TRUE),
  Evidence_status_EN="Unverified score / diagnostic only",
  Evidence_status_FA="نمره تأییدنشده / صرفاً تشخیصی")
}
write.csv(do.call(rbind,summary_rows),file.path(out_dir,"powerbi_group_summary_bilingual.csv"),
 row.names=FALSE,fileEncoding="UTF-8")


# 14. Diagnostic bootstrap intervals for two-group rank and contingency effect sizes.
# These intervals assume the observed rows are independent. This assumption is NOT established;
# record them only as nominal computational/sensitivity outputs, not valid population coverage.
rank_biserial_fun <- function(x,y) {
 n <- length(x);m <- length(y)
 U <- sum(rank(c(x,y),ties.method="average")[seq_len(n)]) - n*(n+1)/2
 2*U/(n*m)-1
}
cramers_fun <- function(g,catval) {
 tab <- table(g,catval)
 if(min(dim(tab))<2) return(0)
 z <- suppressWarnings(chisq.test(tab,correct=FALSE)$statistic)
 sqrt(as.numeric(z)/(sum(tab)*min(dim(tab)-1)))
}
extra_effects <- list()
for (s in c(SCORES,"A_ITEM_SUM_RAW","EM_ITEM_SUM_RAW","H_ITEM_SUM_RAW")) {
 x <- data[data$GROUP==1,s];y <- data[data$GROUP==2,s]
 bs <- replicate(600,rank_biserial_fun(sample(x,replace=TRUE),sample(y,replace=TRUE)))
 extra_effects[[length(extra_effects)+1]] <- data.frame(test="Mann-Whitney",variable=s,
  effect="Rank-biserial",effect_estimate=rank_biserial_fun(x,y),
  bootstrap_ci_low=unname(quantile(bs,.025)),bootstrap_ci_high=unname(quantile(bs,.975)),
  interval_coverage_warning="Diagnostic only: respondent independence unknown")
}
for (s in c("AGE","MARRIAGE","EDUCATIO")) {
 x<-data[data$GROUP==1,s]; y<-data[data$GROUP==2,s]
 bs<-replicate(600,{xx<-sample(x,replace=TRUE);yy<-sample(y,replace=TRUE);
  cramers_fun(c(rep(1,length(xx)),rep(2,length(yy))),c(xx,yy))})
 extra_effects[[length(extra_effects)+1]] <- data.frame(test="Chi-square diagnostic",variable=s,
  effect="Cramer V",effect_estimate=cramers_fun(data$GROUP,data[[s]]),
  bootstrap_ci_low=unname(quantile(bs,.025)),bootstrap_ci_high=unname(quantile(bs,.975)),
  interval_coverage_warning="Diagnostic only: independence unverified; bias near V=0")
}
write.csv(do.call(rbind,extra_effects),file.path(out_dir,"additional_effect_size_CIs_DIAGNOSTIC.csv"),
 row.names=FALSE,fileEncoding="UTF-8")

writeLines(capture.output(sessionInfo()),file.path(out_dir,"R_session_info.txt"))
cat("Completed exports at:",normalizePath(out_dir),"\n")
cat("CRITICAL: 119/120 aligned cross-group questionnaires identical; only",
 length(unique(profile_key)),"unique full questionnaire profiles across",nrow(raw),"rows.\n")
cat("Interpret any inferential p-values as diagnostic calculations only.\n")
