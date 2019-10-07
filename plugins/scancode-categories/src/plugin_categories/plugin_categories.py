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

# from commoncode import saneyaml
# import os.path
# from os.path import exists
# from os.path import isdir

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
        Populate a category mapping with two attributes: category_type and category_rule
        at the File Resource level.
        """
        if not self.is_enabled(categories):
            return

        # with open('/c/code/nexb/dev/scancode-toolkit/plugins/scancode-categories/src/python_rules/python_rules_01.py', 'r') as f:
        #     line = f.readline()
        #     header = []
        #     data = []
        #     while line:
        #         if line.startswith('#'):
        #             header.append(line)
        #         else:
        #             data.append(line)
        #         line = f.readline()

        import json
        # s = '/c/code/nexb/dev/scancode-toolkit/plugins/scancode-categories/src/python_rules/python_rules_01.py'
        # s = r'C:\code\nexb\dev\scancode-toolkit\plugins\scancode-categories\src\python_rules\python_rules_01.py'
        # s = r'C:\nexb\scancode_plugin_tests\rules\python_rules_01.py'
        # does this represent the path passed with the command?
        s = categories

        # jdata = json.loads(s)
        # print(jdata)
        # for d in jdata:
        #     for key, value in d.items():
        #         print(key, value)
        # ============================================
        # # this prints as expected, but test value must be in quotes

        # my_path = os.path.abspath(os.path.dirname(__file__))
        # # my_rules = os.path.join(my_path, 'test_rules_simple_01.py')
        # # try different folder
        # my_rules = os.path.join(my_path, '../python_rules/python_rules_01.py')
        # with open(my_rules) as json_file:
        #     data = json.load(json_file)

        # try to import with full path from different directory
        with open(s) as json_file:
            data = json.load(json_file)




            # print('\nHELLO\n')
            # for p in data['new_rules']:
            #     print('Name: ' + p['name'])
            #     print('Test: ' + p['test'])
            #     print('')
        # ============================================

        # # apply rules to resource
        # for resource in codebase.walk(topdown=False):
        #     self.vet_resource(resource, categories)
        #     codebase.save_resource(resource)

            # same as above but indented one level so we can pass "data" from json.load above
            for resource in codebase.walk(topdown=False):
                # self.vet_resource(resource, categories)
                self.vet_resource(resource, categories, data)
                codebase.save_resource(resource)

    # def vet_resource(self, resource, categories, **kwargs):
    def vet_resource(self, resource, categories, data, **kwargs):
        # ==================================================
        # Next: try to read from list inside python_rules_01.py instead of the list below
        # ==================================================
        # new_rules = [
        #     {
        #         'name': 'cpp_files_01',
        #         "test": (all(extension == resource.extension for extension in [".cpp"]) &
        #                     any(file_type == resource.file_type for file_type in ["C source, ASCII text", "C++ source, ASCII text"])),
        #         'domain': 'general',
        #         'status': 'core'
        #     },
        #     {
        #         'name': 'map_files_01',
        #         "test": (any(extension == resource.extension for extension in [".map"]) &
        #                     any(file_type == resource.file_type for file_type in ["ASCII text"])),
        #         'domain': 'general',
        #         'status': 'non-core'
        #     },
        #     {
        #         'name': 'c_files_01',
        #         "test": (all(resource.extension == extension for extension in [".c"]) &
        #                     any(resource.file_type == file_type for file_type in ["C source, ASCII text"])),
        #         'domain': 'general',
        #         'status': 'core'
        #     },
        # ]

        # # # with open('/c/code/nexb/dev/scancode-toolkit/plugins/scancode-categories/src/python_rules/python_rules_01.py', 'r') as f:
        # # with open('../python_rules/python_rules_01.py', 'r') as f:
        # #     new_rules = [line for line in f]

        # new_path = os.path.abspath(os.path.dirname(__file__))
        # new_yamlRules = os.path.join(new_path, '../python_rules/python_rules_01.py')
        # with open(new_yamlRules) as f:
        #     new_rules = [line for line in f]
        # # # #     # use safe_load instead load
        # # # #     # rules_map = yaml.safe_load(f)
        # # #     new_rules_map = saneyaml.load(f)

        # from python_rules_01 import new_rules

        # import sys
        # import os
        # sys.path.append(os.path.abspath("../../python_rules"))
        # sys.path.append(os.path.abspath("/c/code/nexb/dev/scancode-toolkit/plugins/scancode-categories/src/python_rules/python_rules_01.py"))
        # sys.path.append(os.path.abspath("/c/code/nexb/dev/scancode-toolkit/plugins/scancode-categories/src/python_rules"))

        # all these fail: no module named x
        # from python_rules_01 import new_rules
        # from test_rules import new_rules
        # import test_rules


        # use list located in this same file
        # now we get it fropm a .py file in the same directory
        matched_rules = []
        resource.category = matched_rules
        # for i in new_rules:
        for i in data["new_rules"]:
            # # if i["test"]:
            # convert_to_code = i["test"]
            # if convert_to_code:
            # if exec(i["test"]):
            # execute = exec(i["test"])
            # execute = exec(i["test"].decode("utf-8"))

            # decode_value = i["test"].decode("utf-8")
            # decode_value = i["test"]  # no longer necessary -- see <if eval(i["test"], scope):> below

            # execute = exec(decode_value)
            # if execute:
            # if exec(decode_value):
            scope = locals()  # this captures all local variables, which we pass in eval() just below so the json "test" value can use "resource"!
            # if eval(decode_value, scope):
            if eval(i["test"], scope):
                # with the tests cleaned up, not sure if the 1st part of this if/else is still necessary -- needs further testing
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
