#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from functools import partial

import attr

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import SCAN_OPTIONS_GROUP
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from commoncode.cliutils import OTHER_SCAN_GROUP


@scan_impl
class EmailScanner(ScanPlugin):
    """
    Scan a Resource for emails.
    """
    resource_attributes = dict(emails=attr.ib(default=attr.Factory(list)))

    sort_order = 8

    options = [
        PluggableCommandLineOption(('-e', '--email',),
            is_flag=True, default=False,
            help='Scan <input> for emails.',
            help_group=OTHER_SCAN_GROUP),

        PluggableCommandLineOption(('--max-email',),
            type=int, default=50,
            metavar='INT',
            show_default=True,
            required_options=['email'],
            help='Report only up to INT emails found in a file. Use 0 for no limit.',
            help_group=SCAN_OPTIONS_GROUP),
    ]

    def is_enabled(self, email, **kwargs):
        return email

    def get_scanner(self, max_email=50, test_slow_mode=False, test_error_mode=False, **kwargs):
        from scancode.api import get_emails
        return partial(
            get_emails,
            threshold=max_email,
            test_slow_mode=test_slow_mode,
            test_error_mode=test_error_mode
        )
