# -*- coding: utf-8 -*-
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
import re
from unittest.case import expectedFailure

from commoncode.testcase import FileBasedTesting
from cluecode_assert_utils import check_detection
import cluecode.copyrights

"""
A test suite for ScanCode using Fossology copyright test data.
"""


class TestDetectCopyrights(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_copyright_detection_with_fossology_data(self):
        base_dir = self.get_test_loc('copyright_fossology')
        test_files = [os.path.join(base_dir, tf)
                      for tf in os.listdir(base_dir) if (not tf.endswith('~'))
                      # and '36' in tf
                      ]

        expected_files = []
        files_to_test = []
        for tf in test_files:
            if tf.endswith('_raw'):
                expected_files.append(tf)
                files_to_test.append(tf.replace('_raw', ''))

        assert sorted(test_files) == sorted(files_to_test + expected_files)

        copyregex = re.compile('<s>(.*?)</s>', re.DOTALL)
        authregex = re.compile('<t>(.*>)</t>', re.DOTALL)
        for expected_file, test_file in zip(expected_files, files_to_test):
            expected_text = open(expected_file, 'rb').read()

            expected_copyr = []
            for match in copyregex.finditer(expected_text):
                expected_copyr.extend(match.groups())

            expected_auth = []
            for match in authregex.finditer(expected_text):
                expected_auth.extend(match.groups())

            copyrights, authors, _years, _holders = cluecode.copyrights.detect(test_file)

            print()
            print('file://' + expected_file)
            print('file://' + test_file)

            if copyrights != expected_copyr:
                print('Copyrights')
                for x, r in map(None, expected_copyr, copyrights):
                    if x != r:
                        print(' ', x, ' but -->', r)

            if authors != expected_auth:
                print('Authors')
                for x, r in map(None, expected_auth, authors):
                    if x != r:
                        print(' ', x, ' but -->', r)
