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

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_cyclonedx_xml():
    pass


def test_cyclonedx_json():
    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('cyclonedx')
    args = ['-p', test_dir, '--cyclonedx-json', result_file]
    run_scan_click(args)
