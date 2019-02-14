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

import pytest

from commoncode.testcase import FileDrivenTesting
from commoncode.text import python_safe_name

import cluecode_assert_utils

"""
Tests of ScanCode copyright detection using Fossology copyright test suite data.
"""

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


expected_failures = set('''
    test_fossology_copyright_testdata14
    test_fossology_copyright_testdata19
    test_fossology_copyright_testdata18
    test_fossology_copyright_testdata83
    test_fossology_copyright_testdata87
    test_fossology_copyright_testdata79
    test_fossology_copyright_testdata78
    test_fossology_copyright_testdata5
    test_fossology_copyright_testdata86
    test_fossology_copyright_testdata126
    test_fossology_copyright_testdata31
    '''.split()
)

def build_copyright_test_methods_with_fossology_data():
    """
    Yield one test method for each Fossology copyright test.
    """
    base_dir = test_env.get_test_loc('copyright_fossology')
    test_data_dir = base_dir
    test_files = [os.path.join(base_dir, tf)
                  for tf in os.listdir(base_dir) if (not tf.endswith('~'))]

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

        expected_copyrights = []
        for match in copyregex.finditer(expected_text):
            expected_copyrights.extend(match.groups())

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

        expected_copyrights_fixed = []

        for value in expected_copyrights:
            if value.lower().startswith(
                (b'written', b'auth', b'maint', b'put', b'contri', b'indiv', b'mod')):
                continue

            value = b' '.join(value.split())

            for x, y in reps:
                value = value.replace(x, y)

            value = value.strip()
            value = value.rstrip(b',;:')
            value = value.strip()
            value = b' '.join(value.split())
            expected_copyrights_fixed.append(value.strip())

        expected_copyrights = [e for e in expected_copyrights_fixed if e and e .strip()]

        test_method = make_test_func(test_file, expected_file, expected_copyrights)

        tfn = test_file.replace(test_data_dir, '').strip('\/\\')
        test_name = 'test_fossology_copyright_%(tfn)s' % locals()
        test_name = python_safe_name(test_name)
        if isinstance(test_name, unicode):
            test_name = test_name.encode('utf-8')

        test_method.__name__ = test_name
        test_method.funcname = test_name

        if test_name in expected_failures:
            test_method = pytest.mark.xfail(test_method)

        yield test_method, test_name


def make_test_func(test_file_loc, expected_file_loc, expected):
    def copyright_test_method(self):
        copyrights, _authors, _holders = cluecode_assert_utils.copyright_detector(test_file_loc)
        copyrights = [c.encode('utf-8') for c in copyrights]

        try:
            assert expected == copyrights
        except:
            failure_trace = [
                'Failed to detect copyright in: file://' + test_file_loc, '\n',
                'expected as file://' + expected_file_loc, '\n',
                ] + expected

            assert failure_trace == copyrights

    return copyright_test_method


def build_tests(clazz):
    """
    Dynamically build test methods and attach these to the clazz test class.
    """
    for test_method, test_name in build_copyright_test_methods_with_fossology_data():
        setattr(clazz, test_name, test_method)


class TestCopyrightFossologyDataDriven(FileDrivenTesting):
    # test functions are attached to this class at module import time
    pass


build_tests(clazz=TestCopyrightFossologyDataDriven)
