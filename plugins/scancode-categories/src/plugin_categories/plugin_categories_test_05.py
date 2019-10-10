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

from collections import OrderedDict

import attr
import json

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP


@post_scan_impl
class CategoryRules(PostScanPlugin):
    """
    Identify the category (e.g., Java, JavaScript, Python) for each file in the codebase being scanned.
    """

    options = [
        CommandLineOption(('--categories',),
                                        help='Identify the category (e.g., Java, JavaScript, Python) for each file in the codebase being scanned.  Rules comprise a set of any() and all() functions contained as string values in a list of JSON objects.  The category and related information (including the rule applied to the file) will be added to a new "category" field in the ScanCode JSON output file.',
                                        metavar='FILE',
                                        help_group=POST_SCAN_GROUP)
    ]

    resource_attributes = dict(category=attr.ib(default=attr.Factory(dict)))

    def is_enabled(self, categories, **kwargs):
        return categories

    def process_codebase(self, codebase, categories, **kwargs):
        """
        Populate a category mapping.
        """
        if not self.is_enabled(categories):
            return

        ruleset_path = categories
        with open(ruleset_path) as json_file:
            data = json.load(json_file)

            for resource in codebase.walk(topdown=False):
                self.vet_resource(resource, categories, data)
                codebase.save_resource(resource)

    def vet_resource(self, resource, categories, data, **kwargs):
        matched_rules = []
        resource.category = matched_rules
        for i in data["new_rules"]:
            scope = locals()
            if eval(i["test"], scope):
                if resource.type == 'directory':
                    resource.category = 'directory'
                elif resource.type == 'file':
                    matched_rules.append(OrderedDict((k, i[k]) for k in ('name', 'test', 'domain', 'status')))
                    resource.category = matched_rules

        if not resource.category:
            if resource.type == 'directory':
                resource.category = 'directory'
            else:
                resource.category = "no match"

        return resource
