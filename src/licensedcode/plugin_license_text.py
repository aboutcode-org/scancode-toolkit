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

import attr

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP


# Set to True to enable debug tracing
TRACE = False

if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
else:

    def logger_debug(*args):
        pass


@post_scan_impl
class IsLicenseText(PostScanPlugin):
    """
    Set the "is_license_text" flag to true for at the file level for text files
    that contain mostly (as 90% of their size) license texts or notices.
    Has no effect unless --license, --license-text and --info scan data
    are available.
    """

    resource_attributes = dict(is_license_text=attr.ib(default=False, type=bool, repr=False))

    sort_order = 80

    options = [
        CommandLineOption(('--is-license-text',),
            is_flag=True, default=False,
            required_options=['info', 'license_text'],
            help='Set the "is_license_text" flag to true for files that contain '
                 'mostly license texts and notices (e.g over 90% of the content). [EXPERIMENTAL]',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, is_license_text, **kwargs):
        return is_license_text

    def process_codebase(self, codebase, is_license_text, **kwargs):
        """
        Set the `is_license_text` to True for files taht contain over 90% of
        detected license texts.
        """

        for resource in codebase.walk():
            if not resource.is_text:
                continue
            # keep unique texts/line ranges since we repeat this for each matched licenses
            license_texts = set(
                (lic['matched_text'], lic['start_line'], lic['end_line'],
                 lic.get('matched_rule', {}).get('match_coverage', 0))
                for lic in resource.licenses)
            # use coverage to skew the actual matched length
            license_texts_size = 0
            for txt, _, _, cov in license_texts:
                # these are the meta characters used t mark non matched parts
                txt = txt.replace('[', '').replace(']', '')
                license_texts_size += len(txt) * (cov / 100)
            if TRACE:
                logger_debug(
                    'IsLicenseText: license size:', license_texts_size,
                    'size:', resource.size,
                    'license_texts_size >= (resource.size * 0.9)', license_texts_size >= (resource.size * 0.9),
                    'resource.size * 0.9:', resource.size * 0.9
                )

            if license_texts_size >= (resource.size * 0.9):
                resource.is_license_text = True
                resource.save(codebase)
