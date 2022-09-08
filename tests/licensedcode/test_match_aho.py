#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
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
        idx = index.LicenseIndex(models.load_rules(rules_data_dir=rule_dir))

        query_loc = self.get_test_loc('mach_aho/rtos_exact/gpl-2.0-freertos.RULE')

        qry = query.build_query(location=query_loc, idx=idx)

        matches = match_aho.exact_match(idx, qry.whole_query_run(), idx.rules_automaton)
        assert len(matches) == 1
        match = matches[0]
        assert match.matcher == match_aho.MATCH_AHO_EXACT
