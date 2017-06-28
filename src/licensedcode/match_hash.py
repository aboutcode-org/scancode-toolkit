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

from array import array
from hashlib import md5

from licensedcode.spans import Span
from licensedcode.match import LicenseMatch


"""
Matching strategy using hashes to match a whole text chunk at once.
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


MATCH_HASH = '1-hash'


def tokens_hash(tokens):
    """
    Return a digest binary string computed from a sequence of numeric token ids.
    """
    return md5(array('h', tokens).tostring()).digest()


def index_hash(rule_tokens):
    """
    Return a hash digest string given a sequence of rule tokens.
    """
    return tokens_hash(rule_tokens)


def hash_match(idx, query_run):
    """
    Return a sequence of LicenseMatch by matching the query_tokens sequence
    against the idx index.
    """
    logger_debug('match_hash: start....')
    matches = []
    query_hash = tokens_hash(query_run.tokens)
    rid = idx.rid_by_hash.get(query_hash)
    if rid is not None:
        rule = idx.rules_by_rid[rid]
        itokens = idx.tids_by_rid[rid]
        len_junk = idx.len_junk
        logger_debug('match_hash: Match:', rule.identifier)
        qspan = Span(range(query_run.start, query_run.end + 1))
        ispan = Span(range(0, rule.length))
        hispan = Span(p for p in ispan if itokens[p] >= len_junk)
        match = LicenseMatch(rule, qspan, ispan, hispan, query_run.start, matcher=MATCH_HASH, query=query_run.query)
        matches.append(match)
    return matches
