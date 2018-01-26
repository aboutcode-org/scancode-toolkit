#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

from commoncode.testcase import FileBasedTesting

from licensedcode.spans import Span

from licensedcode import index
from licensedcode import models
from licensedcode import match_hash

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
        assert Span(0, 121) == match.qspan
        assert Span(0, 121) == match.ispan

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
        assert Span(0, 121) == match.qspan
        assert Span(0, 121) == match.ispan
