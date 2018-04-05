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

from commoncode.testcase import FileBasedTesting
from commoncode import text

from licensedcode import cache
from licensedcode.match_spdx_lid import clean_line
from licensedcode.match_spdx_lid import strip_spdx_lid
from licensedcode.query import Query

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestSpdxQueryLinesBasic(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_Query_with_spdx(self):
        idx = cache.get_index()
        querys = '''
 * SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)

 * SPDX-License-Identifier: EPL-2.0 OR Apache-2.0 OR GPL-2.0 WITH Classpath-exception-2.0 OR LicenseRef-GPL-2.0 WITH Assembly-exception
            Always
 *  SPDX-License-Identifier: BSD-3-Clause
// SPDX-License-Identifier: BSD-3-Clause
# SPDX-License-Identifier: BSD-3-Clause
// SPDX-License-Identifier: GPL-1.0+
/* SPDX-License-Identifier: GPL-1.0+ WITH Linux-syscall-note */
 * SPDX-License-Identifier: GPL-2.0
 * SPDX-License-Identifier: GPL-2.0+
 * SPDX-License-Identifier:    GPL-2.0
; SPDX-License-Identifier: GPL-2.0
;;; SPDX-License-Identifier: GPL-2.0
! SPDX-License-Identifier: GPL-2.0
// SPDX-License-Identifier: GPL-2.0
// SPDX-License-Identifier: GPL-2.0+
/* SPDX-License-Identifier: GPL-2.0 */
/* SPDX-License-Identifier: GPL-2.0+ */
# SPDX-License-Identifier: GPL-2.0
// SPDX-License-Identifier: (GPL-2.0 OR BSD-2-Clause)
 * SPDX-License-Identifier: (GPL-2.0+ OR BSD-3-Clause)
// SPDX-License-Identifier: (GPL-2.0 OR BSD-3-Clause)
// SPDX-License-Identifier: (GPL-2.0+ OR BSD-3-Clause)
 * SPDX-License-Identifier: (GPL-2.0 OR MIT)
 * SPDX-License-Identifier: (GPL-2.0+ OR MIT)
// SPDX-License-Identifier: (GPL-2.0 OR MPL-1.1)
/* SPDX-License-Identifier: GPL-2.0 WITH Linux-syscall-note */
/* SPDX-License-Identifier: GPL-2.0+ WITH Linux-syscall-note */
/* SPDX-License-Identifier: ((GPL-2.0 WITH Linux-syscall-note) AND MIT) */
/* SPDX-License-Identifier: ((GPL-2.0 WITH Linux-syscall-note) OR BSD-2-Clause) */
/* SPDX-License-Identifier: ((GPL-2.0 WITH Linux-syscall-note) OR BSD-3-Clause) */
/* SPDX-License-Identifier: ((GPL-2.0+ WITH Linux-syscall-note) OR BSD-3-Clause) */
/* SPDX-License-Identifier: ((GPL-2.0 WITH Linux-syscall-note) OR MIT) */
/* SPDX-License-Identifier: LGPL-2.0+ WITH Linux-syscall-note */
// SPDX-License-Identifier: LGPL-2.1+
/* SPDX-License-Identifier: LGPL-2.1 WITH Linux-syscall-note */
/* SPDX-License-Identifier: LGPL-2.1+ WITH Linux-syscall-note */
// SPDX License Identifier LGPL-2.1+

From uboot: the first two lines are patch-like:
+ * SPDX-License-Identifier:    GPL-2.0+
+SPDX-License-Identifier:    GPL-2.0+
        SPDX-License-Identifier:        GPL-2.0+
 * SPDX-License-Identifier:     GPL-2.0+ BSD-2-Clause
 * SPDX-License-Identifier:     GPL-2.0+        BSD-2-Clause
 * SPDX-License-Identifier: GPL-2.0    BSD-3-Clause
        SPDX-License-Identifier:        GPL-2.0+        BSD-3-Clause
 * SPDX-License-Identifier:     GPL-2.0 IBM-pibs
# SPDX-License-Identifier:      ISC
 * SPDX-License-Identifier:     LGPL-2.0+
 * SPDX-License-Identifier:     LGPL-2.1+
# SPDX-License-Identifier:  GPL-2.0 LGPL-2.1
            '''

        qry = Query(query_string=querys, idx=idx)
        expected = [
            (u'* SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)', 2, 0, 15),
            (u'* SPDX-License-Identifier: EPL-2.0 OR Apache-2.0 OR GPL-2.0 WITH Classpath-exception-2.0 OR LicenseRef-GPL-2.0 WITH Assembly-exception', 4, 16, 42),
            (u'*  SPDX-License-Identifier: BSD-3-Clause', 6, 44, 49),
            (u'// SPDX-License-Identifier: BSD-3-Clause', 7, 50, 55),
            (u'# SPDX-License-Identifier: BSD-3-Clause', 8, 56, 61),
            (u'// SPDX-License-Identifier: GPL-1.0+', 9, 62, 67),
            (u'/* SPDX-License-Identifier: GPL-1.0+ WITH Linux-syscall-note */', 10, 68, 77),
            (u'* SPDX-License-Identifier: GPL-2.0', 11, 78, 83),
            (u'* SPDX-License-Identifier: GPL-2.0+', 12, 84, 89),
            (u'* SPDX-License-Identifier:    GPL-2.0', 13, 90, 95),
            (u'; SPDX-License-Identifier: GPL-2.0', 14, 96, 101),
            (u';;; SPDX-License-Identifier: GPL-2.0', 15, 102, 107),
            (u'! SPDX-License-Identifier: GPL-2.0', 16, 108, 113),
            (u'// SPDX-License-Identifier: GPL-2.0', 17, 114, 119),
            (u'// SPDX-License-Identifier: GPL-2.0+', 18, 120, 125),
            (u'/* SPDX-License-Identifier: GPL-2.0 */', 19, 126, 131),
            (u'/* SPDX-License-Identifier: GPL-2.0+ */', 20, 132, 137),
            (u'# SPDX-License-Identifier: GPL-2.0', 21, 138, 143),
            (u'// SPDX-License-Identifier: (GPL-2.0 OR BSD-2-Clause)', 22, 144, 153),
            (u'* SPDX-License-Identifier: (GPL-2.0+ OR BSD-3-Clause)', 23, 154, 163),
            (u'// SPDX-License-Identifier: (GPL-2.0 OR BSD-3-Clause)', 24, 164, 173),
            (u'// SPDX-License-Identifier: (GPL-2.0+ OR BSD-3-Clause)', 25, 174, 183),
            (u'* SPDX-License-Identifier: (GPL-2.0 OR MIT)', 26, 184, 191),
            (u'* SPDX-License-Identifier: (GPL-2.0+ OR MIT)', 27, 192, 199),
            (u'// SPDX-License-Identifier: (GPL-2.0 OR MPL-1.1)', 28, 200, 209),
            (u'/* SPDX-License-Identifier: GPL-2.0 WITH Linux-syscall-note */', 29, 210, 219),
            (u'/* SPDX-License-Identifier: GPL-2.0+ WITH Linux-syscall-note */', 30, 220, 229),
            (u'/* SPDX-License-Identifier: ((GPL-2.0 WITH Linux-syscall-note) AND MIT) */', 31, 230, 241),
            (u'/* SPDX-License-Identifier: ((GPL-2.0 WITH Linux-syscall-note) OR BSD-2-Clause) */', 32, 242, 255),
            (u'/* SPDX-License-Identifier: ((GPL-2.0 WITH Linux-syscall-note) OR BSD-3-Clause) */', 33, 256, 269),
            (u'/* SPDX-License-Identifier: ((GPL-2.0+ WITH Linux-syscall-note) OR BSD-3-Clause) */', 34, 270, 283),
            (u'/* SPDX-License-Identifier: ((GPL-2.0 WITH Linux-syscall-note) OR MIT) */', 35, 284, 295),
            (u'/* SPDX-License-Identifier: LGPL-2.0+ WITH Linux-syscall-note */', 36, 296, 305),
            (u'// SPDX-License-Identifier: LGPL-2.1+', 37, 306, 311),
            (u'/* SPDX-License-Identifier: LGPL-2.1 WITH Linux-syscall-note */', 38, 312, 321),
            (u'/* SPDX-License-Identifier: LGPL-2.1+ WITH Linux-syscall-note */', 39, 322, 331),
            (u'// SPDX License Identifier LGPL-2.1+', 40, 332, 337),
            (u'+ * SPDX-License-Identifier:    GPL-2.0+', 43, 347, 352),
            (u'+SPDX-License-Identifier:    GPL-2.0+', 44, 353, 358),
            (u'SPDX-License-Identifier:        GPL-2.0+', 45, 359, 364),
            (u'* SPDX-License-Identifier:     GPL-2.0+ BSD-2-Clause', 46, 365, 373),
            (u'* SPDX-License-Identifier:     GPL-2.0+        BSD-2-Clause', 47, 374, 382),
            (u'* SPDX-License-Identifier: GPL-2.0    BSD-3-Clause', 48, 383, 391),
            (u'SPDX-License-Identifier:        GPL-2.0+        BSD-3-Clause', 49, 392, 400),
            (u'* SPDX-License-Identifier:     GPL-2.0 IBM-pibs', 50, 401, 408),
            (u'# SPDX-License-Identifier:      ISC', 51, 409, 412),
            (u'* SPDX-License-Identifier:     LGPL-2.0+', 52, 413, 418),
            (u'* SPDX-License-Identifier:     LGPL-2.1+', 53, 419, 424),
            (u'# SPDX-License-Identifier:  GPL-2.0 LGPL-2.1', 54, 425, 433),
        ]

        assert expected == qry.spdx_lines


class TestMatchSpdx(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_clean_line(self):
        tests = [
            '* SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)',
            '*  SPDX-License-Identifier: BSD-3-Clause  ',
            '// SPDX-License-Identifier: BSD-3-Clause (',
            '# SPDX-License-Identifier: BSD-3-Clause',
            '/* SPDX-License-Identifier: GPL-1.0+ WITH Linux-syscall-note */',
            '* SPDX-License-Identifier: GPL-2.0+',
            '* SPDX-License-Identifier:    GPL-2.0',
            '; SPDX-License-Identifier: GPL-2.0',
            ';;; SPDX-License-Identifier: GPL-2.0',
            '! SPDX-License-Identifier: GPL-2.0',
            '// SPDX-License-Identifier: GPL-2.0+',
            '/* SPDX-License-Identifier: GPL-2.0+ */',
            '* SPDX-License-Identifier: (GPL-2.0+ OR BSD-3-Clause )',
            '(/ SPDX-License-Identifier: (GPL-2.0 OR BSD-3-Clause)',
            '// SPDX-License-Identifier: LGPL-2.1+',
            '+SPDX-License-Identifier:    GPL-2.0+',
            '* SPDX-License-Identifier:     GPL-2.0+        BSD-2-Clause',
            '// SPDX License Identifier LGPL-2.1+',
        ]

        expected = [
            'SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)',
            'SPDX-License-Identifier: BSD-3-Clause',
            'SPDX-License-Identifier: BSD-3-Clause',
            'SPDX-License-Identifier: BSD-3-Clause',
            'SPDX-License-Identifier: GPL-1.0+ WITH Linux-syscall-note',
            'SPDX-License-Identifier: GPL-2.0+',
            'SPDX-License-Identifier: GPL-2.0',
            'SPDX-License-Identifier: GPL-2.0',
            'SPDX-License-Identifier: GPL-2.0',
            'SPDX-License-Identifier: GPL-2.0',
            'SPDX-License-Identifier: GPL-2.0+',
            'SPDX-License-Identifier: GPL-2.0+',
            'SPDX-License-Identifier: (GPL-2.0+ OR BSD-3-Clause )',
            'SPDX-License-Identifier: (GPL-2.0 OR BSD-3-Clause)',
            'SPDX-License-Identifier: LGPL-2.1+',
            'SPDX-License-Identifier: GPL-2.0+',
            'SPDX-License-Identifier: GPL-2.0+ BSD-2-Clause',
            'SPDX License Identifier LGPL-2.1+'
        ]

        for test, expect in zip(tests, expected):
            assert expect == clean_line(test)

    def test_strip_spdx_lid(self):
        test = [
            'SPDX  License   Identifier  : BSD-3-Clause',
            'SPDX-License-Identifier  : BSD-3-Clause',
            ' SPDX License--Identifier: BSD-3-Clause',
            'SPDX-License-Identifier : BSD-3-Clause',
        ]

        results = [strip_spdx_lid(l) for l in test]
        expected = [u'BSD-3-Clause', u'BSD-3-Clause', u' BSD-3-Clause', u'BSD-3-Clause']
        assert expected == results


def get_tester(test_loc , expected_loc, regen=False):

    def test_method(self):
        idx = cache.get_index()
        qry = Query(location=test_loc, idx=idx)
        results = [list(l) for l in qry.spdx_lines]
        if regen:
            with open(expected_loc, 'wb') as ef:
                json.dump(results, ef, indent=2)
            expected = results
        else:
            with open(expected_loc, 'rb') as ef:
                expected = json.load(ef, object_pairs_hook=OrderedDict)

        assert expected == results

    return test_method


def build_spdx_line_tests(clazz, test_dir='spdx/lines', regen=False):
    """
    Dynamically build test methods from test files to test SPDX lines collection.
    """
    test_dir = os.path.join(TEST_DATA_DIR, test_dir)
    for test_file in os.listdir(test_dir):
        if test_file.endswith('.json'):
            continue
        test_loc = os.path.join(test_dir, test_file)
        expected_loc = test_loc + '.json'

        test_name = 'test_collect_spdx_query_lines_%(test_file)s' % locals()
        test_name = text.python_safe_name(test_name)
        test_name = str(test_name)
        test_method = get_tester(test_loc, expected_loc, regen)
        test_method.__name__ = test_name
        test_method.funcname = test_name
        # attach that method to our test class
        setattr(clazz, test_name, test_method)


class TestQuerySpdxLines(unittest.TestCase):
    # test functions are attached to this class at module import time
    pass


build_spdx_line_tests(clazz=TestQuerySpdxLines, regen=False)
