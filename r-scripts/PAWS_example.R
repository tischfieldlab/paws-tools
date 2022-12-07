# script to extract behavioral measurements and painscores from proanalyst CSVs
library(paws) #need to install via github
library(ggplot2)
library(dplyr)
library(kde1d)
library(zoo)

create_group <- function(directory, strain){
  setwd(directory) # I set the wd to write an output file to the same location as the input trials
  baseline_db <- list()
  baseline_db_features <- list()
  baseline_db_scores <-list()
  bdb_scores_pre <- list()
  bdb_scores_post <- list()
  
  a <- list.files(directory)
  for (i in a){
    b <- read.csv(i, sep = "\t")
    baseline_db[[length(baseline_db)+1]] = b
  }
  
  for (i in 1:length(baseline_db)) { 
    baseline_db_features[[i]] <- extract_features(zoo::na.spline(baseline_db[[i]]$x), zoo::na.spline(baseline_db[[i]]$y))
  }
  
  # get pre peak scores
  for (i in 1:length(baseline_db_features)){
    bdb_scores_pre[[i]] <- pain_score(baseline_db_features[[i]], strains=strain, feature.set = "pre.peak")
  }
  
  # get pre peak scores
  for (i in 1:length(baseline_db_features)){
    bdb_scores_post[[i]] <- pain_score(baseline_db_features[[i]], strains=strain, feature.set = "post.peak")
  }
  
  
  pre_score_kde <- kde1d(unlist(bdb_scores_pre,use.names = FALSE))
  post_score_kde <- kde1d(unlist(bdb_scores_post,use.names = FALSE))
  
  return(post_score_kde)
}

c_kde <- create_group("C:/Users/tomva/Desktop/DI-Baseline-CSVs/1VF-CNO","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/DI-Baseline-CSVs/1VF-Saline","C57B6-")
plot(x = c_kde,  ylim = c(0,1), xlim = c(-3,8), main = "1VF Baseline", xlab = "PAWS Score", ylab = "Density", col = 'blue')
lines(x = s_kde, col = 'orange')
legend( x = "topright", legend = c("CNO","Saline"),col = c("blue","orange"), lwd=1, lty=c(1,1), pch=c(NA,NA), cex = 1 )


c_kde <- create_group("C:/Users/tomva/Desktop/DI-Baseline-CSVs/4VF-CNO","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/DI-Baseline-CSVs/4VF-Saline","C57B6-")
plot(x = c_kde,  ylim = c(0,1), xlim = c(-3,8), main = "4VF Baseline", xlab = "PAWS Score", ylab = "Density", col = 'blue')
lines(x = s_kde, col = 'orange')
legend( x = "topright", legend = c("CNO","Saline"),col = c("blue","orange"), lwd=1, lty=c(1,1), pch=c(NA,NA), cex = 1 )


c_kde <- create_group("C:/Users/tomva/Desktop/DI-Baseline-CSVs/Brush-CNO","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/DI-Baseline-CSVs/Brush-Saline","C57B6-")
plot(x = c_kde,  ylim = c(0,1), xlim = c(-3,8), main = "Brush Baseline", xlab = "PAWS Score", ylab = "Density", col = 'blue')
lines(x = s_kde, col = 'orange')
legend( x = "topright", legend = c("CNO","Saline"),col = c("blue","orange"), lwd=1, lty=c(1,1), pch=c(NA,NA), cex = 1 )


c_kde <- create_group("C:/Users/tomva/Desktop/DI-Baseline-CSVs/Pin-CNO","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/DI-Baseline-CSVs/Pin-Saline","C57B6-")
plot(x = c_kde,  ylim = c(0,1), xlim = c(-3,8), main = "Pinprick Baseline", xlab = "PAWS Score", ylab = "Density", col = 'blue')
lines(x = s_kde, col = 'orange')
legend( x = "topright", legend = c("CNO","Saline"),col = c("blue","orange"), lwd=1, lty=c(1,1), pch=c(NA,NA), cex = 1 )
