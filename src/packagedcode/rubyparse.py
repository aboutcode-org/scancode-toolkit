#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import attr
from pygmars import parse
from pygmars import Token
from pygmars import tree

from packagedcode.rubylex import RubyLexer

"""
Extract package and dependency metadata from gemspec, Gemfile and related Ruby-
based manifests like Podfile and podspec files.
"""

VALIDATE = False or os.environ.get('SCANCODE_DEBUG_RUBYPARSE_VALIDATE', False)

# Tracing flags
TRACE = False or os.environ.get('SCANCODE_DEBUG_RUBYPARSE', False)
if TRACE:
    TRACE = int(TRACE)


# Tracing flags
def logger_debug(*args):
    pass


if TRACE:
    use_print = True
    if use_print:
        prn = print
    else:
        import logging
        import sys
        logger = logging.getLogger(__name__)
        # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        logging.basicConfig(stream=sys.stdout)
        logger.setLevel(logging.DEBUG)
        prn = logger.debug

    def logger_debug(*args):
        return prn(' '.join(isinstance(a, str) and a or repr(a) for a in args))

#
# A simple and minimal pygmars grammar to collect gempsec/podspec data
spec_grammar = '''
HEREDOC: {
    <OPERATOR-HEREDOC>
    <LITERAL-STRING-HEREDOCDELIMITER>
        <TEXT-WHITESPACE>*
        <LITERAL-STRING-HEREDOC>+
    <LITERAL-STRING-HEREDOCDELIMITER>
}

STRING: {
    <LITERAL-STRING-DOUBLE-QUOTE|LITERAL-STRING-SINGLE-QUOTE>
        <LITERAL-STRING-VALUE>
    <LITERAL-STRING-DOUBLE-QUOTE|LITERAL-STRING-SINGLE-QUOTE>
}

STRING: {
    <LITERAL-STRING-COLONSYMBOL>
}

STRING-LIST: {
    (<STRING> <TEXT-WHITESPACE>* <PUNCTUATION-COMMA> <TEXT-WHITESPACE>*)+
    <STRING> <TEXT-WHITESPACE>* <PUNCTUATION-COMMA>?
}

ARRAY: {
    <OPERATOR-OPEN-SQUARE-BRACKET>
    <TEXT-WHITESPACE>*
    <STRING-LIST>
    <TEXT-WHITESPACE>*
    <OPERATOR-CLOSE-SQUARE-BRACKET>
}

NAME: { <NAME> <OPERATOR-DOT> <NAME-ATTRIBUTE-.*> }

NAME: { <NAME-NAME|KEYWORD-ATTRIBUTE.*> }

NAME: { <NAME> <OPERATOR-DOT> <NAME> }

ASSIGNMENT-IN-MAPPING: {
    <TEXT-WHITESPACE>*
    <STRING>
    <TEXT-WHITESPACE>*
    <OPERATOR-ROCKET>
    <TEXT-WHITESPACE>*
    <STRING|NAME>
    <TEXT-WHITESPACE>*
}

ASSIGNMENT-IN-MAPPING-COMMA: {<ASSIGNMENT-IN-MAPPING><PUNCTUATION-COMMA>}

ASSIGNMENT-LIST-IN-MAPPING: { <ASSIGNMENT-IN-MAPPING-COMMA>+ <ASSIGNMENT-IN-MAPPING><PUNCTUATION-COMMA>?}

MAPPING: {
    <OPERATOR-OPEN-CURLY-BRACE>
        <ASSIGNMENT-IN-MAPPING>+
    <OPERATOR-CLOSE-CURLY-BRACE>
}

DEPENDENCY: {
    <NAME-ADDGEMDEPENDENCY-.*>
    <TEXT-WHITESPACE>*
    <STRING-LIST>
}

GEM: {
    <KEYWORD-GEM>
    <TEXT-WHITESPACE>*
    <STRING-LIST|STRING>
}

POD: {
    <KEYWORD-POD>
    <TEXT-WHITESPACE>*
    <STRING-LIST> <ASSIGNMENT-IN-MAPPING-COMMA|ASSIGNMENT-IN-MAPPING>*
}

ASSIGNMENT: {
    <TEXT-WHITESPACE>*
    <OPERATOR-EQUAL>
    <TEXT-WHITESPACE>*
    <STRING|HEREDOC|MAPPING|ARRAY|STRING-LIST>
}

ATTRIBUTE-ASSIGNMENT: {<NAME> <ASSIGNMENT> }
'''

# Single value
#     (label='OPERATOR-OPEN-CURLY-BRACE', value='{')
#     (label='STRING', children=(
#       (label='LITERAL-STRING-DOUBLE-QUOTE', value='"')
#       (label='LITERAL-STRING-VALUE', value='Krunoslav Zaher')
#       (label='LITERAL-STRING-DOUBLE-QUOTE', value='"')
#     ))
#     (label='OPERATOR-ROCKET', value='=>')
#     (label='TEXT-WHITESPACE', value=' ')
#     (label='STRING', children=(
#       (label='LITERAL-STRING-DOUBLE-QUOTE', value='"')
#       (label='LITERAL-STRING-VALUE', value='krunoslav.zaher@gmail.com')
#       (label='LITERAL-STRING-DOUBLE-QUOTE', value='"')
#     ))
#     (label='OPERATOR-CLOSE-CURLY-BRACE', value='}')

# Multi value
#     (label='OPERATOR-OPEN-CURLY-BRACE', value='{')
#     (label='TEXT-WHITESPACE', value=' ')

# (STRING (label='LITERAL-STRING-COLONSYMBOL', value=':git'))
#     (label='TEXT-WHITESPACE', value=' ')
#     (label='OPERATOR-ROCKET', value='=>')
#     (label='TEXT-WHITESPACE', value=' ')

#     (label='STRING', children=(
#       (label='LITERAL-STRING-DOUBLE-QUOTE', value='"')
#       (label='LITERAL-STRING-VALUE', value='https://github.com/RxSwiftCommunity/RxDataSources.git')
#       (label='LITERAL-STRING-DOUBLE-QUOTE', value='"')
#     ))
#     (label='PUNCTUATION-COMMA', value=',')

#     (label='TEXT-WHITESPACE', value=' ')

# (STRING (label='LITERAL-STRING-COLONSYMBOL', value=':tag'))
#     (label='TEXT-WHITESPACE', value=' ')
#     (label='OPERATOR-ROCKET', value='=>')
#     (label='TEXT-WHITESPACE', value=' ')

# (NAME (label='NAME', value='s') (label='OPERATOR-DOT', value='.') (label='NAME-ATTRIBUTE', value='version'))
#     (label='OPERATOR-DOT', value='.')
#     (label='NAME', value='to_s')
#     (label='TEXT-WHITESPACE', value=' ')
#     (label='OPERATOR-CLOSE-CURLY-BRACE', value='}')


def convert_grammar_to_one_rule_per_line(grammar):
    """
    Pygmars expects one rule per line.
    """
    rules = grammar.split('\n\n')
    rules = (' '.join(rule.splitlines(False)) for rule in rules)
    return '\n'.join(rules)


spec_grammar = convert_grammar_to_one_rule_per_line(spec_grammar)


def parse_spec(
    text,
    grammar=spec_grammar,
    loop=2,
    trace=TRACE,
    validate=VALIDATE,
):
    """
    Return a pygmars parse Tree built from the ``text`` of a spec file.
    """
    tokens = get_tokens(text)

    parser = parse.Parser(
        grammar=grammar,
        trace=trace,
        validate=validate,
        loop=loop,
    )

    if TRACE:
        tokens = list(tokens)
        logger_debug(f'parse_spec: parsing tokens #: {len(tokens)}')

    if TRACE:
        logger_debug(f'parse_spec: calling parser.parse')

    parse_tree = parser.parse(tokens)

    if TRACE:
        logger_debug(f'parse_spec: got parse_tree: {parse_tree}')

    return parse_tree


def filter_empty_pygments_tokens(pygtokens):
    return ((tpos, ttype, ttext) for tpos, ttype, ttext in pygtokens if ttext)


def get_tokens(text):
    """
    Return a Tokens list from ``text``.
    """
    lexer = RubyLexer()
    pygtokens = lexer.get_tokens_unprocessed(text)
    pygtokens = filter_empty_pygments_tokens(pygtokens)
    return list(Token.from_pygments_tokens(pygtokens))


if __name__ == '__main__':
    import sys  # NOQA

    test_file = sys.argv[1]
    with open(test_file) as tf:
        text = tf.read()

    # dump tokens
    # for token in get_tokens(text):
    #    print(token)

    # dump tree
    parse_tree = parse_spec(text)
    print(parse_tree.pformat(margin=120, indent=2))

