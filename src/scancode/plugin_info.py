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

from collections import OrderedDict

import attr

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode import CommandLineOption
from scancode import OTHER_SCAN_GROUP


@scan_impl
class InfoScanner(ScanPlugin):
    """
    Scan a file Resource for miscellaneous information such as mime/filetype and
    basic checksums.
    """
    resource_attributes = OrderedDict([
        ('date', attr.ib(default=None)),
        ('sha1', attr.ib(default=None)),
        ('md5', attr.ib(default=None)),
        ('mime_type', attr.ib(default=None)),
        ('file_type', attr.ib(default=None)),
        ('programming_language', attr.ib(default=None)),
        ('is_binary', attr.ib(default=False, type=bool)),
        ('is_text', attr.ib(default=False, type=bool)),
        ('is_archive', attr.ib(default=False, type=bool)),
        ('is_media', attr.ib(default=False, type=bool)),
        ('is_source', attr.ib(default=False, type=bool)),
        ('is_script', attr.ib(default=False, type=bool)),
    ])

    sort_order = 0

    options = [
        CommandLineOption(('-i', '--info'),
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
