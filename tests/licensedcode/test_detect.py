#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest

from commoncode.testcase import FileBasedTesting
from licensedcode import cache
from licensedcode import index
from licensedcode import match_aho
from licensedcode import match_seq
from licensedcode.legalese import build_dictionary_from_iterable
from licensedcode.match import LicenseMatch
from licensedcode.models import load_rules
from licensedcode.spans import Span
from licensedcode.tracing import get_texts
from licensedcode_test_utils import mini_legalese
from licensedcode_test_utils import create_rule_from_text_and_expression
from licensedcode_test_utils import create_rule_from_text_file_and_expression

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

"""
Test the core license detection mechanics.
"""


def MiniLicenseIndex(*args, **kwargs):
    return index.LicenseIndex(*args, _legalese=mini_legalese, **kwargs)


class TestIndexMatch(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_does_not_return_matches_for_empty_query(self):
        idx = MiniLicenseIndex([create_rule_from_text_and_expression(text='A one. A two. license A three.')])

        matches = idx.match(query_string='')
        assert matches == []
        matches = idx.match(query_string=None)
        assert matches == []

    def test_match_does_not_return_matches_for_junk_queries(self):
        idx = MiniLicenseIndex([create_rule_from_text_and_expression(text='A one. a license two. license A three.')])

        assert idx.match(query_string=u'some other junk') == []
        assert idx.match(query_string=u'some junk') == []

    def test_match_return_one_match_with_correct_offsets(self):
        idx = MiniLicenseIndex([
            create_rule_from_text_and_expression(text='A one. a license two. A three.',
                 license_expression='abc')]
        )

        querys = u'some junk. A one. A license two. A three.'
        #          0    1     2 3    4 5       6    7 8

        matches = idx.match(query_string=querys)
        assert len(matches) == 1
        match = matches[0]
        qtext, itext = get_texts(match)
        assert qtext == 'one. A license two. A three.'
        assert itext == 'one license two three'

        assert match.qspan == Span(0, 3)
        assert match.ispan == Span(0, 3)

    def test_match_can_match_exactly_rule_text_used_as_query(self):
        test_file = self.get_test_loc('detect/mit/mit.c')
        rule = create_rule_from_text_file_and_expression(text_file=test_file, license_expression='mit')
        idx = MiniLicenseIndex([rule])

        matches = idx.match(test_file)
        assert len(matches) == 1
        match = matches[0]
        assert match.rule == rule
        assert match.qspan == Span(0, 85)
        assert match.ispan == Span(0, 85)
        assert match.coverage() == 100
        assert match.score() == 100

    def test_match_matches_correctly_simple_exact_query_1(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = create_rule_from_text_file_and_expression(text_file=tf1, license_expression='mit')
        idx = MiniLicenseIndex([ftr])

        query_doc = self.get_test_loc('detect/mit/mit2.c')
        matches = idx.match(query_doc)
        assert len(matches) == 1
        match = matches[0]
        assert match.rule == ftr
        assert match.qspan == Span(0, 85)
        assert match.ispan == Span(0, 85)

    def test_match_matches_correctly_simple_exact_query_across_query_runs(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = create_rule_from_text_file_and_expression(text_file=tf1, license_expression='mit')
        idx = MiniLicenseIndex([ftr])
        query_doc = self.get_test_loc('detect/mit/mit3.c')
        matches = idx.match(query_doc)
        assert len(matches) == 1
        match = matches[0]

        qtext, itext = get_texts(match)
        expected_qtext = '''
Permission is hereby granted, free of charge, to any person obtaining a copy
// of this
software and associated documentation files (the "Software"), to deal
// in
#,.,
                                  ///
THE SOFTWARE WITHOUT RESTRICTION, INCLUDING WITHOUT LIMITATION THE RIGHTS
// TO USE, COPY, MODIFY, MERGE, PUBLISH, DISTRIBUTE, SUBLICENSE, AND/OR SELL
// COPIES #,.,
                                  ///
of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
#,.,
                                  ///
// The above copyright notice and this permission notice shall be included in
#,.,
                                  ///
// all copies or substantial portions#,.,
                                  ///
 of the Software.
'''

        assert ' '.join(qtext.split()) == ' '.join(expected_qtext.split())

        expected_itext = u'''
            Permission is hereby granted free of charge to any person obtaining
            copy of this software and associated documentation files the Software to
            deal in the Software without restriction including without limitation
            the rights to use copy modify merge publish distribute sublicense and or
            sell copies of the Software and to permit persons to whom the Software
            is furnished to do so subject to the following conditions The above
            copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software
        '''.lower()
        assert ' '.join(itext.split()) == ' '.join(expected_itext.split())

    def test_match_with_surrounding_junk_should_return_an_exact_match(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = create_rule_from_text_file_and_expression(text_file=tf1, license_expression='mit')
        idx = MiniLicenseIndex([ftr])

        query_loc = self.get_test_loc('detect/mit/mit4.c')
        matches = idx.match(query_loc)
        assert len(matches) == 1
        match = matches[0]
        qtext, itext = get_texts(match)
        expected_qtext = u'''
        Permission "[add] [text]" is hereby granted, free of charge, to any person obtaining a copy
        // of this software and associated documentation files (the "Software"), to deal
        // in the Software without restriction, including without limitation the rights
        // to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        // copies of the Software, and to permit persons to whom the Software is
        // furnished to do so, subject to the following conditions:

        // The above copyright  "[add] [text]"  notice and this permission notice shall be included in
        // all copies or substantial portions of the Software.
        '''.split()
        assert qtext.split() == expected_qtext

        expected_itext = u'''
            permission is hereby granted free of charge to any person obtaining
            copy of this software and associated documentation files the software to
            deal in the software without restriction including without limitation the
            rights to use copy modify merge publish distribute sublicense and or sell
            copies of the software and to permit persons to whom the software is
            furnished to do so subject to the following conditions the above
            copyright notice and this permission notice shall be included in all
            copies or substantial portions of the software
        '''.lower().split()
        assert itext.split() == expected_itext

        assert match.qspan == Span(0, 85)
        assert match.ispan == Span(0, 85)
        assert match.score() == 95.56

    def test_match_to_single_word_does_not_have_zero_score(self):
        idx = MiniLicenseIndex(
            [create_rule_from_text_and_expression(text='LGPL', license_expression='lgpl-2.0')]
        )
        matches = idx.match(query_string='LGPL')
        assert len(matches) == 1
        assert matches[0].score() == 5.0

    def test_match_to_threshold_words_has_hundred_score(self):
        threshold = 18
        idx = MiniLicenseIndex(
            [create_rule_from_text_and_expression(text=' LGPL ' * threshold, license_expression='lgpl-2.0')]
        )
        matches = idx.match(query_string=' LGPL ' * threshold)
        assert len(matches) == 1
        assert matches[0].score() == 100.0

    def test_match_can_match_approximately(self):
        rule_file = self.get_test_loc('approx/mit/mit.c')
        rule = create_rule_from_text_file_and_expression(text_file=rule_file, license_expression='mit')
        idx = MiniLicenseIndex([rule])

        query_doc = self.get_test_loc('approx/mit/mit4.c')
        matches = idx.match(query_doc)
        assert len(matches) == 2
        m1 = matches[0]
        m2 = matches[1]
        assert m1.rule == rule
        assert m2.rule == rule
        assert m1.coverage() == 100
        assert m2.coverage() == 100
        assert m1.score() == 95.56
        assert m2.score() == 93.48

    def test_match_return_correct_positions_with_short_index_and_queries(self):
        idx = MiniLicenseIndex(
            [create_rule_from_text_and_expression(text='MIT License', license_expression='mit')]
        )

        matches = idx.match(query_string='MIT License')
        assert len(matches) == 1

        qtext, itext = get_texts(matches[0])
        assert qtext == 'MIT License'
        assert itext == 'mit license'
        assert matches[0].qspan == Span(0, 1)
        assert matches[0].ispan == Span(0, 1)

        matches = idx.match(query_string='MIT MIT License')
        assert len(matches) == 1

        qtext, itext = get_texts(matches[0])
        assert qtext == 'MIT License'
        assert itext == 'mit license'
        assert Span(1, 2) == matches[0].qspan
        assert Span(0, 1) == matches[0].ispan

        query_doc1 = 'do you think I am a mit license MIT License, yes, I think so'
        # #                                  0       1   2       3
        matches = idx.match(query_string=query_doc1)
        assert len(matches) == 2

        qtext, itext = get_texts(matches[0])
        assert qtext == 'mit license'
        assert itext == 'mit license'
        assert matches[0].qspan == Span(0, 1)
        assert matches[0].ispan == Span(0, 1)

        qtext, itext = get_texts(matches[1])
        assert qtext == 'MIT License,'
        assert itext == 'mit license'
        assert matches[1].qspan == Span(2, 3)
        assert matches[1].ispan == Span(0, 1)

        query_doc2 = '''do you think I am a mit license
                        MIT License
                        yes, I think so'''
        matches = idx.match(query_string=query_doc2)
        assert len(matches) == 2

        qtext, itext = get_texts(matches[0])
        assert qtext == 'mit license'
        assert itext == 'mit license'
        assert matches[0].qspan == Span(0, 1)
        assert matches[0].ispan == Span(0, 1)

        qtext, itext = get_texts(matches[1])
        assert qtext == 'MIT License'
        assert itext == 'mit license'
        assert matches[1].qspan == Span(2, 3)
        assert matches[1].ispan == Span(0, 1)

    def test_match_simple_rule(self):
        tf1 = self.get_test_loc('detect/mit/t1.txt')
        ftr = create_rule_from_text_file_and_expression(text_file=tf1, license_expression='bsd-original')
        idx = MiniLicenseIndex([ftr])

        query_doc = self.get_test_loc('detect/mit/t2.txt')
        matches = idx.match(query_doc)
        assert len(matches) == 1
        match = matches[0]
        assert match.qspan == Span(0, 240)
        assert match.ispan == Span(0, 240)
        assert match.lines() == (1, 27,)
        assert match.coverage() == 100
        assert match.score() == 100

    def test_match_works_with_special_characters_1(self):
        test_file = self.get_test_loc('detect/specialcharacter/kerberos.txt')
        idx = MiniLicenseIndex([create_rule_from_text_file_and_expression(text_file=test_file, license_expression='kerberos')])
        assert len(idx.match(test_file)) == 1

    def test_match_works_with_special_characters_2(self):
        test_file = self.get_test_loc('detect/specialcharacter/kerberos1.txt')
        idx = MiniLicenseIndex([create_rule_from_text_file_and_expression(text_file=test_file, license_expression='kerberos')])
        assert len(idx.match(test_file)) == 1

    def test_match_works_with_special_characters_3(self):
        test_file = self.get_test_loc('detect/specialcharacter/kerberos2.txt')
        idx = MiniLicenseIndex(
            [create_rule_from_text_file_and_expression(text_file=test_file, license_expression='kerberos')]
        )
        assert len(idx.match(test_file)) == 1

    def test_match_works_with_special_characters_4(self):
        test_file = self.get_test_loc('detect/specialcharacter/kerberos3.txt')
        idx = MiniLicenseIndex([create_rule_from_text_file_and_expression(text_file=test_file, license_expression='kerberos')])
        assert len(idx.match(test_file)) == 1

    def test_overlap_detection1(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+
        #
        #   * License texts to detect:
        #   +- license 3 -----------+
        #   | +-license 2 --------+ |
        #   | |  +-license 1 --+  | |
        #   | +-------------------+ |
        #   +-----------------------+
        #
        #   +-license 4 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        license1 = '''Redistribution and use permitted.'''

        license2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        license3 = '''
        this license source
        Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.
        has a permitted license'''

        license4 = '''My Redistributions is permitted.
        Redistribution and use permitted.
        Use is permitted too.'''

        rule1 = create_rule_from_text_and_expression(text=license1, license_expression='overlap')
        rule2 = create_rule_from_text_and_expression(text=license2, license_expression='overlap')
        rule3 = create_rule_from_text_and_expression(text=license3, license_expression='overlap')
        rule4 = create_rule_from_text_and_expression(text=license4, license_expression='overlap')
        idx = MiniLicenseIndex([rule1, rule2, rule3, rule4])

        querys = 'Redistribution and use bla permitted.'
        # test : license1 is in the index and contains no other rule. should return rule1 at exact coverage.
        matches = idx.match(query_string=querys)
        assert len(matches) == 1
        match = matches[0]
        assert match.qspan == Span(0, 3)
        assert match.rule == rule1
        qtext, _itext = get_texts(match)
        assert qtext == 'Redistribution and use [bla] permitted.'

    def test_overlap_detection2(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        license1 = '''Redistribution and use permitted.'''

        license2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        rule1 = create_rule_from_text_and_expression(text=license1, license_expression='overlap')
        rule2 = create_rule_from_text_and_expression(text=license2, license_expression='overlap')
        idx = MiniLicenseIndex([rule1, rule2])

        # test : license2 contains license1: return license2 as exact coverage

        querys = 'Redistribution and use bla permitted.'
        matches = idx.match(query_string=querys)
        assert len(matches) == 1
        match = matches[0]
        assert match.rule == rule1
        qtext, _itext = get_texts(match)
        assert qtext == 'Redistribution and use [bla] permitted.'

    def test_overlap_detection2_exact(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        license1 = '''Redistribution and use permitted.'''

        license2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        rule1 = create_rule_from_text_and_expression(text=license1, license_expression='overlap')
        rule2 = create_rule_from_text_and_expression(text=license2, license_expression='overlap')
        idx = MiniLicenseIndex([rule1, rule2])

        # test : license2 contains license1: return license2 as exact coverage

        querys = 'Redistribution and use bla permitted.'
        matches = idx.match(query_string=querys)
        assert len(matches) == 1
        match = matches[0]
        assert match.rule == rule1
        qtext, _itext = get_texts(match)
        assert qtext == 'Redistribution and use [bla] permitted.'

    def test_overlap_detection3(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+
        #
        #   * License texts to detect:
        #   +- license 3 -----------+
        #   | +-license 2 --------+ |
        #   | |  +-license 1 --+  | |
        #   | +-------------------+ |
        #   +-----------------------+
        #
        # setup index
        license1 = '''Redistribution and use permitted.'''

        license2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        rule1 = create_rule_from_text_and_expression(text=license1, license_expression='overlap')
        rule2 = create_rule_from_text_and_expression(text=license2, license_expression='overlap')
        idx = MiniLicenseIndex([rule1, rule2])

        querys = '''My source.
            Redistributions of source must retain copyright.
            Redistribution and use permitted.
            Redistributions in binary form is permitted.
            My code.'''

        # test : querys contains license2 that contains license1: return license2 as exact coverage
        matches = idx.match(query_string=querys)
        assert len(matches) == 1
        match = matches[0]
        assert match.rule == rule2
        qtext, _itext = get_texts(match)
        expected = '''
            Redistributions of source must retain copyright.
            Redistribution and use permitted.
            Redistributions in binary form is permitted.'''.split()
        assert qtext.split() == expected

    def test_overlap_detection4(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+
        #
        #   +-license 4 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        license1 = '''Redistribution and use permitted.'''

        license2 = '''Redistributions of source must retain copyright.
            Redistribution and use permitted.
            Redistributions in binary form is permitted.'''

        rule1 = create_rule_from_text_and_expression(text=license1, license_expression='overlap')
        rule2 = create_rule_from_text_and_expression(text=license2, license_expression='overlap')
        idx = MiniLicenseIndex([rule1, rule2])

        querys = '''My source.
        Redistribution and use permitted.
        My code.'''

        # test : querys contains license1: return license1 as exact coverage
        matches = idx.match(query_string=querys)
        assert len(matches) == 1
        match = matches[0]
        assert match.rule == rule1
        qtext, _itext = get_texts(match)
        assert qtext == 'Redistribution and use permitted.'

    def test_overlap_detection5(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+
        #
        #   +-license 4 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        license1 = '''Redistribution and use permitted for MIT license.'''

        license2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted for MIT license.
        Redistributions in binary form is permitted.'''

        rule1 = create_rule_from_text_and_expression(text=license1, license_expression='overlap')
        rule2 = create_rule_from_text_and_expression(text=license2, license_expression='overlap')
        idx = MiniLicenseIndex([rule1, rule2])

        querys = '''My source.
        Redistribution and use permitted for MIT license.
        My code.'''

        # test : querys contains license1: return license1 as exact coverage
        matches = idx.match(query_string=querys)
        assert len(matches) == 1

        match = matches[0]
        assert match.rule == rule1
        qtext, _itext = get_texts(match)
        assert qtext == 'Redistribution and use permitted for MIT license.'

    def test_fulltext_detection_works_with_partial_overlap_from_location(self):
        test_doc = self.get_test_loc('detect/templates/license3.txt')
        idx = MiniLicenseIndex([create_rule_from_text_file_and_expression(text_file=test_doc, license_expression='mylicense')])

        query_loc = self.get_test_loc('detect/templates/license4.txt')
        matches = idx.match(query_loc)

        assert len(matches) == 1
        match = matches[0]
        assert match.qspan == Span(0, 41)
        assert match.ispan == Span(0, 41)
        assert match.coverage() == 100
        assert match.score() == 100
        qtext, _itext = get_texts(match)
        expected = '''
            is free software; you can redistribute it and/or # modify it under
            the terms of the GNU Lesser General Public # License as published by
            the Free Software Foundation; either # version 2.1 of the License,
            or (at your option) any later version.'''
        assert ' '.join(qtext.split()) == ' '.join(expected.split())


class TestIndexPartialMatch(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_can_match_with_plain_rule_simple(self):
        tf1_text = u'''X11 License
        Copyright (C) 1996 X Consortium
        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions: The above copyright
        notice and this permission notice shall be included in all copies or
        substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
        WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
        TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
        NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY CLAIM,
        DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
        OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
        OR OTHER DEALINGS IN THE SOFTWARE. Except as contained in this notice, the
        name of the X Consortium shall not be used in advertising or otherwise to
        promote the sale, use or other dealings in this Software without prior
        written authorization from the X Consortium. X Window System is a trademark
        of X Consortium, Inc.
        '''
        rule = create_rule_from_text_and_expression(text=tf1_text, license_expression='x-consortium')
        idx = MiniLicenseIndex([rule])

        query_loc = self.get_test_loc('detect/simple_detection/x11-xconsortium_text.txt')
        matches = idx.match(query_loc)
        assert len(matches) == 1

        match = matches[0]
        assert match.qspan == Span(0, 213)

    def test_match_can_match_with_plain_rule_simple2(self):
        rule_text = u'''X11 License
        Copyright (C) 1996 X Consortium
        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions: The above copyright
        notice and this permission notice shall be included in all copies or
        substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
        WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
        TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
        NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY CLAIM,
        DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
        OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
        OR OTHER DEALINGS IN THE SOFTWARE. Except as contained in this notice, the
        name of the X Consortium shall not be used in advertising or otherwise to
        promote the sale, use or other dealings in this Software without prior
        written authorization from the X Consortium. X Window System is a trademark
        of X Consortium, Inc.
        '''
        rule = create_rule_from_text_and_expression(text=rule_text, license_expression='x-consortium')
        idx = MiniLicenseIndex([rule])

        query_loc = self.get_test_loc('detect/simple_detection/x11-xconsortium_text.txt')
        matches = idx.match(location=query_loc)
        assert len(matches) == 1

        expected_qtext = u'''
        X11 License
        Copyright (C) 1996 X Consortium
        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions: The above copyright
        notice and this permission notice shall be included in all copies or
        substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
        WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
        TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
        NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY CLAIM,
        DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
        OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
        OR OTHER DEALINGS IN THE SOFTWARE. Except as contained in this notice, the
        name of the X Consortium shall not be used in advertising or otherwise to
        promote the sale, use or other dealings in this Software without prior
        written authorization from the X Consortium. X Window System is a trademark
        of X Consortium, Inc.
        '''.split()
        match = matches[0]
        qtext, _itext = get_texts(match)
        assert qtext.split() == expected_qtext

    def test_match_can_match_with_simple_rule_template2(self):
        rule_text = u'''
        IN NO EVENT SHALL THE
        BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
        CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
        SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
        '''
        rule = create_rule_from_text_and_expression(text=rule_text, license_expression='x-consortium')
        idx = MiniLicenseIndex([rule])

        query_string = u'''
        IN NO EVENT SHALL THE Y CORP
        BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
        CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
        SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
        '''

        matches = idx.match(query_string=query_string)
        assert len(matches) == 1
        match = matches[0]
        qtext, itext = get_texts(match)

        expected_qtokens = u'''
        IN NO EVENT SHALL THE [Y] [CORP] BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
        OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
        '''.split()
        assert qtext.split() == expected_qtokens

        expected_itokens = u'''
        IN NO EVENT SHALL THE BE LIABLE FOR ANY CLAIM DAMAGES OR OTHER LIABILITY
        WHETHER IN AN ACTION OF CONTRACT TORT OR OTHERWISE ARISING FROM OUT OF OR IN
        CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
        '''.lower().split()
        assert itext.split() == expected_itokens

    def test_match_can_match_discontinuous_rule_text_1(self):
        test_text = u'''Redistributions in binary form must
         reproduce the above copyright notice'''
        rule = create_rule_from_text_and_expression(text=test_text, license_expression='mylicense')
        idx = MiniLicenseIndex([rule])

        querys = u'''Redistributions in binary form must nexB company
        reproduce the word for word above copyright notice.'''

        matches = idx.match(query_string=querys)
        assert len(matches) == 1
        match = matches[0]
        assert match.coverage() == 100
        assert 36.67 == match.score()
        assert Span(0, 9) == match.qspan
        assert Span(0, 9) == match.ispan

    def test_match_can_match_discontinuous_rule_text_2(self):
        test_text = u'''Redistributions in binary form must
        reproduce the stipulated above copyright notice'''
        rule = create_rule_from_text_and_expression(text=test_text, license_expression='mylicense')
        idx = MiniLicenseIndex([rule])

        querys = u'''Redistributions in binary form must nexB company
        reproduce the stipulated word for word above copyright notice.'''

        matches = idx.match(query_string=querys)
        assert len(matches) == 1

        match = matches[0]
        assert match.coverage() == 100
        assert match.score() == 41.94
        assert match.qspan == Span(0, 10)
        assert match.ispan == Span(0, 10)

    def test_match_can_match_discontinuous_rule_text_3(self):
        test_text = u'''Redistributions in binary form must
        reproduce as is stipulated above copyright notice'''
        rule = create_rule_from_text_and_expression(text=test_text, license_expression='mylicense')
        idx = MiniLicenseIndex([rule])

        querys = u'''Redistributions in binary form must nexB company
        reproduce as is stipulated the word for word above copyright notice.'''

        matches = idx.match(query_string=querys)
        assert len(matches) == 1

        match = matches[0]
        assert match.qspan == Span(0, 11)
        assert match.ispan == Span(0, 11)

    def test_match_can_match_with_sax_rule_for_public_domain(self):
        test_text = '''
        I hereby abandon any property rights to , and release all of  source
        code, compiled code, and documentation contained in this distribution
        into the Public Domain.
        '''
        rule = create_rule_from_text_and_expression(text=test_text, license_expression='public-domain')

        legalese = build_dictionary_from_iterable(
            set(mini_legalese) |
            set(['property', 'abandon', 'rights', ])
        )
        idx = index.LicenseIndex([rule], _legalese=legalese)

        querys = '''
        SAX2 is Free!
        I hereby abandon any property rights to SAX 2.0 (the Simple API for
        XML), and release all of the SAX 2.0 source code, compiled code, and
        documentation contained in this distribution into the Public Domain. SAX
        comes with NO WARRANTY or guarantee of fitness for any purpose.
        SAX2 is Free!
        '''
        matches = idx.match(query_string=querys)

        assert len(matches) == 1
        match = matches[0]

        qtext, itext = get_texts(match)
        expected_qtext = ' '.join(u'''
        I hereby abandon any property rights to [SAX] [2].[0] ([the] [Simple]
        [API] [for] [XML]), [and] [release] [all] [of] [the] [SAX] [2].[0]
        source code, compiled code, and documentation contained in this
        distribution into the Public Domain.
        '''.split())
        assert ' '.join(qtext.split()) == expected_qtext

        expected_itext = ' '.join(u'''
        I hereby abandon any property rights to
        <and> <release> <all> <of>
        source code compiled code and documentation contained in this distribution
        into the Public Domain
        '''.lower().split())
        assert ' '.join(itext.split()) == expected_itext

        assert match.coverage() == 84
        assert match.score() == 84
        assert match.qspan == Span(0, 6) | Span(13, 26)
        assert match.ispan == Span(0, 6) | Span(11, 24)

    def test_match_can_match_with_rule_template_with_gap_near_start_with_few_tokens_before(self):
        # failed when a gapped token starts at a beginning of rule with few tokens before
        test_file = self.get_test_loc('detect/templates/license7.txt')
        rule = create_rule_from_text_file_and_expression(text_file=test_file, license_expression='lic')

        legalese = build_dictionary_from_iterable(
            set(mini_legalese) |
            set(['permission', 'written', 'registered', 'derived', 'damage', 'due'])
        )
        idx = index.LicenseIndex([rule], _legalese=legalese)

        qloc = self.get_test_loc('detect/templates/license8.txt')
        matches = idx.match(qloc)
        assert len(matches) == 1

        match = matches[0]
        expected_qtokens = u"""
            All Rights Reserved.

             Redistribution and use of this software and associated documentation
             ("Software"), with or without modification, are permitted provided
             that the following conditions are met:

             1. Redistributions of source code must retain copyright
                statements and notices.  Redistributions must also contain a
                copy of this document.

             2. Redistributions in binary form must reproduce the
                above copyright notice, this list of conditions and the
                following disclaimer in the documentation and/or other
                materials provided with the distribution.

             3. The name "[groovy]" must not be used to endorse or promote
                products derived from this Software without prior written
                permission of [The] [Codehaus].  For written permission,
                please contact [info]@[codehaus].[org].

             4. Products derived from this Software may not be called "[groovy]"
                nor may "[groovy]" appear in their names without prior written
                permission of [The] [Codehaus]. "[groovy]" is a registered
                trademark of [The] [Codehaus].

             5. Due credit should be given to [The] [Codehaus] -
                [http]://[groovy].[codehaus].[org]/

             [THIS] [SOFTWARE] [IS] [PROVIDED] [BY] [THE] [CODEHAUS] [AND] [CONTRIBUTORS]
             ``AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT
             NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
             FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL
             [THE] [CODEHAUS] OR ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
             INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
             (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
             SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
             HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
             STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
             ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
             OF THE POSSIBILITY OF SUCH DAMAGE.
        """.split()

        expected_itokens = u''' All Rights Reserved Redistribution and use of this
        software and associated documentation Software with or without modification
        are permitted provided that the following conditions are met

        1 Redistributions of source code must retain copyright statements and notices
        Redistributions must also contain copy of this document

        2 Redistributions in binary form must reproduce the above copyright notice
        this list of conditions and the following disclaimer in the documentation and
        or other materials provided with the distribution

        3 The name must not be used to endorse or promote products derived from this
        Software without prior written permission of For written permission please
        contact

        4 Products derived from this Software may not be called nor may appear in
        their names without prior written permission of is registered trademark of

        5 Due credit should be given to


        <THIS> <SOFTWARE> <IS> <PROVIDED> <BY>

        AS IS AND ANY EXPRESSED OR IMPLIED WARRANTIES INCLUDING BUT NOT LIMITED TO
        THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR PARTICULAR
        PURPOSE ARE DISCLAIMED IN NO EVENT SHALL OR ITS CONTRIBUTORS BE LIABLE FOR
        ANY DIRECT INDIRECT INCIDENTAL SPECIAL EXEMPLARY OR CONSEQUENTIAL DAMAGES
        INCLUDING BUT NOT LIMITED TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS
        OF USE DATA OR PROFITS OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON ANY
        THEORY OF LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR TORT INCLUDING
        NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE
        EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
        '''.lower().split()

        qtext, itext = get_texts(match)
        assert qtext.split() == expected_qtokens
        assert itext.split() == expected_itokens

        assert match.coverage() == 97.52
        assert match.score() == 97.52

        expected = Span(2, 97) | Span(99, 124) | Span(126, 129) | Span(131, 137) | Span(147, 175) | Span(177, 250)
        assert match.qspan == expected

        expected = Span(1, 133) | Span(139, 241)
        assert  match.ispan == expected

    def test_match_can_match_with_index_built_from_rule_directory_with_sun_bcls(self):
        rule_dir = self.get_test_loc('detect/rule_template/rules')
        idx = MiniLicenseIndex(load_rules(rule_dir))

        # at line 151 the query has an extra "Software" word inserted to avoid hash matching
        query_loc = self.get_test_loc('detect/rule_template/query.txt')
        matches = idx.match(location=query_loc)
        assert len(matches) == 1
        match = matches[0]
        expected = Span(0, 949) | Span(951, 1739)
        assert match.qspan == expected
        assert match.matcher == match_seq.MATCH_SEQ


class TestMatchAccuracyWithFullIndex(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def check_position(self, test_path, expected, with_span=True):
        """
        Check license detection in file or folder against expected result.
        Expected is a list of (license, lines span, qspan span) tuples.
        """
        test_location = self.get_test_loc(test_path)
        results = []
        # FULL INDEX!!
        idx = cache.get_index()
        matches = idx.match(test_location)
        for match in matches:
            for detected in match.rule.license_keys():
                results.append((detected, match.lines(), with_span and match.qspan or None))
        assert results == expected

    def test_match_has_correct_positions_basic(self):
        idx = cache.get_index()
        querys = u'''Licensed under the GNU General Public License (GPL).
                     Licensed under the GNU General Public License (GPL).
                     Licensed under the GNU General Public License (GPL).'''

        matches = idx.match(query_string=querys)

        rule = [r for r in idx.rules_by_rid if r.identifier == 'gpl_69.RULE'][0]
        m1 = LicenseMatch(rule=rule, matcher='2-aho', qspan=Span(0, 7), ispan=Span(0, 7), start_line=1, end_line=1)
        m2 = LicenseMatch(rule=rule, matcher='2-aho', qspan=Span(8, 15), ispan=Span(0, 7), start_line=2, end_line=2)
        m3 = LicenseMatch(rule=rule, matcher='2-aho', qspan=Span(16, 23), ispan=Span(0, 7), start_line=3, end_line=3)
        assert matches == [m1, m2, m3]

    def test_match_has_correct_line_positions_for_query_with_repeats(self):
        expected = [
            # licenses, match.lines(), qtext,
            ([u'apache-2.0'], (1, 2), u'The Apache Software License, Version 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0.txt'),
            ([u'apache-2.0'], (3, 4), u'The Apache Software License, Version 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0.txt'),
            ([u'apache-2.0'], (5, 6), u'The Apache Software License, Version 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0.txt'),
            ([u'apache-2.0'], (7, 8), u'The Apache Software License, Version 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0.txt'),
            ([u'apache-2.0'], (9, 10), u'The Apache Software License, Version 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0.txt'),
        ]
        test_path = 'positions/license1.txt'

        test_location = self.get_test_loc(test_path)
        idx = cache.get_index()
        matches = idx.match(test_location)
        for i, match in enumerate(matches):
            ex_lics, ex_lines, ex_qtext = expected[i]
            qtext, _itext = get_texts(match)

            try:
                assert match.rule.license_keys() == ex_lics
                assert match.lines() == ex_lines
                assert qtext == ex_qtext
            except AssertionError:
                assert (match.rule.license_keys(), match.lines(), qtext) == expected[i]

    def test_match_does_not_return_spurious_match(self):
        expected = []
        self.check_position('positions/license2.txt', expected)

    def test_match_has_correct_line_positions_for_repeats(self):
        # we had a weird error where the lines were not computed correctly
        # when we had more than one file detected at a time
        expected = [
            # detected, match.lines(), match.qspan,
            (u'apache-2.0', (1, 2), Span(0, 15)),
            (u'apache-2.0', (3, 4), Span(16, 31)),
            (u'apache-2.0', (5, 6), Span(32, 47)),
            (u'apache-2.0', (7, 8), Span(48, 63)),
            (u'apache-2.0', (9, 10), Span(64, 79)),
        ]
        self.check_position('positions/license3.txt', expected)

    def test_match_returns_correct_lines(self):
        test_location = self.get_test_loc('positions/correct_lines')
        expected = [('mit', (1, 1))]
        results = []
        idx = cache.get_index()
        matches = idx.match(test_location)
        for match in matches:
            for detected in match.rule.license_keys():
                results.append((detected, match.lines()))
        assert results == expected

    def test_match_returns_correct_lines2(self):
        test_location = self.get_test_loc('positions/correct_lines2')
        expected = [('mit', (2, 4))]
        results = []
        idx = cache.get_index()
        matches = idx.match(test_location)
        for match in matches:
            for detected in match.rule.license_keys():
                results.append((detected, match.lines()))
        assert results == expected

    def test_match_works_for_apache_rule(self):
        idx = cache.get_index()
        querys = u'''I am not a license.

            The Apache Software License, Version 2.0
            http://www.apache.org/licenses/LICENSE-2.0.txt
            '''
        matches = idx.match(query_string=querys)

        assert len(matches) == 1
        match = matches[0]
        assert match.rule.identifier == 'apache-2.0_212.RULE'
        assert match.matcher == match_aho.MATCH_AHO_EXACT

        qtext, _itext = get_texts(match)
        expected = (
            'license. The Apache Software License, Version 2.0\n'
            'http://www.apache.org/licenses/LICENSE-2.0.txt'
        )
        assert qtext == expected
        assert match.lines() == (1, 4)

    def test_match_does_not_detect_spurious_short_apache_rule(self):
        idx = cache.get_index()
        querys = u'''
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        <title>Apache log4j 1.2 - Continuous Integration</title>
        '''
        matches = idx.match(query_string=querys)
        assert matches == []

    def test_match_does_not_match_false_positive_regions_properly(self):
        # note: this test relies on the false positive rule:
        #  false-positive_busybox_1.RULE
        # with this text:
        #  "libbusybox is GPL, not LGPL, and exports no stable API that might act as a copyright barrier."
        # And relies on the short single world rules that detect GPL and LGPL.
        # the first and last lines should be matched. Not what is in between.
        idx = cache.get_index()
        querys = u'''
            licensed under the LGPL license
            libbusybox is GPL, not LGPL, and exports no stable API
            that might act as a copyright barrier.
            for the license
            license: dual BSD/GPL
            '''
        matches = idx.match(query_string=querys)

        results = [match.matched_text() for match in matches]
        expected = ['licensed under the LGPL license', 'license: dual BSD/GPL']
        assert results == expected

    def test_match_has_correct_line_positions_in_automake_perl_file(self):
        # Reported as https://github.com/nexB/scancode-toolkit/issues/88
        # Note that this test is very sensitive to changes in the licenses data
        # set on purpose. Adding new license and/or frequent tokens will likely
        # make it fail In this case, review the new not-frequent tokens that
        # could be involved, eventually update the rule-side Span offset if this
        # looks acceptable below. Most cases just need to fix the test.
        expected = [
            # detected, match.lines(), match.qspan,
            ('gpl-2.0-plus', (12, 25), Span(48, 157)),
            ('fsf-unlimited-no-warranty', (231, 238), Span(964, 1027)),
            ('free-unknown', (306, 307), Span(1335, 1357)),
        ]
        self.check_position('positions/automake.pl', expected)

    def test_score_is_not_100_for_exact_match_with_extra_words(self):
        idx = cache.get_index()
        test_loc = self.get_test_loc('detect/score/test.txt')
        matches = idx.match(location=test_loc)
        assert len(matches) == 1
        match = matches[0]
        assert 99 < match.score() < 100

    def test_match_texts_with_short_lgpl_and_gpl_notices(self):
        idx = cache.get_index()
        test_loc = self.get_test_loc('detect/short_l_and_gpls')
        matches = idx.match(location=test_loc)
        assert len(matches) == 8
        results = [m.matched_text(whole_lines=False, _usecache=False) for m in matches]
        expected = [
            'This software is distributed under the following licenses:',
            'GNU General Public License (GPL)',
            'GNU Lesser General Public License (LGPL)',
            'This software is distributed under the following licenses:',
            'GNU General Public License (GPL)',
            'GNU Lesser General Public (LGPL)',
            'GNU Lesser General Public (LGPL)',
            'GNU Lesser General Public (LGPL)']
        assert results == expected

    def test_match_filtering_discards_overlapping_trailing_matches_by_one_word(self):
        idx = cache.get_index()

        # "License Python" should not be returned as a second match
        query1 = '''

        simplejson
        ----------
        python-lib/simplejson
        Made available under the MIT license.

        Python Markdown
        ---------------
        python-lib/markdown
        '''

        matches = idx.match(query_string=query1)
        assert len(matches) == 1
        matched_text = matches[0].matched_text(whole_lines=False, _usecache=False)
        assert matched_text == 'Made available under the MIT license.'

    def test_match_filtering_discards_overlapping_leading_matches_by_one_word(self):
        idx = cache.get_index()
        # "apache Licensed" should not be returned as a first match
        # "License Python" should not be returned as a third match
        query2 = '''
        lib/simplejson from Apache

        Licensed under the GPL 2.0 license.

        Python Markdown
        '''

        matches = idx.match(query_string=query2)
        assert len(matches) == 1
        matched_text = matches[0].matched_text(whole_lines=False, _usecache=False)
        assert matched_text == 'Licensed under the GPL 2.0 license.'


class TestMatchBinariesWithFullIndex(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_in_binary_lkms_1(self):
        idx = cache.get_index()
        qloc = self.get_test_loc('positions/ath_pci.ko')
        matches = idx.match(location=qloc)
        assert len(matches) == 1
        match = matches[0]
        assert match.rule.license_keys() == ['bsd-new', 'gpl-2.0']

        qtext, itext = get_texts(match)
        assert qtext == 'license=Dual BSD/GPL'
        assert itext == 'license dual bsd gpl'

    @pytest.mark.scanslow
    def test_match_in_binary_lkms_2(self):
        idx = cache.get_index()
        qloc = self.get_test_loc('positions/eeepc_acpi.ko')
        matches = idx.match(location=qloc)
        assert len(matches) == 1
        match = matches[0]
        assert match.rule.license_keys() == ['gpl-1.0-plus']
        assert match.ispan == Span(0, 1)

        qtext, itext = get_texts(match)
        assert qtext == 'license=GPL'
        assert itext == 'license gpl'

    @pytest.mark.scanslow
    def test_match_in_binary_lkms_3(self):
        idx = cache.get_index()
        qloc = self.get_test_loc('positions/wlan_xauth.ko')
        matches = idx.match(location=qloc)
        assert len(matches) == 1
        match = matches[0]
        assert match.rule.license_keys() == ['bsd-new', 'gpl-2.0']
        assert match.coverage() == 100
        assert match.score() == 100
        qtext, itext = get_texts(match)
        assert qtext == 'license=Dual BSD/GPL'
        assert itext == 'license dual bsd gpl'
        assert match.ispan == Span(0, 3)

    @pytest.mark.scanslow
    def test_spurious_matches_in_binary_are_filtered(self):
        idx = cache.get_index()
        qloc = self.get_test_loc('false_positive/false-positive-in-binaries.zip')

        # Originally we were detecting these spurious license_expressions:
        #     - apache-2.0 with matched_text: ALv2@ : should be kept
        #     - lgpl-2.0-plus with matched_text: lGPl~= : invalid
        #     - gpl-2.0 with matched_text: GPL2\ : invalid
        # Each have these shared attributes:
        # - is_license_reference: yes
        # - rule_length: yes
        # And we matched with trailing punctuatiosn
        # And the file has: is_binary: yes
        matches = idx.match(location=qloc)
        assert len(matches) == 1
        assert matches[0].rule.license_expression == 'apache-2.0'


class TestRegression(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_detection_does_not_munge_first_matched_word(self):
        idx = cache.get_index()
        qloc = self.get_test_loc('detect/truncated/seq-match-truncated.bug')
        matches = idx.match(location=qloc)
        assert len(matches) == 2
        match = matches[1]
        matched_text = match.matched_text(whole_lines=False, _usecache=False)
        first_word = matched_text.split()[0]
        assert first_word == 'Permission'

    def test_detection_does_merge_contained_matches_separated_by_false_positive(self):
        idx = cache.get_index()
        qloc = self.get_test_loc('detect/contained/moz')
        matches = idx.match(location=qloc)
        assert len(matches) == 1
        match = matches[0]
        matched_text = match.matched_text(whole_lines=False, _usecache=False)
        words = matched_text.split()
        first_words = words[0: 3]
        assert first_words == ['BEGIN', 'LICENSE', 'BLOCK']
        last_words = words[-4:-1]
        assert last_words == ['END', 'LICENSE', 'BLOCK']

    def test_detection_return_correct_lgpl_with_correct_text_using_full_index(self):
        idx = cache.get_index()
        query_location = self.get_test_loc('detect/lgpl_not_gpl/query.txt')
        matches = idx.match(location=query_location)
        results = [m.matched_text(_usecache=False) for m in matches][0]
        expected = (
            u'is free software; you can redistribute it and/or modify\n'
            ' * it under the terms of the GNU General Public License as published by\n'
            ' * the Free Software Foundation; either version 2 of the License, or\n'
            ' * (at your option) any later version.\n'
            ' * \n'
            ' * [testVMX] is distributed in the hope that it will be useful,\n'
            ' * but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
            ' * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'
            ' * GNU General Public License for more details.\n'
            ' * \n'
            ' * You should have received a copy of the GNU General Public License\n'
            ' * along with [testVMX]; if not, write to the Free Software\n'
            ' * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  US'
        )
        match = matches[0]
        rule = match.rule
        assert results == expected
        assert rule.license_expression == 'gpl-2.0-plus'

    def test_detection_return_correct_lgpl_with_correct_text_using_controlled_index(self):
        from licensedcode import models

        rules_data_dir = self.get_test_loc('detect/lgpl_not_gpl/index/rules')
        query_location = self.get_test_loc('detect/lgpl_not_gpl/query.txt')
        rules = models.load_rules(rules_data_dir)
        idx = index.LicenseIndex(rules)
        matches = idx.match(location=query_location)
        results = [match.matched_text(_usecache=False) for match in matches][0]
        expected = (
            u'is free software; you can redistribute it and/or modify\n'
            ' * it under the terms of the GNU General Public License as published by\n'
            ' * the Free Software Foundation; either version 2 of the License, or\n'
            ' * (at your option) any later version.\n'
            ' * \n'
            ' * [testVMX] is distributed in the hope that it will be useful,\n'
            ' * but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
            ' * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'
            ' * GNU General Public License for more details.\n'
            ' * \n'
            ' * You should have received a copy of the GNU General Public License\n'
            ' * along with [testVMX]; if not, write to the Free Software\n'
            ' * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307'
        )
        assert results == expected
        matched_rule = matches[0].rule
        assert matched_rule.identifier == 'gpl-2.0-plus_258.RULE'
        assert matched_rule.license_expression == 'gpl-2.0-plus'

    def test_detection_return_correct_mit_not_apache_using_controlled_index(self):
        # we were incorrectly reporting an Apache using a sequence match
        # this has been fixed for https://github.com/nexB/scancode-toolkit/issues/2635
        # the key fix is to privilege the longest rule when two rules are tied
        # as candidates in set matching
        from licensedcode import models

        rules_data_dir = self.get_test_loc('detect/apache-vs-mit/index/rules')
        rules = models.load_rules(rules_data_dir)
        idx = index.LicenseIndex(rules)
        expected = ['mit']

        query_location = self.get_test_loc('detect/apache-vs-mit/incorrect.md')
        matches = idx.match(location=query_location)
        results = [m.rule.license_expression for m in matches]
        assert results == expected

        query_location = self.get_test_loc('detect/apache-vs-mit/correct.md')
        matches = idx.match(location=query_location)
        results = [m.rule.license_expression for m in matches]
        assert results == expected

    def test_detection_return_correct_mit_not_apache_using_full_index(self):
        # we were incorrectly reporting an Apache using a sequence match
        # this has been fixed in https://github.com/nexB/scancode-toolkit/issues/2635

        idx = cache.get_index()
        expected = ['mit']

        query_location = self.get_test_loc('detect/apache-vs-mit/incorrect.md')
        matches = idx.match(location=query_location)
        results = [m.rule.license_expression for m in matches]
        assert results == expected

        query_location = self.get_test_loc('detect/apache-vs-mit/correct.md')
        matches = idx.match(location=query_location)
        results = [m.rule.license_expression for m in matches]
        assert results == expected
