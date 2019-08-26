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


@scan_impl
class LKMClueScanner(ScanPlugin):
    """
    Scan lkm-clue information from the resource
    """
    resource_attributes = dict(
        lkmclue_source_path=attr.ib(default=attr.Factory(list), repr=False))

    options = [
        CommandLineOption(('--lkm-clue',),
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
    Return a mapping with lkm_clue_type and lkm_clue
    """
    type, clue = sourcecode.kernel.find_lkms(resource.location)
    return dict(
        lkm_clue_type=type,
        lkm_clue=clue,
    )
