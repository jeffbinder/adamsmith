import re

f = open('WoN1852-body.html', 'r')

def strip_html_tags(s):
    s = re.sub('<[^>]*>', '', s)
    s = re.sub('<[^>]*$', '', s)
    s = re.sub('^[^>]*>', '', s)
    s = re.sub('&nbsp;', ' ', s)
    return s

pagenum = 0
outf = None
for line in f.readlines():
    newpage = 'a name="Page_' in line
    if newpage:
        line = re.sub('\[Pg [0-9]+\]', '', line)
    line = strip_html_tags(line)
    line = line.replace('\r\n', '\n')
    line = line.strip() + '\n'
    if outf:
        outf.write(line)
    if newpage:
        pagenum += 1
        outf = open('WoN1852-pages/{0:03}'.format(pagenum), 'w')

