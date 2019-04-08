#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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
from commoncode import fileutils

from licensedcode import cache
from licensedcode import models
from licensedcode.match_hash import MATCH_HASH

# Python 2 and 3 support
try:
    # Python 2
    unicode
except NameError:
    # Python 3
    unicode = str  # NOQA

"""
Validate that each license and rule text is properly detected with exact detection.
This runs a lot of tests that may seem useless, but this is the only way we can
guarantee that the rule data set integrity is now drifting.
"""


def make_test(test_file, test_name, negative=False):
    """
    Build and return a test function closing on tests arguments.
    """
    if isinstance(test_name, unicode):
        test_name = test_name.encode('utf-8')

    if negative:
        def closure_test_function(*args, **kwargs):
            idx = cache.get_index()
            matches = idx.match(location=test_file)
            assert not matches
    else:
        def closure_test_function(*args, **kwargs):
            idx = cache.get_index()
            matches = idx.match(location=test_file)
            expected = [dict(rule=fileutils.file_name(test_file), matcher=MATCH_HASH)]
            detected = [dict(rule=m.rule.identifier, matcher=m.matcher) for m in matches]
            assert expected == detected

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
            test_method = make_test(test_file=lic.text_file, test_name=test_name)
            setattr(cls, test_name, test_method)


class TestValidateLicenseTextDetection(unittest.TestCase):
    # Test functions are attached to this class at import time
    pass


build_license_validation_tests(cache.get_licenses_db(), TestValidateLicenseTextDetection)


def build_rule_validation_tests(rules, cls):
    """
    Dynamically build an individual test method for each license texts in a
    `rules` iterable of Rule then attach the test method to the `cls` test
    class.
    """
    for rule in rules:
        test_id = text.python_safe_name(rule.identifier)
        test_name = ('test_validate_detect_rule_' + test_id)
        test_method = make_test(test_file=rule.text_file, test_name=test_name, negative=rule.is_negative)
        setattr(cls, test_name, test_method)


class TestValidateLicenseRuleSelfDetection(unittest.TestCase):
    # Test functions are attached to this class at import time
    pass


build_rule_validation_tests(models.load_rules(), TestValidateLicenseRuleSelfDetection)
