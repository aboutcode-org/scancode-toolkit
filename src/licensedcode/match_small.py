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

from licensedcode.pyahocorasick2 import Trie

from licensedcode.match import LicenseMatch
from licensedcode.whoosh_spans.spans import Span
from operator import itemgetter

"""
Matching strategies for exact matching. This is used for small rules either for
a single token using a simple map or for short rules using an Aho-Corasick
automaton.
"""

# Set to False to enable debug tracing
TRACE = False

if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
else:
    def logger_debug(*args):
        pass


def index_aho(rules_tokens, len_tokens):
    """
    Return an Aho-Corasick Trie for a list of `rules_tokens` tuple of (rid,
    [token ids]) given the maximum number of tokens `len_tokens`.
    """
    trie = Trie(items_range=len_tokens, content=int)
    for rid, tokens in sorted(enumerate(rules_tokens), key=itemgetter(1)):
        trie.add(tokens, (rid, len(rules_tokens)))
    trie.make_automaton()
    return trie


def exact_match(idx, query_run, automaton, rules_subset=None):
    """
    Return a list of exact LicenseMatch by matching the `query_run` against
    the `automaton` and `idx` index. 
    Only return matches for a rule id present in rules_subset if provided. 
    """
    if TRACE: logger_debug(' #exact: start ... ')

    len_junk = idx.len_junk
    rules_by_rid = idx.rules_by_rid

    qtokens = query_run.tokens
    qbegin = query_run.start
    query_run_matchables = query_run.matchables
    line_by_pos = query_run.line_by_pos

    matches = []
    for qend, matched_rids in automaton.search(qtokens):
        for rid in matched_rids:
            if rules_subset and rid not in rules_subset:
                continue

            rule = rules_by_rid[rid]
            len_rule = rule.length
            qposses = range(qbegin + qend - len_rule + 1, qbegin + qend + 1)

            if any(p not in query_run_matchables for p in qposses):
                if TRACE: logger_debug('   #exact: not matchable match')
                continue

            qspan = Span(qposses)
            ispan = Span(range(len_rule))

            itokens = idx.tids_by_rid[rid]
            hispan = Span(p for p in ispan if itokens[p] >= len_junk)

            match = LicenseMatch(rule, qspan, ispan, hispan, line_by_pos, query_run.start, 'aho')
            matches.append(match)

    if TRACE and matches: logger_debug(' ##small exact: matches found#', matches)

    return matches
