#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import pubspec

from packages_test_utils import PackageTester
from packages_test_utils  import build_tests

test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


class TestPubspecDatadriven(PackageTester):
    test_data_dir = test_data_dir


build_tests(
    test_dir=os.path.join(test_data_dir, 'pubspec/specs'),
    clazz=TestPubspecDatadriven,
    test_method_prefix='test_maven2_parse_misc_',
    package_function=pubspec.parse_pub,
    test_file_suffix='pubspec.yaml',
    regen=False,
)

