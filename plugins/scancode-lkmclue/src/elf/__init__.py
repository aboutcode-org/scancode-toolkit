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

from elf.elf import Elf


@scan_impl
class ELFScanner(ScanPlugin):
    """
    Collect the names of shared objects/libraries needed by an Elf binary file.
    """
    resource_attributes = OrderedDict(
        elf_needed_library=attr.ib(default=attr.Factory(list), repr=False),
    )

    options = [
        CommandLineOption(('--elf',),
            is_flag=True, default=False,
            help=' Collect the names of shared objects/libraries needed by an Elf binary file.',
            help_group=SCAN_GROUP,
            sort_order=100),
    ]

    def is_enabled(self, elf, **kwargs):
        return elf

    def get_scanner(self, **kwargs):
        return get_elf_needed_library


def get_elf_needed_library(location, **kwargs):
    """
    Return a list of needed_libraries 
    """
    
    T = contenttype.get_type(location)
    if not T.is_elf:
        return
    elfie = elf.Elf(location)
    results =[]
    for needed_library in  elfie.needed_libraries:
        results.append(needed_library)
    return dict(elf_needed_library=results)
