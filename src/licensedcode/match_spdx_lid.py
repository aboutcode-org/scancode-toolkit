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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import sys

from license_expression import Licensing
from license_expression import LicenseWithExceptionSymbol
from license_expression import splitter as simple_tokenizer
from license_expression import Keyword
from license_expression import LicenseSymbol

from licensedcode.match import LicenseMatch
from licensedcode.spans import Span

"""
Matching strategy for "SPDX-License-Identfier:" expression lines.
"""

# Tracing flags
TRACE = False


def logger_debug(*args):
    pass


if TRACE or os.environ.get('SCANCODE_DEBUG_LICENSE'):
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

MATCH_SPDX_ID = '4-spdx-id'


def spdx_id_match(idx, spdx_lines):
    """
    Return a list of SPDX LicenseMatches by matching the `spdx_lines` against
    the `idx` index.

    `spdx_lines` is a list of tuples of:
        (original line text, line number, abs token pos start, end)

    Note: we only match single-line SPDX-License-Identifier expressions for now.
    """
    from licensedcode.cache import get_spdx_symbols
    from licensedcode.cache import get_unknown_spdx_symbol

    if TRACE: logger_debug(' #spdx_id_match: start ... ')

    licensing = Licensing()
    symbols_by_spdx = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()
    matches = []

    for line_text, line_num, abs_pos_start, abs_pos_end in spdx_lines:

        expression = get_expression(line_text, licensing, symbols_by_spdx, unknown_symbol)

        if TRACE:
            logger_debug(
                ' ##spdx_id_match: expression:',
                repr(expression.render()) if expression is not None else None,
                'line_text:', line_text, 'line_num:', line_num,
                'abs_pos_start:', abs_pos_start, 'abs_pos_end:', abs_pos_end)

        # how many known or unknown-spdx symbols do we have?
        known_syms = 0
        unknown_syms = 0
        for sym in licensing.license_symbols(expression, unique=False, decompose=True):
            if sym == unknown_symbol:
                unknown_syms += 1
            else:
                known_syms += 1

        # build synthetic rule and match from parsed expression
        # rule = TBD
        # qbegin = TBD
        # qspan = Span() # TBD
        # ispan = Span() # TBD
        # hispan = Span() # TBD
        # match = LicenseMatch(rule, qspan, ispan, hispan, qbegin, matcher=MATCH_SPDX_ID, query=query)
        # matches.append(match)

    if TRACE and matches:
        logger_debug(' ##spdx_id_match: matches found#', matches)
        map(print, matches)

    return matches


def get_expression(line_text, licensing, spdx_symbols, unknown_symbol):
    """
    Return an Expression object by parsing the `line_text` string using
    the `licensing` reference Licensing.

    Note that an expression is ALWAYS returned: if the parsing fails or some
    other error happens somehow, this function returns instead a bare
    expression made of only "unknown-spdx" symbol.
    """
    expression = None
    try:
        expression = _parse_expression(line_text, licensing, spdx_symbols, unknown_symbol)
    except:
        try:
            # try to parse again using a lenient recovering parsing process
            # such as for plain space or comma-separated list of licenses (e.g. UBoot)
            expression = _reparse_invalid_expression(line_text, licensing, spdx_symbols, unknown_symbol)
        except:
            pass

    if expression is None:
        expression = unknown_symbol
    return expression


def _parse_expression(line_text, licensing, spdx_symbols, unknown_symbol):
    """
    Return an Expression object by parsing the `line_text` string using the
    `licensing` reference Licensing. Return None or raise an exception on
    errors.
    """
    line = clean_line(line_text)
    line = strip_spdx_lid(line)
    if not line_text:
        return

    expression = licensing.parse(line)
    if TRACE:
        logger_debug('  ##_parse_expression: parsed:',
                     repr(expression.render()) if expression is not None else None)

    if expression is None:
        return

    # collect known symbols and build substitution table: replace known symbols
    # with a symbol wrapping a known license and unkown symbols with the
    # unknown-spdx symbol
    symbols_table = {}

    def _get_matching_symbol(_symbol):
        return spdx_symbols.get(_symbol.key.lower(), unknown_symbol)

    for symbol in licensing.license_symbols(expression, unique=True, decompose=False):
        if isinstance(symbol, LicenseWithExceptionSymbol):
            # we have two symbols:make a a new symbo, from that
            new_with = LicenseWithExceptionSymbol(
                _get_matching_symbol(symbol.license_symbol),
                _get_matching_symbol(symbol.exception_symbol)
            )
            if TRACE:
                logger_debug('  ##_parse_expression: new_with:', new_with)
            symbols_table[symbol] = new_with
        else:
            symbols_table[symbol] = _get_matching_symbol(symbol)

    if TRACE:
        from pprint import pformat
        logger_debug('  ##_parse_expression: symbols_table:', '\n', pformat(symbols_table))

    symbolized = expression.subs(symbols_table)

    if TRACE:
        logger_debug('  ##_parse_expression: symbolized:', repr(symbolized.render()))

    return symbolized


def _reparse_invalid_expression(line_text, licensing, spdx_symbols, unknown_symbol):
    """
    Return an Expression object by parsing the `line_text` string using the
    `licensing` reference Licensing.
    Make a best attempt at parsing eventually ignoring some of the syntax.
    The `line_text` string is assumed to be an invalid non-parseable expression.

    Any keyword and parens will be ignored.

    Note that an expression is ALWAYS returned: if the parsing fails or some
    other error happens somehow, this function returns instead a bare
    expression made of only "unknown-spdx" symbol.
    """
    line = clean_line(line_text)
    line = strip_spdx_lid(line)
    if not line_text:
        return

    results = simple_tokenizer(line)
    # filter tokens to keep only things with an output
    outputs = [r.output for r in results if r.output]
    # filter tokens to keep only symbols and keywords
    tokens = [o.value for o in outputs if isinstance(o.value, (LicenseSymbol, Keyword))]

    # here we have a mix of keywords and symbols that does not parse correctly
    # it could imbalanced or any kind of other reasons. We ignore any parens or
    # keyword and track if we have keywords or parens
    has_keywords = False
    has_symbols = False
    filtered_tokens = []
    for tok in tokens:
        if isinstance(tok, Keyword):
            has_keywords = True
            continue
        else:
            filtered_tokens.append(tok)
            has_symbols = True

    if not has_symbols:
        return unknown_symbol

    # build and reparse a synthetic expression using a default AND as keyword
    # this expression may noit be a correct repsentation of the invalid
    # original, but it always contains an unknown symbol if that's was a not a
    # simple u-boot style expression
    expression_text = ' and '.join(s.key for s in filtered_tokens)
    expression = _parse_expression(expression_text, licensing, spdx_symbols, unknown_symbol)

    if has_keywords:
        # append an arbitrary unknown-spdx symbol to witness that the expression
        # is invalid
        expression = licensing.AND(expression, unknown_symbol)

    return expression


def clean_line(line):
    """
    Return a text line for an SPDX license identifier cleaned from certain
    leading and trailing punctuations and normalized for spaces.
    """
    line = ' '.join(line.split())
    leading_punctuation_spaces = """!"#$%&'*,-./:;<=>?@[\]^_`{|}~\t\r\n ()+"""
    trailng_punctuation_spaces = """!"#$%&'*,-./:;<=>?@[\]^_`{|}~\t\r\n ("""
    return line.lstrip(leading_punctuation_spaces).rstrip(trailng_punctuation_spaces)


stripper = re.compile('spdx(\-|\s)+license(\-|\s)+identifier\s*:?\s*', re.IGNORECASE).sub


def strip_spdx_lid(line):
    """
    Return a text line for an SPDX license identifier line strip from the
    identifier.
    """
    return stripper('', line)
