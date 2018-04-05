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

from boolean.boolean import PARSE_ERRORS
from license_expression import ExpressionError
from license_expression import ParseError
from license_expression import Licensing

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


def build_index(licenses):
    """
    Return index data structures needed for SPDX-License-Identifier matching:
    - SPDX Symbols
    - ScanCode license key Symbols
    - other useful symbols
    - a proper Licensing built on these symbols
    """
    symbols = []
    # 1. collect all the SPDX license ids past and current (see etc/script sync script for basics)
    # 2. collect also all current license keys
    # 3. add a known extra entries: NONE, NOASSERTION, LicenseRef-*
    # build symbols with aliases for license expression parsing
    # create cross ref from SPDX to ScanCode licenses
    for lkey, lic in licenses.items():
        pass

    return Licensing()


def get_license_expression(line_tokens):
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
    Return a list of SPDX LicenseMatches by matching the `spdx_lines` against
    the `idx` index.

    `spdx_lines` is a list of tuples of:
        (original line text, line number, abs token pos start, end)

    Note: we only match single-line SPDX-License-Identifier expressions for now.
    """
    if TRACE: logger_debug(' #spdx_id_match: start ... ')

    matches = []

    # TODO: get Licensing from index
    licensing = idx.get_licensing()

    for line_text, line_num, abs_pos_start, abs_pos_end in spdx_lines:

        expression_tokens = []
        expression = get_expression(line_text, licensing)
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

        #  add match, recomputing positions, lengths, etc

    if TRACE and matches:
        logger_debug(' ##spdx_id_match: matches found#', matches)
        map(print, matches)

    return matches


def get_expression(line_text, licensing):
    """
    Return an Expression object by parsing the `line_text` string using
    the `licensing` reference Licensing.
    """
    line = clean_line(line_text)
    line = strip_spdx_lid(line)



class InvalidExpressionError(Exception):
    pass


def parse_expression(expression, licensing, validate_known=False, validate_strict=False):
    """
    Returns a parsed and normalized expression object given an expression
    string. Raise Exceptions on parsing errors.

    Check and parse the expression license symbols against an optional
    `licensing` Licensing object.

    If `validate_known` is True, raise an Exception if a license symbol is
    unknown e.g. it is not part of the symbols avialbale in `licensing`.

    If `validate_strict` is True, raise an Exception if license symbol in a
    "WITH" exception expression is invalid e.g. in "a WITH b" either: "a" is an
    exception or "b" is not an exception.
    """

    try:
        return licensing.parse(expression, validate=validate_known, strict=validate_strict)
    except ExpressionError as ee:
        msg = str(ee)
        raise InvalidExpressionError(msg)

    except ParseError as pe:
        msg = PARSE_ERRORS[pe.error_code]
        if pe.token_string:
            msg += ': ' + pe.token_string
        raise InvalidExpressionError(msg)

    except (ValueError, TypeError) as ve:
        msg = 'Invalid reference licenses data.\n' + str(ve)
        raise InvalidExpressionError(msg)

    except Exception as e:
        msg = 'Invalid license expression.\n' + str(e)
        raise InvalidExpressionError(msg)


def is_spdx_lid(tokens):
    return tokens == ['spdx', 'license', 'identifier', ]


def clean_line(line):
    """
    Return a text line for an SPDX license identifier cleaned from certain
    leading and trailing punctuations and normalized for spaces.
    """
    line = ' '.join(line.split())
    leading_punctuation = """!"#$%&'*,-./:;<=>?@[\]^_`{|}~()+"""
    trailing_punctuation = """!"#$%&'*,-./:;<=>?@[\]^_`{|}~("""
    line = line.lstrip(leading_punctuation)
    line = line.rstrip(trailing_punctuation)
    return line.strip()


stripper = re.compile('spdx(\-|\s)+license(\-|\s)+identifier\s*:?\s*', re.IGNORECASE).sub


def strip_spdx_lid(line):
    """
    Return a text line for an SPDX license identifier line strip from the
    identifier.
    """
    return stripper('', line)

