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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# from collections import OrderedDict

import attr

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP


@post_scan_impl
class IdentifyContent(PostScanPlugin):
    """
    Identify the primary_content_type (e.g., `Python-source code` or `Python-script`) for each file in the codebase being scanned.
    """

    options = [
        CommandLineOption(('--content',),
                                        is_flag=True, default=False,
                                        help='Analyze a Scan and annotate it with a new primary_content_type field that designates the primary Content Type (primary for analysis) in the format: Language-Type.',
                                        help_group=POST_SCAN_GROUP)
    ]

    resource_attributes = dict(primary_content_type=attr.ib(default=attr.Factory(dict)))

    def is_enabled(self, content, **kwargs):
        return content

    def process_codebase(self, codebase, content, **kwargs):
        """
        Populate a primary_content_type mapping.
        """
        if not self.is_enabled(content):
            return

        for resource in codebase.walk(topdown=False):
            if resource.programming_language == 'Python':
                resource.primary_content_type = "Python-xxx"
            else:
                resource.primary_content_type = "???"

            codebase.save_resource(resource)
