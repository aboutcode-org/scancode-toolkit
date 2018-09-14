#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from itertools import chain
from functools import partial
import textwrap

from licensedcode import query
from licensedcode.spans import Span

"""
Utility function to trace matched texts.
"""


def get_texts(match, location=None, query_string=None, idx=None, width=120):
    """
    Given a match and a query location of query string return a tuple of wrapped
    texts at `width` for:

    - the matched query text as a string.
    - the matched rule text as a string.

    Unmatched positions to known tokens are represented between angular backets <>
    and between square brackets [] for unknown tokens not part of the index.
    Punctuation is removed , spaces are normalized (new line is replaced by a space),
    case is preserved.

    If `width` is a number superior to zero, the texts are wrapped to width.
    """
    return (get_matched_qtext(match, location, query_string, idx, width),
            get_match_itext(match, width))


def get_matched_qtext(match, location=None, query_string=None, idx=None, width=120, margin=0):
    """
    Return the matched query text as a wrapped string of `width` given a match, a
    query location or string and an index.

    Unmatched positions are represented between angular backets <> or square brackets
    [] for unknown tokens not part of the index. Punctuation is removed , spaces are
    normalized (new line is replaced by a space), case is preserved.

    If `width` is a number superior to zero, the texts are wrapped to width with an
    optional `margin`.
    """
    return format_text(matched_query_tokens_str(match, location, query_string, idx), width=width, margin=margin)


def get_match_itext(match, width=120, margin=0):
    """
    Return the matched rule text as a wrapped string of `width` given a match.

    Unmatched positions are represented between angular backets <>.
    Punctuation is removed , spaces are normalized (new line is replaced by a space),
    case is preserved.

    If `width` is a number superior to zero, the texts are wrapped to width with an
    optional `margin`.
    """
    return format_text(matched_rule_tokens_str(match), width=width, margin=margin)


def format_text(tokens, width=120, no_match='<no-match>', margin=4):
    """
    Return a formatted text wrapped at `width` given an iterable of tokens.
    None tokens for unmatched positions are replaced with `no_match`.
    """
    nomatch = lambda s: s or no_match
    tokens = map(nomatch, tokens)
    noop = lambda x: [x]
    initial_indent = subsequent_indent = u' ' * margin
    wrapper = partial(textwrap.wrap, width=width, break_on_hyphens=False,
                      initial_indent=initial_indent,
                      subsequent_indent=subsequent_indent)
    wrap = width and wrapper or noop
    return u'\n'.join(wrap(u' '.join(tokens)))


def matched_query_tokens_str(match, location=None, query_string=None, idx=None):
    """
    Return an iterable of matched query token strings given a query file at
    `location` or a `query_string`, a match and an index.

    Yield None for unmatched positions. Punctuation is removed, spaces are normalized
    (new line is replaced by a space), case is preserved.
    """
    assert idx
    dictionary_get = idx.dictionary.get

    tokens = (query.query_tokenizer(line, lower=False)
              for _ln, line in query.query_lines(location, query_string))
    tokens = chain.from_iterable(tokens)
    match_qspan = match.qspan
    match_qspan_start = match_qspan.start
    match_qspan_end = match_qspan.end
    known_pos = -1
    started = False
    finished = False
    for token in tokens:
        token_id = dictionary_get(token.lower())
        if token_id is None:
            if not started:
                continue
            if finished:
                break
        else:
            known_pos += 1

        if match_qspan_start <= known_pos <= match_qspan_end:
            started = True
            if known_pos == match_qspan_end:
                finished = True

            if known_pos in match_qspan and token_id is not None:
                yield token
            else:
                if token_id is not None:
                    yield '<%s>' % token
                else:
                    yield '[%s]' % token


def matched_rule_tokens_str(match):
    """
    Return an iterable of matched rule token strings given a match.
    Yield None for unmatched positions.
    Punctuation is removed, spaces are normalized (new line is replaced by a space),
    case is preserved.
    """
    ispan = match.ispan
    ispan_start = ispan.start
    ispan_end = ispan.end
    for pos, token in enumerate(match.rule.tokens(lower=False)):
        if ispan_start <= pos <= ispan_end:
            if pos in ispan:
                yield token
            else:
                yield '<%s>' % token


def _debug_print_matched_query_text(match, query, extras=5, logger_debug=None):
    """
    Print a matched query text including `extras` tokens before and after the match.
    Used for debugging license matches.
    """
    # create a fake new match with extra unknown left and right
    new_match = match.combine(match)
    new_qstart = max([0, match.qstart - extras])
    new_qend = min([match.qend + extras, len(query.tokens)])
    new_qspan = Span(new_qstart, new_qend)
    new_match.qspan = new_qspan

    logger_debug(new_match)
    logger_debug(' MATCHED QUERY TEXT with extras')
    qt, _it = get_texts(
        new_match,
        location=query.location, query_string=query.query_string,
        idx=query.idx)
    print(qt)

