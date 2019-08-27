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


@scan_impl
class LKMClueScanner(ScanPlugin):
    """
    Scan lkm-clue information from the resource.
    """
    resource_attributes = OrderedDict(
        lkm_clue=attr.ib(default=attr.Factory(OrderedDict), repr=False),
    )

    options = [
        CommandLineOption(('--lkmclue',),
            is_flag=True, default=False,
            help='Collect LKM module clues and type indicating a possible Linux Kernel Module. (formerly lkm_hint and lkm_line).',
            help_group=SCAN_GROUP,
            sort_order=100),
    ]

    def is_enabled(self, lkmclue, **kwargs):
        return lkmclue

    def get_scanner(self, **kwargs):
        return get_lkm_clues


def get_lkm_clues(location, **kwargs):
    """
    Return a mapping content 
        key: lkm_clue_type and 
        value: list of lkm_clue
    """
    clues = OrderedDict()
    for type, clue in kernel.find_lkms(location):
        if not type or not clue:
            continue
        if clues.get(type):
            clues[type] = clues.get(type).append(clue)
        else:
            clues[type] = [clue]
    return OrderedDict(
        lkm_clue=clues,
    )
