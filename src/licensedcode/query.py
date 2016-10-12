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

Queries are further broken down in query runs that are "slices" of query.
Several heuristics are used to break down the query runs and this process is
quite central to overall speed and accuracy of license detection: since
detection is done query run by query run, and sequence alignment is performed on
the best ranking candidates from a probalistic ranking, the defintion of what
chunkc should be matched matters a lot. If too small, it will favour smaller
rules and increased the processing time as more searches need to be done. Each
search may be stuck on a suboptimal set of candidate rules eventually too small
to make sense when matches are merged. If too big, it decreases the sensitivity
to more specific smaller rules and would mistakenly report licenses that may
contain the text of other smaller licenses. But it does speed up detection as
fewer searches nee to be done. So rather than breaking the queries using a
single universal way for any query, we compute crude statistics on the query
text "structure" using the counts of lines, empty lines, lines with unknown
tokens, lines with junk tokens and decide how to break a query based on these.

For instance, some HTML or code file may be very sparse and their source have a
lot of empty lines. However, this is is most often due to the text having been
damaged or an artifact of some generted HTML or HTML editor. When we can detect
these, we can eventually ignore heuristic to break queries based on sequences of
empty lines.

Conversely, some file may be very dense and may have contain a single line or
only a few lines as can happen in minified JavaScript. In these cases counting
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
        qtype = typecode.get_type(location)
        if qtype.is_binary:
            # use a high number of lines per run for binaries, avoiding too many runs
            qry = Query(location=location, idx=idx, line_threshold=40)
        else:
            qry = Query(location=location, idx=idx, line_threshold=40)
    else:
        qry = Query(query_string=query_string, idx=idx)

    return qry


class Query(object):
    """
    A query represent a whole file or string being matched, holding tokens and a
    line positions.

    A query is broken down in one or more "runs" that are slices of tokens used
    as a matching unit.
    """

    def __init__(self, location=None, query_string=None, idx=None,
                 line_threshold=4, _test_mode=False, tokenizer=query_tokenizer):
        """
        Initialize the query from a location or query string for an idx
        LicenseIndex.

        Break query in runs when there are at least `line_threshold` empty lines
        or junk-only lines.
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

        # index of known position -> number of unknown tokens after that pos
        # for unknowns at the start, the pos is -1
        self.unknowns_by_pos = defaultdict(int)

        self.query_runs = []
        if _test_mode:
            return

        self.tokenize(self.tokens_by_line(tokenizer=tokenizer), line_threshold=line_threshold)

        # sets of integers initialized after query tokenization
        len_junk = idx.len_junk
        self.high_matchables = intbitset([p for p, t in enumerate(self.tokens) if t >= len_junk])
        self.low_matchables = intbitset([p for p, t in enumerate(self.tokens) if t < len_junk])

    def whole_query_run(self):
        """
        Return a query run built from the whole query.
        """
        return QueryRun(query=self, start=0, end=len(self.tokens) - 1)

    def subtract(self, qspan):
        """
        Subtract the qspan matched positions from the parent query matchable
        positions.
        """
        if qspan:
            self.high_matchables.difference_update(qspan)
            self.low_matchables.difference_update(qspan)

    @property
    def matchables(self):
        """
        Return a set of every matchable token ids positions for the whole query.
        """
        return self.low_matchables | self.high_matchables

    def tokens_with_unknowns(self):
        """
        Yield the original tokens stream including unknown tokens (represented
        by None).
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
        Yield a sequence of token_ids from this query, one sequence for each line.
        Populate the query `line_by_pos` and `unknowns_by_pos` mappings as a side
        effect.
        """
        line_by_pos = self.line_by_pos
        self_unknowns_by_pos = self.unknowns_by_pos
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
                    line_by_pos[known_pos] = lnum
                else:
                    # we have not yet started
                    if not started:
                        self_unknowns_by_pos[-1] += 1
                    else:
                        self_unknowns_by_pos[known_pos] += 1
                line_tokens_append(tid)
            yield line_tokens

    def tokenize(self, tokens_by_line, line_threshold=4):
        """
        Tokenize this query and populate the tokens and query runs at each break
        points. Only keep known token ids but consider unknown token ids to
        break a query in runs.

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


class QueryRun(object):
    """
    A query run is a slice of whole query tokens identified by a start and end
    positions inclusive.
    """
    def __init__(self, query, start, end=None):
        """
        Initialize a query run starting at start and ending at end a parent
        query tokens sequence.
        """
        self.query = query

        # absolute start and end positions of this run in the query
        self.start = start
        self.end = end

        self.len_junk = self.query.idx.len_junk

        # lines by positions, used for final reporting
        self.line_by_pos = query.line_by_pos
        # positions with unknown tokens, used for final reporting
        self.unknowns_by_pos = query.unknowns_by_pos

    def __len__(self):
        if self.end is None:
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
        if self.end is None:
            return []
        return self.query.tokens[self.start: self.end + 1]

    def tokens_with_unknowns(self):
        """
        Yield the original tokens stream including unknown tokens (represented
        by None).
        """
        unknowns = self.unknowns_by_pos
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

    @property
    def low_matchables(self):
        return intbitset([pos for pos in self.query.low_matchables if self.start <= pos <= self.end])

    @property
    def high_matchables(self):
        return intbitset([pos for pos in self.query.high_matchables if self.start <= pos <= self.end])

    def is_matchable(self):
        """
        Return True if this query run has some matchable high tokens.
        """
        return self.high_matchables

    @property
    def matchables(self):
        """
        Return a set of every matchable token ids positions for this query.
        """
        return self.low_matchables | self.high_matchables

    def matchable_tokens(self, only_high=False):
        """
        Return an iterable of matchable tokens tids for this query run either
        only high or every tokens ids.
        """
        if not self.high_matchables:
            return []
        matchables = self.matchables
        if only_high:
            matchables = self.high_matchables
        return (tid if pos in matchables else -1 for pos, tid in self.tokens_with_pos())

    def subtract(self, qspan):
        """
        Subtract the qspan matched positions from the parent query matchable
        positions.
        """
        self.query.subtract(qspan)

    def _as_dict(self, brief=False):
        """
        Return a human readable dictionary representing the query replacing
        token ids with their string values. If brief is True, the tokens
        sequence will be truncated to show only the first 5 and last five tokens
        of the run. Used for debugging and testing.
        """
        tokens_by_tid = self.query.idx.tokens_by_tid

        def tokens_string(tks):
            "Return a string from a token id seq"
            return u' '.join(tokens_by_tid[tid] for tid in tks)

        if brief and len(self.tokens) > 10:
            tokens = tokens_string(self.tokens[:5]) + u' ... ' + tokens_string(self.tokens[-5:])
        else:
            tokens = tokens_string(self.tokens)

        dct = {
            'start': self.start,
            'end': self.end,
            'tokens': tokens,
        }
        return dct
