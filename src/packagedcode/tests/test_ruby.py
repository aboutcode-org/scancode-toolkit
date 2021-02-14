# -*- coding: utf-8 -*-
"""
    Basic RubyLexer Test
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2006-2020 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import pytest

from pygments.token import Name
from pygments.lexers.ruby import RubyLexer


@pytest.fixture(scope='module')
def lexer():
    yield RubyLexer()


@pytest.mark.parametrize(
    'method_name',
    (
        # Bare, un-scoped method names
        'a', 'A', 'z', 'Z', 'は', '\u0080', '\uffff',
        'aは0_', 'はA__9', '\u0080はa0_', '\uffff__99Z',

        # Method names with trailing characters
        'aは!', 'はz?', 'はa=',

        # Scoped method names
        'self.a', 'String.は_', 'example.AZ09_!',

        # Operator overrides
        '+', '+@', '-', '-@', '!', '!@', '~', '~@',
        '*', '**', '/', '%', '&', '^', '`',
        '<=>', '<', '<<', '<=', '>', '>>', '>=',
        '==', '!=', '===', '=~', '!~',
        '[]', '[]=',
    )
)
def test_positive_method_names(lexer, method_name):
    """Validate positive method name parsing."""

    text = 'def ' + method_name
    assert list(lexer.get_tokens(text))[-2] == (Name.Function, method_name.rpartition('.')[2])


@pytest.mark.parametrize('method_name', ('1', '_', '<>', '<<=', '>>=', '&&', '||', '==?', '==!', '===='))
def test_negative_method_names(lexer, method_name):
    """Validate negative method name parsing."""

    text = 'def ' + method_name
    assert list(lexer.get_tokens(text))[-2] != (Name.Function, method_name)
