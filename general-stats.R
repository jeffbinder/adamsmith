require("gtools")

headings <- read.csv("headings.csv")
topics <- read.csv("topics.csv")
pages <- read.csv("pages.csv")
pages2 <- read.csv("pages2.csv")

# Some basic histograms
hist(headings$npages, ylab="Number of headings that reference this many pages",
     xlab="Number of distinct pages", main="Histogram of pages referenced per heading")
hist(pages$nheadings, ylab="Number of pages referenced by this many headings",
     xlab="Number of index headings", main="Histogram of index headings per page")
hist(pages$nmentions, ylab="Number of pages referenced by this many subheadings",
     xlab="Number of subheadings", main="Histogram of index subheadings per page")

# # Same as the above, but limited to headings referring to at least a set number of pages.
# hist(headings$npages[headings$npages >= 4], ylab="Number of headings that reference this many pages",
#      xlab="Number of distinct pages", main="Histogram of pages referenced per big heading")
# hist(pages$nbigheadings, ylab="Number of pages referenced by this many headings",
#      xlab="Number of index headings", main="Histogram of big index headings per page")

# Same again, but based on the topic model rather than the index.
hist(topics$npages, ylab="Number of topics that reference this many pages",
     xlab="Number of distinct pages", main="Histogram of pages referenced per topic")
hist(pages2$ntopics, ylab="Number of pages referenced by this many topics",
     xlab="Number of topics", main="Histogram of topics per page")

# Simulation of the number of topics per page, with topic mixtures drawn
# from a Dirichlet distribution with alpha = 50, and topics chosen based on
# a fixed cutoff.
# npages <- 50000
# ntopics <- 106
# alpha <- 50
# cutoff <- 0.01229
# topic_counts <- sapply(1:npages,
#                        function (i) length(which(rdirichlet(1, rep(alpha, ntopics))[1,]
#                                                  >= cutoff)))
# hist(topic_counts, breaks=12, xlab=paste("Num topics with coef >=", cutoff),
#      main=c("Number of top topics in mixtures generated from a Dirichlet",
#             paste("distribution with alpha =", alpha,
#                   "and total number of topics =", ntopics)))

# # Same, but counting pages per topic.
# npages <- 404
# ntopics <- 436
# cutoff <- 0.003145
# x <- rdirichlet(npages, rep(alpha, ntopics))
# doc_counts <- sapply(1:ntopics, function (i) length(which(x[,i] >= cutoff)))
# hist(doc_counts, breaks=10, xlab=paste("Num docs for which topic coef >=", cutoff),
#      main="Number of top documents per topic, based on Dirichlet distribution")
# 
# # 436, 0.003145; 50, 0.0245
# 
# 
# # Same two things, but with the alpha parameter skewed to match the relative
# # commonness/rarity of topics that was observed in the index.
# npages <- 50000
# ntopics <- 436
# alpha <- headings$npages * 5 / max(headings$npages) * .5 + 5 * .5
# cutoff <- 0.007
# topic_counts <- sapply(1:npages,
#                        function (i) length(which(rdirichlet(1, alpha)[1,]
#                                                  >= cutoff)))
# hist(topic_counts, breaks=10, xlab=paste("Num topics with coef >=", cutoff),
#      main=c("Number of top topics in mixtures generated from a Dirichlet",
#             paste("distribution with skewed alpha",
#                   "and total number of topics =", ntopics)))
# 
# npages <- 404
# ntopics <- 436
# cutoff <- 0.007
# x <- rdirichlet(npages, alpha)
# doc_counts <- sapply(1:ntopics, function (i) length(which(x[,i] >= cutoff)))
# hist(doc_counts, breaks=10, xlab=paste("Num docs for which topic coef >=", cutoff),
#      main="Number of top documents per topic, based on Dirichlet distribution")
# 
