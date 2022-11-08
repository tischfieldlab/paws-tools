# script to extract behavioral measurements and painscores from proanalyst CSVs
library(paws)

# initializing lists
# I remember putting the CSVs for a given 'condition' in one folder and running this script for each folder lol
setwd("C:/Users/saboorlab-adm/Downloads/baseline db CSVs/baseline db CSVs") # I set the wd to write an output file to the same location as the input trials
baseline_db <- list()
baseline_db_features <- list()
baseline_db_scores <-list()
bdb_scores_pre <- list()

# reading files and constructing trial list
# change this section to reflect the format of DLC  eg. to 'skip' the headers and work with x and y coordinate columns of interest
a <- list.files("C:/Users/saboorlab-adm/Downloads/baseline db CSVs/baseline db CSVs")
for (i in a){
  b <- read.csv(i, comment.char='#', header=FALSE
  )
  names(b) <- c(
    'index', 'time', 'x', 'y', 'distance', 'speed',
    'x.velocity', 'y.velocity'
  )
  baseline_db[[length(baseline_db)+1]] = b
}

# get behavior features
# change this section to the relevant column vectors
for (i in 1:length(baseline_db)) { 
  baseline_db_features[[i]] <- extract_features(baseline_db[[i]]$x, baseline_db[[i]]$y)
}

# for the following sections, we talked about this and you can do whatever dimensionality reduction you want! 
# get post peak scores
for (i in 1:length(baseline_db_features)){
  baseline_db_scores[[i]] <- pain_score(baseline_db_features[[i]], strains='C57B6-')
}

# get pre peak scores
for (i in 1:length(baseline_db_features)){
  bdb_scores_pre[[i]] <- pain_score(baseline_db_features[[i]], strains='C57B6-', feature.set = "pre.peak")
}

