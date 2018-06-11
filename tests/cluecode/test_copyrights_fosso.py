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

from commoncode.testcase import FileDrivenTesting

import cluecode_assert_utils

"""
A WIP test suite for ScanCode using Fossology copyright test data.
"""

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_copyright_detection_with_fossology_data():
    base_dir = test_env.get_test_loc('copyright_fossology')
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

    copyregex = re.compile('<s>(.*?)</s>', re.DOTALL | re.UNICODE)
    for expected_file, test_file in zip(expected_files, files_to_test):
        expected_text = open(expected_file, 'rb').read()

        expected_copyr = []
        for match in copyregex.finditer(expected_text):
            expected_copyr.extend(match.groups())

        reps = [
            (b'. All rights reserved.', b'.'),
            (b'All Rights Reserved except as specified below.', b''),
            (b' All # Rights Reserved.', b''),
            (b'#', b' '),
            (b'  ', b' '),
            (b'* All Rights Reserved.', b''),
            (b'All rights reserved', b''),
            (b'All Rights Reserved', b''),
            (b'Copyright:', b'Copyright '),
            (b'. .', b'.'),
            (b' *% ', b' '),
            (b'&copy;', b'(c)'),
            (b' * ', b' '),
            (b'Copyright  Copyright', b'Copyright'),
            (b'Copyright Copyright', b'Copyright'),
            (b'All rights reserved.', b''),
            (b'Created 1991.', b''),
            (b'Created 1990.', b''),
            (b'copyright under', b''),
            (b'@copyright{}', b''),
            (b'. .', b'.'),

            (b'', b''),
        ]
        expected_copyr2 = []
        for a in expected_copyr:
            if a.lower().startswith((b'written', b'auth', b'maint', b'put', b'contri', b'indiv', b'mod')):
                continue
            a = b' '.join(a.split())
            for x, y in reps:
                a = a.replace(x, y)
            a = a.strip()
            a = a.rstrip(b',;:')
            a = a.strip()
            a = b' '.join(a.split())
            expected_copyr2.append(a.strip())

        expected_copyr = [e for e in expected_copyr2 if e and e .strip()]

        copyrights, _authors, _holders = cluecode_assert_utils.copyright_detector(test_file)
        copyrights = [c.encode('utf-8') for c in copyrights]

        if copyrights != expected_copyr:
            print()
            print('file://' + expected_file)
            for ex, cop in map(None, expected_copyr, copyrights):
                if ex != cop:
                    print(b'   EX:', ex)
                    print(b'   AC:', cop)
                    print()


if __name__ == '__main__':
    test_copyright_detection_with_fossology_data()
