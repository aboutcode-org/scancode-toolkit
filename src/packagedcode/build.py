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
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os

from collections import defaultdict
from collections import OrderedDict
import ast
import attr

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models
from packagedcode.utils import combine_expressions
from scancode.api import get_licenses


TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


"""
Detect as Packages common build tools and environment such as Make, Autotools,
gradle, Buck, Bazel, Pants, etc.
"""


@attr.s()
class BaseBuildManifestPackage(models.Package):
    metafiles = tuple()

    @classmethod
    def recognize(cls, location):
        if not cls._is_build_manifest(location):
            return

        # we use the parent directory as a name
        name = fileutils.file_name(fileutils.parent_directory(location))
        # we could use checksums as version in the future
        version = None

        # there is an optional array of license file names in targets that we could use
        # declared_license = None
        # there is are dependencies we could use
        # dependencies = []
        return cls(
            name=name,
            version=version)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    @classmethod
    def _is_build_manifest(cls, location):
        if not filetype.is_file(location):
            return False
        fn = fileutils.file_name(location)
        return any(fn == mf for mf in cls.metafiles)


@attr.s()
class AutotoolsPackage(BaseBuildManifestPackage):
    metafiles = ('configure', 'configure.ac',)
    default_type = 'autotools'


@attr.s()
class BazelPackage(BaseBuildManifestPackage):
    metafiles = ('BUILD',)
    default_type = 'bazel'


@attr.s()
class BuckPackage(BaseBuildManifestPackage):
    metafiles = ('BUCK',)
    default_type = 'buck'

    @classmethod
    def recognize(cls, location):
        if not cls._is_build_manifest(location):
            return
        return buck_parse(location)


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
    manifest_parent_directory = fileutils.parent_directory(location)
    for rule_name, args in build_rules.items():
        name = args.get('name')
        if not name:
            continue
        license_files = args.get('licenses', [])
        license_expressions = []
        license_names = []

        for license_file in license_files:
            license_file_path = os.path.join(manifest_parent_directory, license_file)
            if os.path.exists(license_file_path) and os.path.isfile(license_file_path):
                licenses = get_licenses(license_file_path)
                for license, license_expression in zip(
                        licenses.get('licenses', []),
                        licenses.get('license_expressions', [])):
                    short_name = license.get('short_name')
                    if short_name:
                        license_names.append(short_name)
                    license_expressions.append(license_expression)

        rules_to_return.append(
            BuckPackage(
                name=name,
                declared_license=license_names or None,
                license_expression=combine_expressions(license_expressions) or None
            )
        )

    if rules_to_return:
        # FIXME: We will eventually return the entire list instead of the first one
        # once the new package changes are in
        return rules_to_return[0]
