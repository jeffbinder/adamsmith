# Matches up 1784 index to the topic model by using Spearman's rank
# coefficient to find best matches for each topic.

import numpy
import os
import pickle
import scipy.stats
import time

index = pickle.load(open('index.pkl'))

def match():
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

    heading_matches = {}
    topic_matches = {}

    for heading in index:
        heading_pages = set(page for (subheading, page) in index[heading])
        for topic in topic_coefs:
            page_coefs = topic_coefs[topic]
            data = [(pagenum, page_coefs[pagenum],
                     1 if pagenum in heading_pages else 0)
                    for pagenum in page_coefs]
            data = sorted(data, key=lambda x: -x[1])
            coefs = [x[1] for x in data]
            in_heading = [x[2] for x in data]
            correlation, p = scipy.stats.spearmanr(coefs, in_heading)
            topic_pages = set(x[0] for x in data[:len(heading_pages)])
            left = heading_pages - topic_pages
            inner = heading_pages & topic_pages
            right = topic_pages - heading_pages
            heading_matches.setdefault(heading, []) \
                .append((topic, correlation, left, inner, right))
            topic_matches.setdefault(topic, []) \
                .append((heading, correlation, left, inner, right))

    for heading in heading_matches:
        heading_matches[heading] = sorted(heading_matches[heading],
                                          key=lambda x: -x[1])

    for topic in topic_matches:
        topic_matches[topic] = sorted(topic_matches[topic],
                                      key=lambda x: -x[1])

    return heading_matches, topic_matches


# Run a trial for each number of topics, recording the correlation of the
# best fit for each individual topic (THIS WILL WRITE OVER THE TOPIC MODEL/
# FILES!).  Also records the number of headings that are matched with
# correlation >= 0.25 by at least one topic.

# of = open('results_by_num_topics_2.csv', 'w')
# of.write('num_topics,topic_num,avg_best_correlation\n')
# for ntopics in xrange(5, 61):
#     os.system('mallet train-topics --input pages.mallet --num-topics '
#               + str(ntopics) + ' --output-state topic_state.gz '
#               '--output-topic-keys topic_keys.txt --output-doc-topics '
#               'doc_topics.txt')
#     f = open('topic_keys.txt', 'r')
#     top_words_by_topic = {}
#     for line in f.readlines():
#         line = line.strip()
#         topic, _, words = line.split('\t')
#         topic = int(topic)
#         top_words_by_topic[topic] = words.split(' ')[:8]
#     heading_matches, topic_matches = match()
#     avg_correlation = 0.0
#     for topic in topic_matches:
#         print ' '.join(top_words_by_topic[topic]),
#         print topic_matches[topic][0]
#         of.write(str(ntopics) + ',' + str(topic) + ','
#                  + str(topic_matches[topic][0][1]) + '\n')
#         avg_correlation += topic_matches[topic][0][1]
#     avg_correlation /= float(len(topic_matches))
#     print "Average correlation:", avg_correlation
#     time.sleep(1)
#     of.flush()


# Run a bunch of trials, recording the average best fit each time (THIS
# WILL WRITE OVER THE TOPIC MODEL FILES!).

# of = open('results_by_num_topics.csv', 'w')
# of.write('num_topics,avg_best_correlation\n')
# of2 = open('results_by_num_topics_3.csv', 'w')
# of2.write('num_topics,num_strongly_matched_headings\n')
# for ntopics in xrange(5, 61):
#     for trial in xrange(40):
#         os.system('mallet train-topics --input pages.mallet --num-topics '
#                   + str(ntopics) + ' --output-state topic_state.gz '
#                   '--output-topic-keys topic_keys.txt --output-doc-topics '
#                   'doc_topics.txt')
#         f = open('topic_keys.txt', 'r')
#         top_words_by_topic = {}
#         for line in f.readlines():
#             line = line.strip()
#             topic, _, words = line.split('\t')
#             topic = int(topic)
#             top_words_by_topic[topic] = words.split(' ')[:8]
#         heading_matches, topic_matches = match()
#         strongly_matched_headings = set()
#         for heading in heading_matches:
#             if heading_matches[heading][0][1] >= 0.25:
#                 strongly_matched_headings.add(heading)
#         of2.write(str(ntopics) + ',' + str(len(strongly_matched_headings))
#                   + '\n')
#         avg_correlation = 0.0
#         for topic in topic_matches:
#             print ' '.join(top_words_by_topic[topic]),
#             print topic_matches[topic][0]
#             avg_correlation += topic_matches[topic][0][1]
#         avg_correlation /= float(len(topic_matches))
#         print "Average correlation:", avg_correlation
#         time.sleep(1)
#         of.write(str(ntopics) + ',' + str(avg_correlation) + '\n')
#     of.flush(); of2.flush()


# Print results for a topic model that has already been generated.

f = open('topic_keys.txt', 'r')
top_words_by_topic = {}
for line in f.readlines():
    line = line.strip()
    topic, _, words = line.split('\t')
    topic = int(topic)
    top_words_by_topic[topic] = words.split(' ')[:8]

heading_matches, topic_matches = match()

f = open('matches.pkl', 'w')
pickle.dump((heading_matches, topic_matches), f)

print '===== Top topics for headings'

avg_correlation = 0.0
for heading in sorted(heading_matches):
    heading_matches[heading][0] \
        = (' '.join(top_words_by_topic[heading_matches[heading][0][0]]),) \
        + heading_matches[heading][0][1:]
    print heading, heading_matches[heading][0]
    avg_correlation += heading_matches[heading][0][1]
avg_correlation /= float(len(heading_matches))
print avg_correlation

print '===== Top headings for topics'

avg_correlation = 0.0
for topic in topic_matches:
    print ' '.join(top_words_by_topic[topic]),
    print topic_matches[topic][0]
    avg_correlation += topic_matches[topic][0][1]
avg_correlation /= float(len(topic_matches))
print avg_correlation
