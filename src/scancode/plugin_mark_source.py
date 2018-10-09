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

import attr

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP


@post_scan_impl
class MarkSource(PostScanPlugin):
    """
    Set the "is_source" flag to true for directories that contain
    over 90% of source files as direct children.
    Has no effect unless the --info scan is requested.
    """

    resource_attributes = dict(source_count=attr.ib(default=0, type=int))

    sort_order = 8

    options = [
        CommandLineOption(('--mark-source',),
            is_flag=True, default=False,
            requires=['info'],
            help='Set the "is_source" to true for directories that contain '
                 'over 90% of source files as children and descendants. '
                 'Count the number of source files in a directory as a new source_file_counts attribute',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, mark_source, info, **kwargs):
        return mark_source and info

    def process_codebase(self, codebase, mark_source, **kwargs):
        """
        Set the `is_source` to True in directories if they contain over 90% of
        source code files at full depth.
        """
        for resource in codebase.walk(topdown=False):
            if resource.is_file:
                continue

            children = resource.children(codebase)
            if not children:
                continue

            src_count = sum(1 for c in children if c.is_file and c.is_source)
            src_count += sum(c.source_count for c in children if not c.is_file)
            is_source = is_source_directory(src_count, resource.files_count)

            if src_count and is_source:
                resource.is_source = is_source
                resource.source_count = src_count
                codebase.save_resource(resource)


def is_source_directory(src_count, files_count):
    """
    Return True is this resource is a source directory with at least over 90% of
    source code files at full depth.
    """
    return src_count / files_count >= 0.9
