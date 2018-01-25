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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import cluecode.copyrights


def check_detection(expected, test_file_or_iterable,
                    expected_in_results=True,
                    results_in_expected=True,
                    what='copyrights'):
    """
    Run detection of copyright on the `test_file_or_iterable`, checking the
    results match the expected list of values.

    `test_file_or_iterable` is either a path string or an iterable of text lines.

    If `expected_in_results` and `results_in_expected` are True (the default),
    then expected and test results are tested for equality. To accommodate for
    some level of approximate testing, the check can test only if an expected
    result in a test result, or the opposite.

    If `expected_in_results` and `results_in_expected` are both False an
    exception is raised as this is not a case that make sense.
    """
    copyrights, authors, years, holders = cluecode.copyrights.detect(test_file_or_iterable)
    results = {
        'copyrights': copyrights,
        'authors': authors,
        'years': years,
        'holders': holders
    }

    result = results[what]
    if expected_in_results and results_in_expected:
        assert expected == result

    elif not expected_in_results and not results_in_expected:
        raise Exception('expected_in_result and result_in_expected '
                        'cannot be both False')

    elif expected_in_results:
        for i, expect in enumerate(expected):
            msg = repr(expect) + ' not in ' + repr(result[i]) + ' for test file:' + test_file_or_iterable
            assert expect in result[i], msg

    elif results_in_expected:
        for i, res in enumerate(result):
            msg = repr(expected[i]) + ' does not contain ' + repr(res) + ' for test file:' + test_file_or_iterable
            assert res in expected[i], msg
