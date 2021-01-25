# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest

from cluecode_test_utils import build_tests
from cluecode_test_utils import load_copyright_tests
from commoncode.testcase import FileBasedTesting

pytestmark = pytest.mark.scanslow


"""
This test suite is based on many sources including a rather large subset of
Android ICS, providing a rather diversified sample of a typical Linux-based user
space environment.
"""

class TestCopyrightDataDriven(FileBasedTesting):
    # test functions are attached to this class at module import time
    pass


build_tests(copyright_tests=load_copyright_tests(), clazz=TestCopyrightDataDriven, regen=False)
