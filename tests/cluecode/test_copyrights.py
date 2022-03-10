# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import pytest

from commoncode.testcase import FileBasedTesting

from cluecode_test_utils import build_tests
from cluecode_test_utils import load_copyright_tests
from scancode_config import REGEN_TEST_FIXTURES


pytestmark = pytest.mark.scanslow


"""
This test suite is based on many sources including a rather large subset of
Android ICS, providing a rather diversified sample of a typical Linux-based user
space environment.
"""

class TestCopyrightDataDriven(FileBasedTesting):
    # test functions are attached to this class at module import time
    pass


build_tests(copyright_tests=load_copyright_tests(), clazz=TestCopyrightDataDriven, regen=REGEN_TEST_FIXTURES)
