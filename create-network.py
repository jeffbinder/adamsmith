# Creates a network representing the paths that a reader could take by looking up words
# that appear in the index in the index.  Also outputs a list of the subheadings that
# create this sort of path between each pair of subheadings.

import collections
import pickle
import re
from nltk import WordNetLemmatizer

wnl = WordNetLemmatizer()

index = pickle.load(open('index.pkl'))

# Maps lemmatized/lowercased headings to the headings as they appear in the index.
headings = {}
for heading in index:
    heading_words = re.split('[^\w]+', heading.lower())
    heading_words = [wnl.lemmatize(word) for word in heading_words]
    headings[' '.join(heading_words)] = heading

edges = {} # Maps edge pairs to sets of the subheadings that produce them.

for heading in index:
    subheadings = set()
    for subheading, n in index[heading]:
        subheading_words = re.split('[^\w]+', subheading.lower())
        subheading_words = [wnl.lemmatize(word) for word in subheading_words]
        headings_matched = set() # Only match each heading once per subheading
        for i in xrange(len(subheading_words)):
            for j in xrange(i+1, len(subheading_words)+1):
                word_seq = ' '.join(subheading_words[i:j])
                if word_seq in headings:
                    edges.setdefault((heading, headings[word_seq]), []) \
                        .append((subheading, n))

f = open('index_network.csv', 'w')
f.write('Source,Target,Weight\n')
total_mentions = 0
for a, b in edges:
    if a == b:
        continue
    nmentions = len(set(subheading for subheading, n in edges[(a, b)]))
    total_mentions += nmentions
    f.write(a + ',' + b + ',' + str(nmentions) + '\n')
print total_mentions

f = open('index_network_mutual.csv', 'w')
f.write('Source,Target,Weight\n')
total_mentions = 0
for a, b in edges:
    if a == b:
        continue
    if (b, a) not in edges:
        continue
    nmentions = len(set(subheading for subheading, n in edges[(a, b)]))
    total_mentions += nmentions
    f.write(a + ',' + b + ',' + str(nmentions) + '\n')
print total_mentions

f = open('index-paths.txt', 'w')
for a, b in sorted(edges):
    if a == b:
        continue
    if a > b and (b, a) in edges:
        continue
    f.write('==== ' + a + ' <-> ' + b + '\n\n')
    f.write(a + '\n')
    subheadings = set(subheading for subheading, n in edges[(a, b)])
    for subheading in subheadings:
        f.write('    ' + subheading + '\n')
    if (b, a) in edges:
        f.write('\n' + b + '\n')
        subheadings = set(subheading for subheading, n in edges[(b, a)])
        for subheading in subheadings:
            f.write('    ' + subheading + '\n')
    f.write('\n\n')

f = open('index-paths-mutual.txt', 'w')
for a, b in sorted(edges):
    if a == b:
        continue
    if (b, a) not in edges:
        continue
    if a > b:
        continue
    f.write('==== ' + a + ' <-> ' + b + '\n\n')
    f.write(a + '\n')
    subheadings = set(subheading for subheading, n in edges[(a, b)])
    for subheading in subheadings:
        f.write('    ' + subheading + '\n')
    if (b, a) in edges:
        f.write('\n' + b + '\n')
        subheadings = set(subheading for subheading, n in edges[(b, a)])
        for subheading in subheadings:
            f.write('    ' + subheading + '\n')
    f.write('\n\n')

f = open('index-path-pairs.txt', 'w')
npairs = 0
for a, b in sorted(edges):
    if a == b:
        continue
    if (b, a) not in edges:
        continue
    if a > b:
        continue
    subheadings_b = collections.deque(edges[(b, a)])
    for subheading, n in edges[(a, b)]:
        while subheadings_b and subheadings_b[0][1] < n:
            subheadings_b.popleft()
        if not subheadings_b:
            break
        for i in xrange(len(subheadings_b)):
            if subheadings_b[i][1] == n:
                f.write(a + ', ' + subheading + '\n')
                f.write(b + ', ' + subheadings_b[i][0] + '\n\n')
                npairs += 1
print npairs
