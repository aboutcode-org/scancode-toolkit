#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import json
import unittest

from commoncode.testcase import FileBasedTesting
from commoncode import text
from license_expression import Licensing
from license_expression import ExpressionError

from licensedcode import cache
from licensedcode import models
from licensedcode.cache import get_spdx_symbols
from licensedcode.cache import get_unknown_spdx_symbol
from licensedcode.match_spdx_lid import _parse_expression
from licensedcode.match_spdx_lid import _reparse_invalid_expression
from licensedcode.match_spdx_lid import clean_text
from licensedcode.match_spdx_lid import get_expression
from licensedcode.match_spdx_lid import prepare_text
from licensedcode.match_spdx_lid import split_spdx_lid
from licensedcode.match_spdx_lid import _split_spdx_lid
from licensedcode.query import Query
from scancode_config import REGEN_TEST_FIXTURES
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
import pytest
from typing import NamedTuple

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestSPDXLicenses(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_spdx_license_detection_with_markup(self):
        test_dir = self.get_test_loc('match_spdx/scan/license')
        result_file = self.get_temp_file('json')
        args = [
            '--license',
            '--license-text',
            '--license-text-diagnostics',
            '--license-diagnostics',
            '--strip-root',
            '--verbose',
            '--json', result_file,
            test_dir,
        ]
        run_scan_click(args)
        test_loc = self.get_test_loc('match_spdx/scan-expected.json')
        check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


class TestSpdxQueryLines(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_Query_with_spdx_basic(self):
        idx = cache.get_index()
        querys = '''
 * SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)
 * SPDX-License-Identifier: EPL-2.0 OR Apache-2.0 OR GPL-2.0 WITH Classpath-exception-2.0
            Always

From uboot: the first two lines are patch-like:
 * SPDX-License-Identifier:     GPL-2.0+ BSD-2-Clause

Incorrect bu common short:
 * SPDX Short Identifier:     GPL-2.0+ BSD-2-Clause

            '''

        qry = Query(query_string=querys, idx=idx)
        expected = [
            ('SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)', 0, 15),
            ('SPDX-License-Identifier: EPL-2.0 OR Apache-2.0 OR GPL-2.0 WITH Classpath-exception-2.0', 16, 34),
            ('SPDX-License-Identifier:     GPL-2.0+ BSD-2-Clause', 45, 53),
            ('SPDX Short Identifier:     GPL-2.0+ BSD-2-Clause', 57, 65),
        ]

        assert qry.spdx_lines == expected


class TestNuGetSpdxQueryLines(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_Query_with_spdx_basic(self):
        idx = cache.get_index()
        querys = '''
 * https://licenses.nuget.org/(LGPL-2.0-only WITH FLTK-exception OR Apache-2.0)
 * SPDX-License-Identifier: EPL-2.0 OR Apache-2.0 OR GPL-2.0 WITH Classpath-exception-2.0
            Always

From uboot: the first two lines are patch-like:
 * https://licenses.nuget.org/MIT
 * https://licenses.nuget.org/(MIT)
            '''

        qry = Query(query_string=querys, idx=idx)
        expected = [
            ('licenses.nuget.org/(LGPL-2.0-only WITH FLTK-exception OR Apache-2.0)', 1, 14),
            ('SPDX-License-Identifier: EPL-2.0 OR Apache-2.0 OR GPL-2.0 WITH Classpath-exception-2.0', 15, 33),
            ('licenses.nuget.org/MIT', 45, 48),
            ('licenses.nuget.org/(MIT)', 50, 53)
        ]

        assert qry.spdx_lines == expected


def get_query_spdx_lines_test_method(test_loc , expected_loc, regen=REGEN_TEST_FIXTURES):
    """
    Collect a list of tuples (original line text, start known pos, end known
    pos) for SPDX identifier lines found in the file at `test_loc` and assert
    results against expected results found in the JSON file at `expected_loc`
    """

    def test_method(self):
        idx = cache.get_index()
        qry = Query(location=test_loc, idx=idx)
        results = [list(l) for l in qry.spdx_lines]
        if regen:
            with open(expected_loc, 'w') as ef:
                json.dump(results, ef, indent=2)
            expected = results
        else:
            with open(expected_loc) as ef:
                expected = json.load(ef)

        assert results == expected

    return test_method


def build_spdx_line_tests(clazz, test_dir='spdx/lines', regen=REGEN_TEST_FIXTURES):
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
        test_method = get_query_spdx_lines_test_method(test_loc, expected_loc, regen)
        test_method.__name__ = test_name
        # attach that method to our test class
        setattr(clazz, test_name, test_method)


class TestSpdxQueryLinesDataDriven(unittest.TestCase):
    pass


build_spdx_line_tests(clazz=TestSpdxQueryLinesDataDriven, regen=REGEN_TEST_FIXTURES)


class SpdxLidTest(NamedTuple):
    test: str
    expected: [tuple | list]


clean_line_tests = [
    SpdxLidTest(test='* SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)', expected='SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)'),
    SpdxLidTest(test='*  SPDX-License-Identifier: BSD-3-Clause  ', expected='SPDX-License-Identifier: BSD-3-Clause'),
    SpdxLidTest(test='// SPDX-License-Identifier: BSD-3-Clause (', expected='SPDX-License-Identifier: BSD-3-Clause'),
    SpdxLidTest(test='# SPDX-License-Identifier: BSD-3-Clause', expected='SPDX-License-Identifier: BSD-3-Clause'),
    SpdxLidTest(test='/* SPDX-License-Identifier: GPL-1.0+ WITH Linux-syscall-note */', expected='SPDX-License-Identifier: GPL-1.0+ WITH Linux-syscall-note'),
    SpdxLidTest(test='* SPDX-License-Identifier: GPL-2.0+', expected='SPDX-License-Identifier: GPL-2.0+'),
    SpdxLidTest(test='* SPDX-License-Identifier:    GPL-2.0', expected='SPDX-License-Identifier: GPL-2.0'),
    SpdxLidTest(test='; SPDX-License-Identifier: GPL-2.0', expected='SPDX-License-Identifier: GPL-2.0'),
    SpdxLidTest(test=';;; SPDX-License-Identifier: GPL-2.0', expected='SPDX-License-Identifier: GPL-2.0'),
    SpdxLidTest(test='! SPDX-License-Identifier: GPL-2.0', expected='SPDX-License-Identifier: GPL-2.0'),
    SpdxLidTest(test='// SPDX-License-Identifier: GPL-2.0+', expected='SPDX-License-Identifier: GPL-2.0+'),
    SpdxLidTest(test='/* SPDX-License-Identifier: GPL-2.0+ */', expected='SPDX-License-Identifier: GPL-2.0+'),
    SpdxLidTest(test='* SPDX-License-Identifier: (GPL-2.0+ OR BSD-3-Clause )', expected='SPDX-License-Identifier: (GPL-2.0+ OR BSD-3-Clause )'),
    SpdxLidTest(test='(/ SPDX-License-Identifier: (GPL-2.0 OR BSD-3-Clause)', expected='(/ SPDX-License-Identifier: (GPL-2.0 OR BSD-3-Clause)'),
    SpdxLidTest(test='// SPDX-License-Identifier: LGPL-2.1+', expected='SPDX-License-Identifier: LGPL-2.1+'),
    SpdxLidTest(test='+SPDX-License-Identifier:    GPL-2.0+', expected='SPDX-License-Identifier: GPL-2.0+'),
    SpdxLidTest(test='* SPDX-License-Identifier:     GPL-2.0+        BSD-2-Clause', expected='SPDX-License-Identifier: GPL-2.0+ BSD-2-Clause'),
    SpdxLidTest(test='// SPDX License Identifier LGPL-2.1+', expected='SPDX License Identifier LGPL-2.1+'),
    SpdxLidTest(test='* https://licenses.nuget.org/(LGPL-2.0-only WITH FLTK-exception OR Apache-2.0)', expected='https://licenses.nuget.org/(LGPL-2.0-only WITH FLTK-exception OR Apache-2.0)'),
    SpdxLidTest(test='* https://licenses.nuget.org/MIT', expected='https://licenses.nuget.org/MIT'),
    SpdxLidTest(test='* https://licenses.nuget.org/(MIT)', expected='https://licenses.nuget.org/(MIT)'),
    SpdxLidTest(test='<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>', expected='SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1'),
    SpdxLidTest(test='<a href="https://licenses.nuget.org/MIT">MIT</a>', expected='https://licenses.nuget.org/MIT'),
    SpdxLidTest(test='<a href="https://licenses.nuget.org/Apache-2.0">Apache-2.0</a>', expected='https://licenses.nuget.org/Apache-2.0'),
    SpdxLidTest(test='licenses.nuget.org /MIT\">MIT</a>                </div>', expected='licenses.nuget.org /MIT'),
]


@pytest.mark.parametrize('test, expected', clean_line_tests)
def test_clean_line(test, expected):
    result = clean_text(test)
    assert result == expected


prepare_text_tests = [
    SpdxLidTest(test='* SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)', expected=('SPDX-License-Identifier:', '(BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)')),
    SpdxLidTest(test='*  SPDX-License-Identifier: BSD-3-Clause  ', expected=('SPDX-License-Identifier:', 'BSD-3-Clause')),
    SpdxLidTest(test='// SPDX-License-Identifier: BSD-3-Clause (', expected=('SPDX-License-Identifier:', 'BSD-3-Clause')),
    SpdxLidTest(test='# SPDX-License-Identifier: BSD-3-Clause', expected=('SPDX-License-Identifier:', 'BSD-3-Clause')),
    SpdxLidTest(test='/* SPDX-License-Identifier: GPL-1.0+ WITH Linux-syscall-note */', expected=('SPDX-License-Identifier:', 'GPL-1.0+ WITH Linux-syscall-note')),
    SpdxLidTest(test='* SPDX-License-Identifier: GPL-2.0+', expected=('SPDX-License-Identifier:', 'GPL-2.0+')),
    SpdxLidTest(test='* SPDX-License-Identifier:    GPL-2.0', expected=('SPDX-License-Identifier:', 'GPL-2.0')),
    SpdxLidTest(test='; SPDX-License-Identifier: GPL-2.0', expected=('SPDX-License-Identifier:', 'GPL-2.0')),
    SpdxLidTest(test=';;; SPDX-License-Identifier: GPL-2.0', expected=('SPDX-License-Identifier:', 'GPL-2.0')),
    SpdxLidTest(test='! SPDX-License-Identifier: GPL-2.0', expected=('SPDX-License-Identifier:', 'GPL-2.0')),
    SpdxLidTest(test='// SPDX-License-Identifier: GPL-2.0+', expected=('SPDX-License-Identifier:', 'GPL-2.0+')),
    SpdxLidTest(test='/* SPDX-License-Identifier: GPL-2.0+ */', expected=('SPDX-License-Identifier:', 'GPL-2.0+')),
    SpdxLidTest(test='* SPDX-License-Identifier: (GPL-2.0+ OR BSD-3-Clause )', expected=('SPDX-License-Identifier:', '(GPL-2.0+ OR BSD-3-Clause )')),
    SpdxLidTest(test='(/ SPDX-Licence--Identifier: (GPL-2.0 OR BSD-3-Clause)', expected=('SPDX-Licence--Identifier:', '(GPL-2.0 OR BSD-3-Clause)')),
    SpdxLidTest(test='// SPDX-License-Identifier: LGPL-2.1+', expected=('SPDX-License-Identifier:', 'LGPL-2.1+')),
    SpdxLidTest(test='+SPDX-License-Identifier:    GPL-2.0+', expected=('SPDX-License-Identifier:', 'GPL-2.0+')),
    SpdxLidTest(test='* SPDX-License-Identifier:     GPL-2.0+        BSD-2-Clause', expected=('SPDX-License-Identifier:', 'GPL-2.0+ BSD-2-Clause')),
    SpdxLidTest(test='// SPDX Licence Identifier LGPL-2.1+', expected=('SPDX Licence Identifier', 'LGPL-2.1+')),
    SpdxLidTest(test='<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>', expected=('SPDX-License-Identifier:', 'Apache-2.0 WITH SHL-2.1')),
    SpdxLidTest(test='<a href="https://licenses.nuget.org/MIT">MIT</a>', expected=('licenses.nuget.org/', 'MIT')),
    SpdxLidTest(test='<a href="https://licenses.nuget.org/Apache-2.0">Apache-2.0</a>', expected=('licenses.nuget.org/', 'Apache-2.0')),
    SpdxLidTest(test='@REM # SPDX-License-Identifier: BSD-2-Clause-Patent', expected=('SPDX-License-Identifier:', 'BSD-2-Clause-Patent')),
    SpdxLidTest(test='* https://licenses.nuget.org/(LGPL-2.0-only WITH FLTK-exception OR Apache-2.0)', expected=('licenses.nuget.org/', '(LGPL-2.0-only WITH FLTK-exception OR Apache-2.0)')),
    SpdxLidTest(test='* https://licenses.nuget.org/MIT', expected=('licenses.nuget.org/', 'MIT')),
    SpdxLidTest(test='* https://licenses.nuget.org/(MIT)'     , expected=('licenses.nuget.org/', '(MIT)')),
    SpdxLidTest(test='', expected=(None, '')),
]


@pytest.mark.parametrize('test, expected', prepare_text_tests)
def test_prepare_text(test, expected):
    result = prepare_text(test)
    assert result == expected


split_spdx_lids_tests = [
    SpdxLidTest(test='SPDX  License   Identifier  : BSD-3-Clause', expected=('SPDX  License   Identifier  : ', 'BSD-3-Clause')),
    SpdxLidTest(test='SPDX-License-Identifier  : BSD-3-Clause', expected=('SPDX-License-Identifier  : ', 'BSD-3-Clause')),
    SpdxLidTest(test='spdx-license- identifier  : BSD-3-Clause', expected=('spdx-license- identifier  : ', 'BSD-3-Clause')),
    SpdxLidTest(test=' SPDX License--Identifier: BSD-3-Clause', expected=('SPDX License--Identifier: ', 'BSD-3-Clause')),
    SpdxLidTest(test='SPDX-License-Identifier : BSD-3-Clause', expected=('SPDX-License-Identifier : ', 'BSD-3-Clause')),
    SpdxLidTest(test='SPDx-Licence-Identifier : BSD-3-Clause', expected=('SPDx-Licence-Identifier : ', 'BSD-3-Clause')),
    SpdxLidTest(test='SPD-Licence-Identifier : BSD-3-Clause', expected=(None, 'SPD-Licence-Identifier : BSD-3-Clause')),
    SpdxLidTest(test='SPDx Short Identifier : BSD-3-Clause', expected=('SPDx Short Identifier : ', 'BSD-3-Clause')),
    SpdxLidTest(test='SPDx-Licence-Identifier:BSD-3-Clause', expected=('SPDx-Licence-Identifier:', 'BSD-3-Clause')),

    SpdxLidTest(test='https://licenses.nuget.org/(LGPL-2.0-only WITH FLTK-exception OR Apache-2.0)', expected=('licenses.nuget.org/', '(LGPL-2.0-only WITH FLTK-exception OR Apache-2.0)')),
    SpdxLidTest(test='* https://licenses.nuget.org/(MIT)', expected=('licenses.nuget.org/', '(MIT)')),
    SpdxLidTest(test='https://licenses.nuget.org/MIT', expected=('licenses.nuget.org/', 'MIT')),
    SpdxLidTest(test='http://licenses.nuget.org/MIT', expected=('licenses.nuget.org/', 'MIT')),
    SpdxLidTest(test='licenses.nuget.org/MIT', expected=('licenses.nuget.org/', 'MIT')),
    SpdxLidTest(test='Licenses NuGet ORG MIT', expected=('Licenses NuGet ORG ', 'MIT')),
    SpdxLidTest(test='licenses nuget org MIT', expected=('licenses nuget org ', 'MIT')),
    SpdxLidTest(test='licenses MIT', expected=(None, 'licenses MIT')),
    SpdxLidTest(test='URL:http://licenses.nuget.org/MIT', expected=('licenses.nuget.org/', 'MIT')),
]


@pytest.mark.parametrize('test, expected', split_spdx_lids_tests)
def test_split_spdx_lids(test, expected):
    result = split_spdx_lid(test)
    assert result == expected


split_spdx_lid_regex_tests = [
    SpdxLidTest(test='REM DNL SPDX  License   Identifier  : BSD-3-Clause', expected=['REM DNL ', 'SPDX  License   Identifier  : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDX-License-Identifier  : BSD-3-Clause', expected=['', 'SPDX-License-Identifier  : ', 'BSD-3-Clause']),
    SpdxLidTest(test='spdx-license- identifier  : BSD-3-Clause', expected=['', 'spdx-license- identifier  : ', 'BSD-3-Clause']),
    SpdxLidTest(test=' SPDX License--Identifier: BSD-3-Clause', expected=[' ', 'SPDX License--Identifier: ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDX-License-Identifier : BSD-3-Clause', expected=['', 'SPDX-License-Identifier : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDX-License-Identifer : BSD-3-Clause', expected=['' , 'SPDX-License-Identifer : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDX--License--Identifer : BSD-3-Clause', expected=['' , 'SPDX--License--Identifer : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDZ-License-Identifier  : BSD-3-Clause', expected=['' , 'SPDZ-License-Identifier  : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDX-Lincense-Identifier  : BSD-3-Clause', expected=['' , 'SPDX-Lincense-Identifier  : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDX-Lisense-Identifier  : BSD-3-Clause', expected=['' , 'SPDX-Lisense-Identifier  : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDX-Licence-Identifier  : BSD-3-Clause', expected=['' , 'SPDX-Licence-Identifier  : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDX-Licece-Identifier  : BSD-3-Clause', expected=['' , 'SPDX-Licece-Identifier  : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDZ-Licece-Identifer  : BSD-3-Clause', expected=['' , 'SPDZ-Licece-Identifer  : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDX-Licenses-Identifier  : BSD-3-Clause', expected=['' , 'SPDX-Licenses-Identifier  : ', 'BSD-3-Clause']),
    SpdxLidTest(test='SPDX - - Licenses - - Identifier  : BSD-3-Clause', expected=['', 'SPDX - - Licenses - - Identifier  : ', 'BSD-3-Clause']),
]


@pytest.mark.parametrize('test, expected', split_spdx_lid_regex_tests)
def test__split_spdx_lid(test, expected):
    result = _split_spdx_lid(test)
    assert result == expected


def test_get_expression_quoted():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '''LIST "SPDX-License-Identifier: GPL-2.0"'''
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'gpl-2.0'


def test_get_expression_nuget():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = 'https://licenses.nuget.org/MIT'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'mit'


def test_get_expression_multiple_or():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '* SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'bsd-new OR epl-1.0 OR apache-2.0 OR mit'


def test_get_expression_multiple_or_nuget():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = 'https://licenses.nuget.org/(LGPL-2.0-only WITH FLTK-exception OR Apache-2.0)'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'lgpl-2.0 WITH fltk-exception-lgpl-2.0 OR apache-2.0'


def test_get_expression_simple():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '*  SPDX-License-Identifier: BSD-3-Clause'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'bsd-new'


def test_get_expression_with_exception():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '/* SPDX-License-Identifier: GPL-1.0+ WITH Linux-syscall-note */'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'gpl-1.0-plus WITH linux-syscall-exception-gpl'


def test_get_expression_with_plus():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '* SPDX-License-Identifier: GPL-2.0+'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'gpl-2.0-plus'


def test_get_expression_with_extra_parens():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '* SPDX-License-Identifier: (GPL-2.0+ OR MIT)'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'gpl-2.0-plus OR mit'


def test_get_expression_with_extra_parens2():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = 'https://licenses.nuget.org/(GPL-2.0+ OR MIT)'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'gpl-2.0-plus OR mit'


def test_get_expression_extra_parens_2():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '// SPDX-License-Identifier: (GPL-2.0 OR BSD-2-Clause)'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'gpl-2.0 OR bsd-simplified'


def test_get_expression_with_parens_and_with():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '/* SPDX-License-Identifier: ((GPL-2.0 WITH Linux-syscall-note) AND MIT) */'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'gpl-2.0 WITH linux-syscall-exception-gpl AND mit'


def test_get_expression_simple_with():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '/* SPDX-License-Identifier: LGPL-2.0+ WITH Linux-syscall-note */'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'lgpl-2.0-plus WITH linux-syscall-exception-gpl'


def test_get_expression_license_ref():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '/* SPDX-License-Identifier: LicenseRef-ABC  */'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'unknown-spdx'


def test_get_expression_from_html():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = "<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>"
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'apache-2.0 WITH shl-2.1'


def test_get_expression_from_nuget_license_html():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '<a href="https://licenses.nuget.org/MIT">MIT</a>'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression.render() == 'mit'


def test_get_expression_complex():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = ('* SPDX-License-Identifier: '
                 'EPL-2.0 OR aPache-2.0 OR '
                 'GPL-2.0 WITH classpath-exception-2.0 OR '
                 'GPL-2.0')
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)

    expected = 'epl-2.0 OR apache-2.0 OR gpl-2.0 WITH classpath-exception-2.0 OR gpl-2.0'
    assert expression.render() == expected

    expected = ['epl-2.0', u'apache-2.0', u'gpl-2.0', u'classpath-exception-2.0']
    assert licensing.license_keys(expression, unique=True) == expected

    assert all(s.wrapped for s in licensing.license_symbols(expression, decompose=True))


def test_get_expression_without_lid():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = ('EPL-2.0 OR Apache-2.0 OR '
                 'GPL-2.0 WITH Classpath-exception-2.0 OR '
                 'GPL-2.0')
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)

    expected = 'epl-2.0 OR apache-2.0 OR gpl-2.0 WITH classpath-exception-2.0 OR gpl-2.0'
    assert expression.render() == expected

    expected = ['epl-2.0', u'apache-2.0', u'gpl-2.0', u'classpath-exception-2.0', u'gpl-2.0']
    assert licensing.license_keys(expression, unique=False) == expected

    assert all(s.wrapped for s in licensing.license_symbols(expression, decompose=True))


def test_get_expression_complex_with_other_spdx_symbols_and_refs():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = ('* SPDX-License-Identifier: '
                 'EPL-2.0 OR Apache-2.0 '
                 'OR GPL-2.0  WITH Classpath-exception-2.0 '
                 'OR LicenseRef-GPL-2.0 WITH Assembly-exception')

    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)

    expected = 'epl-2.0 OR apache-2.0 OR gpl-2.0 WITH classpath-exception-2.0 OR gpl-2.0 WITH openjdk-exception'
    assert expression.render() == expected

    expected = ['epl-2.0', 'apache-2.0', 'gpl-2.0', 'classpath-exception-2.0', 'gpl-2.0', 'openjdk-exception']
    assert licensing.license_keys(expression, unique=False) == expected

    assert all(s.wrapped for s in licensing.license_symbols(expression, decompose=True))


def test__parse_expression_without_and_raise_exception():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '* SPDX-License-Identifier:     GPL-2.0+ BSD-2-Clause'
    try:
        _parse_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        pytest.fail('exception should be raised')
    except:
        pass


def test_get_expression_without_and_should_not_return_unknown():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '* SPDX-License-Identifier:     GPL-2.0+ BSD-2-Clause'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression != unknown_symbol


def test__reparse_invalid_expression_without_or_should_return_a_proper_expression():
    # this is a uboot-style legacy expression without OR
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = 'GPL-2.0+ BSD-2-Clause'
    expression = _reparse_invalid_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    expected = 'gpl-2.0-plus OR bsd-simplified'
    assert expression.render() == expected


def test__reparse_invalid_expression_with_improper_keyword_should_return_a_proper_expression():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = 'or GPL-2.0+ BSD-2-Clause '
    expression = _reparse_invalid_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    expected = '(gpl-2.0-plus AND bsd-simplified) AND unknown-spdx'
    assert expression.render() == expected


def test__reparse_invalid_expression_with_non_balanced_parens_should_return_a_proper_expression():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '(GPL-2.0+ and (BSD-2-Clause '
    expression = _reparse_invalid_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    expected = '(gpl-2.0-plus AND bsd-simplified) AND unknown-spdx'
    assert expression.render() == expected


def test__parse_expression_with_empty_expression_should_raise_ExpressionError():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '* SPDX-License-Identifier:'
    try:
        _parse_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        pytest.fail('ExpressionError not raised')
    except ExpressionError:
        pass


def test_get_expression_with_empty_expression_should_return_unknown():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = '* SPDX-License-Identifier:'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression == None


def test_get_expression_with_empty_expression_should_return_unknown_nuget():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = 'https://licenses.nuget.org/'
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression == None


def test__parse_expression_with_empty_expression2_should_return_None():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = ''
    expression = _parse_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression is None


def test_get_expression_with_empty_expression2_should_return_unknown():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = ''
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression == None


def test_all_spdx_tokens_exists_in_dictionary():
    idx = cache.get_index()
    dic = idx.dictionary
    licenses = cache.get_licenses_db()
    tokens = set(models.get_all_spdx_key_tokens(licenses))
    keys = set(idx.dictionary)
    try:
        assert tokens.issubset(keys)
    except:
        for token in tokens:
            dic[token]


@pytest.mark.parametrize(
    'test, expected',
    [
        ('eCos-2.0', 'gpl-2.0-plus WITH ecos-exception-2.0'),
        ('GPL-2.0-with-autoconf-exception', 'gpl-2.0 WITH autoconf-exception-2.0'),
        ('GPL-2.0-with-bison-exception', 'gpl-2.0 WITH bison-exception-2.2'),
        ('GPL-2.0-with-classpath-exception', 'gpl-2.0 WITH classpath-exception-2.0'),
        ('GPL-2.0-with-font-exception', 'gpl-2.0 WITH font-exception-gpl'),
        ('GPL-2.0-with-GCC-exception', 'gpl-2.0 WITH gcc-linking-exception-2.0'),
        ('GPL-3.0-with-autoconf-exception', 'gpl-3.0 WITH autoconf-exception-3.0'),
        ('GPL-3.0-with-GCC-exception', 'gpl-3.0 WITH gcc-exception-3.1'),
        ('wxWindows', 'lgpl-2.0-plus WITH wxwindows-exception-3.1'),
    ]
)
def test_get_expression_works_for_legacy_deprecated_old_spdx_symbols(test, expected):
    licensing = Licensing()
    symbols_by_spdx = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    result = get_expression(
        text=test,
        licensing=licensing,
        expression_symbols=symbols_by_spdx,
        unknown_symbol=unknown_symbol,
    )
    assert result.render() == expected


def test_get_expression_does_not_fail_on_empty():
    licensing = Licensing()
    spdx_symbols = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    line_text = 'SPDX-License-Identifier: '
    expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    assert expression == None


def test_Index_match_does_not_fail_on_empty():
    idx = cache.get_index()
    matches = list(idx.match(query_string='SPDX-License-Identifier: '))
    assert not matches


class TestMatchSpdx(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_spdx_match_contains_spdx_prefix(self):
        from licensedcode import index
        from licensedcode import tracing
        rules_dir = self.get_test_loc('spdx/rules-overlap/rules')
        lics_dir = self.get_test_loc('spdx/rules-overlap/licenses')
        rules = models.get_rules(licenses_data_dir=lics_dir, rules_data_dir=rules_dir)
        idx = index.LicenseIndex(rules)
        querys = 'SPDX-license-identifier: BSD-3-Clause-No-Nuclear-Warranty'
        matches = idx.match(query_string=querys)
        assert len(matches) == 1
        match = matches[0]
        qtext, itext = tracing.get_texts(match)
        expected_qtext = 'SPDX-license-identifier: BSD-3-Clause-No-Nuclear-Warranty'
        assert qtext == expected_qtext
        expected_itext = 'spdx license identifier bsd 3 clause no nuclear warranty'
        assert itext == expected_itext

