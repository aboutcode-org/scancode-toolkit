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

import re

from plugincode.output_filter import OutputFilterPlugin
from plugincode.output_filter import output_filter_impl
from scancode import CommandLineOption
from scancode import OUTPUT_FILTER_GROUP


@output_filter_impl
class IgnoreCopyrights(OutputFilterPlugin):
    """
    Filter findings that match given copyright holder or author patterns.
    Has no effect unless the --copyright scan is requested.
    """

    options = [
        CommandLineOption(('--ignore-copyright-holder',),
               multiple=True,
               metavar='<pattern>',
               requires=['copyright'],
               help='Ignore findings with a copyright holder matching <pattern>. '
               'Note that this will ignore a file even if it has other scanned '
               'data such as a license or errors.',
               help_group=OUTPUT_FILTER_GROUP),
        CommandLineOption(
            ('--ignore-author',),
            multiple=True,
            metavar='<pattern>',
            requires=['copyright'],
            help='Ignore findings with an author matching <pattern>. '
               'Note that this will ignore a file even if it has other scanned '
               'data such as a license or errors.',
            help_group=OUTPUT_FILTER_GROUP)
    ]

    def is_enabled(self, copyright, ignore_copyright_holder, ignore_author, **kwargs):  # NOQA
        return copyright and bool(ignore_copyright_holder or ignore_author)

    def process_codebase(self, codebase, ignore_copyright_holder, ignore_author, **kwargs):
        h_regex = [re.compile(r) for r in ignore_copyright_holder]
        a_regex = [re.compile(r) for r in ignore_author]

        for resource in codebase.walk():

            if self._matches(resource, h_regex, 'holders') or self._matches(resource, a_regex, 'authors'):

                resource.is_filtered = True
                codebase.save_resource(resource)

    def _matches(self, resource, patterns, attr):
        identities = self._extract_identities(resource, attr)

        for i in identities:
            if any(p.search(i) for p in patterns):
                return True

        return False

    def _extract_identities(self, resource, attr):
        identities = set()

        for copyright in resource.copyrights:  # NOQA
            identities = identities.union(set(copyright.get(attr, [])))

        return identities
