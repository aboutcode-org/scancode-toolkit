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

import os
import sys


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
    # 1. collect all the SPDX license ids past and current (see
    # etc/script sync script for basics)
    # 2. collect also all current license keys
    # 3. add a few extra entries to the tokens dict to make sure they are never skipped: NONE, NOASSERTION, LicenseRef-*

    # create cross ref from SPDX to ScanCode licenses
    pass


def get_spdx_license_identifier(line_tokenids):
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

def lid_tokens(idx):
    """
    Return a tuple of the three token ids for SPDX, License and
    Identifier from an index idx.
    """
    idct = idx.dictionary
    return idct['spdx'], idct['license'], idct['identifier']


def spdx_id_match(idx, query_run):

    """
    Return a list of SPDX LicenseMatches by matching the `query_run`
    against the `idx` index.
    """
    if TRACE: logger_debug(' #spdx_id_match: start ... ')

    matches = []

    # iterate over tokenids line
    # OR .....
    # use a regex over query text lines instead to get the expression text

    # then
    #  check if possible spdx lid for a line and get get spdx lid text

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
