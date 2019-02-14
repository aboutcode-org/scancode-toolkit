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
from __future__ import unicode_literals

from functools import partial

from plugincode.pre_scan import PreScanPlugin
from plugincode.pre_scan import pre_scan_impl
from scancode import CommandLineOption
from scancode import PRE_SCAN_GROUP
from typecode.contenttype import get_type


@pre_scan_impl
class IgnoreBinaries(PreScanPlugin):
    """
    Ignore binary files.
    """

    options = [
        CommandLineOption(('--ignore-binaries',),
           is_flag=True,
           help='Ignore binary files.',
           sort_order=10,
           help_group=PRE_SCAN_GROUP)
    ]

    def is_enabled(self, ignore_binaries, **kwargs):
        return ignore_binaries

    def process_codebase(self, codebase, ignore_binaries, **kwargs):
        """
        Remove binary Resources from the resource tree.
        """
        if not ignore_binaries:
            return

        resources_to_remove = []

        # walk the codebase to collect resource of binary files to remove.
        for resource in codebase.walk():
            if not resource.is_file:
                continue
            
            if is_binary(resource.location):
                resources_to_remove.append(resource)

        # second, effectively remove the resources
        for resource in resources_to_remove:
            resource.remove(codebase)


def is_binary(location):
    """
    Return True if the resource at location is a binary file.
    """
    t = get_type(location)
    return (
        t.is_binary 
        or t.is_archive 
        or t.is_media 
        or t.is_office_doc
        or t.is_compressed
        or t.is_filesystem
        or t.is_winexe
        or t.is_elf
        or t.is_java_class
        or t.is_data
    )