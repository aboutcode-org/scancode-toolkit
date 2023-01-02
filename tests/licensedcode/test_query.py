#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os
from collections import defaultdict

from commoncode.testcase import FileBasedTesting

from licensedcode import cache
from licensedcode import index
from licensedcode import models
from licensedcode.legalese import build_dictionary_from_iterable
from licensedcode.query import Query

from licensedcode_test_utils import query_tokens_with_unknowns  # NOQA
from licensedcode_test_utils import query_run_tokens_with_unknowns  # NOQA
from scancode_config import REGEN_TEST_FIXTURES
from licensedcode_test_utils import create_rule_from_text_and_expression
from licensedcode_test_utils import create_rule_from_text_file_and_expression

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES):
    """
    Check equality between a result collection and an expected JSON file.
    Regen the expected file if regen is True.
    """
    if regen:
        with open(expected, 'w') as ex:
            ex.write(json.dumps(result, indent=2))

    with open(expected) as ex:
        expected = json.loads(ex.read())

    assert result == expected


def tks_as_str(tks, idx):
    """
    Convert tid to actual token strings
    """
    tokens_by_tid = idx.tokens_by_tid
    return [None if tid is None else tokens_by_tid[tid] for tid  in tks]


class IndexTesting(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def get_test_rules(self, base, subset=None):
        base = self.get_test_loc(base)
        test_files = sorted(os.listdir(base))
        if subset:
            test_files = [t for t in test_files if t in subset]

        return [create_rule_from_text_file_and_expression(text_file=os.path.join(base, license_key), license_expression=license_key)
                for license_key in test_files]


class TestQueryWithSingleRun(IndexTesting):

    def test_Query_tokens_by_line_from_string(self):
        rule_text = 'Redistribution and use in source and binary forms with or without modification are permitted'
        rule = create_rule_from_text_and_expression(text=rule_text, license_expression='bsd')
        legalese = build_dictionary_from_iterable(['redistribution', 'form', ])
        idx = index.LicenseIndex([rule], _legalese=legalese)
        querys = '''
            The
            Redistribution and use in source and binary are permitted

            Athena capital of Grece
            Paris and Athene
            Always'''

        qry = Query(query_string=querys, idx=idx, _test_mode=True)
        result = list(qry.tokens_by_line())
        expected = [
            [],
            [None],
            [1, 2, 3, 4, 5, 2, 6, 12, 13],
            [],
            [None, None, None, None],
            [None, 2, None],
            [None],
        ]

        assert result == expected

        # convert tid to actual token strings
        qtbl_as_str = lambda qtbl: [[None if tid is None else idx.tokens_by_tid[tid] for tid in tids] for tids in qtbl]

        result_str = qtbl_as_str(result)
        expected_str = [
            [],
            [None],
            ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted'],
            [],
            [None, None, None, None],
            [None, 'and', None],
            [None],
        ]

        assert result_str == expected_str

        assert qry.line_by_pos == [3, 3, 3, 3, 3, 3, 3, 3, 3, 6]

        idx = index.LicenseIndex([create_rule_from_text_and_expression(text=rule_text, license_expression='bsd')])
        querys = 'and this is not a license'
        qry = Query(query_string=querys, idx=idx, _test_mode=True)
        result = list(qry.tokens_by_line())
        expected = [['and', None, None, None, 'license']]
        assert qtbl_as_str(result) == expected

    def test_Query_known_and_unknown_positions(self):

        rule_text = 'Redistribution and use in source and binary forms'
        rule = create_rule_from_text_and_expression(text=rule_text, license_expression='bsd')
        legalese = build_dictionary_from_iterable(['redistribution', 'form', ])
        idx = index.LicenseIndex([rule], _legalese=legalese)

        querys = 'The new Redistribution and use in other form always'
        qry = Query(query_string=querys, idx=idx, _test_mode=False)
        # we have only 4 known positions in this query, hence only 4 entries there on a single line
        # "Redistribution and use in"
        assert qry.line_by_pos == [1, 1, 1, 1, 1]

        # this show our 4 known token in this query with their known position
        # "Redistribution and use in"
        assert qry.tokens == [1, 2, 3, 4, 0]

        # the first two tokens are unknown, then starting after "in" we have three trailing unknown.
        assert qry.unknowns_by_pos == {3: 1, 4: 1, -1: 2}
        # This shows how knowns and unknowns are blended
        result = list(query_tokens_with_unknowns(qry))
        expected = [
            # The  new
            None, None,
            # Redistribution
            1,
            # and
            2,
            # use
            3,
            # in
            4,
            # other form always'
            None, 0, None
        ]
        assert result == expected

    def test_Query_tokenize_from_string(self):
        rule_text = 'Redistribution and use in source and binary forms with or without modification are permitted'
        idx = index.LicenseIndex([create_rule_from_text_and_expression(text=rule_text, license_expression='bsd')])
        querys = '''
            The
            Redistribution and use in source and binary are permitted.

            Athena capital of Grece
            Paris and Athene
            Always'''

        qry = Query(query_string=querys, idx=idx, _test_mode=True)
        tokens_by_line = list(qry.tokens_by_line(query_string=querys))
        qry.tokenize_and_build_runs(tokens_by_line)

        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', 'and']
        result = tks_as_str(qry.tokens, idx=idx)
        assert result == expected

        expected = [None, 'redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', None, None, None, None, None, 'and', None, None]
        result = tks_as_str(query_tokens_with_unknowns(qry), idx=idx)
        assert result == expected

        assert len(qry.query_runs) == 1
        qr1 = qry.query_runs[0]
        assert qr1.start == 0
        assert qr1.end == 9
        assert len(qr1) == 10
        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', 'and']
        result = tks_as_str(qr1.tokens, idx=idx)
        assert result == expected
        expected = [None, 'redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', None, None, None, None, None, 'and']
        result = tks_as_str(query_run_tokens_with_unknowns(qr1), idx=idx)
        assert result == expected

    def test_QueryRuns_tokens_with_unknowns(self):
        rule_text = 'Redistribution and use in source and binary forms with or without modification are permitted'
        idx = index.LicenseIndex([create_rule_from_text_and_expression(text=rule_text, license_expression='bsd')])
        querys = '''
            The
            Redistribution and use in source and binary are permitted.

            Athena capital of Grece
            Paris and Athene
            Always'''

        qry = Query(query_string=querys, idx=idx)
        assert set(qry.matchables) == set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

        assert len(qry.query_runs) == 1
        qrun = qry.query_runs[0]

        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', 'and']
        assert tks_as_str(qrun.tokens, idx=idx) == expected

        expected = [None, 'redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', None, None, None, None, None, 'and']
        assert tks_as_str(query_run_tokens_with_unknowns(qrun), idx=idx) == expected

        assert qrun.start == 0
        assert qrun.end == 9

    def test_QueryRun_does_not_end_with_None(self):
        rule_text = 'Redistribution and use in source and binary forms, with or without modification, are permitted'
        idx = index.LicenseIndex([create_rule_from_text_and_expression(text=rule_text, license_expression='bsd')])

        querys = '''
            The
            Redistribution and use in source and binary forms, with or without modification, are permitted.

            Always



            bar
             modification
             foo
            '''
        qry = Query(query_string=querys, idx=idx)
        expected = [
            None,
            'redistribution', 'and', 'use', 'in', 'source', 'and', 'binary',
            'forms', 'with', 'or', 'without', 'modification', 'are', 'permitted',
            None, None,
            'modification',
            None
        ]
        assert tks_as_str(qry.tokens, idx=idx) == [x for x in expected if x]
        assert tks_as_str(query_tokens_with_unknowns(qry), idx=idx) == expected

        assert len(qry.query_runs) == 2
        qrun = qry.query_runs[0]
        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'forms', 'with', 'or', 'without', 'modification', 'are', 'permitted']
        assert tks_as_str(qrun.tokens, idx=idx) == expected
        assert qrun.start == 0
        assert qrun.end == 13

        qrun = qry.query_runs[1]
        expected = ['modification']
        assert tks_as_str(qrun.tokens, idx=idx) == expected
        assert qrun.start == 14
        assert qrun.end == 14

    def test_Query_from_real_index_and_location(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/querytokens')

        qry = Query(location=query_loc, idx=idx, line_threshold=4)
        result = [qr.to_dict() for qr in qry.query_runs]
        expected = [
            {'end': 35,
             'start': 0,
             'tokens': ('redistribution and use in source and binary forms '
                        'redistributions of source code must the this that is not '
                        'to redistributions in binary form must this software is '
                        'provided by the copyright holders and contributors as is')
             },
            {'end': 36, 'start': 36, 'tokens': 'redistributions'}]
        assert result == expected

        expected_lbp = [
            4, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 8,
            9, 9, 9, 9, 9, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 15
        ]
        assert qry.line_by_pos == expected_lbp

    def test_query_and_index_tokens_are_identical_for_same_text(self):
        rule_dir = self.get_test_loc('query/rtos_exact/')
        from licensedcode.models import load_rules
        idx = index.LicenseIndex(load_rules(rule_dir))
        query_loc = self.get_test_loc('query/old_rtos_exact/gpl-2.0-freertos.RULE')

        index_text_tokens = [idx.tokens_by_tid[t] for t in idx.tids_by_rid[0]]

        qry = Query(location=query_loc, idx=idx, line_threshold=4)
        wqry = qry.whole_query_run()

        query_text_tokens = [idx.tokens_by_tid[t] for t in wqry.tokens]

        assert index_text_tokens == query_text_tokens
        assert ' '.join(index_text_tokens) == ' '.join(query_text_tokens)

    def test_query_run_tokens_with_junk(self):
        legalese = build_dictionary_from_iterable(['binary'])
        idx = index.LicenseIndex([
            create_rule_from_text_and_expression(text='a is the binary')],
            _legalese=legalese,
            _spdx_tokens=set(),
        )
        assert idx.len_legalese == 1
        assert idx.dictionary == {'binary': 0, 'is': 1, 'the': 2}

        # two junks
        q = Query(query_string='a the', idx=idx)
        assert q.line_by_pos
        qrun = q.query_runs[0]
        assert qrun.tokens == [2]
        assert qrun.query.unknowns_by_pos == {}

        # one junk
        q = Query(query_string='a binary', idx=idx)
        qrun = q.query_runs[0]
        assert q.line_by_pos
        assert qrun.tokens == [0]
        assert qrun.query.unknowns_by_pos == {}

        # one junk
        q = Query(query_string='binary the', idx=idx)
        qrun = q.query_runs[0]
        assert q.line_by_pos
        assert qrun.tokens == [0, 2]
        assert qrun.query.unknowns_by_pos == {}

        # one unknown at start
        q = Query(query_string='that binary', idx=idx)
        qrun = q.query_runs[0]
        assert q.line_by_pos
        assert qrun.tokens == [0]
        assert qrun.query.unknowns_by_pos == {-1: 1}

        # one unknown at end
        q = Query(query_string='binary that', idx=idx)
        qrun = q.query_runs[0]
        assert q.line_by_pos
        assert qrun.tokens == [0]
        assert qrun.query.unknowns_by_pos == {0: 1}

        # onw unknown in the middle
        q = Query(query_string='binary that a binary', idx=idx)
        qrun = q.query_runs[0]
        assert q.line_by_pos
        assert qrun.tokens == [0, 0]
        assert qrun.query.unknowns_by_pos == {0: 1}

        # onw unknown in the middle
        q = Query(query_string='a binary that a binary', idx=idx)
        qrun = q.query_runs[0]
        assert q.line_by_pos
        assert qrun.tokens == [0, 0]
        assert qrun.query.unknowns_by_pos == {0: 1}

        # two unknowns in the middle
        q = Query(query_string='binary that was a binary', idx=idx)
        qrun = q.query_runs[0]
        assert q.line_by_pos
        assert qrun.tokens == [0, 0]
        assert qrun.query.unknowns_by_pos == {0: 2}

        # unknowns at start, middle and end
        q = Query(query_string='hello dolly binary that was a binary end really', idx=idx)
        #                         u     u           u    u            u    u
        qrun = q.query_runs[0]
        assert q.line_by_pos
        assert qrun.tokens == [0, 0]
        assert qrun.query.unknowns_by_pos == {0: 2, 1: 2, -1: 2}

    def test_query_tokens_are_same_for_different_text_formatting(self):

        test_files = [self.get_test_loc(f) for f in [
            'queryformat/license2.txt',
            'queryformat/license3.txt',
            'queryformat/license4.txt',
            'queryformat/license5.txt',
            'queryformat/license6.txt',
        ]]

        rule_file = self.get_test_loc('queryformat/license1.txt')
        idx = index.LicenseIndex([create_rule_from_text_file_and_expression(text_file=rule_file, license_expression='mit')])

        q = Query(location=rule_file, idx=idx)
        assert len(q.query_runs) == 1
        expected = q.query_runs[0]
        for tf in test_files:
            q = Query(tf, idx=idx)
            qr = q.query_runs[0]
            assert qr.tokens == expected.tokens

    def test_query_run_unknowns(self):
        legalese = build_dictionary_from_iterable(['binary'])
        idx = index.LicenseIndex(
            [create_rule_from_text_and_expression(text='a is the binary')],
            _legalese=legalese,
        )

        assert idx.dictionary == {'binary': 0, 'is': 1, 'the': 2}
        assert idx.len_legalese == 1

        # multiple unknowns at start, middle and end
        q = Query(query_string='that new binary was sure a kind of the real mega deal', idx=idx)
        # known pos                      0               1         2
        # abs pos                  0   1 2      3   4    5 6    7  8   9    10   11
        expected = {-1: 2, 0: 4, 1: 3}
        assert dict(q.unknowns_by_pos) == expected

    def test_query_unknowns_by_pos_and_stopwords_are_not_defaultdic_and_not_changed_on_query(self):
        idx = index.LicenseIndex(
            [create_rule_from_text_and_expression(text='a is the binary')],
            _legalese=build_dictionary_from_iterable(['binary']),
            _spdx_tokens=set()
        )
        q = Query(query_string='binary that was a binary', idx=idx)
        list(q.tokens_by_line())
        assert q.unknowns_by_pos == {0: 2}
        assert q.stopwords_by_pos == {0: 1}

        assert not isinstance(q.unknowns_by_pos, defaultdict)
        assert not isinstance(q.stopwords_by_pos, defaultdict)

        try:
            q.unknowns_by_pos[1]
            assert q.unknowns_by_pos == {0: 2}
        except KeyError:
            pass
        try:
            q.stopwords_by_pos[1]
            assert q.stopwords_by_pos == {0: 1}
        except KeyError:
            pass

    def test_query_unknowns_by_pos_and_stopwords_are_not_set_on_last_query_position(self):
        print('\nINDEX')
        idx = index.LicenseIndex(
            [create_rule_from_text_and_expression(text='is the binary a')],
            _legalese=build_dictionary_from_iterable(['binary']),
            _spdx_tokens=set()
        )
        print('\nQUERY')
        q = Query(query_string='a bar binary that was a binary a is the foo bar a', idx=idx)

        tids = list(q.tokens_by_line())
        assert tids == [[None, 0, None, None, 0, 1, 2, None, None]]
        # word:   a  bar  binary  that  was   a    binary  a   is    the  foo   bar   a
        # tids:  [   None 0,      None, None,      0,          1,    2,   None, None   ]
        # known:  st uk   kn      uk    uk    st   kn      st  kn    kn   uk    uk    st
        # pos:            0                        1           2     3
        assert q.unknowns_by_pos == {-1: 1, 0: 2, 3: 2}
        assert q.stopwords_by_pos == {-1: 1, 0: 1, 1: 1, 3: 1}


class TestQueryWithMultipleRuns(IndexTesting):

    def test_query_runs_from_location(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/querytokens')
        qry = Query(location=query_loc, idx=idx, line_threshold=3)
        result = [q.to_dict(brief=True) for q in qry.query_runs]

        expected = [
            {
             'start': 0,
             'end': 35,
             'tokens': 'redistribution and use in source ... holders and contributors as is'},
            {
             'start': 36,
             'end': 36,
             'tokens': 'redistributions'}
        ]
        assert result == expected

    def test_query_runs_three_runs(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/queryruns')
        qry = Query(location=query_loc, idx=idx)
        expected = [
            {'end': 82,
             'start': 0,
             'tokens': 'the redistribution and use in ... 2 1 3 c 4'},
            {'end': 95,
             'start': 83,
             'tokens': 'this software is provided by ... holders and contributors as is'},
            {'end': 96, 'start': 96, 'tokens': 'redistributions'}
        ]

        result = [q.to_dict(brief=True) for q in qry.query_runs]
        assert result == expected

    def test_QueryRun(self):
        idx = index.LicenseIndex([create_rule_from_text_and_expression(text='redistributions in binary form must redistributions in')])
        qry = Query(query_string='redistributions in binary form must redistributions in', idx=idx)
        qruns = qry.query_runs
        assert len(qruns) == 1
        qr = qruns[0]
        # test
        result = [idx.tokens_by_tid[tid] for tid in qr.tokens]
        expected = ['redistributions', 'in', 'binary', 'form', 'must', 'redistributions', 'in']
        assert result == expected

    def test_QueryRun_repr(self):
        idx = index.LicenseIndex([create_rule_from_text_and_expression(text='redistributions in binary form must redistributions in')])
        qry = Query(query_string='redistributions in binary form must redistributions in', idx=idx)
        qruns = qry.query_runs
        qr = qruns[0]
        # test
        expected = 'QueryRun(start=0, len=7, start_line=1, end_line=1)'
        assert repr(qr) == expected

        expected = 'QueryRun(start=0, len=7, start_line=1, end_line=1, tokens="redistributions in binary form must redistributions in")'
        assert qr.__repr__(trace_repr=True) == expected

    def test_query_runs_text_is_correct(self):
        test_rules = self.get_test_rules('query/full_text/idx',)
        idx = index.LicenseIndex(test_rules)

        query_loc = self.get_test_loc('query/full_text/query')
        qry = Query(location=query_loc, idx=idx, line_threshold=3)

        result = [
            tks_as_str(query_run_tokens_with_unknowns(qr), idx=idx)
            for qr in  qry.query_runs
        ]

        expected = [
            [None, None, None, 'this'],

            '''redistribution and use in source and binary forms with or
            without modification are permitted provided that the following
            conditions are met redistributions of source code must retain the
            above copyright notice this list of conditions and the following
            disclaimer redistributions in binary form must reproduce the above
            copyright notice this list of conditions and the following
            disclaimer in the documentation and or other materials provided with
            the distribution neither the name of nexb inc nor the names of its
            contributors may be used to endorse or promote products derived from
            this software without specific prior written permission this
            software is provided by the copyright holders and contributors as is
            and any express or implied warranties including but not limited to
            the implied warranties of merchantability and fitness for
            particular purpose are disclaimed in no event shall the copyright
            owner or contributors be liable for any direct indirect incidental
            special exemplary or consequential damages including but not limited
            to procurement of substitute goods or services loss of use data or
            profits or business interruption however caused and on any theory of
            liability whether in contract strict liability or tort including
            negligence or otherwise arising in any way out of the use of this
            software even if advised of the possibility of such damage'''.split(),
            ['no', None, 'of'],
        ]
        assert result == expected

    def test_query_runs_with_plain_rule(self):
        rule_text = '''X11 License
            Copyright (C) 1996 X Consortium Permission is hereby granted, free
            of charge, to any person obtaining a copy of this software and
            associated documentation files (the "Software"), to deal in the
            Software without restriction, including without limitation the
            rights to use, copy, modify, merge, publish, distribute, sublicense,
            and/or sell copies of the Software, and to permit persons to whom
            the Software is furnished to do so, subject to the following
            conditions: The above copyright notice and this permission notice
            shall be included in all copies or substantial portions of the
            Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
            KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
            WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
            NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR
            ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
            CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
            WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
            Except as contained in this notice, the name of the X Consortium
            shall not be used in advertising or otherwise to promote the sale,
            use or other dealings in this Software without prior written
            authorization from the X Consortium. X Window System is a trademark
            of X Consortium, Inc.
        '''
        rule = create_rule_from_text_and_expression(text=rule_text, license_expression='x-consortium')
        idx = index.LicenseIndex([rule])

        query_loc = self.get_test_loc('detect/simple_detection/x11-xconsortium_text.txt')
        qry = Query(location=query_loc, idx=idx)
        result = [q.to_dict(brief=False) for q in qry.query_runs]
        expected = [{
            'start': 0,
            'end': 213,
            'tokens':(
                'x11 license copyright c 1996 x consortium permission is hereby '
                'granted free of charge to any person obtaining copy of this '
                'software and associated documentation files the software to deal in '
                'the software without restriction including without limitation the '
                'rights to use copy modify merge publish distribute sublicense and or '
                'sell copies of the software and to permit persons to whom the '
                'software is furnished to do so subject to the following conditions '
                'the above copyright notice and this permission notice shall be '
                'included in all copies or substantial portions of the software the '
                'software is provided as is without warranty of any kind express or '
                'implied including but not limited to the warranties of '
                'merchantability fitness for particular purpose and noninfringement '
                'in no event shall the x consortium be liable for any claim damages or '
                'other liability whether in an action of contract tort or otherwise '
                'arising from out of or in connection with the software or the use or '
                'other dealings in the software except as contained in this notice the '
                'name of the x consortium shall not be used in advertising or '
                'otherwise to promote the sale use or other dealings in this software '
                'without prior written authorization from the x consortium x window '
                'system is trademark of x consortium inc'
            )
        }]
        assert len(qry.query_runs[0].tokens) == 214
        assert result == expected

    def test_query_run_has_correct_offset(self):
        rule_dir = self.get_test_loc('query/runs/rules')
        rules = list(models.load_rules(rule_dir))
        idx = index.LicenseIndex(rules)
        query_doc = self.get_test_loc('query/runs/query.txt')
        q = Query(location=query_doc, idx=idx, line_threshold=4)
        result = [qr.to_dict() for qr in q.query_runs]
        expected = [
            {'end': 0, 'start': 0, 'tokens': 'inc'},
            {'end': 121, 'start': 1,
                'tokens': (
                'this library is free software you can redistribute it and or modify '
                'it under the terms of the gnu library general public license as '
                'published by the free software foundation either version 2 of the '
                'license or at your option any later version this library is '
                'distributed in the hope that it will be useful but without any '
                'warranty without even the implied warranty of merchantability or '
                'fitness for particular purpose see the gnu library general public '
                'license for more details you should have received copy of the gnu '
                'library general public license along with this library see the file '
                'copying lib if not write to the free software foundation inc 51 '
                'franklin street fifth floor boston ma 02110 1301 usa')
            }
        ]

        assert result == expected

    def test_query_run_and_tokenizing_breaking_works__with_plus_as_expected(self):
        rule_dir = self.get_test_loc('query/run_breaking/rules')
        rules = list(models.load_rules(rule_dir))
        idx = index.LicenseIndex(rules)
        query_doc = self.get_test_loc('query/run_breaking/query.txt')
        q = Query(query_doc, idx=idx)
        result = [qr.to_dict() for qr in q.query_runs]
        expected = [
            {'end': 119, 'start': 0,
             'tokens':
                'this library is free software you can redistribute it '
                'and or modify it under the terms of the gnu library '
                'general public license as published by the free software '
                'foundation either version 2 of the license or at your '
                'option any later version this library is distributed in '
                'the hope that it will be useful but without any warranty '
                'without even the implied warranty of merchantability or '
                'fitness for particular purpose see the gnu library '
                'general public license for more details you should have '
                'received copy of the gnu library general public '
                'license along with this library see the file copying lib '
                'if not write to the free software foundation 51 franklin '
                'street fifth floor boston ma 02110 1301 usa'}
        ]

        assert result == expected

        # check rules token are the same exact set as the set of the last query run
        txtid = idx.tokens_by_tid
        qrt = [txtid[t] for t in q.query_runs[-1].tokens]
        irt = [txtid[t] for t in idx.tids_by_rid[0]]
        assert irt == qrt

    def test_QueryRun_with_all_digit_lines(self):
        rule = create_rule_from_text_and_expression(text='''
            redistributions 0 1 2 3 4 1568 5 6 7 368 8 9 10 80 12213 232312 in
            binary 345 in 256
            free 1953
             software 406
             foundation 1151
            free 429
             software 634
             foundation 1955
            free 724
             software 932
             foundation 234
             software 694
             foundation 110
        ''')

        legalese = build_dictionary_from_iterable(['binary', 'redistributions', 'foundation'])
        idx = index.LicenseIndex([rule], _legalese=legalese)

        qs = '''
              25  17   1   -80.00000      .25000    37.00000      .25000
            0: 5107 -2502 -700 496 -656 468 -587 418 -481 347 -325 256 -111 152 166 50
            493 -37 854 -96 1221 -118 1568 -125 1953 -143 2433 -195 2464 -281 2529 -395
            1987 -729 447 -916 -3011 -1181 -5559 -406 -6094 541 -5714 1110 -5247 1289
            -4993 1254 -4960 1151
            1: 4757 -1695 -644 429 -627 411 -602 368 -555 299 -470 206 -328 96 -125 -15
            126 -105 391 -146 634 -120 762 -58 911 -13 1583 -8 1049 -28 1451 123 1377 -464
            907 -603 -4056 -1955 -6769 -485 -5797 929 -4254 1413 -3251 1295 -2871 993
            -2899 724
            2: 4413 -932 -563 355 -566 354 -582 322 -597 258 -579 164 -499 45 -341 -84
            -127 -192 93 -234 288 -157 190 -25 -145 65 1065 74 -1087 -40 -877 1058 -994 18
            1208 694 -5540 -3840 -7658 -332 -4130 1732 -1668 1786 -634 1127 -525 501
            -856 110
        '''

        qry = Query(query_string=qs, idx=idx)
        result = [qr.to_dict() for qr in qry.query_runs]
        # FIXME: we should not even have a query run for things that are all digits
        expected = [
            {'end': 5, 'start': 0, 'tokens': '1 80 0 256 1568 1953'},
            {'end': 12, 'start': 6, 'tokens': '406 1151 1 429 368 634 8'},
            {'end': 17, 'start': 13, 'tokens': '1955 724 2 932 234'},
        ]
        assert result == expected

        assert not any(qr.is_matchable() for qr in qry.query_runs)


class TestQueryWithFullIndex(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_query_from_binary_lkms_1(self):
        location = self.get_test_loc('query/ath_pci.ko')
        idx = cache.get_index()
        result = Query(location, idx=idx)
        assert len(result.query_runs) < 15

    def test_query_from_binary_lkms_2(self):
        location = self.get_test_loc('query/eeepc_acpi.ko')
        idx = cache.get_index()
        result = Query(location, idx=idx)
        assert len(result.query_runs) < 500

        qrs = result.query_runs[:10]
        # for i, qr in enumerate(qrs):
        #     print('qr:', i,
        #           'qr_text:', ' '.join(idx.tokens_by_tid[t] for t in qr.matchable_tokens()))
        assert any('license gpl' in ' '.join(idx.tokens_by_tid[t] for t in qr.matchable_tokens())
                   for qr in qrs)

    def test_query_from_binary_lkms_3(self):
        location = self.get_test_loc('query/wlan_xauth.ko')
        idx = cache.get_index()
        result = Query(location, idx=idx)
        assert len(result.query_runs) < 900
        qr = result.query_runs[0]
        assert 'license dual bsd gpl' in ' '.join(
            idx.tokens_by_tid[t] for t in qr.matchable_tokens())

    def test_query_run_tokens(self):
        query_s = ' '.join(''' 3 unable to create proc entry license gpl
        description driver author eric depends 2 6 24 19 generic smp mod module acpi
        baridationally register driver proc acpi disabled acpi install notify acpi baridationally get
        status cache caches create proc entry baridationally generate proc event acpi evaluate
        object acpi remove notify remove proc entry acpi baridationally driver acpi acpi gcc gnu
        4 2 3 ubuntu 4 2 3 gcc gnu 4 2 3 ubuntu 4 2 3 current stack pointer current
        stack pointer this module end usr modules acpi include linux include asm
        include asm generic include acpi acpi c posix types 32 h types h types h h h
        h h
        '''.split())
        idx = cache.get_index()
        result = Query(query_string=query_s, idx=idx)
        assert len(result.query_runs) == 1
        qr = result.query_runs[0]
        # NOTE: this is not a token present in any rules or licenses
        unknown_tokens = ('baridationally',)
        assert unknown_tokens not in idx.dictionary
        assert ' '.join([t for t in query_s.split()
            if t not in unknown_tokens]) == ' '.join(
                idx.tokens_by_tid[t] for t in qr.tokens)

    def test_query_run_tokens_matchable(self):
        idx = cache.get_index()
        # NOTE: this is not a token present in any rules or licenses
        unknown_token = 'baridationally'
        assert unknown_token not in idx.dictionary

        query_s = ' '.join('''

        3 unable to create proc entry license gpl description driver author eric
        depends 2 6 24 19 generic smp mod module acpi baridationally register driver
        proc acpi disabled acpi install notify acpi baridationally get status cache
        caches create proc entry baridationally generate proc event acpi evaluate
        object acpi remove notify remove proc entry acpi baridationally driver acpi
        acpi gcc gnu 4 2 3 ubuntu 4 2 3 gcc gnu 4 2 3 ubuntu 4 2 3 current stack
        pointer current stack pointer this module end usr src modules acpi include
        linux include asm include asm generic include acpi acpi c posix types 32 h
        types h types h h h h h
        '''.split())
        result = Query(query_string=query_s, idx=idx)
        assert len(result.query_runs) == 1
        qr = result.query_runs[0]
        expected_qr0 = ' '.join('''
        3 unable to create proc entry license gpl description driver author eric
        depends 2 6 24 19 generic smp mod module acpi             register driver
        proc acpi disabled acpi install notify acpi               get status cache
        caches create proc entry                generate proc event acpi evaluate
        object acpi remove notify remove proc entry acpi             driver acpi
        acpi gcc gnu 4 2 3 ubuntu 4 2 3 gcc gnu 4 2 3 ubuntu 4 2 3 current stack
        pointer current stack pointer this module end usr modules acpi include
        linux include asm include asm generic include acpi acpi c posix types 32 h
        types h types h h h h h
        '''.split())
        assert ' '.join(idx.tokens_by_tid[t] for t in qr.tokens) == expected_qr0

        assert ' '.join(idx.tokens_by_tid[t] for p, t in enumerate(
                qr.tokens) if p in qr.matchables) == expected_qr0

        # only gpl and gnu are is in high matchables
        expected = 'license gpl author gnu gnu'
        assert ' '.join(idx.tokens_by_tid[t] for p, t in enumerate(
                qr.tokens) if p in qr.high_matchables) == expected

    def test_query_run_for_text_with_long_lines(self):
        location1 = self.get_test_loc('query/long_lines.txt')
        location2 = self.get_test_loc('query/not_long_lines.txt')
        from typecode.contenttype import get_type
        ft1 = get_type(location1)
        assert ft1.is_text_with_long_lines
        ft2 = get_type(location2)
        assert not ft2.is_text_with_long_lines

        idx = cache.get_index()
        assert len(Query(location1, idx=idx).query_runs) == 17
        assert len(Query(location2, idx=idx).query_runs) == 15

    def test_match_does_not_change_query_unknown_positions(self):
        from licensedcode.match import LicenseMatch
        from licensedcode.spans import Span

        location = self.get_test_loc('query/unknown_positions/lz4.license.txt')
        idx = cache.get_index()
        # build a query first
        qry1 = Query(location, idx=idx)
        # this has the side effect to populate the unknown
        txt = ' '.join(f'{i}-{idx.tokens_by_tid[t]}' for i, t in enumerate(qry1.tokens))
        assert txt == (
            '0-this 1-repository 2-uses 3-2 4-different 5-licenses '
            '6-all 7-files 8-in 9-the 10-lib 11-directory 12-use 13-bsd 14-2 15-clause 16-license '
            '17-all 18-other 19-files 20-use 21-gplv2 22-license 23-unless 24-explicitly 25-stated 26-otherwise '
            '27-relevant 28-license 29-is 30-reminded 31-at 32-the 33-top 34-of 35-each 36-source 37-file '
            '38-and 39-with 40-presence 41-of 42-copying 43-or 44-license 45-file 46-in 47-associated 48-directories '
            '49-this 50-model 51-is 52-selected 53-to 54-emphasize 55-that '
            '56-files 57-in 58-the 59-lib 60-directory 61-are 62-designed 63-to 64-be 65-included 66-into 67-3rd 68-party 69-applications '
            '70-while 71-all 72-other 73-files 74-in 75-programs 76-tests 77-or 78-examples '
            '79-receive 80-more 81-limited 82-attention 83-and 84-support 85-for 86-such 87-scenario'
        )
        list(qry1.tokens_by_line())
        assert qry1.unknowns_by_pos == {}

        # run matching
        matches = idx.match(location=location)
        match = matches[0]

        rule = [
            r for r in idx.rules_by_rid
            if r.identifier == 'bsd-simplified_and_gpl-2.0_1.RULE'
        ][0]

        expected = LicenseMatch(
            matcher='2-aho',
            rule=rule,
            qspan=Span(0, 48),
            ispan=Span(0, 48),
        )

        assert match == expected

        # check that query unknown by pos is the same and empty
        qry2 = match.query

        # this was incorrectly returned as {15: 0, 20: 0, 21: 0, 41: 0, 43: 0}
        # after querying done during matching
        assert qry2.unknowns_by_pos == {}
