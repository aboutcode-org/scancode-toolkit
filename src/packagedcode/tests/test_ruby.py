# -*- coding: utf-8 -*-
"""
    Basic RubyLexer Test
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2006-2014 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import unittest

from pygments.token import Operator, Number, Text
from pygments.lexers import RubyLexer


class RubyTest(unittest.TestCase):

    def setUp(self):
        self.lexer = RubyLexer()

    def testRangeSyntax1(self):
        fragment = u'1..3\n'
        tokens = [
            (Number.Integer, u'1'),
            (Operator, u'..'),
            (Number.Integer, u'3'),
            (Text, u'\n'),
        ]
        self.assertEqual(tokens, list(self.lexer.get_tokens(fragment)))

    def testRangeSyntax2(self):
        fragment = u'1...3\n'
        tokens = [
            (Number.Integer, u'1'),
            (Operator, u'...'),
            (Number.Integer, u'3'),
            (Text, u'\n'),
        ]
        self.assertEqual(tokens, list(self.lexer.get_tokens(fragment)))

    def testRangeSyntax3(self):
        fragment = u'1 .. 3\n'
        tokens = [
            (Number.Integer, u'1'),
            (Text, u' '),
            (Operator, u'..'),
            (Text, u' '),
            (Number.Integer, u'3'),
            (Text, u'\n'),
        ]
        self.assertEqual(tokens, list(self.lexer.get_tokens(fragment)))

