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

from license_expression import Keyword
from license_expression import LicenseSymbol
from license_expression import LicenseWithExceptionSymbol
from license_expression import Licensing

from licensedcode.match import LicenseMatch
from licensedcode.models import SpdxRule
from licensedcode.spans import Span

"""
Matching strategy for license expressions and "SPDX-License-Identifier:"
expression tags.
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


def spdx_id_match(idx, query_run, text):
    """
    Return one LicenseMatch by matching the `text` as an SPDX license expression
    using the `query_run` positions and `idx` index for support.
    """
    from licensedcode.cache import get_spdx_symbols
    from licensedcode.cache import get_unknown_spdx_symbol

    if TRACE:
        logger_debug('spdx_id_match: start:', 'text:', text, 'query_run:', query_run)

    licensing = Licensing()
    symbols_by_spdx = get_spdx_symbols()
    unknown_symbol = get_unknown_spdx_symbol()

    expression = get_expression(text, licensing, symbols_by_spdx, unknown_symbol)
    expression_str = expression.render()

    if TRACE:
        logger_debug('spdx_id_match: expression:', repr(expression_str))

    # how many known or unknown-spdx symbols occurence do we have?
    known_syms = 0
    unknown_syms = 0
    for sym in licensing.license_symbols(expression, unique=False, decompose=True):
        if sym == unknown_symbol:
            unknown_syms += 1
        else:
            known_syms += 1

    match_len = len(query_run)
    match_start = query_run.start
    matched_tokens = query_run.tokens

    # are we starting with SPDX-License-Identifier or not? if yes: fix start
    cleaned = clean_text(text).lower()
    # FIXME: dnl and rem may not be known tokens hence the pos will be wrong
    if cleaned.startswith(('list', 'dnl', 'rem',)):
        match_start += 1
        match_len -= 1
        matched_tokens = matched_tokens[1:]

    # build synthetic rule
    # TODO: ensure that all the SPDX license keys are known symbols
    rule = SpdxRule(
        license_expression=expression_str,
        # FIXME: for now we are putting the original query text as a
        # rule text: this is likely incorrect when it comes to properly
        # computing the known and unknowns and high and lows for this rule.
        # alternatively we could use the expression string, padded with
        # spdx-license-identifier: this may be wrong too, if the line was
        # not padded originally with this tag
        stored_text=text,
        length=match_len)

    # build match from parsed expression
    # collect match start and end: e.g. the whole text
    qspan = Span(range(match_start, query_run.end + 1))

    # we use the query side to build the ispans
    ispan = Span(range(0, match_len))

    len_legalese = idx.len_legalese
    hispan = Span(p for p, t in enumerate(matched_tokens) if t < len_legalese)

    match = LicenseMatch(
        rule=rule, qspan=qspan, ispan=ispan, hispan=hispan,
        query_run_start=match_start,
        matcher=MATCH_SPDX_ID, query=query_run.query
    )

    if TRACE:
        logger_debug('spdx_id_match: match found:', match)
    return match


def get_expression(text, licensing, spdx_symbols, unknown_symbol):
    """
    Return an Expression object by parsing the `text` string using
    the `licensing` reference Licensing.

    Note that an expression is ALWAYS returned: if the parsing fails or some
    other error happens somehow, this function returns instead a bare
    expression made of only "unknown-spdx" symbol.
    """
    expression = None
    try:
        expression = _parse_expression(text, licensing, spdx_symbols, unknown_symbol)
        if TRACE:
            logger_debug('get_expression:1:', expression)
    except Exception:
        try:
            # try to parse again using a lenient recovering parsing process
            # such as for plain space or comma-separated list of licenses (e.g. UBoot)
            expression = _reparse_invalid_expression(text, licensing, spdx_symbols, unknown_symbol)
            if TRACE:
                logger_debug('get_expression:2:', expression)
        except Exception:
            pass

    if expression is None:
        if TRACE:
            logger_debug('get_expression: EMPTY')
        expression = unknown_symbol
    return expression


# TODO: use me??: this is NOT used at all for now because too complex for a too
# small benefit: only ecos-2.0 has ever been see in the wild in U-Boot
# identifiers
# Some older SPDX ids are deprecated and therefore no longer referenced in
# licenses so we track them here. This maps the old SPDX key to a scancode
# expression.
OLD_SPDX_EXCEPTION_LICENSES_SUBS = None

def get_old_expressions_subs_table(licensing):
    global OLD_SPDX_EXCEPTION_LICENSES_SUBS
    if not OLD_SPDX_EXCEPTION_LICENSES_SUBS:
        EXPRESSSIONS_BY_OLD_SPDX_IDS = {
            'eCos-2.0': 'gpl-2.0+ wITH ecos-exception-2.0',
            'GPL-2.0-with-autoconf-exception': 'gpl-2.0 WITH autoconf-exception-2.0',
            'GPL-2.0-with-bison-exception': 'gpl-2.0 WITH bison-exception-2.2',
            'GPL-2.0-with-classpath-exception': 'gpl-2.0 WITH classpath-exception-2.0',
            'GPL-2.0-with-font-exception': 'gpl-2.0 WITH font-exception-2.0',
            'GPL-2.0-with-GCC-exception': 'gpl-2.0 WITH gcc-linking-exception-2.0',
            'GPL-3.0-with-autoconf-exception': 'gpl-3.0 WITH autoconf-exception-3.0',
            'GPL-3.0-with-GCC-exception': 'gpl-3.0 WITH gcc-exception-3.1',
            'Nunit': 'zlib-acknowledgement',
            'wxWindows': 'lgpl-2.0-plus WITH wxwindows-exception-3.1',
            'StandardML-NJ': ' SMLNJ',
        }

        OLD_SPDX_EXCEPTION_LICENSES_SUBS = {
            licensing.parse(k): licensing.parse(v)
            for k, v in EXPRESSSIONS_BY_OLD_SPDX_IDS.items()
        }

    return OLD_SPDX_EXCEPTION_LICENSES_SUBS


def _parse_expression(text, licensing, spdx_symbols, unknown_symbol):
    """
    Return an Expression object by parsing the `text` string using the
    `licensing` reference Licensing. Return None or raise an exception on
    errors.
    """
    text = prepare_text(text)
    if not text:
        return

    expression = licensing.parse(text, simple=True)

    if expression is None:
        if TRACE: logger_debug(' #_parse_expression: parsed: EMPTY')
        return
    if TRACE:
        logger_debug(' #_parse_expression: parsed:', repr(expression.render()))


    # substitute old SPDX symbols with new ones if any
    old_expressions_subs = get_old_expressions_subs_table(licensing)
    updated = expression.subs(old_expressions_subs)

    if TRACE:
        logger_debug(' #_parse_expression: updated:', repr(updated.render()))

    # collect known symbols and build substitution table: replace known symbols
    # with a symbol wrapping a known license and unkown symbols with the
    # unknown-spdx symbol
    symbols_table = {}

    def _get_matching_symbol(_symbol):
        return spdx_symbols.get(_symbol.key.lower(), unknown_symbol)

    for symbol in licensing.license_symbols(updated, unique=True, decompose=False):
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

    symbolized = updated.subs(symbols_table)

    if TRACE:
        logger_debug('  ##_parse_expression: symbolized:', repr(symbolized.render()))

    return symbolized


def _reparse_invalid_expression(text, licensing, spdx_symbols, unknown_symbol):
    """
    Return an Expression object by parsing the `text` string using the
    `licensing` reference Licensing.
    Make a best attempt at parsing eventually ignoring some of the syntax.
    The `text` string is assumed to be an invalid non-parseable expression.

    Any keyword and parens will be ignored.

    Note that an expression is ALWAYS returned: if the parsing fails or some
    other error happens somehow, this function returns instead a bare
    expression made of only "unknown-spdx" symbol.
    """
    text = prepare_text(text)
    if not text:
        return

    results = licensing.simple_tokenizer(text)
    # filter tokens to keep only symbols and keywords
    tokens = [r.value for r in results if isinstance(r.value, (LicenseSymbol, Keyword))]

    # here we have a mix of keywords and symbols that does not parse correctly
    # this could be because of some imbalance or any kind of other reasons. We ignore any parens or
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

    # Build and reparse a synthetic expression using a default AND as keyword.
    # This expression may not be a correct repsentation of the invalid original,
    # but it always contains an unknown symbol if this is a not a simple uboot-
    # style OR expression.
    joined_as = ' AND '
    if not has_keywords:
        # this is bare list of symbols without parens and keywords, u-boot-
        # style: we assume the OR keyword
        joined_as = ' OR '

    expression_text = joined_as.join(s.key for s in filtered_tokens)
    expression = _parse_expression(expression_text, licensing, spdx_symbols, unknown_symbol)

    # this is more than just a u-boot-style list of license keys
    if has_keywords:
        # ... so we append an arbitrary unknown-spdx symbol to witness that the
        # expression is invalid
        expression = licensing.AND(expression, unknown_symbol)

    return expression


def prepare_text(text):
    """
    Return a text suitable for SPDX license identifier detection stripped from
    leading and trailing punctuations, normalized for spaces and without an
    SPDX-License-Identifier prefix.
    """
    text = clean_text(text)
    text = strip_spdx_lid(text)
    text = clean_text(text)
    return text


def clean_text(text):
    """
    Return a text suitable for SPDX license identifier detection cleaned
    from certain leading and trailing punctuations and normalized for spaces.
    """
    text = ' '.join(text.split())
    punctuation_spaces = "!\"#$%&'*,-./:;<=>?@[\]^_`{|}~\t\r\n "
    # do not remove significant expression punctuations: leading parens at head
    # and closing parens or + at tail.
    leading_punctuation_spaces = punctuation_spaces + ")+"
    trailng_punctuation_spaces = punctuation_spaces + "("
    if 'spdx-license-identifier' in text.lower():
        # a line may have ( before the spdx-license-idenifier lead
        leading_punctuation_spaces += '('
    return text.lstrip(leading_punctuation_spaces).rstrip(trailng_punctuation_spaces)


# note: LIST, DNL REM can be vomment indicators is a comment indicators
stripper = re.compile('''(list|dnl|rem)?[\s'"]*spdx(\-|\s)+license(\-|\s)+identifier\s*:?\s*''', re.IGNORECASE).sub


def strip_spdx_lid(text):
    """
    Return a text striped from the a leading "SPDX license identifier" if any.
    """
    return stripper('', text)
