# -*- coding: utf-8 -*-
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

from collections import defaultdict

from intbitset import intbitset

import typecode

from licensedcode.tokenize import query_lines
from licensedcode.tokenize import query_tokenizer


"""
Build license queries from scanned files to feed the detection pipeline.

A query is a sequence of tokens.
Queries are further broken down in query runs that are "slices" of a query.

Several heuristics are used to break down a query in query runs and this process is
important to the overall speed and accuracy of license detection: since the most
costly parts of detection is done query run by query run, and sequence alignment is
performed on the best ranking candidates from a probalistic ranking, the defintion of
what chunk should be matched matters a lot.

If too small, chunking would favour alignment against smaller rules and increase the
processing time as more alignments would need to be computed. If too big, chunking
would eschew alignment against smaller rules.

So based on the chunk side, the alignment may be stuck on working with a suboptimal
set of candidate rules yielding possibly matches that are too small and scattered to
make sense when matches are merged.

If chunks are bigger, this decreases the sensitivity to more specific smaller rules
and would mistakenly report licenses that may contain the text of other smaller
licenses instead of larger longer licenses. But this does speed up detection as fewer
alignments need to be compued. So rather than breaking the queries using a single way
for all queries, we compute crude statistics on the query text "structure" using the
counts of lines, empty lines, lines with unknown tokens, lines with junk tokens and
decide how to break a query based on these.

For instance, some HTML or code file may be very sparse and their source have a lot
of empty lines. However, this is is most often due to the original text having been
transformed when encoded as HTML or an artifact of some generated HTML or HTML
editor. When we can detect these, we can eventually ignore heuristics to break
queries based on sequences of empty lines. (Note this is not yet implemented for
HTML).

Conversely, a file text could be very dense and may contain a single line or only a
few lines of text as can happen with minified JavaScript. In these cases counting
lines is useless and other heuristic are needed.
"""

# Tracing flags
TRACE = False
TRACE_REPR = False


def logger_debug(*args):
    pass

if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


def build_query(location=None, query_string=None, idx=None):
    """
    Return a Query built from location or querty string given an index.
    """
    if location:
        T = typecode.get_type(location)
        # TODO: implement additional type-driven heuristics for query chunking.
        if not T.contains_text:
            return
        if T.is_binary:
            # for binaries we want to avoid a large number of query runs as the
            # license context is often very sparse or absent
            qry = Query(location=location, idx=idx, line_threshold=1000)
        else:
            # for text
            qry = Query(location=location, idx=idx, line_threshold=80)
    else:
        # a string is always considered text
        qry = Query(query_string=query_string, idx=idx)

    return qry


class Query(object):
    """
    A query represent a whole file or string being scanned for licenses. It holds
    tokens, token line positions and query runs. It also tracks which parts have been
    matched as matching progresses.

    A query is broken down in one or more "runs" that are slices of tokens used as a
    matching unit.
    """
    # use slots for a small lower memory usage
    __slots__ = (
        'location',
        'query_string',
        'idx',
        'line_threshold',
        'tokens',
        'line_by_pos',
        'unknowns_by_pos',
        'shorts_and_digits_pos',
        'query_runs',
        'high_matchables',
        'low_matchables',
    )

    def __init__(self, location=None, query_string=None, idx=None,
                 line_threshold=4, _test_mode=False, tokenizer=query_tokenizer):
        """
        Initialize the query from a file `location` or `query_string` string for an
        `idx` LicenseIndex.

        Break query in runs when there are at least `line_threshold` empty lines or
        junk-only lines.
        """
        assert (location or query_string) and idx

        self.location = location
        self.query_string = query_string
        self.idx = idx

        self.line_threshold = line_threshold

        # token ids array
        self.tokens = []

        # index of position -> line number where the pos is the list index
        self.line_by_pos = []

        # index of known position -> number of unknown tokens after that pos
        # for unknowns at the start, the pos is -1
        self.unknowns_by_pos = defaultdict(int)

        # set of query position were there is a short, single letter token or digits-only token
        # TODO: consider using an intbitset
        self.shorts_and_digits_pos = set()

        self.query_runs = []
        if _test_mode:
            return

        self.tokenize_and_build_runs(self.tokens_by_line(tokenizer=tokenizer), line_threshold=line_threshold)

        # sets of integers initialized after query tokenization
        len_junk = idx.len_junk
        self.high_matchables = intbitset([p for p, t in enumerate(self.tokens) if t >= len_junk])
        self.low_matchables = intbitset([p for p, t in enumerate(self.tokens) if t < len_junk])

    def whole_query_run(self):
        """
        Return a query run built from the whole range of query tokens.
        """
        return QueryRun(query=self, start=0, end=len(self.tokens) - 1)

    def subtract(self, qspan):
        """
        Subtract the qspan matched positions from the query matchable positions.
        """
        if qspan:
            self.high_matchables.difference_update(qspan)
            self.low_matchables.difference_update(qspan)

    @property
    def matchables(self):
        """
        Return a set of every matchable token positions for this query.
        """
        return self.low_matchables | self.high_matchables

    def tokens_with_unknowns(self):
        """
        Yield the original tokens stream with unknown tokens represented by None.
        """
        unknowns = self.unknowns_by_pos
        # yield anything at the start
        for _ in range(unknowns[-1]):
            yield None

        for pos, token in enumerate(self.tokens):
            yield token
            for _ in range(unknowns[pos]):
                yield None

    def tokens_by_line(self, tokenizer=query_tokenizer):
        """
        Yield one sequence of tokens for each line in this query.
        Populate the query `line_by_pos`, `unknowns_by_pos`, `unknowns_by_pos` and
        `shorts_and_digits_pos` as a side effect.
        """
        # bind frequently called functions to local scope
        line_by_pos_append = self.line_by_pos.append
        self_unknowns_by_pos = self.unknowns_by_pos
        self_shorts_and_digits_pos_add = self.shorts_and_digits_pos.add
        dic_get = self.idx.dictionary.get

        # note: positions start at zero
        # this is the absolute position, including the unknown tokens
        abs_pos = -1
        # lines start at one
        line_start = 1

        # this is a relative position, excluding the unknown tokens
        known_pos = -1

        started = False
        for lnum, line  in enumerate(query_lines(self.location, self.query_string), line_start):
            line_tokens = []
            line_tokens_append = line_tokens.append
            for abs_pos, token in enumerate(tokenizer(line), abs_pos + 1):
                tid = dic_get(token)
                if tid is not None:
                    known_pos += 1
                    started = True
                    line_by_pos_append(lnum)
                    if len(token) == 1 or token.isdigit():
                        self_shorts_and_digits_pos_add(known_pos)
                else:
                    # we have not yet started
                    if not started:
                        self_unknowns_by_pos[-1] += 1
                    else:
                        self_unknowns_by_pos[known_pos] += 1
                line_tokens_append(tid)
            yield line_tokens

    def tokenize_and_build_runs(self, tokens_by_line, line_threshold=4):
        """
        Tokenize this query and populate tokens and query_runs at each break point.
        Only keep known token ids but consider unknown token ids to break a query in
        runs.

        `tokens_by_line` is the output of the tokens_by_line() method.
        `line_threshold` is the number of empty or junk lines to break a new run.
        """
        len_junk = self.idx.len_junk

        # initial query run
        query_run = QueryRun(query=self, start=0)

        # break in runs based on threshold of lines that are either empty, all
        # unknown or all low id/junk jokens.
        empty_lines = 0

        # token positions start at zero
        pos = 0

        # bind frequently called functions to local scope
        tokens_append = self.tokens.append
        query_runs_append = self.query_runs.append

        for tokens in tokens_by_line:
            # have we reached a run break point?
            if (len(query_run) > 0 and empty_lines >= line_threshold):
                # start new query run
                query_runs_append(query_run)
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
                if token_id is not None:
                    tokens_append(token_id)
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

        # append final run if any
        if len(query_run) > 0:
            self.query_runs.append(query_run)

        if TRACE:
            logger_debug('Query runs for query:', self.location)
            map(print, self.query_runs)


class QueryRun(object):
    """
    A query run is a slice of query tokens identified by a start and end positions
    inclusive.
    """
    __slots__ = ('query', 'start', 'end', 'len_junk', '_low_matchables', '_high_matchables')

    def __init__(self, query, start, end=None):
        """
        Initialize a query run from starting at `start` and ending at `end` from a
        parent `query`.
        """
        self.query = query

        # absolute start and end positions of this run in the query
        self.start = start
        self.end = end

        self.len_junk = self.query.idx.len_junk

        self._low_matchables = None
        self._high_matchables = None

    @property
    def low_matchables(self):
        if not self._low_matchables:
            self._low_matchables = intbitset(
                [pos for pos in self.query.low_matchables
                 if self.start <= pos <= self.end])
        return self._low_matchables

    @property
    def high_matchables(self):
        if not self._high_matchables:
            self._high_matchables = intbitset(
                [pos for pos in self.query.high_matchables
                 if self.start <= pos <= self.end])
        return self._high_matchables

    def __len__(self):
        if self.end is None:
            return 0
        return self.end - self.start + 1

    def __repr__(self, trace_repr=TRACE_REPR):
        base = (
            'QueryRun('
                'start={start}, len={length}, '
                'start_line={start_line}, end_line={end_line}'
        )
        if trace_repr:
            base += ', tokens="{tokens}"'
        base += ')'
        return base.format(**self.to_dict(brief=False, comprehensive=True))

    @property
    def start_line(self):
        return self.query.line_by_pos[self.start]

    @property
    def end_line(self):
        return self.query.line_by_pos[self.end]

    @property
    def tokens(self):
        if self.end is None:
            return []
        return self.query.tokens[self.start: self.end + 1]

    def tokens_with_unknowns(self):
        """
        Yield the original tokens stream including unknown tokens (represented
        by None).
        """
        unknowns = self.query.unknowns_by_pos
        # yield anything at the start only if this is the first query run
        if self.start == 0:
            for _ in range(unknowns[-1]):
                yield None

        for pos, token in self.tokens_with_pos():
            yield token
            if pos == self.end:
                break
            for _ in range(unknowns[pos]):
                yield None

    def tokens_with_pos(self):
        return enumerate(self.tokens, self.start)

    def is_matchable(self, include_low=False, qspans=None):
        """
        Return True if this query run has some matchable high tokens.
        If a list of qspans is provided, their positions are first subtracted.
        """
        if include_low:
            matchables = self.matchables
        else:
            matchables = self.high_matchables

        if not qspans:
            return matchables

        matched = intbitset.union(*[q._set for q in qspans])
        matchables = intbitset(matchables)
        matchables.difference_update(matched)
        return matchables

    @property
    def matchables(self):
        """
        Return a set of every matchable token ids positions for this query.
        """
        return self.low_matchables | self.high_matchables

    def matchable_tokens(self):
        """
        Return an iterable of matchable tokens tids for this query run.
        Return an empty list if there are no high matchable tokens.
        Return -1 for positions with non-matchable tokens.
        """
        high_matchables = self.high_matchables
        if not high_matchables:
            return []
        return (tid if pos in (high_matchables | self.low_matchables) else -1
                for pos, tid in self.tokens_with_pos())

    def subtract(self, qspan):
        """
        Subtract the qspan matched positions from the parent query matchable
        positions.
        """
        if qspan:
            self.query.subtract(qspan)
            # also update locally: this is a property hence the side effect
            self.high_matchables
            self._high_matchables.difference_update(qspan)

            # also update locally: this is a property hence the side effect
            self.low_matchables
            self._low_matchables.difference_update(qspan)

    def to_dict(self, brief=False, comprehensive=False):
        """
        Return a human readable dictionary representing the query run replacing
        token ids with their string values. If brief is True, the tokens
        sequence will be truncated to show only the first 5 and last five tokens
        of the run. Used for debugging and testing.
        """
        tokens_by_tid = self.query.idx.tokens_by_tid

        def tokens_string(tks):
            "Return a string from a token id seq"
            return u' '.join('None' if tid is None else tokens_by_tid[tid] for tid in tks)

        if brief and len(self.tokens) > 10:
            tokens = tokens_string(self.tokens[:5]) + u' ... ' + tokens_string(self.tokens[-5:])
        else:
            tokens = tokens_string(self.tokens)

        to_dict = dict(
            start=self.start,
            end=self.end,
            tokens=tokens,
        )
        if comprehensive:
            to_dict.update(dict(
                start_line=self.start_line,
                end_line=self.end_line,
                length=len(self),
            ))
        return to_dict
