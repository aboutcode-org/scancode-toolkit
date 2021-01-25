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


import attr

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import SCAN_GROUP
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl


@scan_impl
class CopyrightScanner(ScanPlugin):
    """
    Scan a Resource for copyrights.
    """

    resource_attributes = dict([
        ('copyrights',attr.ib(default=attr.Factory(list))),
        ('holders',attr.ib(default=attr.Factory(list))),
        ('authors',attr.ib(default=attr.Factory(list))),
    ])

    sort_order = 4

    options = [
        PluggableCommandLineOption(('-c', '--copyright',),
            is_flag=True, default=False,
            help='Scan <input> for copyrights.',
            help_group=SCAN_GROUP,
            sort_order=50),
    ]

    def is_enabled(self, copyright, **kwargs):  # NOQA
        return copyright

    def get_scanner(self, **kwargs):
        from scancode.api import get_copyrights
        return get_copyrights
