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
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
from collections import OrderedDict
import ast
import os

import attr

from commoncode import fileutils
from packagedcode.build import BaseBuildManifestPackage
from packagedcode.utils import combine_expressions
from scancode.api import get_licenses


@attr.s()
class BuckPackage(BaseBuildManifestPackage):
    metafiles = ('BUCK',)
    default_type = 'buck'

    @classmethod
    def recognize(cls, location):
        if not cls._is_build_manifest(location):
            return
        return buck_parse(location)

    def compute_normalized_license(self):
        return compute_normalized_license(
            self.declared_license,
            manifest_parent_path=self.root_path
        )


# TODO: Prune rule names that do not create things we do not care about like
# `robolectric_test` or `genrule`
buck_rule_names = [
    'command_alias',
    'export_file',
    'filegroup',
    'genrule',
    'http_archive',
    'http_file',
    'remote_file',
    'test_suite',
    'worker_tool',
    'zip_file',
    'android_aar',
    'android_binary',
    'android_build_config',
    'android_instrumentation_apk',
    'android_instrumentation_test',
    'android_library',
    'android_manifest',
    'android_prebuilt_aar',
    'android_resource',
    'apk_genrule',
    'gen_aidl',
    'keystore',
    'ndk_library',
    'prebuilt_jar',
    'prebuilt_native_library',
    'robolectric_test',
    'cxx_binary',
    'cxx_library',
    'cxx_genrule',
    'cxx_precompiled_header',
    'cxx_test',
    'prebuilt_cxx_library',
    'prebuilt_cxx_library_group',
    'd_binary',
    'd_library',
    'd_test',
    'go_binary',
    'go_library',
    'go_test',
    'cgo_library',
    'groovy_library',
    'halide_library',
    'haskell_binary',
    'haskell_library',
    'prebuilt_haskell_library',
    'apple_asset_catalog',
    'apple_binary',
    'apple_bundle',
    'apple_library',
    'apple_package',
    'apple_resource',
    'apple_test',
    'core_data_model',
    'prebuilt_apple_framework',
    'java_binary',
    'java_library',
    'java_test',
    'prebuilt_jar',
    'prebuilt_native_library',
    'kotlin_library',
    'kotlin_test',
    'cxx_lua_extension',
    'lua_binary',
    'lua_library',
    'ocaml_binary',
    'ocaml_library',
    'prebuilt_python_library',
    'python_binary',
    'python_library',
    'python_test',
    'rust_binary',
    'rust_library',
    'rust_test',
    'prebuilt_rust_library',
    'sh_binary',
    'sh_test',
    'csharp_library',
    'prebuilt_dotnet_library'
]


def buck_parse(location):
    build_rules = defaultdict(OrderedDict)
    # Thanks to the BUCK language being a Python DSL, we can use the `ast`
    # library to parse BUCK files
    with open(location, 'rb') as f:
        tree = ast.parse(f.read())
    for statement in tree.body:
        # We only care about function calls or assignments to functions whose
        # names are in `buck_rule_names`
        if (isinstance(statement, ast.Expr)
                or isinstance(statement, ast.Call)
                or isinstance(statement, ast.Assign)
                and isinstance(statement.value, ast.Call)
                and isinstance(statement.value.func, ast.Name)
                and statement.value.func.id in buck_rule_names):
            rule_name = statement.value.func.id
            # Process the rule arguments
            for kw in statement.value.keywords:
                arg_name = kw.arg
                if isinstance(kw.value, ast.Str):
                    build_rules[rule_name][arg_name] = kw.value.s
                if isinstance(kw.value, ast.List):
                     # We collect the elements of a list if the element is not a function call
                    build_rules[rule_name][arg_name] = [elt.s for elt in kw.value.elts if not isinstance(elt, ast.Call)]

    rules_to_return = []
    for rule_name, args in build_rules.items():
        name = args.get('name')
        if not name:
            continue
        license_files = args.get('licenses', [])
        rules_to_return.append(
            BuckPackage(
                name=name,
                declared_license=license_files or None,
                root_path=fileutils.parent_directory(location)
            )
        )

    if rules_to_return:
        # FIXME: We will eventually return the entire list instead of the first one
        # once the new package changes are in
        return rules_to_return[0]


def compute_normalized_license(declared_license, manifest_parent_path):
    """
    Return a normalized license expression string detected from a list of
    declared license items.
    """
    if not declared_license or not manifest_parent_path:
        return

    license_expressions = []
    for license_file in declared_license:
        license_file_path = os.path.join(manifest_parent_path, license_file)
        if os.path.exists(license_file_path) and os.path.isfile(license_file_path):
            licenses = get_licenses(license_file_path)
            license_expressions.extend(licenses.get('license_expressions', []))

    return combine_expressions(license_expressions)
