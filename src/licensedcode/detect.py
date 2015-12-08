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

from itertools import combinations
import time
import logging

from licensedcode.whoosh_spans.spans import Span
from licensedcode import index
from licensedcode.models import get_all_rules

from textcode import analysis


logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)

# general debug flag
DEBUG = False
# debug flag for match filtering
DEBUG_FILTER = False
# debug flag for perfs: install pympler and set this to collect memory usage and other stats
DEBUG_PERF = False


def get_license_matches(location=None, minimum_score=100):
    """
    Yield detected license matches in the file at `location`.

    minimum_score is the minimum score threshold from 0 to 100. The default is
    100 means only exact licenses will be detected. With any value below 100,
    approximate license results are included. Note that the minimum length for
    an approximate match is four words.
    """
    return get_index().match(location, minimum_score=minimum_score)



def detect_license(location=None, minimum_score=100):
    """
    DEPRECATED: legacy API
    Yield detected licenses in the file at `location`. This is a
    wrapper to IndexLicense.match working on the full license index and
    returning only strings as opposed to objects

    An exception may be raised on error.
    Directories yield nothing and are not walked for their containing files.
    Use commoncode.fileutils.walk for walking a directory tree..

    Note that for testing purposes, location can be a list of lines too.

    minimum_score is the minimum score threshold from 0 to 100.
    """
    for match in get_license_matches(location, minimum_score=minimum_score):
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
            # FXIEME: we should pass these len and counts downstream
            tokens, _min_len, _max_len, _gaps_count = rule.get_tokens()
            self.license_index.index_one_from_tokens(rid, tokens)
            self.rules_by_id[rid] = rule

        if DEBUG_PERF:
            duration = time.time() - start
            len_rules_by_id = len(self.rules_by_id)
            print('Finished building index with %(len_rules_by_id)d rules '
                  'in %(duration)f seconds.' % locals())

    def match(self, location, minimum_score=100):
        """
        Match the file at location against the index and return a sequence of
        LicenseMatch.
        If minimum_score is less than 100, also include approximate matches.
        """
        if DEBUG:
            print('LicenseIndex.match: location=%(location)r, minimum_score=%(minimum_score)r' % locals())

        qdoc = analysis.text_lines(location)
        if DEBUG:
            qdoc = list(qdoc)
            print(' LicenseIndex.match: Query doc has %d lines.' % len(qdoc))
            qdoc = iter(qdoc)

        exact_matches = self.license_index.match(qdoc, minimum_score=minimum_score)
        if DEBUG:
            len_exact_matches = len(exact_matches)
            print(' LicenseIndex.match: exact_matches#: %(len_exact_matches)r' % locals())

        exact_license_matches = []
        for rule_id, matched_pos in exact_matches.items():
            rule = self.rules_by_id[rule_id]
            for match in matched_pos:
                index_position, query_position = match
                lmatch = LicenseMatch(rule, query_position, index_position, score=100.00)
                exact_license_matches.append(lmatch)
        if DEBUG:
            print(' LicenseIndex.match: unfiltered exact_license_matches: %(exact_license_matches)r' % locals())
        if DEBUG_FILTER:
            print(' in EXACT: LicenseIndex.match: filtered with filter_overlapping_matches')
        filtered_exact = filter_overlapping_matches(exact_license_matches, discard_negative=True)
        return sorted(filtered_exact, key=lambda x: x.span)


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
     - index_position and query_position: the detailed position Token of the
       match and matched to texts
     - score: a float normalized between 0 and 100. Higher means better.
       Exact match score is always 100.
    """

    def __init__(self, rule, query_position, index_position=None, score=0):
        self.rule = rule

        # matched positions, for reference (such as displaying matches)
        self.index_position = increment_line_numbers(index_position)
        self.query_position = increment_line_numbers(query_position)

        # matched query position span (absolute token positions, zero-based)
        self.span = Span(query_position.start, query_position.end)
        self.score = score

    def __repr__(self):
        return ('LicenseMatch(\n %(rule)r,\n span=%(span)r, score=%(score)r,'
                '\n  ipos=%(index_position)r,'
                '\n  qpos=%(query_position)r\n)' % self.__dict__)

    def __len__(self):
        return len(self.span)

    def is_same(self, othermatch):
        """
        Return True if othermatch has the same span, detected license keys and
        score.
        """
        return (self.has_same_license(othermatch) and self.span == othermatch.span
                and self.score == othermatch.score)

    def is_more_relevant_than(self, othermatch):
        """
        Return True if self is more relevant than othermatch.
        """
        return self.span == othermatch.span and self.score >= othermatch.score

    def has_same_license(self, othermatch):
        """
        Return True if othermatch has the same detected license keys.
        """
        return (set(self.rule.licenses) == set(othermatch.rule.licenses))

    def is_real_license_match(self):
        """
        Return True if this match points to a real license (and not a negative
        rule with no license key.) 
        """
        return self.rule.licenses


def filter_overlapping_matches(matches, discard_negative=True):
    """
    Return filtered `matches`, removing duplicated or superfluous matches based
    on match position containment and detected licenses overlap. Matches that
    are entirely contained in another bigger match are removed. When more than
    one matched position matches the same license(s), only one match of this set
    is kept. 
    If discard_negative is True, negative matches (e.g. matches to non- license
    rules) are also filtered in the stream and not filtered out.
    """
    if DEBUG_FILTER:
        print()

    ignored_matches = set()
    all_pairs = combinations(matches, 2)
    for current_match, match in all_pairs:
        if DEBUG_FILTER:
            print('\ncurrent_match: %(current_match)r' % locals())
        if current_match in ignored_matches:
            if DEBUG_FILTER:
                print('  current in ignored %(current_match)r' % locals())
            continue

        if DEBUG_FILTER:
            print('  match: %(match)r' % locals())

        if match in ignored_matches:
            if DEBUG_FILTER:
                print('    Passing already ignored: %(match)r' % locals())
            continue

        if current_match is match:
            if DEBUG_FILTER:
                print('    Passing self: %(match)r' % locals())
            continue
        # skip duplicates: keep only one of matches to same span and licenses
        if current_match.is_same(match):
            ignored_matches.add(current_match)
            if DEBUG_FILTER:
                print('    skipping duplicate: %(current_match)r' % locals())
            continue

        # filter smaller matches contained in larger matches
        if current_match.span in match.span:
            ignored_matches.add(current_match)
            if DEBUG_FILTER:
                print('    skipping contained: %(current_match)r \n    is in%(match)r' % locals())
            continue
        elif match.span in current_match.span:
            ignored_matches.add(match)
            if DEBUG_FILTER:
                print('    skipping contained: %(match)r \n    is in %(current_match)r' % locals())
            continue


        # filter matches with same span, but different licenses
        # keep the most specific license (e.g with the fewest gaps)
        if match.span == current_match.span:
            if current_match.score == 100:
                is_less_specific = current_match.rule.min_len >= match.rule.min_len
                if is_less_specific:
                    if DEBUG_FILTER:
                        print('   skipping less specific: %(current_match)r' % locals())
                    ignored_matches.add(current_match)
                    continue
                else:
                    if DEBUG_FILTER:
                        print('   skipping less specific: %(match)r' % locals())
                    ignored_matches.add(match)
                    continue
            else:
                if current_match.is_more_relevant_than(match):
                    if DEBUG_FILTER:
                        print('    skipping more relevant: %(current_match)r' % locals())
                    ignored_matches.add(current_match)
                    continue
                else:
                    if DEBUG_FILTER:
                        print('    skipping more relevant: %(match)r' % locals())
                    ignored_matches.add(match)
                    continue

        # filter negative matches to empty or not-a-license
        if discard_negative and not current_match.is_real_license_match():
            ignored_matches.add(current_match)
            if DEBUG_FILTER:
                print('    skipping negative: %(current_match)r' % locals())
            continue

        # FIXME: handle touching and overlapping matches
        # if (current_match.span.overlaps(match.span) or current_match.span.touches(match.span)):
        #     current_licenses = current_match.rule.licenses
        #     match_licenses = match.rule.licenses
        #     for lic in current_licenses:
        #         if (lic in match_licenses or any(l.startswith(lic) for l in match_licenses)):
        #             ignored_matches.add(current_match)
        #             break
        #     continue

    return [match for match in matches if match not in ignored_matches]
