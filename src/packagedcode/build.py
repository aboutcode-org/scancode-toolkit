#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from collections import defaultdict
import ast
import io
import json
import logging
import os

from packageurl import PackageURL
from pygments import highlight
from pygments.formatter import Formatter
from pygments.lexers import GroovyLexer
from pygments.token import Token
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
    file_patterns = tuple()

    @classmethod
    def recognize(cls, location):
        if not cls.is_manifest(location):
            return

        # we use the parent directory as a name
        name = fileutils.file_name(fileutils.parent_directory(location))
        # we could use checksums as version in the future
        version = None

        # there is an optional array of license file names in targets that we could use
        # declared_license = None
        # there is are dependencies we could use
        # dependencies = []
        yield cls(
            name=name,
            version=version)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)


@attr.s()
class AutotoolsPackage(BaseBuildManifestPackage, models.PackageManifest):
    file_patterns = ('configure', 'configure.ac',)
    default_type = 'autotools'


starlark_rule_types = [
    'binary',
    'library'
]


def check_rule_name_ending(rule_name):
    """
    Return True if `rule_name` ends with a rule type from `starlark_rule_types`

    Return False otherwise
    """
    for rule_type in starlark_rule_types:
        if rule_name.endswith(rule_type):
            return True
    return False


@attr.s()
class StarlarkManifestPackage(BaseBuildManifestPackage, models.PackageManifest):

    @classmethod
    def recognize(cls, location):
        if not cls.is_manifest(location):
            return

        # Thanks to Starlark being a Python dialect, we can use the `ast`
        # library to parse it
        with open(location, 'rb') as f:
            tree = ast.parse(f.read())

        build_rules = defaultdict(list)
        for statement in tree.body:
            # We only care about function calls or assignments to functions whose
            # names ends with one of the strings in `rule_types`
            if (isinstance(statement, ast.Expr)
                    or isinstance(statement, ast.Call)
                    or isinstance(statement, ast.Assign)
                    and isinstance(statement.value, ast.Call)
                    and isinstance(statement.value.func, ast.Name)):
                rule_name = statement.value.func.id
                # Ensure that we are only creating packages from the proper
                # build rules
                if not check_rule_name_ending(rule_name):
                    continue
                # Process the rule arguments
                args = {}
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
                    yield cls(
                        name=name,
                        declared_license=license_files,
                        root_path=fileutils.parent_directory(location)
                    )
        else:
            # If we don't find anything in the manifest file, we yield a Package with
            # the parent directory as the name
            yield cls(
                name=fileutils.file_name(fileutils.parent_directory(location))
            )

    def compute_normalized_license(self):
        """
        Return a normalized license expression string detected from a list of
        declared license items.
        """
        declared_license = self.declared_license
        manifest_parent_path = self.root_path

        if not declared_license or not manifest_parent_path:
            return

        license_expressions = []
        for license_file in declared_license:
            license_file_path = os.path.join(manifest_parent_path, license_file)
            if os.path.exists(license_file_path) and os.path.isfile(license_file_path):
                licenses = get_licenses(license_file_path)
                license_expressions.extend(licenses.get('license_expressions', []))

        return combine_expressions(license_expressions)


@attr.s()
class BazelPackage(StarlarkManifestPackage):
    file_patterns = ('BUILD',)
    default_type = 'bazel'


@attr.s()
class BuckPackage(StarlarkManifestPackage):
    file_patterns = ('BUCK',)
    default_type = 'buck'


@attr.s()
class MetadataBzl(BaseBuildManifestPackage, models.PackageManifest):
    file_patterns = ('METADATA.bzl',)
    # TODO: Not sure what the default type should be, change this to something
    # more appropriate later
    default_type = 'METADATA.bzl'

    @classmethod
    def recognize(cls, location):
        if not cls.is_manifest(location):
            return

        with open(location, 'rb') as f:
            tree = ast.parse(f.read())

        metadata_fields = {}
        for statement in tree.body:
            if not (hasattr(statement, 'targets') and isinstance(statement, ast.Assign)):
                continue
            # We are looking for a dictionary assigned to the variable `METADATA`
            for target in statement.targets:
                if not (target.id == 'METADATA' and isinstance(statement.value, ast.Dict)):
                    continue
                # Once we find the dictionary assignment, get and store its contents
                statement_keys = statement.value.keys
                statement_values = statement.value.values
                for statement_k, statement_v in zip(statement_keys, statement_values):
                    if isinstance(statement_k, ast.Str):
                        key_name = statement_k.s
                    # The list values in a `METADATA.bzl` file seem to only contain strings
                    if isinstance(statement_v, ast.List):
                        value = []
                        for e in statement_v.elts:
                            if not isinstance(e, ast.Str):
                                continue
                            value.append(e.s)
                    if isinstance(statement_v, ast.Str):
                        value = statement_v.s
                    metadata_fields[key_name] = value

        parties = []
        maintainers = metadata_fields.get('maintainers', [])
        for maintainer in maintainers:
            parties.append(
                models.Party(
                    type=models.party_org,
                    name=maintainer,
                    role='maintainer',
                )
            )

        # TODO: Create function that determines package type from download URL,
        # then create a package of that package type from the metadata info
        yield cls(
            type=metadata_fields.get('upstream_type', ''),
            name=metadata_fields.get('name', ''),
            version=metadata_fields.get('version', ''),
            declared_license=metadata_fields.get('licenses', []),
            parties=parties,
            homepage_url=metadata_fields.get('upstream_address', ''),
            # TODO: Store 'upstream_hash` somewhere
        )

    def compute_normalized_license(self):
        """
        Return a normalized license expression string detected from a list of
        declared license strings.
        """
        if not self.declared_license:
            return

        detected_licenses = []
        for declared in self.declared_license:
            detected_license = models.compute_normalized_license(declared)
            detected_licenses.append(detected_license)

        if detected_licenses:
            return combine_expressions(detected_licenses)


class BuildGradleFormatter(Formatter):
    def format(self, tokens, outfile):
        quoted = lambda x: (x.startswith('"') and x.endswith('"')) or (x.startswith("'") and value.endswith("'"))
        start_dependencies_block = False
        lines = []
        current_dep_line = []
        for ttype, value in tokens:
            if not start_dependencies_block:
                if ttype == Token.Name and value == 'dependencies':
                    # If we are at the start of the 'dependencies' code block,
                    # we continue executing the rest of the dependency
                    # collection code within this for-loop
                    start_dependencies_block = True
                    continue
                else:
                    # If we do not see the 'dependencies' block yet, we continue
                    # and do not execute the code within this for-loop.
                    continue

            if ttype == Token.Name:
                current_dep_line.append(value)
            elif ttype in (Token.Literal.String.Single, Token.Literal.String.Double,):
                if quoted(value):
                    value = value[1:-1]
                current_dep_line.append(value)
            elif ttype == Token.Text and value == '\n' and current_dep_line:
                # If we are looking at the end of a dependency declaration line,
                # append the info from the line we are looking at to our main collection
                # of dependency info and reset `current_dep_line` so we can
                # start collecting info for the next line
                lines.append(current_dep_line)
                current_dep_line = []
            elif ttype == Token.Operator and value == '}':
                # we are at the end of the dependencies block, so we can back out
                # and return the data we collected
                break
            else:
                # Ignore all other tokens and values that we do not care for
                continue
        json.dump(lines, outfile)


def build_package(cls, dependencies):
    package_dependencies = []
    for dependency_line in dependencies:
        if len(dependency_line) != 2:
            continue

        dependency_type, dependency = dependency_line
        namespace, name, version = dependency.split(':')

        is_runtime = True
        is_optional = False
        if 'test' in dependency_type:
            is_runtime = False
            is_optional = True

        package_dependencies.append(
            models.DependentPackage(
                purl=PackageURL(
                    type='build.gradle',
                    namespace=namespace,
                    name=name,
                    version=version
                ).to_string(),
                scope='dependencies',
                requirement=version,
                is_runtime=is_runtime,
                is_optional=is_optional,
            )
        )

    yield cls(
        dependencies=package_dependencies,
    )


@attr.s()
class BuildGradle(BaseBuildManifestPackage, models.PackageManifest):
    file_patterns = ('build.gradle',)
    extensions = ('.gradle',)
    # TODO: Not sure what the default type should be, change this to something
    # more appropriate later
    default_type = 'build.gradle'

    @classmethod
    def recognize(cls, location):
        if not cls.is_manifest(location):
            return
        with io.open(location, encoding='utf-8') as loc:
            file_contents = loc.read()
        dependencies = highlight(
            file_contents, GroovyLexer(), BuildGradleFormatter())
        dependencies = json.loads(dependencies)
        return build_package(cls, dependencies)
