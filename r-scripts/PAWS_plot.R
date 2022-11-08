library(paws)
library(ggplot2)
library(dplyr)
library(kde1d)


# compute features for Jones et al. (2020) paw trajectories
paw.features <- lapply(jones2020.tracks, function(track) {extract_features(track$time.series)})

# get strain information for each track
strains <- sapply(jones2020.tracks, function(track) track$strain)

# compute pain scores
scores = pain_score(paw.features, strains=strains)

paws.data = data.frame(scores, strains)

paws.kdelist = paws.data %>% 
                  group_by(strains) %>%
                  #tally(sort = TRUE) 
                  #group_map(~ plot(kde(x = .x$scores)))
                  group_map(~ kde1d(.x$scores))
plot.new()
plot(x = paws.kdelist[[1]], ylim = c(0,1), xlim = c(-2,6), xlab = "PAWS Score", ylab = "Density", col = )
lines(paws.kdelist[[2]])
lines(paws.kdelist[[3]])
lines(paws.kdelist[[4]])
lines(paws.kdelist[[5]])
lines(paws.kdelist[[6]])
