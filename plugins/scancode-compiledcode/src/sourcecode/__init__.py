#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals

from collections import OrderedDict
from functools import partial
from itertools import chain

import attr

from commoncode import fileutils
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode import CommandLineOption
from scancode import SCAN_GROUP
from typecode import contenttype

from sourcecode import kernel
from sourcecode.metrics import file_lines_count


@scan_impl
class CodeCommentLinesScanner(ScanPlugin):
    """
    Scan the number of lines of code and lines of the comments.
    """
    resource_attributes = OrderedDict(
        codelines=attr.ib(default=attr.Factory(int), repr=False),
        commentlines=attr.ib(default=attr.Factory(int), repr=False),

    )

    options = [
        CommandLineOption(('--codecommentlines',),
            is_flag=True, default=False,
            help='  Scan the number of lines of code and lines of the comments.',
            help_group=SCAN_GROUP,
            sort_order=100),
    ]

    def is_enabled(self, codecommentlines, **kwargs):
        return codecommentlines

    def get_scanner(self, **kwargs):
        return get_codecommentlines


def get_codecommentlines(location, **kwargs):
    """
    Return the cumulative number of lines of code in the whole directory tree
    at `location`. Use 0 if `location` is not a source file.
    """
    codelines = 0
    commentlines = 0
    codelines, commentlines = file_lines_count(location)
    return OrderedDict(
        codelines=codelines,
        commentlines=commentlines
    )
