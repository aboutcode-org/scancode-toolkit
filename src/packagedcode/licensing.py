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
from __future__ import print_function
from __future__ import unicode_literals

import logging

from license_expression import Licensing
from six import string_types

from licensedcode.spans import Span

"""
Detect and normalize licenses as found in package manifests data.
"""

TRACE = False

def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, string_types) and a or repr(a)
                                     for a in args))


def matches_have_unknown(matches, licensing):
    """
    Return True if any of the LicenseMatch in `matches` has an unknown license.
    """
    for match in matches:
        exp = match.rule.license_expression_object
        if any(key in ('unknown', 'unknown-spdx') for key in licensing.license_keys(exp)):
            return True


def get_normalized_expression(query_string, try_as_expression=True):
    """
    Given a text `query_string` return a single detected license expression.
    `query_string` is typically the value of a license field as found in package
    manifests. If `try_as_expression` is True try frst to parse this as a
    license_expression. Return None if there is the `query_string` is empty.
    Return "unknown" as a license expression if there is a `query_string` but
    nothing was detected.
    """
    if not query_string or not query_string.strip():
        return

    if TRACE:
        logger_debug('get_normalized_expression: query_string: "{}"'.format(query_string))

    from licensedcode.cache import get_index
    idx = get_index()
    licensing = Licensing()

    # we match twice in a cascade: as an expression, then as plain text if we
    # did not succeed.
    matches = None
    if try_as_expression:
        try:
            matched_as_expression = True
            matches = idx.match(query_string=query_string, as_expression=True)
            if matches_have_unknown(matches, licensing):
                # rematch also if we have unknowns
                matched_as_expression = False
                matches = idx.match(query_string=query_string, as_expression=False)
    
        except Exception:
            matched_as_expression = False
            matches = idx.match(query_string=query_string, as_expression=False)
    else:
        matched_as_expression = False
        matches = idx.match(query_string=query_string, as_expression=False)

    if not matches:
        # we have a query_string text but there was no match: return an unknown
        # key
        return 'unknown'

    if TRACE:
        logger_debug('get_normalized_expression: matches:', matches)

    # join the possible multiple detected license expression with an AND
    expression_objects = [m.rule.license_expression_object for m in matches]
    if len(expression_objects) == 1:
        combined_expression_object = expression_objects[0]
    else:
        combined_expression_object = licensing.AND(*expression_objects)

    if matched_as_expression:
        # then just return the expression(s)
        return str(combined_expression_object)

    # Otherwise, verify that we consumed 100% of the query string e.g. that we
    # have no unknown leftover.

    # 1. have all matches 100% coverage?
    all_matches_have_full_coverage = all(m.coverage() == 100 for m in matches)

    # TODO: have all matches a high enough score?

    # 2. are all declared license tokens consumed?
    query = matches[0].query
    # the query object should be the same for all matches. Is this always true??
    for mt in matches:
        if mt.query != query:
            # FIXME: the expception may be swallowed in callers!!!
            raise Exception(
                'Inconsistent package.declared_license: text with multiple "queries".'
                'Please report this issue to the scancode-toolkit team.\n'
                '{}'.format(query_string))

    query_len = len(query.tokens)
    matched_qspans = [m.qspan for m in matches]
    matched_qpositions = Span.union(*matched_qspans)
    len_all_matches = len(matched_qpositions)
    declared_license_is_fully_matched = query_len == len_all_matches

    if not all_matches_have_full_coverage or not declared_license_is_fully_matched:
        # We inject an 'unknown' symbol in the expression
        unknown = licensing.parse('unknown', simple=True)
        combined_expression_object = licensing.AND(combined_expression_object, unknown)

    return str(combined_expression_object)
