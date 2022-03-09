#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging

from packageurl import PackageURL
from pygmars import Token
from pygmars.parse import Parser
from pygments import lex
from pygments.lexers import GroovyLexer
import attr

from packagedcode import models
from packagedcode.build import BaseBuildManifestPackageData


TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


grammar = """
    LIT-STRING: {<LITERAL-STRING-SINGLE|LITERAL-STRING-DOUBLE>}

    PACKAGE-IDENTIFIER: {<OPERATOR> <TEXT>? <NAME-LABEL> <TEXT>? <LIT-STRING>}
    DEPENDENCY-1: {<PACKAGE-IDENTIFIER>{3} <OPERATOR>}

    DEPENDENCY-2: {<NAME> <TEXT> <LIT-STRING> <TEXT>}

    DEPENDENCY-3: {<NAME> <TEXT>? <OPERATOR> <LIT-STRING> <OPERATOR>}

    DEPENDENCY-4: {<NAME> <TEXT> <NAME-LABEL> <TEXT> <LIT-STRING> <PACKAGE-IDENTIFIER> <PACKAGE-IDENTIFIER> <OPERATOR>? <TEXT>}

    DEPENDENCY-5: {<NAME> <TEXT> <NAME> <OPERATOR> <NAME-ATTRIBUTE>}

    NESTED-DEPENDENCY-1: {<NAME> <OPERATOR> <DEPENDENCY-1>+ }
"""


def get_tokens(contents):
    for i, (token, value) in enumerate(lex(contents, GroovyLexer())):
        yield i, token, value


def get_pygmar_tokens(contents):
    tokens = Token.from_pygments_tokens(get_tokens(contents))
    for token in tokens:
        if token.label == 'NAME' and token.value == 'dependencies':
            token.label = 'DEPENDENCIES-START'
        yield token


def get_parse_tree(build_gradle_location):
    # Open build.gradle and create a Pygmars parse tree from its contents
    with open(build_gradle_location) as f:
        contents = f.read()
    parser = Parser(grammar, trace=0)
    return parser.parse(list(get_pygmar_tokens(contents)))


def is_literal_string(string):
    return string == 'LITERAL-STRING-SINGLE' or string == 'LITERAL-STRING-DOUBLE'


def remove_quotes(string):
    """
    Remove starting and ending quotes from `string`.

    If `string` has no starting or ending quotes, return `string`.
    """
    quoted = lambda x: (x.startswith('"') and x.endswith('"')) or (x.startswith("'") and x.endswith("'"))
    if quoted:
        return string[1:-1]
    else:
        return string


def get_dependencies_from_parse_tree(parse_tree):
    dependencies = []
    in_dependency_block = False
    brackets_counter = 0
    first_bracket_seen = False
    in_nested_dependency = False
    nested_dependency_parenthesis_counter = 0
    first_parenthesis_seen = False
    for tree_node in parse_tree:
        if tree_node.label == 'DEPENDENCIES-START':
            in_dependency_block = True
            continue

        if in_dependency_block:
            if tree_node.label == 'OPERATOR':
                if tree_node.value == '{':
                    if not first_bracket_seen:
                        first_bracket_seen = True
                    brackets_counter += 1
                elif tree_node.value == '}':
                    brackets_counter -= 1

            if brackets_counter == 0 and first_bracket_seen:
                break

            # TODO: Find way to simplify logic with DEPENDENCY-1
            if tree_node.label == 'NESTED-DEPENDENCY-1':
                dependency = {}
                in_nested_dependency = True
                scope = None
                last_key = None
                for child_node in tree_node.leaves():
                    if child_node.label == 'NAME':
                        scope = child_node.value

                    if child_node.label == 'OPERATOR' and child_node.value == '(':
                        if not first_parenthesis_seen:
                            first_parenthesis_seen = True
                        nested_dependency_parenthesis_counter += 1

                    if child_node.label == 'NAME-LABEL':
                        value = child_node.value
                        if value == 'group:':
                            last_key = 'namespace'
                        if value == 'name:':
                            last_key = 'name'
                        if value == 'version:':
                            last_key = 'version'

                    if is_literal_string(child_node.label):
                        dependency[last_key] = remove_quotes(child_node.value)
                if scope:
                    dependency['scope'] = scope
                dependencies.append(dependency)

            if in_nested_dependency:
                if tree_node.label == 'OPERATOR' and tree_node.value == ')':
                    nested_dependency_parenthesis_counter -= 1

                if nested_dependency_parenthesis_counter == 0 and first_parenthesis_seen:
                    in_nested_dependency = False
                    scope = None

            if tree_node.label == 'DEPENDENCY-1':
                name_label_to_dep_field_name = {
                    'group:': 'namespace',
                    'name:': 'name',
                    'version:': 'version'
                }
                dependency = {}
                last_key = None
                for child_node in tree_node.leaves():
                    value = child_node.value
                    if child_node.label == 'NAME-LABEL':
                        last_key = name_label_to_dep_field_name.get(value, '')
                    if is_literal_string(child_node.label):
                        if last_key:
                            dependency[last_key] = remove_quotes(value)
                if in_nested_dependency and scope:
                    dependency['scope'] = scope
                dependencies.append(dependency)

            if tree_node.label == 'DEPENDENCY-2':
                dependency = {}
                for child_node in tree_node.leaves():
                    if child_node.label == 'NAME':
                        dependency['scope'] = child_node.value
                    if is_literal_string(child_node.label):
                        value = child_node.value
                        value = remove_quotes(value)

                        namespace = ''
                        name = ''
                        version = ''
                        split_value = value.split(':')
                        split_value_length = len(split_value)
                        if split_value_length == 4:
                            # We are assuming `value` is in the form of "namespace:name:version:module"
                            # We are currently not reporting down to the module level
                            namespace, name, version, _ = split_value
                        if split_value_length == 3:
                            # We are assuming `value` is in the form of "namespace:name:version"
                            namespace, name, version = split_value
                        if split_value_length == 2:
                            # We are assuming `value` is in the form of "namespace:name"
                            namespace, name = split_value

                        dependency['namespace'] = namespace
                        dependency['name'] = name
                        dependency['version'] = version
                dependencies.append(dependency)

            if tree_node.label == 'DEPENDENCY-3':
                dependency = {}
                for child_node in tree_node.leaves():
                    if child_node.label == 'NAME':
                        dependency['scope'] = child_node.value
                    if is_literal_string(child_node.label):
                        value = child_node.value
                        value = remove_quotes(value)
                        # We are assuming `value` is in the form of "namespace:name:version"
                        split_dependency_string = value.split(':')
                        if len(split_dependency_string) != 3:
                            break
                        namespace, name, version = split_dependency_string
                        dependency['namespace'] = namespace
                        dependency['name'] = name
                        dependency['version'] = version
                dependencies.append(dependency)

            # TODO: See if you can refactor logic with DEPENDENCY-1
            if tree_node.label == 'DEPENDENCY-4':
                dependency = {}
                last_key = None
                for child_node in tree_node.leaves():
                    if child_node.label == 'NAME':
                        dependency['scope'] = child_node.value
                    if child_node.label == 'NAME-LABEL':
                        value = child_node.value
                        if value == 'group:':
                            last_key = 'namespace'
                        if value == 'name:':
                            last_key = 'name'
                        if value == 'version:':
                            last_key = 'version'
                    if is_literal_string(child_node.label):
                        dependency[last_key] = remove_quotes(child_node.value)
                dependencies.append(dependency)

            if tree_node.label == 'DEPENDENCY-5':
                dependency = {}
                for child_node in tree_node.leaves():
                    if child_node.label == 'NAME':
                        dependency['scope'] = child_node.value
                    if child_node.label == 'NAME-ATTRIBUTE':
                        dependency['name'] = child_node.value
                dependencies.append(dependency)
    return dependencies


def get_dependencies(build_gradle_location):
    parse_tree = get_parse_tree(build_gradle_location)
    # Parse `parse_tree` for dependencies and print them
    return get_dependencies_from_parse_tree(parse_tree)


def build_package(cls, dependencies):
    package_dependencies = []
    for dependency in dependencies:
        # Ignore collected dependencies that do not have a name
        name = dependency.get('name', '')
        if not name:
            continue

        namespace = dependency.get('namespace', '')
        version =  dependency.get('version', '')
        scope = dependency.get('scope', '')
        is_runtime = True
        is_optional = False
        if 'test' in scope.lower():
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
                scope=scope,
                extracted_requirement=version,
                is_runtime=is_runtime,
                is_optional=is_optional,
            )
        )

    yield cls(
        dependencies=package_dependencies,
    )


@attr.s()
class BuildGradle(BaseBuildManifestPackageData, models.PackageDataFile):
    file_patterns = ('build.gradle',)
    extensions = ('.gradle',)
    # TODO: Not sure what the default type should be, change this to something
    # more appropriate later
    default_type = 'build.gradle'

    @classmethod
    def recognize(cls, location):
        if not cls.is_package_data_file(location):
            return
        dependencies = get_dependencies(location)
        return build_package(cls, dependencies)
