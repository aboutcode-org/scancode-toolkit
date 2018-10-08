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

from functools import partial

import attr

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode import CommandLineOption
from scancode import OTHER_SCAN_GROUP
from scancode import SCAN_OPTIONS_GROUP


@scan_impl
class EmailScanner(ScanPlugin):
    """
    Scan a Resource for emails.
    """
    resource_attributes = dict(emails=attr.ib(default=attr.Factory(list)))

    sort_order = 8

    options = [
        CommandLineOption(('-e', '--email',),
            is_flag=True, default=False,
            help='Scan <input> for emails.',
            help_group=OTHER_SCAN_GROUP),

        CommandLineOption(('--max-email',),
            type=int, default=50,
            metavar='INT',
            show_default=True,
            requires=['email'],
            help='Report only up to INT emails found in a file. Use 0 for no limit.',
            help_group=SCAN_OPTIONS_GROUP),
    ]

    def is_enabled(self, email, **kwargs):
        return email

    def get_scanner(self, max_email=50, **kwargs):
        from scancode.api import get_emails
        return partial(get_emails, threshold=max_email)
