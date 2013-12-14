# Output an example of an apparently connected topic-heading pair to examine
# in R.

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

heading = 'Justice'
topic = 28

f = open('example_comparison.csv', 'w')
f.write('pagenum,coef,in_heading\n')
heading_pages = set(x[1] for x in index[heading])
data = [(pagenum, topic_coefs[topic][pagenum],
         1 if pagenum in heading_pages else 0)
        for pagenum in topic_coefs[topic]]
data = sorted(data, key=lambda x: x[1])
for row in data:
    f.write(','.join(str(x) for x in row) + '\n')
