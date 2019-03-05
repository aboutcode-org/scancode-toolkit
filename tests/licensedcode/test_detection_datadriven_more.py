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

from test_detection_datadriven import load_license_tests
from test_detection_datadriven import build_tests


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data/licenses')

"""
Data-driven tests using expectations stored in YAML files.
"""


class TestSlicDataDriven(unittest.TestCase):
    # test functions are attached to this class at module import time
    pass


# tests data from https://github.com/gerv/slic
TEST_DATA_DIR_SLIC = os.path.join(os.path.dirname(__file__), 'data/slic-tests/identification')

build_tests(license_tests=load_license_tests(TEST_DATA_DIR_SLIC),
            clazz=TestSlicDataDriven, regen=False)


class TestFossLicDataDriven(unittest.TestCase):
    # test functions are attached to this class at module import time
    pass


# tests data from Fossology
TEST_DATA_DIR_FOSS1 = os.path.join(os.path.dirname(__file__), 'data/more_licenses/licenses')

build_tests(license_tests=load_license_tests(TEST_DATA_DIR_FOSS1),
            clazz=TestFossLicDataDriven, regen=False)


class TestFossTestsDataDriven(unittest.TestCase):
    # test functions are attached to this class at module import time
    pass


# reference licenses from Fossology
TEST_DATA_DIR_FOSS2 = os.path.join(os.path.dirname(__file__), 'data/more_licenses/tests')

build_tests(license_tests=load_license_tests(TEST_DATA_DIR_FOSS2),
            clazz=TestFossTestsDataDriven, regen=False)


class TestDebLicCheckTestsDataDriven(unittest.TestCase):
    # test functions are attached to this class at module import time
    pass


# license tests from Debian licensecheck
TEST_DATA_DIR_DEBLC = os.path.join(os.path.dirname(__file__), 'data/debian/licensecheck')

build_tests(license_tests=load_license_tests(TEST_DATA_DIR_DEBLC),
            clazz=TestDebLicCheckTestsDataDriven, regen=False)
