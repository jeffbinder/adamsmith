# Matches up 1784 index with the topic model.  A set of pages is produced
# for each topic using a set cutoff for coefficients; this is compared to
# the set of pages listed under each index heading using the Jaccard metric.
# Also produces CSV files representing the results of chopping up the topic
# model, for processing in R.

import pickle

steps = 1000

def jaccard(S1, S2):
    return float(len(S1 & S2)) / len(S1 | S2)

index = pickle.load(open('index.pkl'))

f = open('doc_topics.txt', 'r')
f.readline()
topic_coefs = {}
for line in f.readlines():
    line = line.split('\t')
    pagenum = line[1].split('/')[-1].replace('%20', ' ').replace('%3F', '?')
    pagenum = int(pagenum)
    line = line[2:]
    ntopics = len(line) / 2
    for i in xrange(0, ntopics):
        topic = int(line[i*2])
        coef = float(line[i*2 + 1])
        topic_coefs.setdefault(topic, {})[pagenum] = coef

# Output an example of an apparently connected topic-heading pair to examine
# in R.
heading = 'Colonies'
topic = 35
f = open('example_comparison.csv', 'w')
f.write('pagenum,coef,in_heading\n')
heading_pages = set(x[1] for x in index[heading])
data = [(pagenum, topic_coefs[topic][pagenum],
         1 if pagenum in heading_pages else 0)
        for pagenum in topic_coefs[topic]]
data = sorted(data, key=lambda x: x[1])
for row in data:
    f.write(','.join(str(x) for x in row) + '\n')
exit()

def match(coef_cutoff):
    pagenums_by_topic = {}
    topics_by_pagenum = {}
    for topic in topic_coefs:
        for pagenum in topic_coefs[topic]:
            coef = topic_coefs[topic][pagenum]
            if coef > coef_cutoff:
                pagenums_by_topic.setdefault(topic, set()).add(pagenum)
                topics_by_pagenum.setdefault(pagenum, set()).add(topic)

    f = open('topics.csv', 'w')
    f.write('i,npages\n')
    for topic in pagenums_by_topic:
        npages = len(pagenums_by_topic[topic])
        f.write(','.join(str(x) for x in [topic, npages]) + '\n')

    f = open('pages2.csv', 'w')
    f.write('i,ntopics\n')
    for pagenum in topics_by_pagenum:
        ntopics = len(topics_by_pagenum[pagenum])
        f.write(','.join(str(x) for x in [pagenum, ntopics]) + '\n')

    heading_matches = {}
    topic_matches = {}

    for heading in index:
        heading_pages = set(page for (subheading, page) in index[heading])
        for topic in pagenums_by_topic:
            topic_pages = pagenums_by_topic[topic]
            left = heading_pages - topic_pages
            inner = heading_pages & topic_pages
            right = topic_pages - heading_pages
            similarity = jaccard(heading_pages, topic_pages)
            heading_matches.setdefault(heading, []) \
                .append((topic, similarity, left, inner, right))
            topic_matches.setdefault(topic, []) \
                .append((heading, similarity, left, inner, right))

    for heading in heading_matches:
        heading_matches[heading] = sorted(heading_matches[heading],
                                          key=lambda x: -x[1])

    for topic in topic_matches:
        topic_matches[topic] = sorted(topic_matches[topic],
                                      key=lambda x: -x[1])

    return heading_matches, topic_matches


# Run through a bunch of possible cutoffs to see how good the match is.

for i in xrange(steps):
    cutoff = (i + 1.0) / steps
    heading_matches, topic_matches = match(cutoff)
    avg_similarity = 0.0
    num_unique_matches = 0
    headings_matched = set()
    for topic in topic_matches:
        avg_similarity += topic_matches[topic][0][1]
        if len(topic_matches[topic]) < 2 \
                or (topic_matches[topic][0][1]
                    > topic_matches[topic][1][1]):
            num_unique_matches += 1
            headings_matched.add(topic_matches[topic][0][0])
    avg_similarity /= float(len(topic_matches))
    print cutoff, num_unique_matches, len(headings_matched), avg_similarity
    break


# Output the results with our selected cutoff.

heading_matches, topic_matches = match(0.053)

print '===== Top headings for topics'

avg_similarity = 0.0
for topic in topic_matches:
    print topic, topic_matches[topic][0]
    avg_similarity += topic_matches[topic][0][1]
avg_similarity /= float(len(topic_matches))
print avg_similarity

print '===== Top topics for headings'

avg_similarity = 0.0
for heading in sorted(heading_matches):
    print heading, heading_matches[heading][0]
    avg_similarity += heading_matches[heading][0][1]
avg_similarity /= float(len(heading_matches))
print avg_similarity
