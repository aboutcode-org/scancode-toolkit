#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

import os
import unittest

from commoncode import text

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
Validate that each license and rule text is properly detected in context.
"""


def make_test(expected_expression, test_file, test_data_file, test_name):
    """
    Build and return a test function closing on tests arguments.
    """
    if isinstance(test_name, unicode):
        test_name = test_name.encode('utf-8')

    def closure_test_function(*args, **kwargs):
        idx = cache.get_index()
        matches = idx.match(location=test_file)

        detected_expressions = [m.rule.license_expression for m in matches]
        try:
            assert [expected_expression] == detected_expressions
        except:
            # On failure, we compare against more result data to get additional
            # failure details, including the test_file and full match details
            failure_trace = detected_expressions[:]
            failure_trace.extend([test_name, 'test file: file://' + test_file])

            for match in matches:
                qtext, itext = get_texts(match, location=test_file, idx=idx)
                rule_text_file = match.rule.text_file
                rule_data_file = match.rule.data_file
                failure_trace.extend(['', '',
                    '======= MATCH ====', match,
                    '======= Matched Query Text for:',
                    'file://{test_file}'.format(**locals())
                ])
                if test_data_file:
                    failure_trace.append('file://{test_data_file}'.format(**locals()))
                failure_trace.append(qtext.splitlines())
                failure_trace.extend(['',
                    '======= Matched Rule Text for:'
                    'file://{rule_text_file}'.format(**locals()),
                    'file://{rule_data_file}'.format(**locals()),
                    itext.splitlines(),
                ])
            # this assert will always fail and provide a detailed failure trace
            failure_trace = [test_name, 'test file: file://' + test_file] + failure_trace

            assert [expected_expression] == detected_expressions + failure_trace

    closure_test_function.__name__ = test_name
    closure_test_function.funcname = test_name

    return closure_test_function


def build_license_validation_tests(licenses_by_key, cls):
    """
    Dynamically build an individual test method for each license texts in a
    `licenses_by_key` {key: License} mapping then attach the test method to the
    `cls` test class.
    """
    # TODO: add test to detect the standard notice??

    for key, lic in licenses_by_key.items():
        if lic.text_file and os.path.exists(lic.text_file):
            test_name = ('test_validate_detect_license_' + text.python_safe_name(key))
            test_method = make_test(key, lic.text_file, lic.data_file, test_name)
            setattr(cls, test_name, test_method)


class TestValidateLicenseTextDetection(unittest.TestCase):
    # Test functions are attached to this class at import time
    pass


# build_license_validation_tests(cache.get_licenses_db(), TestValidateLicenseTextDetection)


def build_rule_validation_tests(rules, cls):
    """
    Dynamically build an individual test method for each license texts in a
    `rules` iterable of Rule then attach the test method to the `cls` test
    class.
    """
    for rule in rules:
        test_id = text.python_safe_name(rule.identifier)
        if rule.negative:
            continue
        test_name = ('test_validate_detect_rule_' + test_id)
        test_method = make_test(
            rule.license_expression, rule.text_file, rule.data_file, test_name)

        setattr(cls, test_name, test_method)


class TestValidateLicenseRuleSelfDetection(unittest.TestCase):
    # Test functions are attached to this class at import time
    pass


# build_rule_validation_tests(models.load_rules(), TestValidateLicenseRuleSelfDetection)
