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

import os

from commoncode.testcase import FileBasedTesting
from licensedcode import index
from licensedcode import match_aho
from licensedcode import models
from licensedcode import query


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestMatchExact(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_freertos(self):
        rule_dir = self.get_test_loc('mach_aho/rtos_exact/')
        idx = index.LicenseIndex(models.load_rules(rule_dir))

        query_loc = self.get_test_loc('mach_aho/rtos_exact/gpl-2.0-freertos.RULE')

        qry = query.build_query(location=query_loc, idx=idx)

        matches = match_aho.exact_match(idx, qry.whole_query_run(), idx.rules_automaton)
        assert 1 == len(matches)
        match = matches[0]
        assert match_aho.MATCH_AHO_EXACT == match.matcher
