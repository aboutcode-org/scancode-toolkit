#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals

import logging
import os
import sys

from commoncode.fileutils import copyfile
from commoncode.fileutils import get_temp_dir
from licensedcode.match_spdx_lid import MATCH_SPDX_ID
from plugincode.post_scan import post_scan_impl
from plugincode.post_scan import PostScanPlugin
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP

TRACE = False

logger = logging.getLogger(__name__)


def logger_debug(*args):
    pass


if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

"""
A post-scan plugin to remove detected license boilerplate and replace this with
SPDX license identifiers.
"""


@post_scan_impl
class SpdxLicenseIdentifierCreator(PostScanPlugin):
    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!WARNING: THIS PLUGIN DOES MODIFY THE SCANNED CODE!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    Remove license boilerplate text from scanned source code files and replace
    it with a SPDX-License-Identifer only if this is an exact 100% match to a
    single license rule in a single block of continuous text and if the match is
    for official SPDX license ids.

    This option has no effect unless all these other scan options are requested:
     `--license --info --diag --license-text`
    """

    sort_order = 9

    options = [
        CommandLineOption(('--espedexify',),
            is_flag=True, default=False,
            requires=['license', 'license-text', 'license-diag', 'info'],
            help='Remove license boilerplate text from scanned source code '
                 'files and replace it with a SPDX-License-Identifier comment '
                 'line.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, espedexify, license, license_text, license_diag, info, **kwargs):  # NOQA
        return espedexify and license and license_text and license_diag and info

    def process_codebase(self, codebase, **kwargs):
        # Processing sketch:
        # Skip non-files, non code files and files without detected licenses
        # skip files with a detected licenses that does not meet criteria
        # build SPDX license expression
        # strip license from scanned file and replace with SPDX license id
        for resource in codebase.walk():

            location = resource.location

            if TRACE:
                logger_debug('Processing file:', location)

            if not resource.is_file or not resource.licenses:
                if TRACE: logger_debug('Skipping directory or special file')
                continue

            if not os.path.exists(location):
                if TRACE: logger_debug('Skipping non-existing file')
                continue

            if not resource.is_source:
                if TRACE: logger_debug('Skipping non-source file')
                continue

            if not resource.licenses:
                if TRACE: logger_debug('Skipping file without license')
                continue

            licenses = resource.licenses

            has_spdx_lid = any(lic['matched_rule']['matcher'] == MATCH_SPDX_ID for lic in licenses)
            if has_spdx_lid:
                if TRACE: logger_debug('Skipping file with SPDX License identifier already there')
                continue

            matched_line_blocks = set((lic['start_line'], lic['end_line'],) for lic in licenses)
            if len(matched_line_blocks) != 1:
                if TRACE: logger_debug('Skipping file with more than one detected license text block')
                continue

            matched_rules = set(lic['matched_rule']['identifier'] for lic in licenses)
            if len(matched_rules) != 1:
                if TRACE: logger_debug('Skipping file with more than one detected license rule')
                continue

            is_official_spdx = all(lic['spdx_license_key'] for lic in licenses)
            if not is_official_spdx:
                if TRACE: logger_debug('Skipping file matched to non-official SPDX license ids')
                continue

            # from now on, we may have multiple records, but we have only
            # one matched rule
            base_match = licenses[0]
            matched_rule = base_match['matched_rule']
            start_line = base_match['start_line']
            end_line = base_match['end_line']

            # TODO: this is too strict may be: skip if not 100% score and coverage
            if base_match['score'] != 100 or matched_rule['match_coverage'] != 100:
                if TRACE: logger_debug('Skipping file with not 100% score and coverage')
                continue

            removed = remove_license_text(location, start_line, end_line)
            if TRACE: logger_debug('SUCCESS: Removed license text:\n', removed)
            spdx_id = build_spdx_id(licenses)

            # TODO: get matched text to infer comment style
            matched_text = None
            comment_style = get_comment_makers(location, start_line, end_line, matched_text)
            added = add_spdx_id(location, spdx_id, start_line, comment_style)

            if TRACE: logger_debug('SUCCESS: Added SPDX license id:\n', added)


def build_spdx_id(licenses):
    """
    Return a SPDX-License-Identifier string build from a list of
    license matches.
    """
    keys = [lic['spdx_license_key'] for lic in licenses]

    base_match = licenses[0]
    rule = base_match['matched_rule']
    choice = rule['license_choice']
    operator = ' OR ' if choice else ' AND '

    expression = operator.join(keys)

    multi = len(keys) > 1
    if multi:
        expression = '({})'.format(expression)
    return 'SPDX-License-Identifier: {}'.format(expression)


def get_comment_makers(location, start_line, end_line, matched_text):
    """
    Return a tuple of comment marker strings detected in the file at
    `location` as the (start comment marker, end comment marker). The
    end marker may be an empty string. Return None if the match is not
    in a comment (such as in a literal).
    """
    # TODO: implement me
    return '//', ''


def remove_license_text(location, start_line, end_line):
    """
    Remove the matched license text from `start_line` to `end_line`
    inclusive from the text file at `location`.
    Return the removed text as a string.
    NOTE: `start_line` and `end_line` are 1-based and not zero-based.
    WARNING: this modifies the file.
    """
    # modifications are saved in a temp file and copied back at the end
    tmp_dir = get_temp_dir(prefix='spdx_id')
    new_file = os.path.join(tmp_dir, 'new_file')

    # FIXME: consider the casse where this is not the whole that was
    # matched and only part of the licene should be removed
    removed = ''
    with open(new_file, 'wb') as outputf:
        with open(location, 'rb') as inputf:
            for ln, line in enumerate(inputf, start=1):
                if ln >= start_line and ln <= end_line:
                    removed += line
                    continue

                outputf.write(line)
    copyfile(new_file, location)
    return removed


def add_spdx_id(location, spdx_id, start_line, comment_style):
    """
    Add the spdx_id SPDX-License-Identifier string to the file at
    `location` at `start_line` using the `comment_style` tuple of
    start and end comment markers.
    Return the added text line as a string.
    NOTE: `start_line` is 1-based and not zero-based.
    WARNING: this modifies the file.
    """
    startc, endc = comment_style
    identifier = '{startc} {spdx_id} {endc}'.format(**locals()).strip()

    # modifications are saved in a temp file and copied back at the end
    tmp_dir = get_temp_dir(prefix='spdx_id')
    new_file = os.path.join(tmp_dir, 'new_file')

    with open(new_file, 'wb') as outputf:
        with open(location, 'rb') as inputf:
            for ln, line in enumerate(inputf, start=1):
                if ln == start_line:
                    outputf.write(identifier)
                outputf.write(line)
    copyfile(new_file, location)
    return identifier
