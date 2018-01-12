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

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl


@post_scan_impl
class OnlyFindings(PostScanPlugin):
    """
    Prune files or directories without scan findings for the requested scans.
    """

    name = 'only-findings'

    @classmethod
    def get_plugin_options(cls):
        from scancode.cli import ScanOption
        return [
            ScanOption(('--only-findings',), is_flag=True,
                help='''
                Only return files or directories with findings for the requested
                scans. Files and directories without findings are omitted (not
                considering basic file information as findings).''')
        ]

    def is_enabled(self):
        return any(se.value == True for se in self.command_options
                      if se.name == 'only_findings')

    def process_codebase(self, codebase):
        """
        Remove Resources from codebase bottom-up if they have no scan data, no
        errors and no children.
        """
        for resource in codebase.walk(topdown=False):
            if not has_findings(resource):
                # TODO: test me, this is likely a source of bugs???
                codebase.remove_resource(resource)


def has_findings(resource):
    """
    Return True if this resource has findings.
    """
    return (resource.errors
            or resource.children_rids
            or any(resource.get_scans().values())
            # NEVER remove the root resource
            or resource.is_root())
