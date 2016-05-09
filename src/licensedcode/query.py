#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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
from itertools import chain
import textwrap

from bitarray import bitarray

from licensedcode import NGRAM_LENGTH
from licensedcode.tokenize import query_lines
from licensedcode.tokenize import query_ngrams
from licensedcode.tokenize import query_tokenizer
from licensedcode.tokenize import query_multigrams


"""
Build license queries from scanned files.
"""

TRACE_REPR = False


class Query(object):
    """
    A query represent a whole file or string being matched, holding tokens and a
    positions line index. A query is broken down in one or more "runs" that are
    logical chunks of tokens used as a matching unit.
    """

    def __init__(self, location=None, query_string=None, idx=None,
                 line_threshold=4, _test_mode=False):
        """
        Initialize the query from a location or query string for an idx LicenseIndex.
        """
        assert (location or query_string) and idx
        self.location = location
        self.query_string = query_string
        self.idx = idx

        self.line_threshold = line_threshold
        # token ids array
        self.tokens = []

        # index of position -> line number
        self.line_by_pos = {}

        # track positions that are still matchable
        self.matchable_positions = set()

        self.query_runs = []
        if not _test_mode:
            tbl = self.tokens_by_line()
            self.tokenize(tbl, line_threshold=line_threshold)
            self.set_matchable_positions()

    def tokens_by_line(self):
        """
        Yield a sequence of token_ids for each line of this query and populate
        the query line_by_pos mapping as a side effect.
        """
        dic_get = self.idx.dictionary.get
        # positions start at zero
        pos = 0
        # lines start at one
        for lnum, line  in enumerate(query_lines(self.location, self.query_string), 1):
            line_tokens = []
            for token in query_tokenizer(line):
                tid = dic_get(token)
                if tid is not None:
                    self.line_by_pos[pos] = lnum
                line_tokens.append(tid)
                pos += 1
            yield line_tokens

    def tokenize(self, tokens_by_line, line_threshold=4):
        """
        Tokenize this query, populating the tokens, line_by_pos and query runs
        at each break points.

        `tokens_by_line` is the output of the tokens_by_line() method. 
        `line_threshold` is the number of empty or junk lines to break a new run.
        """
        len_junk = self.idx.len_junk

        # initial query run
        query_run = QueryRun(query=self, start=0)

        # break in runs based on threshold of lines that are either empty, all
        # unknown or all junk jokens.
        empty_lines = 0

        # token positions start at zero
        pos = 0

        for tokens in tokens_by_line:
            # have we reached a run break point?
            if len(query_run) > 0 and empty_lines >= line_threshold:
                self.query_runs.append(query_run)

                # start new query run
                query_run = QueryRun(query=self, start=pos)
                empty_lines = 0

            if len(query_run) == 0:
                query_run.start = pos

            if not tokens:
                empty_lines += 1
                continue

            line_has_known_tokens = False
            line_has_good_tokens = False

            for token_id in tokens:
                self.tokens.append(token_id)
                if token_id is not None:
                    line_has_known_tokens = True
                    if token_id >= len_junk:
                        line_has_good_tokens = True
                    query_run.end = pos

                pos += 1

            if not line_has_known_tokens:
                empty_lines += 1
                continue

            if line_has_good_tokens:
                empty_lines = 0
            else:
                empty_lines += 1

        # yield final run if any
        if len(query_run) > 0:
            self.query_runs.append(query_run)

    def set_matchable_positions(self):
        for pos, token_id in enumerate(self.tokens):
            if token_id is not None:
                self.matchable_positions.add(pos)

    def whole_query_run(self):
        """
        Return a query run built from the whole query.
        """
        return QueryRun(query=self, start=0, end=len(self.tokens) - 1)

    def subtract(self, qspan):
        """
        Update this query matchable positions by removing a matched positions
        qspan from matchable positions.
        """
        if not qspan:
            return
        self.matchable_positions.difference_update(qspan)


class QueryRun(object):
    """
    A query run is a slice of query tokens identified by a start and end
    positions, inclusive. It is akin to a view on the whole query tokens
    sequence.
    """
    def __init__(self, query, start, end=-1):
        """
        Initialize a query run starting at start for a parent query.
        """
        self.query = query
        # absolute start position of this run in the query
        self.start = start

        # absolute end position of this run in the query
        self.end = end

        self._vector = None
        self._bv = None
        self._freqs = None

        # passed from the Query, to track still matchable positions on the whole query
        self.line_by_pos = query.line_by_pos
        self.matchable_positions = query.matchable_positions
        self._tokens_range = range(self.query.idx.len_tokens)


    def __len__(self):
        if self.end < 0:
            return 0
        return self.end - self.start + 1

    def __repr__(self):
        data = self.start, len(self)
        if TRACE_REPR:
            data += (u' '.join('None' if tid is None else self.query.idx.tokens_by_tid[tid] for tid in self.tokens),)
            return 'QueryRun<start=%d, len=%d, tokens=%r>' % data
        return 'QueryRun<start=%d, len=%d>' % data

    @property
    def tokens(self):
        return self.query.tokens[self.start: self.end + 1]

    def _as_dict(self, brief=False):
        """
        Return a human readable dictionary representing the query replacing
        token ids with their string values. If brief is True, the tokens
        sequence will be truncated to show only the first 5 and last five tokens
        of the run. 
        Used for debugging and testing.
        """
        tokens_by_tid = self.query.idx.tokens_by_tid

        def tokens_string(tks):
            "Return a string from a token id seq"
            return u' '.join((tid is not None and tid >= 0) and tokens_by_tid[tid] or u'None' for tid in tks)

        if brief and len(self.tokens) > 10:
            tokens = tokens_string(self.tokens[:5]) + u' ... ' + tokens_string(self.tokens[-5:])
        else:
            tokens = tokens_string(self.tokens)

        return {
            'start': self.start,
            'end': self.end,
            'matchable': self.matchable(),
            'tokens': tokens,
        }

    def bv(self):
        """
        Return a bitvector built from this run tokens.
        """
        if not self._bv:
            self._bv = bitarray(self.vector())
        return self._bv

    def matchable(self):
        """
        Return True if this query run has some matchable tokens.
        """
        len_junk = self.query.idx.len_junk
        match_poss = self.matchable_positions
        if not match_poss and match_poss is not None:
            return False
        left_to_match = self.pos_tokens()
        if match_poss is not None:
            left_to_match = ((pos, tid) for pos, tid in left_to_match if pos in match_poss)
        return any(tid >= len_junk for _pos, tid in left_to_match)

    def pos_tokens(self):
        """
        Return an iterable of (pos, token) where pos is the absolute position in
        the original query.
        """
        for pos, token_id in enumerate(self.tokens, self.start):
            yield pos, token_id
            if pos == self.end:
                break

    def vector(self):
        """
        Build and return a query vector from the accumulated tokens. The query
        vector is a list of lists of absolute positions, similar to the inverted
        index structure: the index in the outer list is a token id.
        """
        if not self._vector:
            vector = [[] for _ in range(self.query.idx.len_tokens)]
            for pos, token_id in self.pos_tokens():
                if (self.matchable_positions is not None
                and pos in self.matchable_positions):
                        vector[token_id].append(pos)
            self._vector = vector
        return self._vector

    def ngrams(self, ngram_length=NGRAM_LENGTH):
        """
        Return an iterable of (start, ngram) tuples for this query tokens.
        The start is the absolute token position in the whole query,
        """
        for start, ngram in query_ngrams(self.tokens, ngram_length=ngram_length, start=self.start):
            # only return ngrams that have no position already matched
            if self.matchable_positions is not None:
                if any(p not in self.matchable_positions for p in range(start, start + ngram_length)):
                    continue
            yield start, ngram

    def multigrams(self, len_junk, ngram_length=NGRAM_LENGTH):
        """
        Return an iterable of (start, ngram) tuples for this query tokens.
        The start is the absolute token position in the whole query,
        """
        return query_multigrams(self.tokens, ngram_length=ngram_length, len_junk=len_junk, offset=self.start)

    def frequencies(self, start=0):
        """
        Return a Counter of token ids for this run. Start is the len_junk.
        """
        # FIXME: would iterating tokens and using tokens lists/arrays be faster?
        if not self._freqs:
            allf = Counter({tid: len(postings) for tid, postings in enumerate(self.vector()) if postings})
            highf = Counter({tid: lposts for tid, lposts in allf.items() if tid >= start})
            lowf = Counter({tid: lposts for tid, lposts in allf.items() if tid < start})
            self._freqs = highf, lowf
        return self._freqs

    def subtract(self, matched_positions):
        """
        Subtract matched positions from the parent query matchable positions.
        Reset query run cached data structures.
        """
        if not matched_positions:
            return
        self.query.subtract(matched_positions)
        self._vector = None
        self._bv = None
        self._freqs = None


def matched_query_tokens_str(match, location=None, query_string=None, dictionary=None):
    """
    Return an iterable of matched query token strings given a query file at
    `location` or a `query_string`, a match and a dictionary. Yield None for
    unmatched positions.

    Punctuation is removed , spaces are normalized (new line is replaced by a
    space), case is preserved. 

    Used primarily to recover the matched texts for testing or reporting.
    """
    assert dictionary
    pos = -1
    started = False
    finished = False
    tokens = (query_tokenizer(line, lower=False) for line in query_lines(location, query_string))
    tokens = chain.from_iterable(tokens)
    for pos, token in enumerate(tokens):
        token_id = dictionary.get(token.lower())
        if token_id is None:
            if not started:
                continue
            if finished:
                break

        if match.qspan.start <= pos <= match.qspan.end:
            started = True
            if pos == match.qspan.end:
                finished = True

            tok = None
            if token_id is not None and pos in match.qspan:
                tok = token
            yield tok


def matched_rule_tokens_str(match):
    """
    Return an iterable of matched rule token strings given a match. Yield None
    for unmatched positions. Yield <gap> for gaps.

    Punctuation is removed , spaces are normalized (new line is replaced by a
    space), case is preserved.

    Used primarily to recover the matched texts for testing or reporting.
    """
    span = match.ispan
    gaps = match.rule.gaps
    for pos, token in enumerate(match.rule.tokens(lower=False)):
        if span.start <= pos <= span.end:
            tok = None
            if pos in span:
                tok = token
            yield tok
            if gaps and pos in gaps:
                yield '<gap>'


def get_texts(match, location=None, query_string=None, dictionary=None, width=120):
    """
    Given a match and a query location of query string return a tuple of:
    - the matched query text as a string.
    - the matched rule text as a string.

    Used primarily to recover the matched texts for testing or reporting.

    Unmatched positions are represented as <no-match>, rule gaps as <gap>. 
    Punctuation is removed , spaces are normalized (new line is replaced by a
    space), case is preserved. 

    If `width` is a number superior to zero, the texts are wrapped to width.
    """
    assert dictionary

    nomatch = lambda s: s or '<no-match>'
    matched_qtokens = map(nomatch, matched_query_tokens_str(match, location, query_string, dictionary))
    matched_itokens = map(nomatch, matched_rule_tokens_str(match))

    # return wrapped texts
    noop = lambda x: x
    wrap = width and partial(textwrap.wrap, width=width, break_on_hyphens=False) or noop
    return (u'\n'.join(wrap(u' '.join(matched_qtokens))),
            u'\n'.join(wrap(u' '.join(matched_itokens))))
