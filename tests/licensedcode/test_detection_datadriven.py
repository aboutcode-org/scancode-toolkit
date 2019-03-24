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

from os.path import abspath
from os.path import join
from os.path import dirname
import unittest


from licensedcode_test_utils import build_tests

"""
Data-driven tests using expectations stored in YAML files.
Test functions are attached to test classes at module import time
"""

TEST_DIR = abspath(join(dirname(__file__), 'data'))

class TestLicenseDataDriven(unittest.TestCase):
    pass

build_tests(
    join(TEST_DIR, 'licenses'),
    clazz=TestLicenseDataDriven, regen=False)


class TestLicenseRetrographyDataDriven(unittest.TestCase):
    pass

build_tests(
    join(TEST_DIR, 'retro_licenses/OS-Licenses-master'),
    clazz=TestLicenseRetrographyDataDriven, regen=False)


class TestLicenseSpdxDataDriven(unittest.TestCase):
    pass

build_tests(
    join(TEST_DIR, 'spdx/licenses'),
    clazz=TestLicenseSpdxDataDriven, regen=False)


class TestLicenseToolsDataDriven(unittest.TestCase):
    # this is for license-related npm tools with a lot of license references in
    # code, tests and data
    pass

build_tests(
    join(TEST_DIR, 'license_tools'),
    clazz=TestLicenseToolsDataDriven, regen=False)


class TestSlicDataDriven(unittest.TestCase):
    # tests data from https://github.com/gerv/slic
    pass

build_tests(
    join(TEST_DIR, 'slic-tests/identification'),
    clazz=TestSlicDataDriven, regen=False)


class TestFossLicDataDriven(unittest.TestCase):
    # tests data from Fossology
    pass

build_tests(
    join(TEST_DIR, 'more_licenses/licenses'),
    clazz=TestFossLicDataDriven, regen=False)


class TestFossTestsDataDriven(unittest.TestCase):
    # reference licenses from Fossology
    pass

build_tests(
    join(TEST_DIR, 'more_licenses/tests'),
    clazz=TestFossTestsDataDriven, regen=False)


class TestDebLicCheckTestsDataDriven(unittest.TestCase):
    # license tests from Debian licensecheck
    pass

build_tests(
    join(TEST_DIR, 'debian/licensecheck'),
    clazz=TestDebLicCheckTestsDataDriven, regen=False)
