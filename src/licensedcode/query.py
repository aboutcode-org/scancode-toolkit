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

from collections import Counter
from functools import partial
import textwrap

from textcode.analysis import text_lines

from licensedcode import NGRAM_LENGTH
from licensedcode import match
from licensedcode.tokenize import ngrams
from licensedcode.tokenize import query_tokenizer


"""
Build license queries from scanned files .
"""

DEBUG_REPR = False


def iterlines(location=None, query_string=None, with_empty=False):
    """
    Given a file at location or a query string, return an iterable of (line_num,
    line text). Line numbers start at one.
    """
    # TODO: OPTIMIZE: tokenizing line by line may be rather slow
    # we could instead get lines and tokens at once in a batch?
    if location:
        lines = text_lines(location)
    elif query_string:
        lines = query_string.splitlines(False)
    else:
        lines = []

    # line numbers starts at one
    for line_num, line in enumerate(lines, 1):
        if line:
            line = line.strip()
        if with_empty:
            yield line_num, line
        else:
            if line:
                yield line_num, line


class QueryRun(object):
    """
    A query run is a chunk of query tokens.
    """
    __slots__ = 'idx', 'start', 'tokens', 'line_by_pos', '_tokens_range'
    def __init__(self, idx, start):
        self.idx = idx
        # absolute position of this run in the query
        self.start = start

        # note: tokens may be updated afterwards
        self.tokens = []

        self.line_by_pos = {}

        self._tokens_range = range(self.idx.len_tokens)

    def __repr__(self):
        if DEBUG_REPR:
            data = (self.start, len(self.tokens), self.matchable(),
                    u' '.join(self.idx.tokens_by_tid[tid] for tid in self.tokens),)
            return 'QueryRun<start=%d, len=%d, matchable=%r, tokens=%r>' % data
        else:
            data = (self.start, len(self.tokens), self.matchable(),)
            return 'QueryRun<start=%d, len=%d, matchable=%r>' % data

    def __eq__(self, other):
        return (isinstance(other, QueryRun)
            and self.tokens == other.tokens
            and self.start == other.start
            and self.line_by_pos == other.line_by_pos)

    def __hash__(self):
        """
        QueryRuns are hashable.
        """
        return hash((self.start, tuple(self.tokens), tuple(self.line_by_pos.items())))

    def __copy__(self):
        nqr = QueryRun(self.idx, self.start)
        nqr.tokens = self.tokens[:]
        nqr.line_by_pos = dict(self.line_by_pos)
        return nqr
        
    def _as_dict(self, brief=False):
        """
        Return a human readable dictionary representing the query replacing
        token ids with their string values. If brief is True, the tokens
        sequence will be truncated to show only the first 5 and last five tokens
        of the run. 
        Used for debugging and testing.
        """
        tokens_by_tid = self.idx.tokens_by_tid

        def tokens_string(tks):
            "Return a string from a token id seq"
            return u' '.join((tid is not None and tid >= 0) and tokens_by_tid[tid] or u'None' for tid in tks)

        if brief and len(self.tokens) > 10:
            tokens = tokens_string(self.tokens[:5]) + u' ... ' + tokens_string(self.tokens[-5:])
        else:
            tokens = tokens_string(self.tokens)

        return {
            'start': self.start,
            'matchable': self.matchable(),
            'tokens': tokens,
            'lines': (min(self.line_by_pos.values()), max(self.line_by_pos.values()),)
        }

    def bv(self):
        """
        Return a bitvector built from this run tokens.
        """
        return build_bv(self.tokens, self.idx.bv_template)

    def matchable(self):
        """
        Return True if this query run has some matchable tokens.
        """
        return any(tid >= self.idx.len_junk for tid in self.tokens)

    def tokens_pos(self):
        """
        Return an iterable of (pos, token) where pos is the absolute position in
        the original query.
        """
        for pos, token_id in enumerate(self.tokens, self.start):
            yield pos, token_id

    def vector(self):
        """
        Build and return a query vector from the accumulated tokens. The query
        vector is a list of lists of absolute positions, similar to the inverted
        index structure: the index in the outer list is a token id.
        """
        vector = [[] for _ in self._tokens_range]
        for pos, token_id in self.tokens_pos():
            if token_id is not None:
                vector[token_id].append(pos)
        return vector

    def ngrams(self, _ngram_length=NGRAM_LENGTH):
        """
        Return an iterable of (ngram, start,) tuples for this query tokens.
        """
        # FIXME: wee should return start, ngram instead
        return query_ngrams(self.tokens, self.start, _ngram_length)

    def frequencies(self):
        """
        Return a Counter of token ids for this run.
        """
        # FIXME: would iterating tokens be faster?
        return Counter({tid: len(postings) for tid, postings in enumerate(self.vector()) if postings})

    def substract(self, matches):
        """
        Update this query run given a sequence of LicenseMatch by replacing
        token query positions contained in any LicenseMatch by None.
        """
        mposses = match.query_positions(matches, offset=self.start)
        self.tokens = [None if pos in mposses else tid for pos, tid in enumerate(self.tokens)]


def build_bv(tokens, bv_template):
        bv  = bv_template.copy()
        st = set(t for t in tokens if t is not None)
        for token_id in st:
            bv[token_id] = True
        return bv


class Query(object):
    """
    Keep track of a file being queried for licenses, exposing various derived
    data structures as required for matching.
    """
    def __init__(self, location=None, query_string=None, idx=None):
        """
        Initialize the query from a location or query string and a LicenseIndex.
        """
        assert (location or query_string) and idx
        self.location = location
        self.query_string = query_string
        self.idx = idx

    def query_runs(self, line_threshold=3):
        """
        Yield QueryRun objects for this query.
        line_threshold is the threshold is number of empty of junk lines to break a new run
        """
        len_junk = self.idx.len_junk

        # initial query run
        query_run = QueryRun(self.idx, start=0)

        # TODO: add junk/unknown threshold

        # break in runs based on lines either empty, all unknown or all junk
        empty_lines = 0

        # positions start at zero: note that we ignore unknown positions
        pos = 0
        for line_num, line  in iterlines(self.location, self.query_string, with_empty=True):
            # have we reached a run break point?
            if query_run.tokens and empty_lines >= line_threshold:
                yield query_run

                # start new query run
                query_run = QueryRun(self.idx, start=pos)
                empty_lines = 0

            if not line:
                empty_lines += 1
                continue

            line_has_known_tokens = False
            line_has_good_tokens = False

            for token in query_tokenizer(line):
                token_id = self.idx.dictionary.get(token)
                if token_id is not None:
                    line_has_known_tokens = True
                    if token_id >= len_junk:
                        line_has_good_tokens = True
                    query_run.tokens.append(token_id)
                    query_run.line_by_pos[pos] = line_num
                    # TODO: optimize: we could build the initial vector, ngrams and more early on
                    pos += 1

            if not query_run.tokens:
                query_run.start = pos

            if not line_has_known_tokens:
                empty_lines += 1
                continue

            if line_has_good_tokens:
                empty_lines = 0
            else:
                empty_lines += 1

        # yield final run if any
        if query_run.tokens:
            yield query_run


def query_ngrams(query_tokens, start=0, _ngram_length=NGRAM_LENGTH):
    """
    Return an iterable of (ngram, start,) tuples given an iterable of query
    (token, pos) tuples. Skip ngrams that contain a None as a side effect of
    filtering.
    """
    return ((ngram, start,) for start, ngram in enumerate(ngrams(query_tokens, _ngram_length), start=start) if None not in ngram)


def _query_token_strings(location=None, query_string=None, dictionary=None, lower=False):
    """
    Return an iterable of (normalized query token strings, real_pos, query_pos)
    given a file at `location` or a `query_string` [one of these is required].

    real_pos is the absolute real token position in the original query stream.

    query_pos is the token position assigned during internal query processing
    where unknown tokens position were skipped.

    Punctuation is removed. Does not lowercase tokens by default. Set lower to
    True to get lowercase tokens.

    Used primarily to recover the matched texts for testing or reporting.
    """
    assert dictionary
    real_pos = 0
    query_pos = 0
    token_is_known = False
    for _line_num, line in iterlines(location, query_string):
        for token in query_tokenizer(line, lower):
            token_id = dictionary.get(token.lower())
            if token_id is None:
                # return -1 for query_pos until we have at least started counting one known index token
                _query_pos = -1 if not token_is_known else query_pos
                yield None, real_pos, _query_pos
            else:
                token_is_known = True
                yield token, real_pos, query_pos
                query_pos += 1
            real_pos += 1


def get_texts(match, location=None, query_string=None, dictionary=None, width=120, no_match='<no-match>'):
    """
    Given a match and a query location of query string return a tuple of:
    - the matched query text as a string.
    - the matched rule text as a string.

    Unmatched positions are represented as <no-match>.
    The punctuation is stripped from strings. Token case is preserved.
    If width is a number superior to zero, the returned texts are wrapped to that width.
    Used for testing and final reporting.
    """
    assert dictionary

    # rebuild matched query text
    matched_qpos = match.qspan
    matched_qstart = match.qspan.start
    matched_qend = match.qspan.end
    matched_qtokens = []
    qstarted = False
    for token, _real_pos, query_pos in _query_token_strings(location, query_string, dictionary):
        if query_pos == -1:
            continue

        if query_pos < matched_qstart or query_pos > matched_qend:
            continue

        if query_pos in matched_qpos:
            qtok = token or no_match
        else:
            qtok = no_match

        if not qstarted:
            if qtok == no_match:
                continue
            else:
                qstarted = True
        matched_qtokens.append(qtok)

    # rebuild matched index text
    matched_ipos = match.ispan

    matched_itokens = []
    for pos, token in enumerate(match.rule.tokens(lower=False)):
        if pos in matched_ipos:
            itok = token or no_match
            matched_itokens.append(itok)

    # return wrapped texts
    noop = lambda x: x
    wrap = width and partial(textwrap.wrap, width=width, break_on_hyphens=False) or noop
    return (u'\n'.join(wrap(u' '.join(matched_qtokens))),
            u'\n'.join(wrap(u' '.join(matched_itokens))))
