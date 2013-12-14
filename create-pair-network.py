# This script takes in index-path-pairs-edited.txt, which should contain the
# list of paired subheadings that create-network.py creates in index-path-pairs.txt,
# with spurious examples removed, and produces a CSV file suitable for use with
# Gephi.

network = {}

inf = open('index-path-pairs.txt')
lines = inf.readlines()
for i in xrange(0, len(lines), 3):
    a, b = lines[i].split(', ')[0], lines[i+1].split(', ')[0]
    if a < b:
        edge = a, b
    else:
        edge = b, a
    if edge in network:
        network[edge] += 1
    else:
        network[edge] = 1

f = open('index-pairs.csv', 'w')
f.write('Source,Target,Weight,Type\n')
for a, b in network:
    f.write(a + ',' + b + ',' + str(network[(a, b)]) + ',Undirected\n')
