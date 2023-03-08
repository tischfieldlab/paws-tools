# script to extract behavioral measurements and painscores from proanalyst CSVs
library(paws) #need to install via github
library(ggplot2)
library(dplyr)
library(kde1d)
library(zoo)
library(rJava)
library(xlsx)

parameters <- set_parameters(fps=4000, window.filter.size=0.03, window.filter.order=2, 
                             downsample=1, projection.window=0.2, shake.filter.size=0.05,
                             velocity.filter.size=0.02)

create_group <- function(directory, strain){
  setwd(directory) # I set the wd to write an output file to the same location as the input trials
  baseline_db <- list()
  baseline_db_features <- list()
  baseline_db_scores <-list()
  bdb_scores_pre <- list()
  bdb_scores_post <- list()
  bdb_post_features <- list()
  bdb_pre_features <- list()
  
  a <- list.files(directory)
  for (i in a){
    b <- read.csv(i, sep = "\t")
    baseline_db[[length(baseline_db)+1]] = b
  }
  
  for (i in 1:length(baseline_db)) { 
    baseline_db_features[[i]] <- extract_features(zoo::na.spline(baseline_db[[i]]$x), zoo::na.spline(baseline_db[[i]]$y), parameters=parameters)
  }
  
  # get pre peak scores
  for (i in 1:length(baseline_db_features)){
    bdb_scores_pre[[i]] <- pain_score(baseline_db_features[[i]], strains=strain, feature.set = "pre.peak")
  }
  
  # get pre peak scores
  for (i in 1:length(baseline_db_features)){
    bdb_scores_post[[i]] <- pain_score(baseline_db_features[[i]], strains=strain, feature.set = "post.peak")
  }
  
  
  #pre_score_kde <- kde1d(unlist(bdb_scores_pre,use.names = FALSE))
  #post_score_kde <- kde1d(unlist(bdb_scores_post,use.names = FALSE))
  for (i in 1:length(baseline_db_features)){
    bdb_post_features[[i]] <- baseline_db_features[[i]][["post.peak"]]
    bdb_pre_features[[i]] <- baseline_db_features[[i]][["pre.peak"]]
  }
  bdb_post_features <- do.call("rbind", bdb_post_features)
  bdb_pre_features <- do.call("rbind", bdb_pre_features)
  
  return(bdb_post_features)
}

Mouse_ID <- list("F1","M1","F3","M3","F4","M4","F6","M6")

c_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/06VF-CNO","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/06VF-Saline","C57B6-")

c_kde["Treatment"] = "CNO"
c_kde$Mouse_ID <- Mouse_ID
s_kde["Treatment"] = "Saline"
s_kde$Mouse_ID = Mouse_ID

Stim.df <- rbind(c_kde, s_kde)
Stim.df["Stimulation"] = "0.6VF"
Stim.df["Injury"] = "Baseline"

Total.df <- Stim.df


c_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/4VF-CNO","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/4VF-Saline","C57B6-")

c_kde["Treatment"] = "CNO"
c_kde$Mouse_ID <- Mouse_ID
s_kde["Treatment"] = "Saline"
s_kde$Mouse_ID = Mouse_ID

Stim.df <- rbind(c_kde, s_kde)
Stim.df["Stimulation"] = "4VF"
Stim.df["Injury"] = "Baseline"

Total.df <- rbind(Total.df, Stim.df)


c_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/Brush-CNO","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/Brush-Saline","C57B6-")

c_kde["Treatment"] = "CNO"
c_kde$Mouse_ID <- Mouse_ID
s_kde["Treatment"] = "Saline"
s_kde$Mouse_ID = Mouse_ID

Stim.df <- rbind(c_kde, s_kde)
Stim.df["Stimulation"] = "Brush"
Stim.df["Injury"] = "Baseline"

Total.df <- rbind(Total.df, Stim.df)

c_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/Pin-CNO","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/Pin-Saline","C57B6-")

c_kde["Treatment"] = "CNO"
c_kde$Mouse_ID <- Mouse_ID
s_kde["Treatment"] = "Saline"
s_kde$Mouse_ID = Mouse_ID

Stim.df <- rbind(c_kde, s_kde)
Stim.df["Stimulation"] = "Pin"
Stim.df["Injury"] = "Baseline"

Total.df <- rbind(Total.df, Stim.df)

c_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/016VF-CNO-Chronic","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/016VF-Saline-Chronic","C57B6-")

c_kde["Treatment"] = "CNO"
c_kde$Mouse_ID <- Mouse_ID
s_kde["Treatment"] = "Saline"
s_kde$Mouse_ID = Mouse_ID

Stim.df <- rbind(c_kde, s_kde)
Stim.df["Stimulation"] = "0.16VF"
Stim.df["Injury"] = "Chronic"

Total.df <- rbind(Total.df, Stim.df)

c_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/06VF-CNO-Chronic","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/06VF-Saline-Chronic","C57B6-")

c_kde["Treatment"] = "CNO"
c_kde$Mouse_ID <- Mouse_ID
s_kde["Treatment"] = "Saline"
s_kde$Mouse_ID = Mouse_ID

Stim.df <- rbind(c_kde, s_kde)
Stim.df["Stimulation"] = "0.6VF"
Stim.df["Injury"] = "Chronic"

Total.df <- rbind(Total.df, Stim.df)

c_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/4VF-CNO-Chronic","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/4VF-Saline-Chronic","C57B6-")

c_kde["Treatment"] = "CNO"
c_kde$Mouse_ID <- Mouse_ID
s_kde["Treatment"] = "Saline"
s_kde$Mouse_ID = Mouse_ID

Stim.df <- rbind(c_kde, s_kde)
Stim.df["Stimulation"] = "4VF"
Stim.df["Injury"] = "Chronic"

Total.df <- rbind(Total.df, Stim.df)

c_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/Brush-CNO-Chronic","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/Brush-Saline-Chronic","C57B6-")

c_kde["Treatment"] = "CNO"
c_kde$Mouse_ID <- Mouse_ID
s_kde["Treatment"] = "Saline"
s_kde$Mouse_ID = Mouse_ID

Stim.df <- rbind(c_kde, s_kde)
Stim.df["Stimulation"] = "Brush"
Stim.df["Injury"] = "Chronic"

Total.df <- rbind(Total.df, Stim.df)

c_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/Pin-CNO-Chronic","C57B6-")
s_kde <- create_group("C:/Users/tomva/Desktop/2023_01_23/Pin-Saline-Chronic","C57B6-")

c_kde["Treatment"] = "CNO"
c_kde$Mouse_ID <- Mouse_ID
s_kde["Treatment"] = "Saline"
s_kde$Mouse_ID = list("F1","M1","F3","M3","M4","F6","M6")

Stim.df <- rbind(c_kde, s_kde)
Stim.df["Stimulation"] = "Pin"
Stim.df["Injury"] = "Chronic"

Total.df <- rbind(Total.df, Stim.df)

write.xlsx(Total.df, "C:/Users/tomva/Desktop/2023_01_23/Total_dataframe.xlsx")
