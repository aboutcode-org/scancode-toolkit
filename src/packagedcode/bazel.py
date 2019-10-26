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
class BazelPackage(BaseBuildManifestPackage):
    metafiles = ('BUILD',)
    default_type = 'bazel'

    @classmethod
    def recognize(cls, location):
        if not cls._is_build_manifest(location):
            return
        for package in bazel_parse(location):
            yield package

    def compute_normalized_license(self):
        return compute_normalized_license(
            self.declared_license,
            manifest_parent_path=self.root_path
        )


def bazel_parse(location):
    build_rules = defaultdict(list)
    # Thanks to the Skylark language being a Python DSL, we can use the `ast`
    # library to parse Bazel BUILD files
    with open(location, 'rb') as f:
        tree = ast.parse(f.read())
    for statement in tree.body:
        if (isinstance(statement, ast.Expr)
                or isinstance(statement, ast.Call)
                or isinstance(statement, ast.Assign)
                and isinstance(statement.value, ast.Call)
                and isinstance(statement.value.func, ast.Name)):
            rule_name = statement.value.func.id
            # Process the rule arguments
            args = OrderedDict()
            for kw in statement.value.keywords:
                arg_name = kw.arg
                if isinstance(kw.value, ast.Str):
                    args[arg_name] = kw.value.s
                if isinstance(kw.value, ast.List):
                     # We collect the elements of a list if the element is not a function call
                    args[arg_name] = [elt.s for elt in kw.value.elts if not isinstance(elt, ast.Call)]
            if args:
                build_rules[rule_name].append(args)

    if build_rules:
        for rule_name, rule_instances_args in build_rules.items():
            for args in rule_instances_args:
                name = args.get('name')
                if not name:
                    continue
                license_files = args.get('licenses')
                yield BazelPackage(
                    name=name,
                    declared_license=license_files,
                    root_path=fileutils.parent_directory(location)
                )
    else:
        # If we don't find anything in the BUCK file, we yield a Package with
        # the parent directory as the name, like the default implementation of
        # `recognize()` for `BaseBuildManifestPackage`
        yield BazelPackage(
            # we use the parent directory as a name
            name=fileutils.file_name(fileutils.parent_directory(location))
        )


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
