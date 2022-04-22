#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_licenses_reference_works():
    test_dir = test_env.get_test_loc('plugin_licenses_reference/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license', '--package', '--licenses-reference',
        test_dir, '--json-pp', result_file, '--verbose']
    run_scan_click(args)
    check_json_scan(
        test_env.get_test_loc('plugin_licenses_reference/scan.expected.json'),
        result_file, remove_file_date=True, remove_uuid=True, regen=REGEN_TEST_FIXTURES,
    )
