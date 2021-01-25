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

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OTHER_SCAN_GROUP


@scan_impl
class InfoScanner(ScanPlugin):
    """
    Scan a file Resource for miscellaneous information such as mime/filetype and
    basic checksums.
    """
    resource_attributes = dict([
        ('date', attr.ib(default=None, repr=False)),
        ('sha1', attr.ib(default=None, repr=False)),
        ('md5', attr.ib(default=None, repr=False)),
        ('sha256', attr.ib(default=None, repr=False)),
        ('mime_type', attr.ib(default=None, repr=False)),
        ('file_type', attr.ib(default=None, repr=False)),
        ('programming_language', attr.ib(default=None, repr=False)),
        ('is_binary', attr.ib(default=False, type=bool, repr=False)),
        ('is_text', attr.ib(default=False, type=bool, repr=False)),
        ('is_archive', attr.ib(default=False, type=bool, repr=False)),
        ('is_media', attr.ib(default=False, type=bool, repr=False)),
        ('is_source', attr.ib(default=False, type=bool, repr=False)),
        ('is_script', attr.ib(default=False, type=bool, repr=False)),
    ])

    sort_order = 0

    options = [
        PluggableCommandLineOption(('-i', '--info'),
            is_flag=True, default=False,
            help='Scan <input> for file information (size, checksums, etc).',
            help_group=OTHER_SCAN_GROUP, sort_order=10
            )
    ]

    def is_enabled(self, info, **kwargs):
        return info

    def get_scanner(self, **kwargs):
        from scancode.api import get_file_info
        return get_file_info
