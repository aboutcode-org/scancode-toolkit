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
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a)
                                     for a in args))


def get_normalized_expression(query_string, as_expression=False):
    """
    Given a text `query_string` return a single detected license expression.
    `query_string` is typically the value of a license field as found in package
    manifests.

    If `as_expression` is True will try to detect the `query_string` only as if
    it were an SPDX license expression.

    For example::
    >>> get_normalized_expression('mit')
    u'unknown'
    >>> get_normalized_expression('mit', True)
    'mit'
    >>> get_normalized_expression('mit or asasa or Apache-2.0', True)
    'mit OR unknown-spdx OR apache-2.0'
    >>> get_normalized_expression('mit or asasa or Apache-2.0')
    'apache-2.0 AND unknown'
    """
    from licensedcode.cache import get_index
    idx = get_index()
    licensing = Licensing()

    if as_expression:
        # FIXME: min score???
        matches = idx.match(query_string=query_string, as_expression=True)
        if matches:
            # join and return expressions (though we should have a single one)
            expressions = [m.rule.license_expression for m in matches]
            exps = ['({})'.format(exp) for exp in expressions]
            combined_expression = ' AND '.join(exps)
            combined_expression = licensing.parse(combined_expression, simple=True)
            return str(combined_expression)

    # we either have not an expression of we failed to get proper matches
    matches = idx.match(query_string=query_string, as_expression=False)
    if not matches:
        # always return something
        return 'unknown'

    # we need to verify that we consumed 100% of the query string?
    query = matches[0].query

    if not query:
        # we are in trouble
        pass

    query_len = len(query.tokens)

    expressions = [m.rule.license_expression for m in matches]
    has_unknown = False
    if len(expressions) != 1:
        has_unknown = True

    if not has_unknown:
        # check if we have collectively consumed all the tokens
        # combine all qspans matched e.g. with coverage 100%
        # this coverage check is because we have provision to match fragments (unused for now)
        matched_qspans = [m.qspan for m in matches]
        # do not match futher if we do not need to
        matched_positions = Span.union(*matched_qspans)
        len_all_matches = len(matched_positions)
        if query_len != len_all_matches:
            # need to add something to the expressions telling us we do not have an exact match
            has_unknown = True

    if not has_unknown:
        # if some matches do not have 100% coverage, add unknown
        if any(m.coverage() != 100 for m in matches):
            has_unknown = True

    if has_unknown and 'unknown' not in expressions:
        expressions += ['unknown']

    if len(expressions) != 1:
        exps = ['({})'.format(exp) for exp in expressions]
        combined_expression = ' AND '.join(exps)
        combined_expression = licensing.parse(combined_expression, simple=True)
        return str(combined_expression)
    else:
        return expressions[0]
