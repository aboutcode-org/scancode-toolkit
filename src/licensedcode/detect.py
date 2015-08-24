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

import time
import logging

from licensedcode.whoosh_spans.spans import Span

from textcode import analysis

from licensedcode import index
from licensedcode.models import get_all_rules
from licensedcode import models

logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)

# install pympler and set this to true to collect memory usage and other stats
DEBUG = False
DEBUG_PERF = False


def get_license_matches(location=None, perfect=True):
    """
    Yield detected license matches in the file at `location`.
    """
    return get_index().match(location)


def detect_license(location=None, perfect=True):
    """
    Yield detected licenses in the file at `location`. This is a
    wrapper to IndexLicense.match working on the full license index and
    returning only strings as opposed to objects

    An exception may be raised on error.
    Directories yield nothing and are not walked for their containing files.
    Use commoncode.fileutils.walk for walking a directory tree..

    Note that for testing purposes, location can be a list of lines too.
    """
    for match in get_license_matches(location):
        # TODO: return one result per match with a license
        # yielding the default license if provided
        for detected_license in match.rule.licenses:
            yield (detected_license,
                   match.query_position.start_line, match.query_position.end_line,
                   match.query_position.start_char, match.query_position.end_char,
                   match.rule.identifier,
                   match.score,)


# global in-memory cache of the license index
_LICENSES_INDEX = None


def get_index():
    """
    Return the index from a loaded index if loaded or from building and loading
    from files.
    """
    global _LICENSES_INDEX
    if not _LICENSES_INDEX:
        _LICENSES_INDEX = get_license_index()
    return _LICENSES_INDEX


def get_license_index(rules=None):
    """
    Return a LicenseIndex built from a list of rules.
    """
    if not rules:
        rules = get_all_rules()

    if DEBUG_PERF:
        from pympler import asizeof  # @UnresolvedImport
        print('Memory size of rules:', asizeof.asizeof(rules))

    idx = LicenseIndex(rules)

    if DEBUG_PERF:
        print('Memory size of index:', asizeof.asizeof(idx))

    return idx


class LicenseIndex(object):
    """
    A license detection Index.
    This holds an Index and loaded Rules.
    """
    def __init__(self, rules):
        """
        Init the Index with an iterable of Rule objects.
        """
        self.license_index = index.Index()

        if DEBUG_PERF:
            start = time.time()
            print('LicenseIndex: Starting building index.')

        # index rules text and keep a mapping of rules rid --> rule object
        self.rules_by_id = {}

        # note: we use numeric ids
        for rid, rule in enumerate(rules):
            self.license_index.index_one_from_tokens(rid, rule.get_tokens())
            self.rules_by_id[rid] = rule

        if DEBUG_PERF:
            duration = time.time() - start
            len_rules_by_id = len(self.rules_by_id)
            print('Finished building index with %(len_rules_by_id)d rules '
                  'in %(duration)f seconds.' % locals())

    def match(self, location, perfect=True):
        """
        Match the file at location against the index and return a sequence of
        LicenseMatch.
        If perfect is True, only return perfect matches.
        """
        if DEBUG:
            print('LicenseIndex.match: location=%(location)r, perfect=%(perfect)r ' % locals())

        qdoc = analysis.text_lines(location)
        if DEBUG:
            qdoc = list(qdoc)
            print(' LicenseIndex.match: Query doc has %d lines.'
                      % len(qdoc))
            print('  LicenseIndex.match: Query doc:')
            print(u''.join(qdoc))
            qdoc = iter(qdoc)
        matches = self.license_index.match(qdoc, perfect)

        license_matches = []
        for rule_id, matched_pos in matches.items():
            rule = self.rules_by_id[rule_id]
            for match in matched_pos:
                index_position, query_position = match
                lmatch = LicenseMatch(rule, query_position, index_position, score=100)
                license_matches.append(lmatch)
        return filter_matches(license_matches)


def increment_line_numbers(token):
    """
    Return the token with start and end line numbers incremented by one.
    Internally we start at zero, externally we start at one.
    """
    if  token:
        token.start_line += 1
        token.end_line += 1
    return token


class LicenseMatch(object):
    """
    A license detection match object holds:
     - a rule: matched Rule object

     - the span of the matched region: start and end positions of the analyzed
       text where the rule was matched.

     - index_position and query_position: the detailed position Token of the match and matched to texts
     - score: a float normalized between 0 and 100. Higher means better.
       Exact match score is always 100.
    """

    def __init__(self, rule, query_position, index_position=None, score=0):
        self.rule = rule

        # pos matched, for reference (such as displaying matches)
        self.index_position = increment_line_numbers(index_position)
        self.query_position = increment_line_numbers(query_position)

        # position span
        self.span = Span(query_position.start, query_position.end)
        self.score = score

    def __repr__(self):
        return ('LicenseMatch(rule=%r, start=%r, end=%r)'
                % (self.rule, self.span.start, self.span.end))

    def __len__(self):
        return len(self.span)

    def is_same(self, othermatch):
        """
        Return True if othermatch has the same span, detected license keys and
        score.
        """
        return (self.has_same_license(othermatch)
           and self.span == othermatch.span
           and self.score == othermatch.score)

    def has_same_license(self, othermatch):
        """
        Return True if othermatch has the same detected license keys.
        """
        return (set(self.rule.licenses) ==
               set(othermatch.rule.licenses))

    def is_real_license_match(self):
        """
        Return True if this match points to a real license (and not a non-
        license text).
        This is based on the magic 'not-a-license' license key
        """
        return self.rule.licenses != [models.not_a_license_key]


def filter_matches(matches):
    """
    Return filtered `matches`, removing duplicated or superfluous matches
    based on match position containment and detected licenses overlap. Matches
    that are entirely contained in another bigger match are removed. When more
    than one matched position matches the same license(s), only one match of
    this set is kept.
    """
    ignored_matches = set()
    for current_match in matches:
        for match in matches:
            # skip the current match
            if match == current_match:
                continue
            # keep matches with same span, but different licenses
            if (current_match.span == match.span and
                not current_match.is_same(match)):
                continue

            # keep only one if same matches for same span and licenses
            if (current_match.is_same(match)
                and current_match not in ignored_matches):
                ignored_matches.add(match)
                continue

            # filter contained matches
            if current_match.span in match.span:
                ignored_matches.add(current_match)
                continue

            # FIXME: handle touching and overlapping matches
            # if (current_match.span.overlaps(match.span)
            #       or current_match.span.touches(match.span)):
            #     current_licenses = current_match.rule.licenses
            #     match_licenses = match.rule.licenses
            #     for lic in current_licenses:
            #         if (lic in match_licenses or
            #             any(l.startswith(lic) for l in match_licenses)):
            #             ignored_matches.add(current_match)
            #             break
            #     continue

    return [match for match in matches
            if match not in ignored_matches and
            match.is_real_license_match()]
