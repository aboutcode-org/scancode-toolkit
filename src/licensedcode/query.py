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

from functools import partial
import textwrap

from textcode.analysis import text_lines

from licensedcode import NGRAM_LENGTH
from licensedcode.tokenize import ngrams
from licensedcode.tokenize import query_tokenizer
from licensedcode.whoosh_spans.spans import Span


"""
Build queries from the files being scanned.
"""

# debug flags
DEBUG = False

if DEBUG:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
else:
    def logger_debug(*args):
        pass


def iterlines(location=None, query=None):
    """
    Given a file at location or a query string, return an iterable of (line_num,
    line text). Line numbers start at one.
    """
    # TODO: OPTIMIZE: tokenizing line by line may be rather slow
    # we could instead get lines and tokens at once in a batch?
    if location:
        lines = text_lines(location)
    elif query:
        lines = query.splitlines(False)
    else:
        lines = []

    # line numbers starts at one
    for line_num, line in enumerate(lines, 1):
        if line:
            line = line.strip()
        if line:
            yield line_num, line


def query_data(location=None, query=None, dictionary=None):
    """
    Return a line by position mapping, a query vector and a query_tokens
    sequence given:
    - a file at `location` or a `query` string [one of these is required],
    - a `dictionary` mapping token strings to token ids [required],
    Line numbers start at one, token positions at zero.
    Unknown tokens are skipped and do not increment positions.
    """
    assert dictionary
    line_by_pos = {}
    vector = [[] for _ in range(len(dictionary))]
    tokens = []
    pos = 0
    for line_num, line in iterlines(location, query):
        for token in query_tokenizer(line):
            token_id = dictionary.get(token)
            # note: zero is a valid token_id. Only None is not.
            if token_id is not None:
                vector[token_id].append(pos)
                line_by_pos[pos] = line_num
                tokens.append(token_id)
                pos += 1

    return line_by_pos, vector, tokens


def query_ngrams(query_tokens, _ngram_length=NGRAM_LENGTH):
    """
    Return an iterable of (ngram, start, end) tuples given an iterable of query
    (token, pos) tuples. Skip ngrams that contain a None as a side effect of
    filtering.
    """
    return ((ngram, start,) for start, ngram in enumerate(ngrams(query_tokens, _ngram_length)) if None not in ngram)


def filtered_query_data(query_tokens, matches, len_tokens):
    """
    Return a new query_tokens and a corresponding query_vector given a sequence
    of query_tokens, a sequence of LicenseMatch and the len_tokens number of
    known tokens. The tokens are filtered by replacing any token position
    contained in any matched qspans by None. Filtered tokens are ignored from
    the vector.
    """
    logger_debug('filtered_query_data')
    filtered_tokens = filtered_query_tokens(query_tokens, matches)
    assert filtered_tokens
    filtered_vector = filtered_query_vector_from_tokens(filtered_tokens, len_tokens)
    return filtered_tokens, filtered_vector


def filtered_query_vector_from_tokens(query_tokens, len_tokens):
    """
    Return a new query vector given a sequence of filtered query_tokens
    (eventually containing None for filtered positions).
    """
    vector = [[] for _ in range(len_tokens)]
    for qpos, token_id in enumerate(query_tokens):
        if token_id is not None:
            vector[token_id].append(qpos)
    return vector


def filtered_query_tokens(query_tokens, matches):
    """
    Return a new query_tokens sequence of query token given a sequence of
    query_tokens and a sequence of LicenseMatch. The tokens are filtered by
    replacing any token position contained in any matched qspans by None.
    """
    mpos = matched_query_positions(matches)
    return [None if pos in mpos else tid for pos, tid in enumerate(query_tokens)]


def matched_query_positions(matches):
    """
    Return a set of unique matched query positions given a sequence of
    LicenseMatch.
    """
    matched_pos = set()
    matched_pos_update = matched_pos.update
    for match in matches:
        for qspan in match.qspans:
            matched_pos_update(range(qspan.start, qspan.end + 1))
    return matched_pos


def _query_token_strings(location=None, query=None, dictionary=None, lower=False):
    """
    Return an iterable of (normalized query token strings, real_pos, query_pos)
    given a file at `location` or a `query` string [one of these is required].

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
    for _line_num, line in iterlines(location, query):
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


def get_texts(match, location=None, query=None, dictionary=None, width=120):
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

    no_match = '<no-match>'

    # rebuild matched query text
    matched_qpos = Span.ranges(match.qspans)
    matched_qreg = Span.ranges([match.qregion])

    matched_qtokens = []
    qstarted = False
    for token, _real_pos, query_pos in _query_token_strings(location, query, dictionary):
        if query_pos == -1:
            continue

        if query_pos not in matched_qreg:
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
    matched_ipos = Span.ranges(match.ispans)
    matched_ireg = Span.ranges([match.iregion])

    matched_itokens = []
    for pos, token in enumerate(match.rule.tokens(lower=False)):
        if pos not in matched_ireg:
            continue
        if pos in matched_ipos:
            itok = token or no_match
            matched_itokens.append(itok)

    # return wrapped texts
    noop = lambda x: x
    wrap = width and partial(textwrap.wrap, width=width, break_on_hyphens=False) or noop
    return (u'\n'.join(wrap(u' '.join(matched_qtokens))),
            u'\n'.join(wrap(u' '.join(matched_itokens))))
