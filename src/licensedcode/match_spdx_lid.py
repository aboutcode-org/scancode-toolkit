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
import sys

import attr
from boolean.boolean import PARSE_ERRORS
from license_expression import ExpressionError
from license_expression import ParseError
from license_expression import Licensing
from license_expression import LicenseSymbolLike


from licensedcode.tokenize import matched_query_text_tokenizer

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


def build_index():
    """
    Return index data structures needed for SPDX-License-Identifier matching.
    """
    # 1. collect all the SPDX license ids past and current (see etc/script sync script for basics)
    # 2. collect also all current license keys
    # 3. add a known extra entries: NONE, NOASSERTION, LicenseRef-*
    # build symbols with aliases for license expression parsing
    # create cross ref from SPDX to ScanCode licenses
    pass


def get_license_exprfession(line_tokens):
    """
    Return a possible license expression string given a sequence of
    token ids for a single line of tokens, or None.

    The string is from an original query text line but does not
    contain the SPDX-License-Identifier part.

    For example with "// SPDX-License-Identifier: GPL-2.0 OR MIT"
    then this function will return: "GPL-2.0 OR MIT".
    """
    pass


MATCH_SPDX_ID = '4-spdx-id'


def spdx_id_match(idx, spdx_lines):

    """
    Return a list of SPDX LicenseMatches by matching the `spdx_lines`
    against the `idx` index.
    """
    if TRACE: logger_debug(' #spdx_id_match: start ... ')

    matches = []

    for tokens in spdx_lines:
        tokens = [tok for tok in tokens if not tok.is_marker]

        spdx_lid_tokens = []
        expression_tokens = []
        started = False
        for token in tokens:
            if not started:
                tvl = token.value.lower()
                if tvl not in ('spdx', 'license', 'identifier',):
                    continue
                else:
                    spdx_lid_tokens.append(token)
                    if tvl == 'identifier':
                        started = True
            else:
                expression_tokens.append(token)
        pass
        # 1. clean Tokens stream to discard non-expression bits
        # 2. build proper symbols
        # 3. lookup symbols in index, not unkown/unmatched symbols
        # 4. parse expression
        # 5. build match from parsed expression, using positions from token stream

        # then
        #  try to parse expression and match back to SPDX licenses
        #   with license_expresssion (without or with a backup license list)
        #   as plain space or comma separated list (e.g. UBoot)

        #  lookup SPDX license ids cross refs or check ScanCode ids
        #  or fall back on detecting a license for each parts

        #  add match recomputing positions, lengths, etc

    if TRACE and matches:
        logger_debug(' ##spdx_id_match: matches found#', matches)
        map(print, matches)

    return matches


@attr.s(slots=True)
class SpdxToken(object):
    """
    Used to represent a token in collected matched texts and SPDX identifiers.
    """
    # text value for this token.
    value = attr.ib()
    # line number, one-based
    line_num = attr.ib()
    # absolute start and end position for known tokens, zero-based. -1 for unknown tokens
    start_pos = attr.ib(default=-1)
    end_pos = attr.ib(default=-1)

    # False if this is punctuation
    is_text = attr.ib(default=False)
    # True if this is a known token
    is_known = attr.ib(default=False)

    # True if this is some SPDX identifier marker
    is_marker = attr.ib(default=False)


def collect_spdx_tokens(line, line_num, start_pos_in_line, dic_getter, max_tokens=100):
    """
    Return a list of SPDX license identifier Tokens with pos (starting at
    start_pos_in_line) and line number given a line, its number and a dictionary
    getter `dic_getter`. Return only up to max_tokens tokens.
    """
    toks = spdx_tokens(line, line_num, start_pos_in_line, dic_getter)
    toks = merge_tokens(toks)
    toks = clean_tokens(toks)
    toks = strip_tokens(toks)
    return list(toks)[: max_tokens]


def spdx_tokens(line, line_num, start_pos_in_line, dic_getter):
    """
    Yield SPDX license identifier Tokens with pos (starting at
    start_pos_in_line) and line number given a line, its number and a dictionary
    getter `dic_getter`.
    """
    start_pos = start_pos_in_line - 1
    for is_text, token in matched_query_text_tokenizer(line):
        token_lower = token.lower()
        is_known = is_text and dic_getter(token_lower) is not None
        if is_known:
            start_pos += 1

        # remove some leading and trailing punct that would not be part of the
        # expressions
        token = token.strip(':=#/;{}*&%$@"[]\'?*<>')
        if token:
            tok = SpdxToken(value=token, line_num=line_num, is_text=is_text, is_known=is_known)
            if is_known:
                tok.start_pos = start_pos
                tok.end_pos = start_pos
            yield tok


def merge_tokens(tokens):
    """
    Return a modified sequence of SpdxToken merging contiguous tokens.
    """

    def is_text(t):
        return t.is_text or t.value in ('.', '-', '+')

    def is_spdx_id(t):
        return t.value.lower() in ('spdx', 'license', 'identifier')

    tokens = list(tokens)
    if TRACE: logger_debug('merge:')

    i = 0
    while i < len(tokens) - 1:
        j = i + 1
        while j < len(tokens):
            cur = tokens[i]
            nxt = tokens[j]
            if TRACE:
                logger_debug('curr:', cur)
                logger_debug('next:', nxt)

            if j - i > 1:
                if TRACE: logger_debug('  break1')
                break

            if not (is_text(cur) and is_text(nxt)):
                if TRACE: logger_debug('  break2')
                break

            if not (cur.is_known and nxt.is_known):
                start_pos = end_pos = -1
                is_known = False
            elif cur.is_known and nxt.is_known:
                start_pos = cur.start_pos
                end_pos = nxt.end_pos
                is_known = True
            elif cur.is_known:
                start_pos = nxt.start_pos
                end_pos = nxt.end_pos
                is_known = True
            elif nxt.is_known:
                start_pos = nxt.start_pos
                end_pos = nxt.end_pos
                is_known = True

            cur.value = cur.value + nxt.value
            cur.line_num = nxt.line_num
            cur.start_pos = start_pos
            cur.end_pos = end_pos
            cur.is_text = True
            cur.is_known = is_known
            if TRACE: logger_debug('  new:', cur)

            del tokens[j]

            if cur.value.lower() == 'spdx-license-identifier':
                cur.is_marker = True
                if TRACE: logger_debug('  break is_spdx:', cur)
                break

            logger_debug()
        i += 1
        logger_debug()

    return tokens


def strip_tokens(tokens):
    """
    Yield non-empty, stripped SpdxToken from an iterable of tokens.
    """
    for token in tokens:
        token.value = token.value.strip()
        if token.value:
            yield token


def clean_tokens(tokens):
    """
    Yield cleaned SpdxToken from an iterable of tokens.
    """
    started = False
    for token in tokens:
        if not started:
            if token.is_marker:
                started = True
            else:
                continue
        yield token


def build_licensing(licenses=None):
    """
    Returns a Licensing from `licenses`: either a License QuerySet or a
    pre-built Licensing object (which is returned as-is).
    """
    if isinstance(licenses, Licensing):
        return licenses
    return Licensing(licenses)


def parse_expression(expression, licenses=None, validate_known=True, validate_strict=False):
    """
    Returns a parsed expression object given an expression string.
    Raise Exceptions on parsing errors

    Check and parse the expression license symbols against an optional
    `licenses` Licensing object.

    If `validate_known` is True, raise an Exception if a license
    symbol is unknown. Also include in exception message information
    about the available licenses.

    If `validate_strict` is True, raise am Exception if license
    symbol in a "WITH" exception expression is invalid e.g. in "a WITH
    b" either: "a" is an exception or "b" is not an exception.
    """
    licensing = build_licensing(licenses)
    return licensing.parse(expression, validate=validate_known, strict=validate_strict)


def get_license_objects(expression, licenses=None):
    """
    Returns a list of unique License instances from an expression string.
    Raise Exceptions on parsing errors

    Check and parse the expression license symbols against an optional
    `licenses` Licensing object.

    The expression is assumed to:
     - be composed only from license keys (and not from license names)
     - contain ONLY known license keys

    Furthermore, the validity of "WITH" expression is not checked
    (e.g. `validate_strict` is not used when parsing then expression).
    """
    licensing = build_licensing(licenses)
    parsed = licensing.parse(expression, validate=False, strict=False)
    symbols = licensing.license_symbols(parsed, unique=True, decompose=True)
    return [symbol.wrapped for symbol in symbols if isinstance(symbol, LicenseSymbolLike)]


def normalize_and_validate_expression(expression, licenses=None, validate_known=True,
                                      validate_strict=False, include_available=False):
    """
    Returns a normalized and validated license expression.
    Raise Django ValidationErrors exception on errors.

    If `validate_known` is True and `include_available` is True, the
    exception message will contain extra information listing available
    licenses when the expression uses an unknown license.

    See `parse_expression` for other arguments.
    """
    include_available = validate_known and include_available
    licensing = build_licensing(licenses)

    try:
        parsed = parse_expression(expression, licensing, validate_known, validate_strict)

    except ExpressionError as ee:
        msg = force_text(ee)
        if include_available:
            msg += available_licenses_message(licensing)
        raise ValidationError(mark_safe(msg), code='invalid')

    except ParseError as pe:
        msg = PARSE_ERRORS[pe.error_code]
        if pe.token_string:
            msg += ': ' + pe.token_string
        if include_available:
            msg += available_licenses_message(licensing)
        raise ValidationError(mark_safe(msg), code='invalid')

    except (ValueError, TypeError) as ve:
        msg = 'Invalid reference licenses data.\n' + force_text(ve)
        raise ValidationError(mark_safe(msg), code='invalid')

    except Exception as e:
        msg = 'Invalid license expression.\n' + force_text(e)
        raise ValidationError(mark_safe(msg), code='invalid')

    # NOTE: we test for None because an expression cannot be resolved to
    # a boolean and a plain "if parsed" would attempt to resolve the
    # expression to a boolean.
    if parsed is not None:
        return parsed.render(template='{symbol.key}')

