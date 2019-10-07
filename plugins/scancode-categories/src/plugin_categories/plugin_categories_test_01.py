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

# from collections import Counter
# from collections import defaultdict
from collections import OrderedDict

import attr

from commoncode import saneyaml
import os.path
from os.path import exists
from os.path import isdir

# from cluecode.copyrights import CopyrightDetector
# from commoncode.text import python_safe_name
# from license_expression import Licensing
# from packagedcode import get_package_instance
# from packagedcode.build import BaseBuildManifestPackage
# from packagedcode.utils import combine_expressions
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
                                        # is_flag=True,
                                        help='Identify the category (e.g., Java, JavaScript, Python) for each file in the codebase being scanned.  The category and related information (including the rule applied to the file) will be added to a new field in the ScanCode output file.',
                                        # sort_order=10,
                                        metavar='FILE',
                                        help_group=POST_SCAN_GROUP)
    ]

    # attributes = dict(category=attr.ib())
    # resource_attributes = dict(category=attr.ib(default=attr.Factory(dict)))
    resource_attributes = dict(category=attr.ib(default=attr.Factory(dict)))

    # def is_enabled(self, fingerprint, info, **kwargs):
    # def is_enabled(self, category, **kwargs):
    def is_enabled(self, categories, **kwargs):
        # return fingerprint and info
        # return category
        return categories

    # def process_codebase(self, codebase, fingerprint, **kwargs):
    # def process_codebase(self, codebase, category, **kwargs):
    def process_codebase(self, codebase, categories, **kwargs):
        if not self.is_enabled(categories):
        # if not self.is_enabled(categories):
            return

        # apply rules to resource
        for resource in codebase.walk(topdown=False):
            # if not resource.is_file:
                # continue

            # if resource.sha1 != 1:
            #     resource.category = 'whatever'
            #     # resource.save(codebase)
            #     codebase.save_resource(resource)

            # resource.category = 'some_new_value'
            # resource.category = resource.programming_language
            # resource.categories = 'some_value'
            # resource.save(codebase)
            # ========================
            # if not resource.is_file:
            #     resource.category = 'I am a simple directory and have no programming_language'
            # elif resource.programming_language:
            #     resource.category = 'I am a file and my programming_language is ' + resource.programming_language
            # else:
            #     resource.category = 'I am a file but I have no programming_language'

            self.vet_resource(resource, categories)

            codebase.save_resource(resource)

    def vet_resource(self, resource, categories, **kwargs):
        # yamlRules = r'C:\code\jupyter_notebooks\nexb-jupyter\a_kreatv_d2d_05\yaml\kv_rules_01.yaml'
        # yamlRules = './yaml_rules/test_yaml_rules_01.yml'  #doesn't work
        my_path = os.path.abspath(os.path.dirname(__file__))
        yamlRules = os.path.join(my_path, '../yaml_rules/test_yaml_rules_01.yml')
        # with open(yamlRules) as f:
        #     # use safe_load instead load
        #     # rules_map = yaml.safe_load(f)
        #     rules_map = saneyaml.load(f)

        # with open(yamlRules, 'r') as conf:
        #     conf_content = conf.read()
        # rules_map =  saneyaml.load(conf_content)

        # policies = load_license_policy(license_policy).get('license_policies', [])
        # rules_map = load_license_policy(yamlRules).get('rules', [])
        # pass in the rules_location in the command -- the variable should be the same name as the name of the plugin command i.e. 'categories'
        # no does not work: NameError: global name 'categories' is not defined
        rules_map = load_rules(categories).get('rules', [])

        # if resource.programming_language:
        #         resource.category = 'Yo -- I am a file and my programming_language is ' + resource.programming_language
        matched_rules = []
        # for rule in rules_map:
        #     # if resource.extension == rule.get('extension'):
        #     #     # resource.category = rule.get('name')
        #     #     # resource.category = rule
        #     #     matched_rules.append(rule)
        #     #     resource.category = matched_rules
        #     if resource.extension in rule.get('extension'):
        #         matched_rules.append(rule)
        #         resource.category = matched_rules
        #     # else:
        #     #     resource.category = 'YIKES!'
# ============================================
        # rulelist = [
        #     {
        #         'name': 'cpp_files01',
        #         'extension': ['.cpp'],
        #         'domain': 'general',
        #         'status': 'core'
        #     },
        #     {
        #         'name': 'cpp_files02',
        #         'extension': ['.cpp'],
        #         'domain': 'general',
        #         'status': 'core'
        #     }
        # ]

        # for rule in rulelist:
        #     if resource.extension in rule.get('extension'):
        #         matched_rules.append(rule)
        #         resource.category = matched_rules
# ============================================

        rulelist = [
            {
                'name': 'cpp_files01',
                # 'test': 'any(extension in resource.extension for extension in (".cpp", ".js"))',
                "test": "any(resource.extension == extension for extension in (\".cpp\", \".js\"))",
                'domain': 'general',
                'status': 'core'
            },
            {
                'name': 'cpp_files02',
                # 'test': 'all(extension in resource.extension for extension in (".cpp", ".js"))',
                "test": "all(resource.extension == extension for extension in (\".cpp\", \".js\"))",
                'domain': 'general',
                'status': 'core'
            }
        ]

        # for rule in rulelist:
        #     if rule.get('test'):
        #         matched_rules.append(rule)
        #         resource.category = matched_rules


        # if all(resource.extension == extension for extension in [".cpp", ".js"]):
        #     matched_rules.append('rule01')
        #     resource.category = matched_rules
        # elif any(resource.extension == extension for extension in [".cppppppp", ".js"]):
        #     matched_rules.append('rule02')
        #     resource.category = matched_rules
        # elif (any(extension == resource.extension for extension in [".cpp", ".js"]) &
        #      any(file_type == resource.file_type for file_type in ["C source, ASCII text"])):
        #     matched_rules.append('rule03')
        #     resource.category = matched_rules
        # elif (resource.extension in [".cpp", ".js"]):
        #     matched_rules.append('rule04')
        #     resource.category = matched_rules
        # else:
        #     resource.category = "no match"

# ==================================================
# read from list inside python_rules_01.py instead of the list below

        # new_rules = [
        #     {
        #         'name': 'cpp_files01',
        #         "test": (all(extension == resource.extension for extension in [".cpp"]) &
        #                     any(file_type == resource.file_type for file_type in ["C source, ASCII text"])),
        #         'domain': 'general',
        #         'status': 'core'
        #     },
        #     {
        #         'name': 'cpp_files02',
        #         "test": (all(resource.extension == extension for extension in [".cpp"]) &
        #                     any(resource.file_type == file_type for file_type in ["C source, ASCII text"])),
        #         'domain': 'general',
        #         'status': 'core'
        #     },
        #     {
        #         'name': 'cpp_files03',
        #         "test": (all(resource.extension in extension for extension in [".cpp"]) &
        #                     any(resource.file_type == file_type for file_type in ["C source, ASCII text"])),
        #         'domain': 'general',
        #         'status': 'core'
        #     },
        #     {
        #         'name': 'cpp_files04',
        #         "test": (all(resource.extension in extension for extension in [".cppppppppp"]) &
        #                     any(resource.file_type == file_type for file_type in ["C source, ASCII text"])),
        #         'domain': 'general',
        #         'status': 'core'
        #     },
        #     {
        #         'name': 'cpp_files05',
        #         "test": (all(resource.extension in extension for extension in [".pcppppppppp"]) &
        #                     any(resource.file_type == file_type for file_type in ["C source, ASCII text"])),
        #         'domain': 'general',
        #         'status': 'core'
        #     },
        #     {
        #         'name': 'cpp_files06',
        #         "test": (all(resource.extension in extension for extension in [".pcppppppppp"]) |
        #                     any(resource.file_type == file_type for file_type in ["C source, ASCII text"])),
        #         'domain': 'general',
        #         'status': 'core'
        #     },
        #     {
        #         'name': 'cpp_files07',
        #         "test":
        #             (
        #                 all(resource.extension in extension for extension in [".pcppppppppp"]) |
        #                 any(resource.file_type == file_type for file_type in ["C source, ASCII text"])
        #             ),
        #         'domain': 'general',
        #         'status': 'core'
        #     },
        #     {
        #         'name': 'cpp_files08',
        #         "test": (any(extension == resource.extension for extension in [".cpp", ".js"]) &
        #                     any(file_type == resource.file_type for file_type in ["C source, ASCII text"])),
        #         'domain': 'general',
        #         'status': 'core'
        #     }
        # ]

        # from python_rules_01 import new_rules
        # my_new_rules = new_rules

        # new_path = os.path.abspath(os.path.dirname(__file__))
        # theRules = os.path.join(new_path, '../python_rules/python_rules_01.txt')
        # file1 = open(theRules, "rb")
        # new_rules = file1
        # # import json
        # # with open(theRules) as json_file:
        # #     new_rules = json.load(json_file)

        # new_path = os.path.abspath(os.path.dirname(__file__))
        # new_yamlRules = os.path.join(new_path, '../yaml_rules/test_yaml_rules_02.yml')
        # # with open(new_yamlRules) as f:
        # # #     # use safe_load instead load
        # # #     # rules_map = yaml.safe_load(f)
        # #     new_rules_map = saneyaml.load(f)

        # # for i in new_rules:
        # for i in new_rules_map:
        # # for i in new_rules['new_rules']:
        # # for i in my_new_rules:
        #     # if i.get('test'):
        #     if i["test"]:
        #         # matched_rules.append(i.get('name'))
        #         # matched_rules.append(i)
        #         matched_rules.append(OrderedDict((k, i[k]) for k in ('name', 'domain', 'status')))
        #         resource.category = matched_rules
        #     else:
        #         resource.category = 'no match'

        # this loads a yaml file passed in the command
        """
        - pass a yaml rules file
        - python file with relevant code:
        C:\code\nexb\dev\scancode-toolkit\plugins\scancode-categories\src\plugin_categories\plugin_categories_test_01.py
        - yaml does not seem to enable the use of conditonal expressions or other tests -- no code
        - values seem to always be treated as strings, even if not enclosed in quotes
        - the attempted test for true/false instead tests for the presence of a value, so every resource is treated as satisfying every test

        /c/code/nexb/dev/scancode-toolkit/scancode -i -n 2 /c/nexb/scancode_plugin_tests/sample_codebases/bionic-master-libc-bionic.tar.gz-extract --categories /c/code/nexb/dev/scancode-toolkit/plugins/scancode-categories/src/yaml_rules/test_yaml_rules_02.yml --json /c/nexb/scancode_plugin_tests/scan_output/libc-bionic-categories-scan02.json
        """
        rules_map_01 = load_rules(categories).get('rules', [])

        # if resource.programming_language:
        #         resource.category = 'Yo -- I am a file and my programming_language is ' + resource.programming_language
        matched_rules_01 = []
        for rule in rules_map_01:
            # if resource.extension == rule.get('extension'):
            #     # resource.category = rule.get('name')
            #     # resource.category = rule
            #     matched_rules.append(rule)
            #     resource.category = matched_rules

            if rule.get("test"):
                matched_rules_01.append(rule)
                resource.category = matched_rules_01
            else:
                resource.category = "egads"


# ============================================
        return resource


# def load_license_policy(license_policy_location):
def load_rules(rules_location):
    """
    Return a category rules dictionary loaded from a category rules file.
    """
    if not rules_location or not exists(rules_location):
        return {}
    elif isdir(rules_location):
        return {}
    with open(rules_location, 'r') as conf:
        conf_content = conf.read()
    return saneyaml.load(conf_content)
