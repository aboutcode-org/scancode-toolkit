#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os.path import abspath
from os.path import join
from os.path import dirname
import unittest

from licensedcode_test_utils import build_tests  # NOQA
from scancode_config import REGEN_TEST_FIXTURES



"""
Data-driven tests using expectations stored in YAML files.
Test functions are attached to test classes at module import time
"""

TEST_DIR = abspath(join(dirname(__file__), 'data'))


class TestLicenseDataDriven(unittest.TestCase):
    pass


build_tests(
    TEST_DIR,
    clazz=TestLicenseDataDriven, regen=REGEN_TEST_FIXTURES)
