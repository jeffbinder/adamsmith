# Parses the HTML index from Project Gutenberg, pickles it, produces some
# basic stats, and exports data to CSV files for further analysis in R.

import pickle
import re

f = open('WoN1852-index.html', 'r')

def strip_html_tags(s):
    s = re.sub('<[^>]*>', '', s)
    s = re.sub('<[^>]*$', '', s)
    s = re.sub('^[^>]*>', '', s)
    s = re.sub('&nbsp;', ' ', s)
    return s

index = {}
pagenum = None
def record_line(heading, line):
    global pagenum
    subheading = line
    if subheading.endswith(', ib'):
        subheading = subheading[:-4]
        index.setdefault(heading, []) \
            .append((subheading, pagenum))
    elif subheading.endswith('. ib'):
        subheading = subheading[:-3]
        index.setdefault(heading, []) \
            .append((subheading, pagenum))
    else:
        if ', ib.' in subheading:
            subheading, rest = subheading.split(', ib.')
            index.setdefault(heading, []) \
                .append((subheading, pagenum))
            subheading += rest
        if '. ib.' in subheading:
            subheading, rest = subheading.split(' ib.')
            index.setdefault(heading, []) \
                .append((subheading, pagenum))
            subheading += rest
        l = subheading.split(', <a href="http://www.gutenberg.org/files/38194/38194-h/38194-h.htm#Page_')
        subheading = l[0]
        for pagenum in l[1:]:
            pagenum = pagenum.split('"')[0]
            pagenum = int(pagenum)
            index.setdefault(heading, []) \
                .append((subheading, pagenum))

heading = None
for line in f.readlines():
    line = re.sub('<span class="pagenum">[^s]*</span>', '', line)
    if line.startswith('<i>'):
        line = line[3:-6]
        line = re.sub('\\. See <i>[^.]+', '', line)
        line = line.replace('</i> and <i>', ' and ')
        line = line.replace(', <i>Append</i>', '')
        try:
            heading, line = line.split('</i>')
        except:
            print line
        if line.startswith(', '):
            line = line[2:]
        if line.startswith(' '):
            line = line[1:]
        record_line(heading, line)
    elif line.startswith('<span style="margin-left: 1em;">'):
        line = line[32:-13]
        line = line[0].lower() + line[1:]
        record_line(heading, line)

pages = {}
for heading in index:
    for subheading, page in index[heading]:
        pages.setdefault(page, []).append((heading, subheading))

nheadings = len(index)
avg_subheadings_per_heading = 0
avg_pages_per_heading = 0
f = open('headings.csv', 'w')
f.write('i,nsubheadings,npages\n')
for i, heading in enumerate(index):
    nsubheadings = len(index[heading])
    referenced_pages = set(s[1] for s in index[heading])
    npages = len(referenced_pages)
    f.write(','.join(str(x) for x in [i+1, nsubheadings, npages]) + '\n')
    avg_subheadings_per_heading += nsubheadings
    avg_pages_per_heading += npages
avg_subheadings_per_heading /= float(nheadings)
avg_pages_per_heading /= float(nheadings)

print nheadings
print avg_subheadings_per_heading
print avg_pages_per_heading

npages_referenced = len(pages)
for i in xrange(1, 404+1):
    pages.setdefault(i, set())
npages = len(pages)
avg_mentions_per_page = 0
avg_headings_per_page = 0
f = open('pages.csv', 'w')
f.write('i,nmentions,nheadings,nbigheadings\n')
for i, page in enumerate(pages):
    nmentions = len(pages[page])
    nheadings = len(set(s[0] for s in pages[page]))
    nbigheadings = len(set(s[0] for s in pages[page]
                           if len(set(t[1] for t in index[s[0]]))
                           > 4))
    f.write(','.join(str(x) for x in [i+1, nmentions, nheadings,
                                      nbigheadings]) + '\n')
    avg_mentions_per_page += nmentions
    avg_headings_per_page += nheadings
avg_mentions_per_page /= float(npages)
avg_headings_per_page /= float(npages)

print npages_referenced, '/', npages
print avg_mentions_per_page
print avg_headings_per_page

f = open('index.pkl', 'w')
pickle.dump(index, f)
