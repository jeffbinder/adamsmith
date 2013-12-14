# Output the number of subheadings matching a given pattern

import pickle
import re

index = pickle.load(open('index.pkl'))

nsubheadings = 0
nmatching_subheadings = 0
for heading in index:
    subheadings = set()
    for subheading, n in index[heading]:
        subheadings.add(subheading)
    for subheading in subheadings:
        nsubheadings += 1
        if re.search(r'(^|[^a-zA-Z])how($|[^a-zA-Z])', subheading):
            nmatching_subheadings += 1
        elif 'how' in subheading:
            print subheading

print nmatching_subheadings, nsubheadings
    