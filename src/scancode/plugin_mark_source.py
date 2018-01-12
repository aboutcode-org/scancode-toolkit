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

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl


@post_scan_impl
class MarkSource(PostScanPlugin):
    """
    Set the "is_source" flag to true for directories that contain
    over 90% of source files as direct children.
    Has no effect unless the --info scan is requested.
    """

    name = 'mark-source'

    @classmethod
    def get_plugin_options(cls):
        from scancode.cli import ScanOption
        return [
            ScanOption(('--mark-source',), is_flag=True,
                help='''
                Set the "is_source" flag to true for directories that contain
                over 90% of source files as direct children.
                Has no effect unless the --info scan is requested.
                ''')
        ]

    def is_enabled(self):
        # FIXME: we need infos for this to work, we should use a better way to
        # express dependencies on one or more scan
        return all(se.value for se in self.command_options
                      if se.name in ('mark_source', 'infos'))

    def process_codebase(self, codebase):
        """
        Set the `is_source` to True in directories if they contain over 90% of
        source code files at full depth.
        """
        codebase.update_counts()
        # TODO: these two nested walk() calls are not super efficient
        for resource in codebase.walk(topdown=False):
            if resource.is_file:
                continue
            src_count = sum(1 for c in resource.walk(topdown=True) if c.is_file and c.is_source)
            files_count = resource.files_count
            resource.is_source = is_source_directory(src_count, files_count)


def is_source_directory(src_count, files_count):
    """
    Return True is this resource is a source directory with at least over 90% of
    source code files at full depth.
    """
    return src_count / files_count >= 0.9
