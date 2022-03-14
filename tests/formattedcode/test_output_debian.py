# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import shutil

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import run_scan_plain
from scancode_config import REGEN_TEST_FIXTURES


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def check_debian_copyright_output(test_dir, expected_file, regen=REGEN_TEST_FIXTURES):
    """
    Rrun a scan on ``test_dir`` with a debian output and check if the created
    file matches ``expected_file``.
    """
    result_file = test_env.get_temp_file('copyright')
    args = [
        '--copyright',
        '--license',
        '--license-text',
        '--debian', result_file,
        test_dir,
    ]

    run_scan_plain(args)

    if regen:
        shutil.copyfile(result_file, expected_file)

    with open(expected_file) as exp:
        expected = exp.read()

    with open(result_file) as res:
        result = res.read()

    assert result == expected


def test_debian_basic():
    test_dir = test_env.get_test_loc('debian/basic/scan')
    expected_file = test_env.get_test_loc('debian/basic/expected.copyright')
    check_debian_copyright_output(test_dir, expected_file, regen=REGEN_TEST_FIXTURES)


def test_debian_multiple_files():
    test_dir = test_env.get_test_loc('debian/multiple_files/scan')
    expected_file = test_env.get_test_loc('debian/multiple_files/expected.copyright')
    check_debian_copyright_output(test_dir, expected_file, regen=REGEN_TEST_FIXTURES)
