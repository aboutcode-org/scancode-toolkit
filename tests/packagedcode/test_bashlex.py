#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode.bashlex import BashShellLexer

from packages_test_utils  import build_tests
from packages_test_utils import check_result_equals_expected_json
from packages_test_utils import get_test_files
from packages_test_utils import PackageTester

test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


class TestBashlexDatadriven(PackageTester):
    test_data_dir = test_data_dir


def lexer_tester(location):
    """
    Note that we test the representation of each lexer item as this is
    makes more sense when reviewing test results.
    """
    with open(location) as inp:
        text = inp.read()
    lexer = BashShellLexer()
    return list(map(repr, lexer.get_tokens_unprocessed(text)))


build_tests(
    test_dir=os.path.join(test_data_dir, 'bashlex'),
    test_file_suffix=('.sh', 'APKBUILD'),
    clazz=TestBashlexDatadriven,
    tested_function=lexer_tester,
    test_method_prefix='test_collect_shell_variables_',
    regen=False,
)
