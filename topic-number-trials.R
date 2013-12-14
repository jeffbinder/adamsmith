# Creates a chart of the output of topic-number trials.

x <- read.csv('results_by_num_topics.csv')
plot(x$num_topics, x$avg_best_correlation, ylim=c(0, 0.4), xlim=c(0, 60),
     xlab="Number of topics", ylab="Average best-match correlation for topics")

x <- read.csv('results_by_num_topics_2.csv')
plot(x$num_topics, x$avg_best_correlation, ylim=c(0, 0.4), xlim=c(0, 60),
     xlab="Number of topics in model", ylab="Best-match correlation for this topic")

x <- read.csv('results_by_num_topics_3.csv')
plot(x$num_topics, x$num_strongly_matched_headings, col="darkgrey", ylim=c(0, 40), xlim=c(0, 60),
     xlab="Number of topics in model", ylab="Number of index headings correlated >= 0.25 w/ some topic",
     main="Number of index headings matched by topic models (40 trials)")
x1 <- aggregate(x, by=list(x$num_topics), FUN=mean)
lines(x1$num_topics, x1$num_strongly_matched_headings, lwd=3)
