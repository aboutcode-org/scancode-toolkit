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
        query_doc = self.get_test_loc('hash/rules/lgpl-2.0-plus_23.RULE')

        matches = idx.match(query_doc)
        assert 1 == len(matches)
        match = matches[0]
        assert 100 == match.coverage()
        assert match_hash.MATCH_HASH == match.matcher
        assert rules[0] == match.rule
        assert Span(0, 119) == match.qspan
        assert Span(0, 119) == match.ispan

    def test_match_hash_returns_correct_offset(self):
        rule_dir = self.get_test_loc('hash/rules')
        rules = list(models.load_rules(rule_dir))
        idx = index.LicenseIndex(rules)
        query_doc = self.get_test_loc('hash/query.txt')
        matches = idx.match(query_doc)
        assert 1 == len(matches)
        match = matches[0]
        assert match_hash.MATCH_HASH == match.matcher
        assert 100 == match.coverage()
        assert rules[0] == match.rule
        assert Span(0, 119) == match.qspan
        assert Span(0, 119) == match.ispan
