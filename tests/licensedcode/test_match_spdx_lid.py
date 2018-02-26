#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from collections import OrderedDict
import json
import unittest

import attr

from commoncode.testcase import FileBasedTesting
from commoncode import text

from licensedcode.match_spdx_lid import clean_tokens
from licensedcode.match_spdx_lid import collect_spdx_tokens
from licensedcode.match_spdx_lid import merge_tokens
from licensedcode.match_spdx_lid import spdx_tokens
from licensedcode.match_spdx_lid import SpdxToken
from licensedcode.match_spdx_lid import strip_tokens
from licensedcode.tokenize import query_lines

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestSpdxQueryCollector(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_spdx_tokens_with_empty_dict(self):
        line = u'/* SPDX-License-Identifier=: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT) */junk'
        line_num = 1
        start_pos_in_line = 1
        dic_getter = {}.get
        result = list(spdx_tokens(line, line_num, start_pos_in_line, dic_getter))
        expected = [
            SpdxToken(value=u' ', line_num=1, is_text=False, is_known=False),
            SpdxToken(value=u'SPDX', line_num=1, is_text=True, is_known=False),
            SpdxToken(value=u'-', line_num=1, is_text=False, is_known=False),
            SpdxToken(value=u'License', line_num=1, is_text=True, is_known=False),
            SpdxToken(value=u'-', line_num=1, is_text=False, is_known=False),
            SpdxToken(value=u'Identifier', line_num=1, is_text=True, is_known=False),
            SpdxToken(value=u' (', line_num=1, is_text=False, is_known=False),
            SpdxToken(value=u'BSD', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'3', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'Clause', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'EPL', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'1', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u'.', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'0', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'Apache', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'2', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u'.', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'0', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'MIT', line_num=1, start_pos=-1, is_text=True, is_known=False),
            SpdxToken(value=u') ', line_num=1, start_pos=-1, is_text=False, is_known=False),
            SpdxToken(value=u'junk', line_num=1, start_pos=-1, is_text=True, is_known=False)
        ]

        assert expected == result

    def test_spdx_tokens_with_dict_with_malformed_tag(self):
        line = 'SPDX license identifier: MPL-2.0'
        line_num = 1
        start_pos_in_line = 0
        dic_getter = {
            'spdx': 0,
            'license': 1,
            'identifier': 2,
            '0': 3,
            '1': 4,
            '2': 5,
            '3': 6,
            'bsd': 7,
            'clause': 8,
            'or': 9,
            'and': 10,
            'mit': 11,
            'with': 12,
            'epl': 12,
            'with': 12,
        }.get
        expected = [
            SpdxToken(value=u'SPDX', line_num=1, start_pos=0, end_pos=0, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'license', line_num=1, start_pos=1, end_pos=1, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'identifier', line_num=1, start_pos=2, end_pos=2, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'MPL', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'2', line_num=1, start_pos=3, end_pos=3, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'.', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'0', line_num=1, start_pos=4, end_pos=4, is_text=True, is_known=True, is_marker=False)
        ]
        result = list(spdx_tokens(line, line_num, start_pos_in_line, dic_getter))
        assert expected == result

    def test_merge_tokens_with_malformed_tag(self):
        tokens = [
            SpdxToken(value=u'SPDX', line_num=1, start_pos=0, end_pos=0, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'license', line_num=1, start_pos=1, end_pos=1, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'identifier', line_num=1, start_pos=2, end_pos=2, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'MPL', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'2', line_num=1, start_pos=3, end_pos=3, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'.', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'0', line_num=1, start_pos=4, end_pos=4, is_text=True, is_known=True, is_marker=False)
        ]
        expected = [
            SpdxToken(value=u'SPDX license identifier', line_num=1, start_pos=0, end_pos=2, is_text=True, is_known=True, is_marker=True),
            SpdxToken(value=u'MPL-2.0', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False)
        ]

        assert expected == list(merge_tokens(tokens))

    def test_strip_tokens_with_malformed_tag(self):
        tokens = [
            SpdxToken(value=u'SPDX', line_num=1, start_pos=0, end_pos=0, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'license', line_num=1, start_pos=1, end_pos=1, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'identifier', line_num=1, start_pos=2, end_pos=2, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'MPL', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'2', line_num=1, start_pos=3, end_pos=3, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'.', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'0', line_num=1, start_pos=4, end_pos=4, is_text=True, is_known=True, is_marker=False)
        ]
        expected = [
            SpdxToken(value=u'SPDX', line_num=1, start_pos=0, end_pos=0, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'license', line_num=1, start_pos=1, end_pos=1, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'identifier', line_num=1, start_pos=2, end_pos=2, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'MPL', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'2', line_num=1, start_pos=3, end_pos=3, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'.', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'0', line_num=1, start_pos=4, end_pos=4, is_text=True, is_known=True, is_marker=False)
        ]

        assert expected == list(strip_tokens(tokens))

    def test_spdx_tokens_with_dict(self):
        line = u'/* SPDX-License-Identifier=: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 with MIT) */=;"{}[]junk'
        line_num = 1
        start_pos_in_line = 1
        dic_getter = {
            'spdx': 0,
            'license': 1,
            'identifier': 2,
            '0': 3,
            '1': 4,
            '2': 5,
            '3': 6,
            'bsd': 7,
            'clause': 8,
            'or': 9,
            'and': 10,
            'mit': 11,
            'with': 12,
            'epl': 12,
            'with': 12,
        }.get
        result = list(spdx_tokens(line, line_num, start_pos_in_line, dic_getter))
        expected = [
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'SPDX', line_num=1, start_pos=1, end_pos=1, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'License', line_num=1, start_pos=2, end_pos=2, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'Identifier', line_num=1, start_pos=3, end_pos=3, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' (', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'BSD', line_num=1, start_pos=4, end_pos=4, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'3', line_num=1, start_pos=5, end_pos=5, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'Clause', line_num=1, start_pos=6, end_pos=6, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=7, end_pos=7, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'EPL', line_num=1, start_pos=8, end_pos=8, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'1', line_num=1, start_pos=9, end_pos=9, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'.', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'0', line_num=1, start_pos=10, end_pos=10, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=11, end_pos=11, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'Apache', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'2', line_num=1, start_pos=12, end_pos=12, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'.', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'0', line_num=1, start_pos=13, end_pos=13, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'with', line_num=1, start_pos=14, end_pos=14, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'MIT', line_num=1, start_pos=15, end_pos=15, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u') ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'junk', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False)
        ]

        assert expected == result

    def test_collect_spdx_tokens_with_dict_and_max(self):
        line = u'/* SPDX-License-Identifier=: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 with MIT) */junk'
        line_num = 5
        start_pos_in_line = 1
        dic_getter = {
            'spdx': 0,
            'license': 1,
            'identifier': 2,
            '0': 3,
            '1': 4,
            '2': 5,
            '3': 6,
            'bsd': 7,
            'clause': 8,
            'or': 9,
            'and': 10,
            'mit': 11,
            'with': 12,
            'epl': 12,
            'with': 12,
        }.get
        result = list(collect_spdx_tokens(line, line_num, start_pos_in_line, dic_getter, max_tokens=10))
        expected = [
            SpdxToken(value=u'SPDX-License-Identifier', line_num=5, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=True),
            SpdxToken(value=u'(', line_num=5, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'BSD-3-Clause', line_num=5, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=5, start_pos=7, end_pos=7, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'EPL-1.0', line_num=5, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=5, start_pos=11, end_pos=11, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'Apache-2.0', line_num=5, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'with', line_num=5, start_pos=14, end_pos=14, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'MIT', line_num=5, start_pos=15, end_pos=15, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u')', line_num=5, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False)
        ]

        assert expected == result

    def test_merge_tokens(self):

        test = [
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'SPDX', line_num=1, start_pos=1, end_pos=1, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'License', line_num=1, start_pos=2, end_pos=2, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'Identifier', line_num=1, start_pos=3, end_pos=3, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' (', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'BSD', line_num=1, start_pos=4, end_pos=4, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'3', line_num=1, start_pos=5, end_pos=5, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'Clause', line_num=1, start_pos=6, end_pos=6, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=7, end_pos=7, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'EPL', line_num=1, start_pos=8, end_pos=8, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'1', line_num=1, start_pos=9, end_pos=9, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'.', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'0', line_num=1, start_pos=10, end_pos=10, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=11, end_pos=11, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'Apache', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'-', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'2', line_num=1, start_pos=12, end_pos=12, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'.', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'0', line_num=1, start_pos=13, end_pos=13, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'with', line_num=1, start_pos=14, end_pos=14, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'MIT', line_num=1, start_pos=15, end_pos=15, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u') ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'junk', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False)
        ]

        result = list(merge_tokens(test))
        expected = [
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'SPDX-License-Identifier', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=True),
            SpdxToken(value=u' (', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'BSD-3-Clause', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=7, end_pos=7, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'EPL-1.0', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=11, end_pos=11, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'Apache-2.0', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'with', line_num=1, start_pos=14, end_pos=14, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'MIT', line_num=1, start_pos=15, end_pos=15, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u') ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'junk', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False)
        ]

        assert expected == result

    def test_clean_tokens(self):
        test = [
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'SPDX-License-Identifier', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=True),
            SpdxToken(value=u' (', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'BSD-3-Clause', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=7, end_pos=7, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'EPL-1.0', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=11, end_pos=11, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'Apache-2.0', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'with', line_num=1, start_pos=14, end_pos=14, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u' ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'MIT', line_num=1, start_pos=15, end_pos=15, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u') ', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'junk', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False)
        ]
        result = list(clean_tokens(test))
        expected = [
            SpdxToken(value=u'SPDX-License-Identifier', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=True),
            SpdxToken(value=u'(', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'BSD-3-Clause', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=7, end_pos=7, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'EPL-1.0', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'OR', line_num=1, start_pos=11, end_pos=11, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'Apache-2.0', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False),
            SpdxToken(value=u'with', line_num=1, start_pos=14, end_pos=14, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u'MIT', line_num=1, start_pos=15, end_pos=15, is_text=True, is_known=True, is_marker=False),
            SpdxToken(value=u')', line_num=1, start_pos=-1, end_pos=-1, is_text=False, is_known=False, is_marker=False),
            SpdxToken(value=u'junk', line_num=1, start_pos=-1, end_pos=-1, is_text=True, is_known=False, is_marker=False)
        ]

        assert expected == result


known_toks = ''' 0 0+ 1+ 1 2 3 4 agpl and any apache assembly bsd by cc
classpath clause ecos epl exception gpl ibm identifier isc later lgpl license
licenseref linux mit mpl netbsd or pibs spdx syscall unlicense with
'''.split()

tokens_dictionary = {key: value for value, key in enumerate(known_toks)}


def get_tester(test_loc , expected_loc, regen=False):

    def test_method(self):
        dic_getter = tokens_dictionary.get
        results = []
        for line_num, line in enumerate(query_lines(test_loc), 1):
            toks = collect_spdx_tokens(line, line_num, 0, dic_getter)
            toks = [attr.asdict(t, dict_factory=OrderedDict) for t in toks]
            if toks:
                results.append(toks)

        if regen:
            with open(expected_loc, 'wb') as ef:
                json.dump(results, ef, indent=2)
            expected = results
        else:
            with open(expected_loc, 'rb') as ef:
                expected = json.load(ef, object_pairs_hook=OrderedDict)

        assert expected == results

    return test_method


def build_tokenize_tests(clazz, test_dir='spdx/tokenize', regen=False):
    """
    Dynamically build test methods from test files to test SPDX tokenization.
    """
    test_dir = os.path.join(TEST_DATA_DIR, test_dir)
    for test_file in os.listdir(test_dir):
        if test_file.endswith('.json'):
            continue
        test_loc = os.path.join(test_dir, test_file)
        expected_loc = test_loc + '.json'

        test_name = 'test_collect_spdx_tokens_%(test_file)s' % locals()
        test_name = text.python_safe_name(test_name)
        test_name = str(test_name)
        test_method = get_tester(test_loc, expected_loc, regen)
        test_method.__name__ = test_name
        test_method.funcname = test_name
        # attach that method to our test class
        setattr(clazz, test_name, test_method)


class TestSpdxTokens(unittest.TestCase):
    # test functions are attached to this class at module import time
    pass


build_tokenize_tests(clazz=TestSpdxTokens)
