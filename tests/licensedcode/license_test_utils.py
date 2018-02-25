#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from unittest.case import expectedFailure
from unittest.case import skip

from commoncode import functional
from commoncode.text import python_safe_name
from licensedcode import cache
from licensedcode.tracing import get_texts

# Python 2 and 3 support
try:
    # Python 2
    unicode
except NameError:
    # Python 3
    unicode = str  # NOQA

"""
License test utilities.
"""


def make_license_test_function(
        expected_licenses, test_file, test_data_file, test_name,
        detect_negative=True, min_score=0,
        expected_failure=False,
        # if not False, a reason string must be provided
        skip_test=False,
        # if True detailed traces including matched texts will be returned
        trace_text=False):
    """
    Build and return a test function closing on tests arguments.
    """
    if isinstance(test_name, unicode):
        test_name = test_name.encode('utf-8')

    if not isinstance(expected_licenses, list):
        expected_licenses = [expected_licenses]

    def closure_test_function(*args, **kwargs):
        idx = cache.get_index()
        matches = idx.match(location=test_file, min_score=min_score,
                            # if negative, do not detect negative rules when testing negative rules
                            detect_negative=detect_negative)

        if not matches:
            matches = []

        # TODO: we should expect matches properly, not with a grab bag of flat license keys
        # flattened list of all detected license keys across all matches.
        detected_licenses = functional.flatten(map(unicode, match.rule.licenses) for match in matches)
        try:
            if not detect_negative:
                # we skipped negative detection for a negative rule
                # we just want to ensure that the rule was matched proper
                assert matches and not expected_licenses and not detected_licenses
            else:
                assert expected_licenses == detected_licenses
        except:
            # On failure, we compare against more result data to get additional
            # failure details, including the test_file and full match details
            match_failure_trace = []

            if trace_text:
                for match in matches:
                    qtext, itext = get_texts(match, location=test_file, idx=idx)
                    rule_text_file = match.rule.text_file
                    rule_data_file = match.rule.data_file
                    match_failure_trace.extend(['', '',
                        '======= MATCH ====', match,
                        '======= Matched Query Text for:',
                        'file://{test_file}'.format(**locals())
                    ])
                    if test_data_file:
                        match_failure_trace.append('file://{test_data_file}'.format(**locals()))
                    match_failure_trace.append(qtext.splitlines())
                    match_failure_trace.extend(['',
                        '======= Matched Rule Text for:'
                        'file://{rule_text_file}'.format(**locals()),
                        'file://{rule_data_file}'.format(**locals()),
                        itext.splitlines(),
                    ])
            # this assert will always fail and provide a detailed failure trace
            assert expected_licenses == detected_licenses + [test_name, 'test file: file://' + test_file] + match_failure_trace

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    if skip_test:
        skipper = skip(repr(skip_test))
        closure_test_function = skipper(closure_test_function)

    if expected_failure:
        closure_test_function = expectedFailure(closure_test_function)

    return closure_test_function


def print_matched_texts(match, location=None, query_string=None, idx=None):
    """
    Convenience function to print matched texts for tracing and debugging tests.
    """
    qtext, itext = get_texts(match, location=location, query_string=query_string, idx=idx)
    print()
    print('Matched qtext:')
    print(qtext)
    print()
    print('Matched itext:')
    print(itext)


def check_license(location=None, query_string=None, expected=(), test_data_dir=None):
    if query_string:
        idx = cache.get_index()
        matches = idx.match(location=location, query_string=query_string)
        results = functional.flatten(map(unicode, match.rule.licenses) for match in matches)
        assert expected == results
    else:
        test_name = python_safe_name('test_' + location.replace(test_data_dir, ''))
        tester = make_license_test_function(
            expected_licenses=expected, test_file=location,
            test_data_file=None, test_name=test_name,
            trace_text=True)
        tester()
