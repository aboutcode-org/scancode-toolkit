# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from cluecode import copyrights
from cluecode import linux_credits
from commoncode.testcase import FileDrivenTesting

from scancode_config import REGEN_TEST_FIXTURES
from scancode.cli_test_utils import check_json

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_detect_credits_authors():
    location = test_env.get_test_loc('credits/CREDITS')
    expected = test_env.get_test_loc('credits/CREDITS-expected-credits.json', must_exist=False)

    results = [o.to_dict() for o in linux_credits.detect_credits_authors(location)]
    check_json(expected, results, regen=REGEN_TEST_FIXTURES)


def test_detect_copyrights__for_credits():
    location = test_env.get_test_loc('credits/CREDITS')
    expected = test_env.get_test_loc('credits/CREDITS-expected-copyrights.json', must_exist=False)

    results = [o.to_dict() for o in copyrights.detect_copyrights(location, include_authors=True)]
    check_json(expected, results, regen=REGEN_TEST_FIXTURES)
