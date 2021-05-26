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

from license_expression import Licensing
from license_expression import ExpressionError

from commoncode.testcase import FileBasedTesting
from commoncode import text

from licensedcode import cache
from licensedcode.cache import get_spdx_symbols
from licensedcode.cache import get_unknown_spdx_symbol
from licensedcode.match_spdx_lid import _parse_expression
from licensedcode.match_spdx_lid import _reparse_invalid_expression
from licensedcode.match_spdx_lid import clean_text
from licensedcode.match_spdx_lid import get_expression
from licensedcode.match_spdx_lid import prepare_text
from licensedcode.match_spdx_lid import split_spdx_lid
from licensedcode.match_spdx_lid import _split_spdx_lid
from licensedcode import models
from licensedcode.query import Query


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


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
            '''

        qry = Query(query_string=querys, idx=idx)
        expected = [
            ('SPDX-License-Identifier:  (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)',  0,  15),
            ('SPDX-License-Identifier:  EPL-2.0 OR Apache-2.0 OR GPL-2.0 WITH Classpath-exception-2.0',16,  34),
            ('SPDX-License-Identifier:      GPL-2.0+ BSD-2-Clause', 45, 53)]

        assert qry.spdx_lines == expected


def get_query_spdx_lines_test_method(test_loc , expected_loc, regen=False):
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
            wmode = 'w'
            with open(expected_loc, wmode) as ef:
                json.dump(results, ef, indent=2)
            expected = results
        else:
            with open(expected_loc, 'rb') as ef:
                expected = json.load(ef, encoding='utf-8')

        assert results == expected

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
        test_method = get_query_spdx_lines_test_method(test_loc, expected_loc, regen)
        test_method.__name__ = test_name
        # attach that method to our test class
        setattr(clazz, test_name, test_method)


class TestSpdxQueryLinesDataDriven(unittest.TestCase):
    pass


build_spdx_line_tests(clazz=TestSpdxQueryLinesDataDriven, regen=False)


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
            '(/ SPDX-License-Identifier: (GPL-2.0 OR BSD-3-Clause)',
            'SPDX-License-Identifier: LGPL-2.1+',
            'SPDX-License-Identifier: GPL-2.0+',
            'SPDX-License-Identifier: GPL-2.0+ BSD-2-Clause',
            'SPDX License Identifier LGPL-2.1+'
        ]
        results = [clean_text(test) for test in tests]
        assert results == expected

    def test_prepare_text(self):
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
            '(/ SPDX-Licence--Identifier: (GPL-2.0 OR BSD-3-Clause)',
            '// SPDX-License-Identifier: LGPL-2.1+',
            '+SPDX-License-Identifier:    GPL-2.0+',
            '* SPDX-License-Identifier:     GPL-2.0+        BSD-2-Clause',
            '// SPDX Licence Identifier LGPL-2.1+',
        ]

        expected = [
            ('SPDX-License-Identifier:', '(BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)'),
            ('SPDX-License-Identifier:', 'BSD-3-Clause'),
            ('SPDX-License-Identifier:', 'BSD-3-Clause'),
            ('SPDX-License-Identifier:', 'BSD-3-Clause'),
            ('SPDX-License-Identifier:', 'GPL-1.0+ WITH Linux-syscall-note'),
            ('SPDX-License-Identifier:', 'GPL-2.0+'),
            ('SPDX-License-Identifier:', 'GPL-2.0'),
            ('SPDX-License-Identifier:', 'GPL-2.0'),
            ('SPDX-License-Identifier:', 'GPL-2.0'),
            ('SPDX-License-Identifier:', 'GPL-2.0'),
            ('SPDX-License-Identifier:', 'GPL-2.0+'),
            ('SPDX-License-Identifier:', 'GPL-2.0+'),
            ('SPDX-License-Identifier:', '(GPL-2.0+ OR BSD-3-Clause )'),
            ('SPDX-Licence--Identifier:', '(GPL-2.0 OR BSD-3-Clause)'),
            ('SPDX-License-Identifier:', 'LGPL-2.1+'),
            ('SPDX-License-Identifier:', 'GPL-2.0+'),
            ('SPDX-License-Identifier:', 'GPL-2.0+ BSD-2-Clause'),
            ('SPDX Licence Identifier', 'LGPL-2.1+')
        ]
        results = [prepare_text(test) for test in tests]
        assert results == expected

    def test_prepare_text_with_rem(self):
        assert prepare_text('') == (None, '')
        assert prepare_text('@REM # SPDX-License-Identifier: BSD-2-Clause-Patent') == ('SPDX-License-Identifier:', 'BSD-2-Clause-Patent')

    def test_split_spdx_lid(self):
        test = [
            'SPDX  License   Identifier  : BSD-3-Clause',
            'SPDX-License-Identifier  : BSD-3-Clause',
            'spdx-license- identifier  : BSD-3-Clause',
            ' SPDX License--Identifier: BSD-3-Clause',
            'SPDX-License-Identifier : BSD-3-Clause',
            'SPDx-Licence-Identifier : BSD-3-Clause',
            'SPD-Licence-Identifier : BSD-3-Clause',
        ]
        results = [split_spdx_lid(l) for l in test]
        expected = [
            ('SPDX  License   Identifier  : ', 'BSD-3-Clause'),
            ('SPDX-License-Identifier  : ', 'BSD-3-Clause'),
            ('spdx-license- identifier  : ', 'BSD-3-Clause'),
            ('SPDX License--Identifier: ', 'BSD-3-Clause'),
            ('SPDX-License-Identifier : ', 'BSD-3-Clause'),
            ('SPDx-Licence-Identifier : ', 'BSD-3-Clause'),
            (None, 'SPD-Licence-Identifier : BSD-3-Clause'),
        ]
        assert results == expected

    def test__split_spdx_lid(self):
        test = [
            'REM DNL SPDX  License   Identifier  : BSD-3-Clause',
            'SPDX-License-Identifier  : BSD-3-Clause',
            'spdx-license- identifier  : BSD-3-Clause',
            ' SPDX License--Identifier: BSD-3-Clause',
            ' SPDX Licence--Identifier: BSD-3-Clause',
            'SPDX-License-Identifier : BSD-3-Clause',
            'SPDX-License-Identifer : BSD-3-Clause',
        ]
        results = [_split_spdx_lid(l) for l in test]
        expected = [
            ['REM DNL ', 'SPDX  License   Identifier  : ', 'BSD-3-Clause'],
            ['', 'SPDX-License-Identifier  : ', 'BSD-3-Clause'],
            ['', 'spdx-license- identifier  : ', 'BSD-3-Clause'],
            [' ', 'SPDX License--Identifier: ', 'BSD-3-Clause'],
            [' ', 'SPDX Licence--Identifier: ', 'BSD-3-Clause'],
            ['', 'SPDX-License-Identifier : ', 'BSD-3-Clause'],
            ['SPDX-License-Identifer : BSD-3-Clause'],
        ]
        assert results == expected

    def test_get_expression_quoted(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '''LIST "SPDX-License-Identifier: GPL-2.0"'''
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression.render() == 'gpl-2.0'

    def test_get_expression_multiple_or(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '* SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression.render() == 'bsd-new OR epl-1.0 OR apache-2.0 OR mit'

    def test_get_expression_simple(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '*  SPDX-License-Identifier: BSD-3-Clause'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression.render() == 'bsd-new'

    def test_get_expression_with_exception(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '/* SPDX-License-Identifier: GPL-1.0+ WITH Linux-syscall-note */'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression.render() == 'gpl-1.0-plus WITH linux-syscall-exception-gpl'

    def test_get_expression_with_plus(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '* SPDX-License-Identifier: GPL-2.0+'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression.render() == 'gpl-2.0-plus'

    def test_get_expression_with_extra_parens(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '* SPDX-License-Identifier: (GPL-2.0+ OR MIT)'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression.render() == 'gpl-2.0-plus OR mit'

    def test_get_expression_extra_parens_2(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '// SPDX-License-Identifier: (GPL-2.0 OR BSD-2-Clause)'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression.render() == 'gpl-2.0 OR bsd-simplified'

    def test_get_expression_with_parens_and_with(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '/* SPDX-License-Identifier: ((GPL-2.0 WITH Linux-syscall-note) AND MIT) */'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression.render() == 'gpl-2.0 WITH linux-syscall-exception-gpl AND mit'

    def test_get_expression_simple_with(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '/* SPDX-License-Identifier: LGPL-2.0+ WITH Linux-syscall-note */'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression.render() == 'lgpl-2.0-plus WITH linux-syscall-exception-gpl'

    def test_get_expression_license_ref(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '/* SPDX-License-Identifier: LicenseRef-ABC  */'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression.render() == 'unknown-spdx'

    def test_get_expression_complex(self):
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

    def test_get_expression_without_lid(self):
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

    def test_get_expression_complex_with_unknown_symbols_and_refs(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = ('* SPDX-License-Identifier: '
                     'EPL-2.0 OR Apache-2.0 '
                     'OR GPL-2.0  WITH Classpath-exception-2.0 '
                     'OR LicenseRef-GPL-2.0 WITH Assembly-exception')

        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)

        expected = 'epl-2.0 OR apache-2.0 OR gpl-2.0 WITH classpath-exception-2.0 OR unknown-spdx WITH unknown-spdx'
        assert expression.render() == expected

        expected = ['epl-2.0', 'apache-2.0', 'gpl-2.0', 'classpath-exception-2.0', 'unknown-spdx', 'unknown-spdx']
        assert licensing.license_keys(expression, unique=False) == expected

        assert all(s.wrapped for s in licensing.license_symbols(expression, decompose=True))

    def test__parse_expression_without_and_raise_exception(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '* SPDX-License-Identifier:     GPL-2.0+ BSD-2-Clause'
        try:
            _parse_expression(line_text, licensing, spdx_symbols, unknown_symbol)
            self.fail('exception should be raised')
        except:
            pass

    def test_get_expression_without_and_should_not_return_unknown(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '* SPDX-License-Identifier:     GPL-2.0+ BSD-2-Clause'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression != unknown_symbol

    def test__reparse_invalid_expression_without_or_should_return_a_proper_expression(self):
        # this is a uboot-style legacy expression without OR
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = 'GPL-2.0+ BSD-2-Clause'
        expression = _reparse_invalid_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        expected = 'gpl-2.0-plus OR bsd-simplified'
        assert expression.render() == expected

    def test__reparse_invalid_expression_with_improper_keyword_should_return_a_proper_expression(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = 'or GPL-2.0+ BSD-2-Clause '
        expression = _reparse_invalid_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        expected = '(gpl-2.0-plus AND bsd-simplified) AND unknown-spdx'
        assert expression.render() == expected

    def test__reparse_invalid_expression_with_non_balanced_parens_should_return_a_proper_expression(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '(GPL-2.0+ and (BSD-2-Clause '
        expression = _reparse_invalid_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        expected = '(gpl-2.0-plus AND bsd-simplified) AND unknown-spdx'
        assert expression.render() == expected

    def test__parse_expression_with_empty_expression_should_raise_ExpressionError(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '* SPDX-License-Identifier:'
        try:
            _parse_expression(line_text, licensing, spdx_symbols, unknown_symbol)
            self.fail('ExpressionError not raised')
        except ExpressionError:
            pass

    def test_get_expression_with_empty_expression_should_return_unknown(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = '* SPDX-License-Identifier:'
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression == None

    def test__parse_expression_with_empty_expression2_should_return_None(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = ''
        expression = _parse_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression is None

    def test_get_expression_with_empty_expression2_should_return_unknown(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = ''
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression == None

    def test_all_spdx_tokens_exists_in_dictionary(self):
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

    def test_get_expression_works_for_legacy_deprecated_old_spdx_symbols(self):
        exp_by_old = {
            'eCos-2.0': 'gpl-2.0-plus WITH ecos-exception-2.0',
            'GPL-2.0-with-autoconf-exception': 'gpl-2.0 WITH autoconf-exception-2.0',
            'GPL-2.0-with-bison-exception': 'gpl-2.0 WITH bison-exception-2.2',
            'GPL-2.0-with-classpath-exception': 'gpl-2.0 WITH classpath-exception-2.0',
            'GPL-2.0-with-font-exception': 'gpl-2.0 WITH font-exception-gpl',
            'GPL-2.0-with-GCC-exception': 'gpl-2.0 WITH gcc-linking-exception-2.0',
            'GPL-3.0-with-autoconf-exception': 'gpl-3.0 WITH autoconf-exception-3.0',
            'GPL-3.0-with-GCC-exception': 'gpl-3.0 WITH gcc-exception-3.1',
            'wxWindows': 'lgpl-2.0-plus WITH wxwindows-exception-3.1',
        }
        licensing = Licensing()
        symbols_by_spdx = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()

        for test, expected in exp_by_old.items():
            result = get_expression(
                test, licensing, symbols_by_spdx, unknown_symbol).render()
            assert result == expected

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

    def test_get_expression_does_not_fail_on_empty(self):
        licensing = Licensing()
        spdx_symbols = get_spdx_symbols()
        unknown_symbol = get_unknown_spdx_symbol()
        line_text = 'SPDX-License-Identifier: '
        expression = get_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        assert expression == None

    def test_Index_match_does_not_fail_on_empty(self):
        idx = cache.get_index()
        matches = list(idx.match(query_string='SPDX-License-Identifier: '))
        assert not matches

