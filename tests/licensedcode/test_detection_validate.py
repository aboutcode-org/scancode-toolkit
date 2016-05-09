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

from __future__ import absolute_import, print_function

import os
import unittest

from commoncode import functional
from commoncode import text
from licensedcode import index
from licensedcode import models
from licensedcode import query


# set to True to print matched texts on test failure.
TRACE_TEXTS = True


"""
Validate that each license text and each rule is properly detected.
"""

def license_keys(matches, unique_keys=False):
    """
    Return a flattened list of detected license keys, sorted by position and then rule order.
    """
    all_keys = functional.flatten(match.rule.licenses for match in matches)
    if unique_keys:
        all_keys = sorted(set(all_keys))
    return all_keys


def make_license_test_function(expected_licenses, test_file, test_name, unique_keys=False, min_score=100, detect_negative=True):
    """
    Build a test function closing on tests arguments
    """
    if not isinstance(expected_licenses, list):
        expected_licenses = [expected_licenses]

    def data_driven_test_function(self):
        idx = index.get_index()
        file_tested = test_file
        matches = idx.match(location=test_file, min_score=min_score, _detect_negative=detect_negative)
        if not matches:
            assert [] == ['No match: min_score:{min_score}. detect_negative={detect_negative}, test_file: file://{file_tested}'.format(**locals())]

        detected_licenses = functional.flatten(match.rule.licenses for match in matches)
        try:
            assert expected_licenses == detected_licenses
        except:
            # on failure, we compare against more result data to get additional
            # failure details, including the test_file and full match details
            matches_texts = []
            if TRACE_TEXTS:
                for match in matches:
                    qtext, itext = query.get_texts(match, location=test_file, dictionary=idx.dictionary)
                    matches_texts.extend(['', '', 
                        '======= MATCH ====', match, 
                        '======= Matched Query Text for: file://' + test_file , qtext.splitlines(), '',
                        '======= Matched Rule Text for file://' + match.rule.text_file, itext.splitlines(),
                    ])
            assert expected_licenses == [detected_licenses] + [test_name, 'test file: file://' + test_file] + matches_texts

    data_driven_test_function.__name__ = test_name
    data_driven_test_function.funcname = test_name
    return data_driven_test_function


def build_license_validation_tests(licenses_by_key, cls):
    """
    Dynamically build an individual test method for each license texts and spdx
    texts in a licenses `data_set` then mapping attaching the test method to the
    `cls` test class.
    """
    for license_key, license_obj in licenses_by_key.items():
        if license_obj.text_file and os.path.exists(license_obj.text_file):
            test_name = ('test_validate_self_detection_of_text_for_' + text.python_safe_name(license_key))
            # also verify that we are detecting exactly with the license rule itself
            test_method = make_license_test_function(license_key, license_obj.text_file, test_name, unique_keys=True, min_score=100, detect_negative=True)
            setattr(cls, test_name, test_method)

        if license_obj.spdx_license_key:
            if license_obj.spdx_file and os.path.exists(license_obj.spdx_file):
                test_name = ('test_validate_self_detection_of_spdx_text_for_' + text.python_safe_name(license_key))
                test_method = make_license_test_function(license_key, license_obj.spdx_file, test_name, unique_keys=True, min_score=100, detect_negative=True)
                setattr(cls, test_name, test_method)


class TestValidateLicenseTextDetection(unittest.TestCase):
    # Test functions are attached to this class at import time
    pass


build_license_validation_tests(models.get_licenses_by_key(), TestValidateLicenseTextDetection)


def build_rule_validation_tests(rules, cls):
    """
    Dynamically build an individual test method for each rule texts in a rules
    `data_set` then mapping attaching the test method to the `cls` test class.
    """
    for rule in rules:
        expected_identifier = rule.identifier()
        test_name = ('test_validate_self_detection_of_rule_for_' + text.python_safe_name(expected_identifier))
        test_method = make_license_test_function(rule.licenses, rule.text_file, test_name, unique_keys=True, min_score=100, detect_negative=not rule.negative())
        setattr(cls, test_name, test_method)


class TestValidateLicenseRuleSelfDetection(unittest.TestCase):
    # Test functions are attached to this class at import time
    pass


build_rule_validation_tests(models.rules(), TestValidateLicenseRuleSelfDetection)
