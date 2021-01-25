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
from commoncode.cliutils import OTHER_SCAN_GROUP
from commoncode.cliutils import SCAN_OPTIONS_GROUP
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl


@scan_impl
class UrlScanner(ScanPlugin):
    """
    Scan a Resource for URLs.
    """

    resource_attributes = dict(urls=attr.ib(default=attr.Factory(list)))

    sort_order = 10

    options = [
        PluggableCommandLineOption(('-u', '--url',),
            is_flag=True, default=False,
            help='Scan <input> for urls.',
            help_group=OTHER_SCAN_GROUP),

        PluggableCommandLineOption(('--max-url',),
            type=int, default=50,
            metavar='INT',
            required_options=['url'],
            show_default=True,
            help='Report only up to INT urls found in a file. Use 0 for no limit.',
            help_group=SCAN_OPTIONS_GROUP),
    ]

    def is_enabled(self, url, **kwargs):
        return url

    def get_scanner(self, max_url=50, **kwargs):
        from scancode.api import get_urls
        return partial(get_urls, threshold=max_url)
