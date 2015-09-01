#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import print_function, absolute_import

from collections import defaultdict
from functools import partial
import logging

from textcode import analysis
from textcode.analysis import Token


logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


DEBUG = False
DEBUG_CANDIDATES = False
DEBUG_ALIGN = False
if DEBUG or DEBUG_CANDIDATES or DEBUG_ALIGN:
    from pprint import pformat


def posting_list():
    """
    Per doc postings mapping a docid to a list of positions.
    """
    return defaultdict(list)


def build_empty_indexes(ngram_len):
    """
    Build and return the nested indexes structure.

    The resulting index structure can be visualized this way::

    1. The unigrams index is in indexes[1] with this structure:
    {1:
     {
      u1: {index_docid1: [posting_list1], index_docid2: [posting_list2]},
      u2: {index_docid1: [posting_list3], index_docid3: [posting_list4]}
     }
    }

    2. The bigrams index is in indexes[2] with this structure:
    {2:
     {
      u3, u4: {index_docid1: [posting_list7], index_docid2: [posting_list6]},
      u5, u6: {index_docid1: [posting_list5], index_docid3: [posting_list8]}
     }
    }
    and so on, until ngram_len
    """
    indexes = {}
    for i in range(1, ngram_len + 1):
        indexes[i] = defaultdict(posting_list)
    return indexes


def tokenizers(ngram_len=analysis.DEFAULT_NGRAM_LEN):
    """
    Return a tuple of specialized tokenizers given an `ngram_len` for each
    of: (plain text, template text, query text).
    """
    text = partial(analysis.ngram_tokenizer, template=False, ngram_len=ngram_len)
    template = partial(analysis.ngram_tokenizer, template=True, ngram_len=ngram_len)
    query = partial(analysis.multigram_tokenizer, ngram_len=ngram_len)
    return text, template, query


class Index(object):
    """
    An index is used to index reference documents and then match query documents
    against these reference documents.

    Terms used here:
     - index_doc: indexed document
     - index_docid: indexed document ID
     - query_doc: query document
     - query_docid: query document ID

    We use several inverted indexes mapping a Token value to a list of
    per Token positions for each indexed document ID (index_docid): There is one
    index for every ngram length from one up to ngram_len.

    These multiple indexes handle cases where the a query document text to
    detect cannot matched with a given ngram length for instance when there are
    regions of text with fewer tokens than an ngram length such as with very
    short query documents or very short indexed documents. This approach ensures
    that we can detect texts of (very) short texts such as GPL_v2 which is only
    two tokens once tokenized and could not be detected with an ngram length of
    three.

    Typically indexes for smaller ngrams length are rather small and contain
    short (but important) documents.

    Templated indexed documents (i.e. with gaps) are supported for all ngram
    lengths.

    These cases are supported:
     - small index_doc or query_doc with fewer tokens than ngram length.

     - small regions of text between two template regions with fewer tokens
       than an ngram length.

     - small regions of text at the beginning of an index_doc just before a
       template region and with fewer tokens than an ngram length.

     - small regions of text at the end of an index_doc and just after a template
       region and with fewer tokens than an ngram length.
    """

    def __init__(self, ngram_len=analysis.DEFAULT_NGRAM_LEN):
        self.ngram_len = ngram_len
        self.text_tknzr, self.template_tknzr, self.query_tknzr = tokenizers(ngram_len)

        # the nested indexes structure
        self.indexes = build_empty_indexes(ngram_len)

        # a mapping of docid to a count of Tokens in an index_doc
        self.tokens_count_per_index_doc = {}

    def _get_index_for_len(self, length):
        return self.indexes[length]

    def _index_token(self, docid, token):
        """
        Index a single token for a document with `docid`.
        """
        # token.length gets us the index to populate for a certain ngram length
        idx_for_ngramlen = self._get_index_for_len(token.length)
        idx_for_ngramlen[token.value][docid].append(token)

    def _lookup_token(self, token):
        """
        Lookup a token in the appropriate index. Return the postings or None.
        """
        idx_for_ngramlen = self._get_index_for_len(token.length)
        return idx_for_ngramlen.get(token.value)

    def get_tokens_count(self, index_docid):
        return self.tokens_count_per_index_doc[index_docid]

    def set_tokens_count(self, index_docid, val):
        self.tokens_count_per_index_doc[index_docid] = val

    def index_one(self, docid, doc, template=False):
        """
        Index one `doc` document where `docid` is a document identifier and
        `doc` is an iterable of unicode text lines. Use the template tokenizer
        if template is True.
        """
        if template:
            tokenizer = self.template_tknzr
        else:
            tokenizer = self.text_tknzr

        self.index_one_from_tokens(docid, tokenizer(doc))

    def index_one_from_tokens(self, docid, tokens):
        """
        Index one document where `docid` is a document identifier and `tokens`
        is an iterable of tokens.
        """
        for token in tokens:
            # token.length gets us the index to populate for a certain ngram length
            idx_for_ngramlen = self._get_index_for_len(token.length)
            idx_for_ngramlen[token.value][docid].append(token)
        if tokens:
            # set the tokens count for a doc to the end of the last token
            # the token start/end is zero-based. So we increment the count by one
            self.set_tokens_count(docid, token.end + 1)

    def _index_many(self, docs, template=False):
        """
        Index a `docs` iterable of (docid, doc) tuples where `docid` is a
        document identifier and `doc` is an iterable of unicode text lines.
        Use a template tokenizer if template is True.
        """
        for docid, doc in docs:
            self.index_one(docid, doc, template)

    def match(self, query_doc, perfect=True):
        """
        Return matches as a mapping of matched index docid to a list of tuples
        (matched index doc pos, matched query doc pos).

        Match `query_doc` against the index where `query_doc` is an iterable
        of unicode text lines.

        Only check for perfect, exact matches if `perfect` is True.
        """
        if not query_doc:
            return {}

        # get candidates sharing at least one ngram
        candidate_matches = self.candidates(query_doc)

        if not candidate_matches:
            return {}

        all_results = defaultdict(list)

        by_index_position_start = lambda x: x[0].start

        # first find contiguous matches
        for docid, matches in candidate_matches.items():
            sorted_matches = sorted(matches, key=by_index_position_start)
            for idx, match in enumerate(sorted_matches):
                index_position, query_position = match
                # perfect contiguous matches must start at index_position 0
                if index_position.start != 0:
                    break
                else:
                    # TODO: "if not perfect " if we are not starting at 0
                    # collect partial matches
                    pass
                # start of a possible full match at index_position 0
                subset = sorted_matches[idx + 1:]

                if DEBUG:
                    lsub = len(subset) + 1
                    print('     Index.match: about to align %(lsub)r '
                          'candidate matches for %(docid)r:\n'
                          'index_position: %(index_position)r\nquery_position: %(query_position)r\n'
                          % locals())

                matched_positions = self.align_matches(index_position, query_position, subset)

                if DEBUG:
                    lmp = len(matched_positions)
                    print('    Index.match: aligned %(lmp)r matches for '
                          '%(docid)r. Now merging' % locals())

                merged = merge_aligned_positions(matched_positions)

                if DEBUG:
                    lmrg = len(merged)
                    print('    Index.match: merged %(lmp)r aligned '
                          'matches in %(lmrg)r positions for %(docid)r'
                          % locals())
                    print('    Index.match: merged positions are: '
                          '\n%s\n' % pformat(merged))

                if merged:
                    all_results[docid].append(merged)

        filtered = self.filter_matches(all_results, perfect)
        return filtered

    def align_matches(self, cur_index_position, cur_query_position, matches):
        """
        Given a first match as position 0 and subsequent potential matches, try
        to find a longer match skipping eventual gaps to yield a perfect
        alignment.

        This how ngrams are handled with ngram_len of 3:
        -----------------------------------------------
        With this index_doc and this query_doc:
        index_doc:   name is joker, name is joker
        ngrams: name is joker, is joker name, joker name is, name is joker
                i0             i1             i2             i3
        query_doc: Hi my name is joker, name is joker yes.
        ngrams: hi my name, my name is, name is joker, is joker name, joker name is, name is joker, is joker yes
                q0          q1          q2             q3             q4             q5             q6
        will yield these candidates:
            i0, q2 (name is joker)
            i0, q5 (name is joker) ==> this should be skipped because q5 does not follow q2
            i1, q3 (is joker name)
            i2, q4 (joker name is)
            i3, q2 (name is joker) ==> this should be skipped because q2 does not follow q4
            i3, q5 (name is joker)

        And this how gaps are handled, abstracting ngrams:
        --------------------------------------------------
        With this  index_doc and this query_doc::
        index_doc: my name is {{2 Joe}} the joker
                   i0 i1   i2-g2        i3  i4
        query_doc: Yet, my name is Jane Heinz the joker.
                   q0   q1 q2   q3 q4   q5    q6  q7
        will yield these candidates:
            i0, q1
            i1, q2
            i2-g2, q3
            i3, q6 : here q6 <= q3 + 1 + g2
            i4, q7
        With the same index_doc and this query_doc:
        query_doc: Yet, my name is Jane the joker.
                   q0   q1 q2   q3 q4   q5  q6
        will yet these candidates:
            i0, q1
            i1, q2
            i2-g2, q3
            i3, q5 : here q5 <= q3 + 1 + g2
            i4, q7
        """

        # add first match
        matched = [(cur_index_position, cur_query_position,)]
        cumulative_gap = 0

        if DEBUG_ALIGN:
            print()

        for match in matches:
            prev_index_position, prev_query_position = matched[-1]
            cumulative_gap += prev_index_position.gap
            cur_index_position, cur_query_position = match

            if DEBUG_ALIGN:
                print(''.join(['Index.aligned match: positions \n',
                      '  prev_index_position: %(start)r %(end)r %(value)r\n' % prev_index_position._asdict(),
                      '   cur_index_position : %(start)r %(end)r %(value)r\n' % cur_index_position._asdict(),
                      '  prev_query_position: %(start)r %(end)r %(value)r\n' % prev_query_position._asdict(),
                      '   cur_query_position : %(start)r %(end)r %(value)r' % cur_query_position._asdict(),
                      ]))

                print('Index.aligned match: prev_index_position.start:%d < '
                      'cur_index_position.start:%d <= prev_index_position.end + 1:%d'
                      % (prev_index_position.start, cur_index_position.start,
                         prev_index_position.end + 1,))

            if (prev_index_position.start < cur_index_position.start <= prev_index_position.end + 1):

                if DEBUG_ALIGN:
                    print('Index.aligned match: possible contiguous tokens')

                # we are contiguous in index_position: are we contiguous in query_position?
                if prev_query_position.start + 1 == cur_query_position.start:

                    if DEBUG_ALIGN:
                        print('Index.aligned match: Keeping contiguous '
                              'tokens: prev_query_position.start + 1 '
                              '== cur_query_position.start\n')

                    matched.append((cur_index_position, cur_query_position,))
                    continue
                else:
                    # we are not contiguous, but could we be when gaps are
                    # considered?

                    if DEBUG_ALIGN:
                        print('Index.aligned match: '
                              'prev_query_position.start:%d < cur_query_position.start:%d '
                              '<= prev_query_position.start + 1 + cumulative_gap '
                              '+ self.ngram_len: %d' %
                              (prev_query_position.start, cur_query_position.start,
                               prev_query_position.start + cumulative_gap + self.ngram_len,))

                    if (prev_query_position.start < cur_query_position.start and
                        cur_query_position.start <= (prev_query_position.start + cumulative_gap + self.ngram_len)):
                        # we are contiguous gap-wise, keep this match

                        if DEBUG_ALIGN:
                            print('Index.aligned match: Keeping gap-wise contiguous tokens\n')

                        matched.append((cur_index_position, cur_query_position,))
                    continue
            else:
                if DEBUG_ALIGN:
                    print('Index.aligned match: Skipping tokens\n')

                continue
        return matched

    def candidates(self, query_doc):
        """
        Find candidate matches for query_doc against index where query doc is
        an iterable of unicode text lines. Return candidate matches as a
        mapping of:
        matched index docid -> sorted set of tuples (matched index doc pos,
                                                     matched query doc pos).
        """
        if DEBUG_CANDIDATES:
            print()
            print('=>Index.candidates: entering')
            query_doc = list(query_doc)
            print(' Index.candidates: Query doc has %d lines.' % len(query_doc))
            print(u''.join(query_doc))
            print()
            query_doc = iter(query_doc)

        # map index_docid -> sorted set of tuples (index_position, query_position)
        candidate_matches = defaultdict(list)
        # iterate over query_doc tokens using query_tknzr
        for qtoken in self.query_tknzr(query_doc):
            if DEBUG_CANDIDATES:
                print('  Index.candidates: processing\n   %(qtoken)r' % locals())

            # query the proper inverted index for the value len, aka the ngram length
            matches = self._lookup_token(qtoken)

            if not matches:
                continue
            # accumulate matches for each docid
            for docid, postings in matches.items():
                for itoken in postings:
                    if DEBUG_CANDIDATES:
                        print('  Index.candidates: %(docid)r matched from:\n      %(itoken)r\n      %(qtoken)r' % locals())

                    candidate_matches[docid].append((itoken, qtoken))
        return candidate_matches

    def filter_matches(self, all_matches, perfect=True):
        """
        Filter matches such as non-perfect or overlapping matches. If perfect
        is True, return only perfect matches.
        """
        if DEBUG:
            print('=>Index.filter_matches entering with perfect %r' % perfect)

        if not perfect:
            # TODO: implement me
            return all_matches
        else:
            # keep only perfect matches
            kept_results = defaultdict(list)
            for docid, matches in all_matches.iteritems():
                tok_cnt = self.get_tokens_count(docid)
                for index_position, query_position in matches:
                    # perfect matches length must match the index_doc token count
                    # the token count is 1-based, the end is zero-based
                    # FIXME: this does not make sense with gaps
                    if tok_cnt == index_position.end + 1:
                        kept_results[docid].append((index_position, query_position))
            return kept_results


def merge_aligned_positions(positions):
    """
    Given a sequence of tuples of (index_doc, query_doc) Token positions, return
    a single tuple of new (index_doc, query_doc) Token positions representing
    the merged positions from every index_position and every query_position.
    """
    index_docs, query_docs = zip(*positions)
    return merge_positions(index_docs), merge_positions(query_docs)


def merge_positions(positions):
    """
    Given a iterable of Token positions, return a new merged Token position
    computed from the first and last positions.

    Does not keep gap and token values. Does not check if positions are
    contiguous or overlapping.
    """
    positions = sorted(positions)
    first = positions[0]
    last = positions[-1]
    return Token(start=first.start, end=last.end,
                 start_line=first.start_line, start_char=first.start_char,
                 end_line=last.end_line, end_char=last.end_char)
