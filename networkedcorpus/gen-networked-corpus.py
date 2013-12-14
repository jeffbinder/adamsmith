#!/usr/bin/python

# This is a custom branch of the Networked Corpus system created for the
# indexing project.  Major alterations are marked with "CUSTOM".

import codecs
import collections
import gzip
import json
import math
import numpy
import optparse
import os
import pickle
import re
import scipy.stats
import shutil
import sys

# CUSTOM: data for the Chapter numbers displayed at the top of pages.
Chapters = [('Book I', 1),
            ('Introduction', 1),
            ('Chap. I', 2),
            ('Chap. II', 6),
            ('Chap. III', 8),
            ('Chap. IV', 9),
            ('Chap. V', 12),
            ('Chap. VI', 20),
            ('Chap. VII', 23),
            ('Chap. VIII', 27),
            ('Chap. IX', 36),
            ('Chap. X', 41),
            ('Chap. XI', 60),
            ('Book II', 111),
            ('Introduction', 111),
            ('Chap. I', 112),
            ('Chap. II', 115),
            ('Chap. III', 135),
            ('Chap. IV', 144),
            ('Chap. V', 147),
            ('Book III', 155),
            ('Chap. I', 155),
            ('Chap. II', 157),
            ('Chap. III', 162),
            ('Chap. IV', 167),
            ('Book IV', 173),
            ('Chap. I', 173),
            ('Chap. II', 183),
            ('Chap. III', 192),
            ('Chap. IV', 203),
            ('Chap. V', 205),
            ('Chap. VI', 222),
            ('Chap. VII', 227),
            ('Chap. VIII', 266),
            ('Chap. IX', 275),
            ('Appendix', 287),
            ('Book V', 289),
            ('Chap. I', 289),
            ('Chap. II', 343),
            ('Chap. III', 385)]

# Displayed in the usage message.
description_text = \
'Generate an annotated HTML version of a corpus based on a MALLET topic model.'

# Preface of the generated HTML files.
html1 = u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <script src="docs_by_topic.js"></script>
  <script src="topic_names.js"></script>
  <script src="doc_names.js"></script>
  <script src="extracts.js"></script>
  <script src="matches.js"></script>
  <script src="index-data.js"></script>
  <script src="jquery.js"></script>
  <script src="protovis.min.js"></script>
  <script src="protovis-msie.min.js"></script>
  <script src="common.js"></script>
  <script src="browser.js"></script>
  <link rel="stylesheet" type="text/css" href="browser.css"></link>
  <title>{0}</title>
 </head>
 <body>
  <div id="header">
    <div id="title-area">
    </div>
    <div style='clear:both'></div>
    <div id="prev-next-area">
    </div>
  </div>
  <div id="main-area">
'''

# End of the generated HTML files.
html2 = u'''
  </div>
  <div id="footer">
    <div id="top-topic-area">
    </div>
  </div>
  <div id="bottom-spacer"></div>
 </body>
</html>
'''

# Preface of the generated index file.
index_html1 = u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <link rel="stylesheet" type="text/css" href="index.css"></link>
  <title>Networked Corpus Index</title>
 </head>
 <body>
  <div id="header">
    <div style="margin-bottom:5px">
      The Wealth of Nations
    </div>
    <div style="margin-left:auto;margin-right:auto">
      Table of contents |
      <a href="topic-index.html">List of topics</a> |
      <a href="smith-index.html">1784 index</a>
    </div>
    <div id="top-topic-area" style="float:right">
    </div>
  </div>
  <div id="main-area">
    <table id="text-table">
'''

# End of the generated index file.
index_html2 = u'''
    </table>
  </div>
 </body>
</html>
'''

# Preface of the generated List of topics file.
topic_index_html1 = u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <script src="docs_by_topic.js"></script>
  <script src="topic_names.js"></script>
  <script src="doc_names.js"></script>
  <script src="extracts.js"></script>
  <script src="matches.js"></script>
  <script src="index-data.js"></script>
  <script src="jquery.js"></script>
  <script src="common.js"></script>
  <script src="index.js"></script>
  <script src="protovis.min.js"></script>
  <script src="protovis-msie.min.js"></script>
  <link rel="stylesheet" type="text/css" href="index.css"></link>
  <title>Networked Corpus Index</title>
  <script>
this_doc = null;
  </script>
 </head>
 <body>
  <div id="header">
    <div style="margin-bottom:5px">
      The Wealth of Nations
    </div>
    <div style="margin-left:auto;margin-right:auto">
      <a href="index.html">Table of contents</a> |
      List of topics |
      <a href="smith-index.html">1784 index</a>
    </div>
    <div id="top-topic-area" style="float:right">
    </div>
  </div>
  <div id="main-area">
    <table id="text-table">
'''

# End of the generated List of topics file.
topic_index_html2 = u'''
    </table>
  </div>
 </body>
</html>
'''

# CUSTOM: preface of the reconstruction of 1784 index.
smith_index_html1 = u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <script src="docs_by_topic.js"></script>
  <script src="topic_names.js"></script>
  <script src="doc_names.js"></script>
  <script src="extracts.js"></script>
  <script src="index-data.js"></script>
  <script src="jquery.js"></script>
  <script src="common.js"></script>
  <script src="index.js"></script>
  <link rel="stylesheet" type="text/css" href="index.css"></link>
  <title>Networked Corpus Index</title>
  <script>
this_doc = null;
  </script>
 </head>
 <body>
  <div id="header">
    <div style="margin-bottom:5px">
      The Wealth of Nations
    </div>
    <div style="margin-left:auto;margin-right:auto">
      <a href="index.html">Table of contents</a> |
      <a href="topic-index.html">List of topics</a> |
      1784 index
    </div>
    <div id="top-topic-area" style="float:right">
    </div>
  </div>
  <div id="main-area">
    <table id="text-table">
'''

# End of the generated List of topics file.
smith_index_html2 = u'''
    </table>
  </div>
 </body>
</html>
'''

# List of files to copy to the output directory (from the 'res' directory
# in the directory in which the script resides).
resource_files = ['browser.css', 'index.css',
                  'common.js', 'browser.js', 'index.js',
                  'jquery.js', 'protovis.min.js', 'protovis-msie.min.js',
                  'notch-left.png']

def tokenize(s):
    # A horrible hack to get around the fact that Python's RE engine
    # can't easily match (unicode) alphabetical characters only.
    sprime = re.sub('([^\w]|[0-9_])', '\x00\\1\x00', s,
                    flags=re.UNICODE)
    return re.split('\x00+', sprime, flags=re.UNICODE)

def truncate(f):
    # Replace very small numbers with 0.  We do this because SVG can't
    # parse floating point numbers with 3-digit exponents in paths (?).
    if abs(f) < 1.0e-5:
        return 0.0
    return f

def alphanumeric_sort(l): 
    # Sort alphabetically, but handle multi-digit numbers correctly.
    return sorted(l, key=lambda s: [int(x) if x.isdigit() else x
                                    for x in re.split('([0-9]+)', s)] )

def parse_subdoc(subdoc):
    # Parse the standard form in which subunit filenames are supposed to be.
    subdoc = os.path.split(subdoc)[-1]
    try:
        subdoc_base, ext = subdoc.split('.')
    except ValueError:
        subdoc_base = subdoc
        ext = None
    try:
        doc, subdoc_index = subdoc_base.split('-')
        subdoc_index = int(subdoc_index)
    except ValueError:
        print ('Error: for the --model-trained-on-subunits option to'
               ' work, the files passed to MALLET must be of the'
               ' form "docname-subunit[.ext]" where docname is the'
               ' base name of one of the complete text files and'
               ' subunit is an integer.')
        exit()
    if ext is not None:
        doc += '.' + ext
    return doc, subdoc_index

def gen_annotations(indir, in_doc_topics, in_topic_keys, in_topic_state,
                    outdir, min_topic_appearances, min_pointedness,
                    num_words_per_topic, resdir, bandwidth,
                    extra_stopwords, subunits):

    topic_state = {}
    topic_appearances_by_doc = {}
    top_topics_by_doc = {}
    docs_by_topic = {}
    top_words_by_topic = {}

    # CUSTOM: load the index and index matches.
    index = pickle.load(open('index.pkl'))
    heading_matches, topic_matches = pickle.load(open('matches.pkl'))

    # CUSTOM: invert the index.
    reverse_index = {}
    for heading in index:
        for subheading, doc in index[heading]:
            doc = '{0:03}'.format(doc)
            reverse_index.setdefault(doc, set()).add(heading)

    # Load 'stopwords.txt' from the resource directory, as well as the
    # file with additional stopwords (if one is specified).
    stopwords_file = open(os.path.join(resdir, 'stopwords.txt'))
    stopwords = stopwords_file.read().split(' ')
    stopwords_file.close()
    if extra_stopwords:
        extra_stopwords_file = codecs.open(extra_stopwords, 'r', 'utf-8')
        stopwords += tokenize(extra_stopwords_file.read())
        extra_stopwords_file.close()
    stopwords = set(stopwords)

    # Load the data from the MALLET topic-state file.
    f = gzip.open(in_topic_state, 'r')
    f.readline(); f.readline(); f.readline()
    if subunits:
        subunit_topic_state = {}

        # The topic_stage.gz file will be organized by subunit, so we will
        # need to do some reconstruction.
        for line in f.readlines():
            line = unicode(line, 'utf-8').strip()
            subdocnum, subdoc, pos, wordtypeindex, wordtype, topic \
                = line.split(' ')
            topic = int(topic)
            # Figure out which of the original documents this is a subunit of.
            doc, subunit_index = parse_subdoc(subdoc)
            subunit_topic_state.setdefault(doc, {}) \
                .setdefault(subunit_index, []) \
                .append((wordtype, topic))
            topic_appearances_by_doc.setdefault(doc, set()).add(topic)

        # Construct topic state for the original documents.
        for doc in subunit_topic_state:
            for subunit_index in sorted(subunit_topic_state[doc].keys()):
                topic_state.setdefault(doc, [])
                topic_state[doc] += subunit_topic_state[doc][subunit_index]

    else:
        for line in f.readlines():
            line = unicode(line, 'utf-8').strip()
            docnum, doc, pos, wordtypeindex, wordtype, topic = line.split(' ')
            topic = int(topic)
            doc = os.path.split(doc)[-1]
            topic_state.setdefault(doc, []) \
                .append((wordtype, topic))
            topic_appearances_by_doc.setdefault(doc, set()).add(topic)

    # Load the data from the MALLET doc-topic file
    f = open(in_doc_topics, 'r')
    f.readline()
    topic_coefs_by_doc = {}
    for line in f.readlines():
        line = line.split('\t')
        doc = line[1].split('/')[-1].replace('%20', ' ').replace('%3F', '?')
        line = line[2:]
        ntopics = len(line) / 2
        if ntopics > 9:
            ntopics = 9;
        if subunits:
            doc, subunit_index = parse_subdoc(doc)
        for i in xrange(0, ntopics):
            topic = int(line[i*2])
            coef = float(line[i*2 + 1])
            # Only include topics that account for at least one word.
            if topic in topic_appearances_by_doc[doc]:
                topic_coefs_by_doc.setdefault(doc, {}).setdefault(topic, 0.0)
                topic_coefs_by_doc[doc][topic] += coef
                # If we are in subunit mode, we will come across each
                # document multiple times, so we sum up all the coefs.

    # Sort out the top topics by document.
    for doc in topic_coefs_by_doc:
        for topic in sorted(topic_coefs_by_doc[doc],
                            key=lambda topic: -topic_coefs_by_doc[doc][topic])[:9]:
            top_topics_by_doc.setdefault(doc, []).append(topic)
        # CUSTOM: we need to save the topic coefficients.
        for topic in sorted(topic_coefs_by_doc[doc],
                            key=lambda topic: -topic_coefs_by_doc[doc][topic]):
            docs_by_topic.setdefault(topic, []).append((doc, topic_coefs_by_doc[doc][topic]))

    # Load the data from the MALLET topic-keys file.
    f = codecs.open(in_topic_keys, 'r', 'utf-8')
    for line in f.readlines():
        line = line.strip()
        topic, n, words = line.split('\t') # What is the second value?
        topic = int(topic)
        top_words_by_topic[topic] = words.split(' ')[:num_words_per_topic]

    # Create the output directory (if necessary).
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    elif not os.path.isdir(outdir):
        print >>sys.stderr, ("Error: '{0}' exists but is not a directory!"
                             .format(outdir))
        exit()

    # Generate and save topic names.
    topic_names = dict([(topic, ' '.join(top_words_by_topic[topic]
                                         [:num_words_per_topic]))
                        for topic in top_words_by_topic])
    outf = open(os.path.join(outdir, 'topic_names.js'), 'w')
    outf.write('topic_names = ' + json.dumps(topic_names) + ';\n')

    # Convert the individual documents to HTML and add annotations,
    # also saving the text of the lines where the link for a given
    # topic will plant you in the document, and getting a list of the
    # documents with links for each topic.
    extracts = {}
    firstlines = {}
    pointed_topics_by_doc = {}
    docs_by_pointed_topic = {}
    current_book = None
    current_chapter = None
    Chapter_queue = collections.deque(Chapters)
    for doc in os.listdir(indir):
        state = list(topic_state[doc])
        pointed_topics_by_doc[doc] = []
        
        while Chapter_queue and Chapter_queue[0][1] == int(doc):
            section_name, _ = Chapter_queue.popleft()
            if section_name.startswith('Book'):
                current_book = section_name
            else:
                current_chapter = section_name

        f = codecs.open(os.path.join(indir, doc), 'r', 'utf-8')
        text = f.read()
        f.close()
        lines = text.split(u'\n')
        nlines = len(lines)
        firstlines[doc] = lines[0]
        line_toks = [tokenize(line) for line in lines]

        # Scour the topic state to find the topic assignments for each
        # token in this document.  Also save the line numbers on which
        # words associated with each of the top topics appear.
        line_toks_annotated = []
        topic_appearances = {}
        ntoks = 0
        for i, toks in enumerate(line_toks):
            ntoks += len(toks)
            toks_annotated = []
            for tok in toks:
                match_tok = tok.lower()
                # The last condition is because the first line is supposed
                # to contain a title that is not included in a subunit.
                if match_tok.isalpha() and match_tok not in stopwords \
                        and not (subunits and i == 0):
                    wordtype, topic = state.pop(0)
                    if wordtype != match_tok:
                        print doc, 'line', i, ': expected', wordtype, \
                            'but found', match_tok
                        exit()
                else:
                    topic = None
                toks_annotated.append((tok, topic))
                topic_appearances.setdefault(topic, []) \
                    .append(i)
            line_toks_annotated.append(toks_annotated)

        # Compute estimates of the density of each top topic over the
        # lines of the document, and identify which topics are 'pointed'.
        topic_density_fcns = {}
        topic_density_maxima = {}
        for topic in top_words_by_topic:
            if not (topic in top_topics_by_doc[doc]
                    or topic in pointed_topics_by_doc[doc]):
                continue
            appearances = [float(x) for x in topic_appearances[topic]]
            try:
                # Compute the KDE if possible.
                kde = scipy.stats.gaussian_kde(appearances)
            except ValueError:
                continue
            except numpy.linalg.linalg.LinAlgError:
                continue
            # SciPy lets you set a bandwidth adjustment factor that gets 
            # squared and multiplied by the variance of the data to determine
            # the actual bandwidth.  We want to set the bandwidth directly,
            # so we need to work around this.
            kde.set_bandwidth(1.0)
            kde.set_bandwidth(math.sqrt(bandwidth / float(kde.covariance[0])))
            topic_density_fcns[topic] = [truncate(kde(float(i))[0])
                                         for i in xrange(nlines)]
            # Identify 'pointed' topics.
            if len(appearances) < min_topic_appearances:
                continue
            maximum = numpy.argmax(topic_density_fcns[topic])
            mean = float(kde.integrate_box_1d(0.0, nlines - 1.0)) \
                / nlines
            if topic_density_fcns[topic][maximum] \
                    > mean * min_pointedness:
                topic_density_maxima.setdefault(maximum, []).append(topic)
                pointed_topics_by_doc[doc].append(topic)
                docs_by_pointed_topic.setdefault(topic, []).append(doc)
    
        # Create an HTML document with all of the words associated with
        # top topics marked as such, and annotations added to the lines
        # of greatest density for each top topic.
        outf = codecs.open(os.path.join(outdir, doc + '.html'), 'w', 'utf-8')
        outf.write(html1.format(firstlines[doc]))
        # Save the density functions.
        outf.write('<script>\n')
        outf.write('density_fcns = ' + json.dumps(topic_density_fcns) + ';\n')
        outf.write('this_doc = "' + doc + '";\n')
        # CUSTOM: display only pointed topics on the page.
        outf.write('top_topics = ' + json.dumps(pointed_topics_by_doc[doc]) + ';\n')
        # CUSTOM: save the index headings for this page.
        outf.write('index_headings = '
                   + json.dumps(sorted(reverse_index.get(doc, []))) + ';\n')
        outf.write('book = ' + json.dumps(current_book) + ';\n')
        outf.write('chapter = ' + json.dumps(current_chapter) + ';\n')
        outf.write('</script>\n')
        outf.write('<table id="text-table">')
        extracts[doc] = {}
        for i, toks in enumerate(line_toks_annotated):
            if i == 0:
                outf.write('<tr class="first-row"><td class="text-line">')
            elif i == nlines - 1:
                outf.write('<tr class="last-row"><td class="text-line">')
            else:
                outf.write('<tr><td class="text-line">')
            if i in topic_density_maxima:
                for topic in topic_density_maxima[i]:
                    outf.write('<a name="topic' + str(topic) + '">')
                    if len(toks) == 1 and toks[0][0] == u'':
                        # Avoid pulling blank lines as extracts.
                        if i < len(line_toks_annotated) - 1:
                            extract_toks = line_toks_annotated[i + 1]
                        else:
                            extract_toks = line_toks_annotated[i - 1]
                    else:
                        extract_toks = toks
                    extracts[doc][topic] = ''.join(tok for tok, topic
                                                   in extract_toks)
            for tok, topic in toks:
                if topic in top_topics_by_doc[doc] \
                        or topic in pointed_topics_by_doc[doc]:
                    outf.write('<span class="topic' + str(topic) + '">' +
                               tok + '</span>')
                else:
                    outf.write(tok)
            if i in topic_density_maxima:
                for topic in topic_density_maxima[i]:
                    outf.write('</a>')
            if i == 0:
                outf.write('&nbsp;</td><td rowspan="'
                           + str(nlines + 1)
                           + '" id="chart-cell" valign="top">'
                           + '<div id="chart-area"><div id="chart">'
                           + '</div></div></td>'
                           + '<td class="marginal-link-cell">')
            else:
                outf.write('&nbsp;</td><td class="marginal-link-cell">')
            if i in topic_density_maxima:
                for topic in topic_density_maxima[i]:
                    outf.write('<span class="marginal-link" id="'
                               + str(topic) + '"></span>')
            if i == 0:
                outf.write('</td><td valign="top" rowspan="'
                           + str(nlines)
                           + '" id="popup-cell">'
                           + '<div id="popup-area"></div></td></tr>\n')
            else:
                outf.write('</td></tr>\n')

        outf.write('</table>')
        outf.write(html2)

    # Sort the lists of top docs.
    for topic in docs_by_topic:
        d = docs_by_topic[topic]
        docs_by_topic[topic] = sorted(d, key=lambda x: -x[1])
    for topic in docs_by_pointed_topic:
        d = docs_by_pointed_topic[topic]
        docs_by_pointed_topic[topic] = alphanumeric_sort(d)

    # CUSTOM: process the topic/index heading matches and get a list of
    # matched headings to display in the List of topics.
    for heading in heading_matches:
        # Eliminate weak matches to save space.
        matches = heading_matches[heading]
        heading_matches[heading] = [(topic, corr)
                                    for (topic, corr, left, inner, right)
                                    in matches
                                    if corr >= 0.15]
        if not heading_matches[heading]:
            # Always include at least one.
            topic, corr, left, inner, right = matches[0]
            heading_matches[heading] \
                = [(topic, corr, list(left), list(inner), list(right))]
    for topic in topic_matches:
        matches = topic_matches[topic]
        topic_matches[topic] = [(heading, corr)
                                for (heading, corr, left, inner, right)
                                in matches
                                if corr >= 0.15]
        if not topic_matches[topic]:
            heading, corr, left, inner, right = matches[0]
            topic_matches[topic] \
                = [(heading, corr, list(left), list(inner), list(right))]
    # Maps the headings to their best-matching topics.
    matched_headings = {}
    for heading in heading_matches:
        if len(heading_matches[heading]) \
                and heading_matches[heading][0][1] >= 0.20:
            matched_headings[heading] = heading_matches[heading][0][0]
    # Sort by the numbers of the best-matching topics, so that we get an ordering
    # that shows the match-up reasonably well.
    matched_headings = sorted(matched_headings.keys(),
                              key=lambda x: matched_headings[x])
    matched_heading_queue = collections.deque(matched_headings)

    # Save the matches.
    outf = open(os.path.join(outdir, 'matches.js'), 'w')
    outf.write('heading_matches = ' + json.dumps(heading_matches) + ';\n')
    outf.write('topic_matches = ' + json.dumps(topic_matches) + ';\n')

    # Save the list of documents to display for each topic.
    outf = open(os.path.join(outdir, 'docs_by_topic.js'), 'w')
    outf.write('docs_by_pointed_topic = ' + json.dumps(docs_by_pointed_topic) + ';\n')
    outf.write('docs_by_topic = ' + json.dumps(docs_by_topic) + ';\n')

    # Save the list of document names
    outf = open(os.path.join(outdir, 'doc_names.js'), 'w')
    outf.write('doc_names = ' + json.dumps(firstlines) + ';\n')

    # Save the extracts.
    outf = codecs.open(os.path.join(outdir, 'extracts.js'), 'w', 'utf-8')
    outf.write('extracts = ' + json.dumps(extracts) + ';\n')

    # Save the index.
    outf = codecs.open(os.path.join(outdir, 'index-data.js'), 'w', 'utf-8')
    outf.write('index = ' + json.dumps(index) + ';\n')

    # Create the index file.
    # CUSTOM: this is created manually
#     outf = codecs.open(os.path.join(outdir, 'index.html'), 'w', 'utf-8')
#     outf.write(index_html1)
#     docs = alphanumeric_sort(os.listdir(indir))
#     ndocs = len(docs)
#     for i, doc in enumerate(docs):
#         if i == 0:
#             outf.write('<tr class="first-row">')
#         elif i == ndocs - 1:
#             outf.write('<tr class="last-row">')
#         else:
#             outf.write('<tr>')
#         outf.write('<td class="index-entry"><a href="' + doc
#                    + '.html">' + doc + '</a>: '
#                    + firstlines[doc] + '</td></tr>')
#     outf.write(index_html2)

    # Create the List of topics file.
    outf = codecs.open(os.path.join(outdir, 'topic-index.html'), 'w', 'utf-8')
    outf.write(topic_index_html1)
    outf.write('<script>matched_headings = '
               + json.dumps(matched_headings) + ';</script>')
    topic_list = sorted(top_words_by_topic.keys())
    ntopics = len(topic_list)
    nheadings = len(matched_heading_queue)
    for i, topic in enumerate(topic_list):
        if i == 0:
            outf.write('<tr class="first-row">')
        elif i == ntopics - 1 and len(matched_heading_queue) == 1:
            outf.write('<tr class="last-row last-matched-heading">')
        elif i == ntopics - 1:
            outf.write('<tr class="last-row">')
        elif len(matched_heading_queue) == 1:
            outf.write('<tr class="last-matched-heading">')
        else:
            outf.write('<tr>')
        # CUSTOM: add the matched headings.
        if matched_heading_queue:
            heading = matched_heading_queue.popleft()
            outf.write('<td class="matched-heading" id="heading' + str(heading)
                       + '"><a href="smith-index.html#' + heading
                       + '">' + heading + '</a></td>')
        else:
            outf.write('<td class="matched-heading"></td>')
        if i == 0:
            outf.write('<td valign="top" rowspan="'
                       + str(max(ntopics, nheadings))
                       + '" id="match-cell"><div id="match-area"></div></td>')
        outf.write('<td class="index-entry" id="' + str(topic)
                   + '"><a class="topic-link" '
                   + 'href="javascript:show_index_popup('
                   + str(topic) + ')">Topic ' + str(topic) + '</a>: '
                   + topic_names[topic].encode('ascii', 'xmlcharrefreplace')
                   + '</td>')
        if i == 0:
            outf.write('<td valign="top" rowspan="' + str(max(ntopics, nheadings) + 1)
                       + '" id="popup-cell"><div id="popup-area"></div></td>')
        outf.write('</tr>')
    while matched_heading_queue:
        if len(matched_heading_queue) == 1:
            outf.write('<tr class="last-matched-heading">')
        else:
            outf.write('<tr>')
        heading = matched_heading_queue.popleft()
        outf.write('<td class="matched-heading" id="heading' + str(heading)
                   + '"><a href="smith-index.html#' + heading
                   + '">' + heading + '</a></td>')
        outf.write('<td class="blank-index-entry"></td></tr>')
    outf.write('<tr><td>&nbsp;</td><td>&nbsp;</td><td class="blank-index-entry">&nbsp;</td></tr>')
    outf.write(topic_index_html2)

    # CUSTOM: create the 1784 index file.
    outf = codecs.open(os.path.join(outdir, 'smith-index.html'), 'w', 'utf-8')
    outf.write(smith_index_html1)
    heading_list = sorted(index.keys())
    nheadings = len(heading_list)
    nsubheadings = sum(len(index[heading]) for heading in index)
    for i, heading in enumerate(heading_list):
        if i == 0:
            outf.write('<tr class="first-row">')
        else:
            outf.write('<tr>')
        outf.write('<td class="index-heading"><a id="' + str(heading)
                   + '">' + str(heading) + '</a></td>')
        if i == 0:
            outf.write('<td valign="top" rowspan="'
                       + str(nheadings + nsubheadings + 1)
                       + '" id="popup-cell"><div id="popup-area"></div></td>')
        outf.write('</tr>')
        for j, (subheading, pagenum) in enumerate(index[heading]):
            if j > 0 and subheading == index[heading][j-1][0]:
                # An additional page for the previous subheading.  Don't start a new row.
                outf.write(', <a href="' + '{0:03}'.format(pagenum)
                           + '.html">' + str(pagenum) + '</a>')
            else:
                if j > 0:
                    outf.write('</td></tr>')
                outf.write('<tr><td class="index-subheading">'
                           + subheading.encode('ascii', 'xmlcharrefreplace')
                           + ' <a href="' + '{0:03}'.format(pagenum)
                           + '.html">' + str(pagenum) + '</a>')
        outf.write('</td></tr>')
    outf.write(smith_index_html2)

    # Copy the resource files to the output directory.
    for filename in resource_files:
        shutil.copy(os.path.join(resdir, filename), outdir)


if __name__ == '__main__':
    parser = optparse.OptionParser(description=description_text,
                                   usage='%prog --input-dir=INDIR'
                                   '--output-dir=OUTDIR [options]')

    parser.add_option('--input-dir', dest='indir', action='store',
                      help='directory containing text files')

    parser.add_option('--input-doc-topics', dest='in_doc_topics',
                      action='store', default='doc_topics.txt',
                      help="location of the 'doc-topics' file from"
                      " MALLET (default 'doc_topics.txt')")

    parser.add_option('--input-topic-keys', dest='in_topic_keys',
                      action='store', default='topic_keys.txt',
                      help="location of the 'topic-keys' file from"
                      " MALLET (default 'topic_keys.txt')")

    parser.add_option('--input-topic-state', dest='in_topic_state',
                      action='store', default='topic_state.gz',
                      help="location of the 'topic-state' file from"
                      " MALLET (default 'topic_state.gz')")

    parser.add_option('--output-dir', dest='outdir', action='store',
                      help='directory in which to deposit the HTML files')

    parser.add_option('--word-cutoff', dest='min_topic_appearances',
                      type=float, action='store', default=30,
                      help='minimum number of words a topic must contribute'
                      ' to a document to be linked (default 30)')

    parser.add_option('--pointedness-cutoff', dest='min_pointedness',
                      type=float, action='store', default=0.0,
                      help='minimum ratio of maximum : average density'
                      ' for a link to be established (default 0.0)')

    parser.add_option('--words-per-topic', dest='num_words_per_topic',
                      type=int, action='store', default=7,
                      help='number of words per topic to display (default 10)')

    parser.add_option('--kde-bandwidth', dest='bandwidth',
                      type=float, action='store', default=6.0,
                      help='amount of smoothing to apply to the density'
                      ' functions (default 6.0)')

    parser.add_option('--extra-stopwords', dest='extra_stopwords',
                      type=str, action='store', default=None,
                      help='file (whitespace-delimited) containing extra'
                      ' stopwords')

    parser.add_option('--model-trained-on-subunits', dest='subunits',
                      action='store_true',
                      help='indicates that the model was trained on subunits'
                      ' of the texts (e.g. paragraphs)')

    (options, args) = parser.parse_args()

    if not (options.indir and options.outdir):
        parser.error('--input-dir and --output-dir must be specified!')

    gen_annotations(resdir=os.path.join(sys.path[0], 'res'),
                    **options.__dict__)
