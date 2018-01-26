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
from licensedcode import models

from license_test_utils import make_license_test_function

"""
Validate that each license text and each rule is properly detected.
"""


def build_license_validation_tests(licenses_by_key, cls):
    """
    Dynamically build an individual test method for each license texts in a licenses
    `data_set` then mapping attaching the test method to the `cls` test class.
    """
    for license_key, license_obj in licenses_by_key.items():
        if license_obj.text_file and os.path.exists(license_obj.text_file):
            test_name = ('test_validate_self_detection_of_text_for_' + text.python_safe_name(license_key))
            # also verify that we are detecting exactly with the license rule itself
            test_method = make_license_test_function(
                license_key, license_obj.text_file, license_obj.data_file, test_name, detect_negative=True, trace_text=True)
            setattr(cls, test_name, test_method)


class TestValidateLicenseTextDetection(unittest.TestCase):
    # Test functions are attached to this class at import time
    pass


build_license_validation_tests(cache.get_licenses_db(), TestValidateLicenseTextDetection)


def build_rule_validation_tests(rules, cls):
    """
    Dynamically build an individual test method for each rule texts in a rules
    `data_set` then mapping attaching the test method to the `cls` test class.
    """
    for rule in rules:
        if rule.negative:
            continue
        expected_identifier = rule.identifier
        test_name = ('test_validate_self_detection_of_rule_for_' + text.python_safe_name(expected_identifier))
        test_method = make_license_test_function(
            rule.licenses, rule.text_file, rule.data_file, test_name, detect_negative=not rule.negative, trace_text=True
        )
        setattr(cls, test_name, test_method)


class TestValidateLicenseRuleSelfDetection(unittest.TestCase):
    # Test functions are attached to this class at import time
    pass


build_rule_validation_tests(models.load_rules(), TestValidateLicenseRuleSelfDetection)
