# This script does some tests on the example_comparison.csv file create by
# match-index.py: an example of what data we have to look at with respect
# to a topic and an index heading that are well-correlated.

x <- read.csv('example_comparison.csv')

plot(x$coef, type="l", xlab="Pages, sorted by topic coefficient",
     ylab="Topic coefficient", main="Pages listed under index heading (circles) vs. topic coefficient (line)")

xs = which(x$in_heading == 1)
ys = rep(0, length(xs))
points(y=ys, x=xs)

cor.test(x$coef, x$in_heading, method="spearman")
