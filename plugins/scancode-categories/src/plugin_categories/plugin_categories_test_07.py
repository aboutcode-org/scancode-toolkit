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
                                        help='Identify the category (e.g., Java, JavaScript, Python) for each file in the codebase being scanned.  Rules comprise a set of field values( e.g., file_type and mime_type) contained as string values in a list of JSON objects.  The category and related information (including the rule applied to the file) will be added to a new "category" field in the ScanCode JSON output file.',
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
        #
        for i in data["new_rules"]:
            if resource.type == 'directory':
                resource.category = 'directory'
            elif resource.type == 'file':
                for test in i["test"]:
                    # if the test value list is empty, ignore by defining as true
                    if not test["extension"]:
                        extension_test = (0 == 0)
                    else:
                        extension_test = any(extension == resource.extension for extension in test["extension"])

                    if not test["file_type"]:
                        file_type_test = (0 == 0)
                    else:
                        file_type_test = any(file_type == resource.file_type for file_type in test["file_type"])

                    if not test["mime_type"]:
                        mime_type_test = (0 == 0)
                    else:
                        mime_type_test = any(mime_type == resource.mime_type for mime_type in test["mime_type"])

                    if not test["name"]:
                        name_test = (0 == 0)
                    else:
                        name_test = any(name == resource.name for name in test["name"])

                    if not test["programming_language"]:
                        programming_language_test = (0 == 0)
                    else:
                        programming_language_test = any(programming_language == resource.programming_language for programming_language in test["programming_language"])

                    # define the AND and OR tests
                    and_tests = extension_test & file_type_test & mime_type_test & name_test & programming_language_test
                    or_tests = extension_test | file_type_test | mime_type_test | name_test | programming_language_test

                    # check whether operator is AND or OR
                    if test["operator"] == "and":
                        if and_tests:
                            # i = OrderedDict((k, i[k]) for k in ('rule', 'domain', 'status', 'notes', 'test'))
                            # d2 = OrderedDict((k, test[k]) for k in ('operator', 'extension', 'file_type', 'mime_type', 'name'))
                            # i["test"] = d2
                            # matched_rules.append(i)
                            # resource.category = matched_rules
                            self.create_category(i, test, resource, matched_rules)
                    elif test["operator"] == "or":
                        if or_tests:
                            # i = OrderedDict((k, i[k]) for k in ('rule', 'domain', 'status', 'notes', 'test'))
                            # d2 = OrderedDict((k, test[k]) for k in ('operator', 'extension', 'file_type', 'mime_type', 'name'))
                            # i["test"] = d2
                            # matched_rules.append(i)
                            # resource.category = matched_rules
                            self.create_category(i, test, resource, matched_rules)

        if not resource.category:
            if resource.type == 'directory':
                resource.category = 'directory'
            else:
                resource.category = "no match"

        return resource

    def create_category(self, i, test, resource, matched_rules):
        i = OrderedDict((k, i[k]) for k in ('rule', 'domain', 'notes', 'status', 'test'))
        d2 = OrderedDict((k, test[k]) for k in ('operator', 'extension', 'file_type', 'mime_type', 'name', 'programming_language'))
        i["test"] = d2
        matched_rules.append(i)
        resource.category = matched_rules

        return resource
