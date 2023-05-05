#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import os

import pytest

from commoncode.testcase import FileDrivenTesting
from commoncode.text import python_safe_name

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


pytestmark = pytest.mark.scanslow


"""
Data-driven Score test utilities.
"""


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def make_test_function(test_name, test_dir, expected_file, regen=REGEN_TEST_FIXTURES):
    """
    Build and return a test function closing on tests arguments and the function
    name. Create only a single function for multiple tests (e.g. copyrights and
    holders together).
    """

    def closure_test_function(*args, **kwargs):
        result_file = test_env.get_temp_file('json')
        args = ['--license',
                '--copyright',
                '--info',
                '--classify',
                '--package',
                '--license-clarity-score',
                test_dir, '--json', result_file]
        run_scan_click(args)
        run_scan_click(args)
        check_json_scan(
            test_env.get_test_loc(expected_file),
            result_file,
            remove_file_date=True,
            regen=regen,
        )

    test_name = 'test_license_clarity_score_%(test_name)s' % locals()
    test_name = python_safe_name(test_name)
    if isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    closure_test_function.__name__ = test_name

    return closure_test_function, test_name


def build_tests(test_base_dir, clazz, regen=REGEN_TEST_FIXTURES):
    """
    Dynamically build test methods from a sequence of CopyrightTest and attach
    these method to the clazz test class.
    """
    test_dirs = test_env.get_test_loc(test_base_dir)
    for td in os.listdir(test_dirs):
        td_loc = os.path.join(test_dirs, td)
        if not os.path.isdir(td_loc):
            continue
        expected_file_loc = td_loc.rstrip('/\\') + '-expected.json'

        if regen and not os.path.exists(expected_file_loc):
            with io.open(expected_file_loc, 'w') as o:
                o.write(u'')

        method, name = make_test_function(
            test_name=td,
            test_dir=td_loc,
            expected_file=expected_file_loc,
            regen=regen)

        # attach that method to our test class
        setattr(clazz, name, method)


class TestLicenseScore(FileDrivenTesting):
    # test functions are attached to this class at module import time
    pass


build_tests(test_base_dir='score', clazz=TestLicenseScore, regen=REGEN_TEST_FIXTURES)
