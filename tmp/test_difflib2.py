
"""
From Python's 2.7 branch test/test_difflib2.py
https://hg.python.org/cpython/raw-file/b91c323a605e/Lib/test/test_difflib2.py
Heavily modified tand streamlined o use the simplified difflib2
"""

from __future__ import absolute_import

import unittest
import sys

from licensedcode.difflib2 import get_matched_seqs
from licensedcode.difflib2 import Match
from licensedcode.difflib2 import SequenceMatcher as SM


class TestSequenceMatcher(unittest.TestCase):
    def test_match_with_one_insert(self):
        sm = SM('a' + 'b' * 100)
        mb = sm.match('b' * 100)
        assert [Match(qstart=0, istart=1, size=100)] == mb

    def test_match_with_one_delete(self):
        sm = SM('a' * 40 + 'b' * 40)
        a = 'a' * 40 + 'c' + 'b' * 40
        assert [Match(qstart=0, istart=0, size=40), Match(qstart=41, istart=40, size=40)] == sm.match(a)

    def test_match_empty_lists(self):
        sm = SM([])
        assert [] == sm.match([])


    def test_match_with_defaults_seqa(self):
        sm = SM('b')
        assert [] == sm.match()

    def test_match_with_defaults_seqb(self):
        sm = SM([])
        assert [] == sm.match('a')

    def test_match_repeated(self):
        s = SM("abcd")
        _first = s.match("abxcd")
        second = s.match("abxcd")
        assert 2 == second[0].size
        assert 2 == second[1].size

    def test_match_does_not_exceed_recursion_limit(self):
        # Check if the problem described in patch #1413711 exists.
        limit = sys.getrecursionlimit()
        old = [(i % 2 and "K:%d" or "V:A:%d") % i for i in range(limit * 2)]
        new = [(i % 2 and "K:%d" or "V:B:%d") % i for i in range(limit * 2)]
        sm = SM(new)
        result = sm.match(old)
        assert limit == len(result)

    def test_match_with_tab(self):
        # Check fix for bug #1488943
        sm = SM("\t\tI am a bug")
        result = sm.match("\tI am a buggy")
        assert [Match(qstart=0, istart=1, size=11)] == result

patch914575_from1 = """
   1. Beautiful is beTTer than ugly.
   2. Explicit is better than implicit.
   3. Simple is better than complex.
   4. Complex is better than complicated.
"""

patch914575_to1 = """
   1. Beautiful is better than ugly.
   3.   Simple is better than complex.
   4. Complicated is better than complex.
   5. Flat is better than nested.
"""

expected1 = '''
   1. Beautiful is be<gap>er than ugly.
   <gap>. <gap> <gap> Simple is better than complex.
   4. Compl<gap>e<gap> is better than compl<gap>i<gap>a<gap>ted.
123
123
123
123
123
123
123
123
123
123
''' * 3

patch914575_from2 = """
\t\tLine 1: preceeded by from:[tt] to:[ssss]
  \t\tLine 2: preceeded by from:[sstt] to:[sssst]
  \t \tLine 3: preceeded by from:[sstst] to:[ssssss]
Line 4:  \thas from:[sst] to:[sss] after :
Line 5: has from:[t] to:[ss] at end\t
"""

patch914575_to2 = """
    Line 1: preceeded by from:[tt] to:[ssss]
    \tLine 2: preceeded by from:[sstt] to:[sssst]
      Line 3: preceeded by from:[sstst] to:[ssssss]
Line 4:   has from:[sst] to:[sss] after :
Line 5: has from:[t] to:[ss] at end
"""

expected2 = '''
<gap>Line 1: preceeded by from:[tt] to:[ssss]
  <gap>\tLine 2: preceeded by from:[sstt] to:[sssst]
  <gap> <gap>Line 3: preceeded by from:[sstst] to:[ssssss]
Line 4:  <gap>has from:[sst] to:[sss] after :
Line 5: has from:[t] to:[ss] at end<gap>
'''

patch914575_from3 = """line 0
1234567890123456789012345689012345
line 1
line 2
line 3
line 4   changed
line 5   changed
line 6   changed
line 7
line 8  subtracted
line 9
1234567890123456789012345689012345
short line
just fits in!!
just fits in two lines yup!!
the end"""

patch914575_to3 = """line 0
1234567890123456789012345689012345
line 1
line 2    added
line 3
line 4   chanGEd
line 5a  chanGed
line 6a  changEd
line 7
line 8
line 9
1234567890
another long line that needs to be wrapped
just fitS in!!
just fits in two lineS yup!!
the end"""

expected3 = '''line 0
1234567890123456789012345689012345
line 1
line 2<gap>
line 3
line 4   chan<gap>d
line 5<gap>  chan<gap>ed
line 6<gap>  chang<gap>d
line 7
line 8<gap>
line 9
1234567890<gap>
<gap>h<gap>o<gap> line<gap>
just fit<gap> in!!
just fits in two line<gap> yup!!
the end'''


class TestSFpatches(unittest.TestCase):

    def test_match_html_diff1(self):
        # Check SF patch 914575 for generating HTML differences
        # updated to use a plain match
        a = ((patch914575_from1 + '123\n' * 10) * 3)
        b = (patch914575_to1 + '123\n' * 10) * 3
        ma, mb = get_matched_seqs(a, b)
        assert ma == mb
        assert expected1 == '<gap>'.join(ma)

        a = '456\n' * 10 + a
        b = '456\n' * 10 + b
        ma, mb = get_matched_seqs(a, b)
        assert ma == mb
        expected = '456\n' * 10 + expected1
        assert expected == '<gap>'.join(ma)

    def test_match_html_diff2(self):
        ma, mb = get_matched_seqs(patch914575_from2, patch914575_to2)
        assert ma == mb
        assert expected2 == '<gap>'.join(ma)

    def test_match_html_diff3(self):
        ma, mb = get_matched_seqs(patch914575_from3, patch914575_to3)
        assert ma == mb
        assert expected3 == '<gap>'.join(ma)
