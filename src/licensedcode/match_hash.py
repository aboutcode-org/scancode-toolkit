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

from hashlib import md5

from licensedcode.whoosh_spans.spans import Span
from licensedcode.match import LicenseMatch


"""
Matching strategy using whole rules hashes
"""

# Set to True to enable debug tracing
TRACE = False

if TRACE :
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


MATCH_TYPE = 'hash'


def tokens_hash(tokens):
    return md5(' '.join(map(str, tokens))).digest()


def index_hash(rule_tokens):
    """
    Return a hash digest string given a sequence of rule tokens.
    """
    # FIXME: handle gaps!
    return tokens_hash(rule_tokens)


def match_hash(idx, query_run):
    """
    Return a sequence of LicenseMatch by matching the query_toeksn sequence
    against the idx index.
    """
    logger_debug('match_hash: start....')

    matches = []
    query_hash = tokens_hash(t for t in query_run.tokens if t is not None)
    qspan = Span(p for p, t in enumerate(query_run.tokens) if t is not None)
    matched_rids = idx.hashes.get(query_hash, [])
    for rid in matched_rids:
        rule = idx.rules_by_rid[rid]
        logger_debug('match_hash: Match:', rule.identifier())
        ispan = Span(range(0, rule.length))
        hispan = Span(p for p, t in enumerate(idx.tokens_by_rid[rid]) if t >= idx.len_junk)

        match = LicenseMatch(rule, qspan, ispan, hispan=hispan, line_by_pos=query_run.line_by_pos, query_run_start = query_run.start, _type=MATCH_TYPE)
        matches.append(match)
    # FIXME: why a set????
    return list(set(matches))
