# This script verifies that all of the subheadings in the index appear in page
# number order, and looks for headings that refer to non-contiguous passages.

import pickle

index = pickle.load(open('index.pkl'))

for heading in index:
    subheadings = index[heading]
    prev_subheading = subheadings[0][0]
    prev_pagenum = subheadings[0][1]
    for subheading, pagenum in subheadings[1:]:
        if pagenum < prev_pagenum:
            print 'Ordering inconsistency in ', heading, ', ', prev_subheading
        prev_subheading = subheading
        prev_pagenum = pagenum
    
for heading in index:
    subheadings = index[heading]
    prev_subheading = subheadings[0][0]
    prev_pagenum = subheadings[0][1]
    for subheading, pagenum in subheadings:
        if subheading != prev_subheading:
            continue
        if pagenum > prev_pagenum + 5:
            print 'Non-contiguity in ', heading, ', ', subheading
        prev_subheading = subheading
        prev_pagenum = pagenum
    