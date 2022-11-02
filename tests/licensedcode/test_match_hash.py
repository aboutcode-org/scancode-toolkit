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
from licensedcode import models
from licensedcode import match_hash
from licensedcode.spans import Span


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestHashMatch(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_hash_can_match_exactly(self):
        rule_dir = self.get_test_loc('hash/rules')
        rules = list(models.load_rules(rule_dir))
        idx = index.LicenseIndex(rules)
        query_doc = self.get_test_loc('hash/old_rules/lgpl-2.0-plus_23.RULE')

        matches = idx.match(query_doc)
        assert len(matches) == 1
        match = matches[0]
        assert match.coverage() == 100
        assert match.matcher == match_hash.MATCH_HASH
        assert match.rule == rules[0]
        assert match.qspan == Span(0, 119)
        assert match.ispan == Span(0, 119)

    def test_match_hash_returns_correct_offset(self):
        rule_dir = self.get_test_loc('hash/rules')
        rules = list(models.load_rules(rule_dir))
        idx = index.LicenseIndex(rules)
        query_doc = self.get_test_loc('hash/query.txt')
        matches = idx.match(query_doc)
        assert len(matches) == 1
        match = matches[0]
        assert match.matcher == match_hash.MATCH_HASH 
        assert match.coverage() == 100 
        assert match.rule == rules[0]
        assert match.qspan == Span(0, 119)
        assert match.ispan == Span(0, 119)
