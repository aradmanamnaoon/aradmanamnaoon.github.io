source("R/original_sapa_audit.R")
k <- data.frame(row.names=paste0("q_",1:10))
for(s in scales) k[[s]] <- c(-1L,rep(1L,9L))
stopifnot(validate_key(k))
x <- data.frame(q_1=c(1,2,NA),q_2=c(6,5,4))
y <- keyed(x,c(-1L,1L))
stopifnot(identical(as.numeric(y[,1]),c(6,5,NA_real_)),
          identical(as.numeric(y[,2]),c(6,5,4)))
k[1,"IPIP50Extra"] <- 0L
stopifnot(inherits(try(validate_key(k),silent=TRUE),"try-error"))
cat("SAPA synthetic key-validation tests passed\n")

