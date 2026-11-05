#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import os
import sys

from packageurl import PackageURL
from pygmars import Token
from pygmars.parse import Parser
from pygments import lex

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from packagedcode import groovy_lexer
from packagedcode import models

# Tracing flags
TRACE = False or os.environ.get('SCANCODE_DEBUG_PACKAGE_GRADLE', False)

# set to 1 to enable pygmars deep tracing
TRACE_DEEP = 0
if os.environ.get('SCANCODE_DEBUG_PACKAGE_GRADLE_DEEP'):
    TRACE_DEEP = 1
    TRACE = False


# Tracing flags
def logger_debug(*args):
    pass


if TRACE or TRACE_DEEP:
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
    if True:
        printer = print
    else:
        printer = logger.debug

    def logger_debug(*args):
        return printer(' '.join(isinstance(a, str) and a or repr(a) for a in args))

# TODO: split groovy and kotlin handlers


class BuildGradleHandler(models.DatafileHandler):
    datasource_id = 'build_gradle'
    path_patterns = ('*/build.gradle', '*/build.gradle.kts',)
    # TODO: Not sure what the default type should be, change this to something
    # more appropriate later
    default_package_type = 'maven'
    primary_language = 'Java'
    description = 'Gradle build script'

    @classmethod
    def parse(cls, location, package_only=False):
        dependencies = get_dependencies(location)
        return build_package(cls, dependencies, package_only)

    # TODO: handle complex cases of nested builds with many packages
    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        models.DatafileHandler.assign_package_to_parent_tree(
            package=package,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
        )


grammar = """
    LIT-STRING: {<LITERAL-STRING-SINGLE|LITERAL-STRING-DOUBLE>}

    PACKAGE-IDENTIFIER: {<OPERATOR> <TEXT>? <NAME-LABEL> <TEXT>? <LIT-STRING>}
    DEPENDENCY-1: {<PACKAGE-IDENTIFIER>{3} <OPERATOR>}

    DEPENDENCY-2: {<NAME> <TEXT> <LIT-STRING> <TEXT>}

    DEPENDENCY-3: {<NAME> <TEXT>? <OPERATOR> <LIT-STRING> <OPERATOR>}

    DEPENDENCY-4: {<NAME> <TEXT> <NAME-LABEL> <TEXT> <LIT-STRING> <PACKAGE-IDENTIFIER> <PACKAGE-IDENTIFIER> <OPERATOR>? <TEXT>}

    DEPENDENCY-VERSION-CATALOG: {<NAME> <TEXT> <NAME> <OPERATOR> <NAME-ATTRIBUTE> (<OPERATOR> <NAME-ATTRIBUTE>)*}

    NESTED-DEPENDENCY-1: {<NAME> <OPERATOR> <DEPENDENCY-1>+ }
"""


def get_tokens(contents):
    """
    Yield tuples of (position, Token, value) from lexing a ``contents`` string.
    """
    for i, (token, value) in enumerate(lex(contents, groovy_lexer.GroovyLexer())):
        yield i, token, value


def get_pygmar_tokens(contents):
    tokens = Token.from_pygments_tokens(get_tokens(contents))
    for token in tokens:
        if token.label == 'NAME' and token.value == 'dependencies':
            token.label = 'DEPENDENCIES-START'
        yield token


def get_parse_tree(build_gradle_location, trace=TRACE_DEEP):
    """
    Return a Pygmars parse tree from a ``build_gradle_location`` build.gradle
    """
    with open(build_gradle_location) as f:
        contents = f.read()

    parser = Parser(grammar, trace=trace)

    lexed_tokens = list(get_pygmar_tokens(contents))
    if TRACE:
        logger_debug(f'get_parse_tree: lexed_tokens: {lexed_tokens}')

    parse_tree = parser.parse(lexed_tokens)

    if TRACE:
        logger_debug(f'get_parse_tree: parse_tree: {parse_tree}')

    return parse_tree


def is_literal_string(string):
    return string in ('LITERAL-STRING-SINGLE', 'LITERAL-STRING-DOUBLE')


def remove_quotes(string):
    """
    Remove starting and ending quotes from ``string``.

    If ``string`` has no starting or ending quotes, return ``string``.
    """
    quoted = lambda x: (
        (x.startswith('"') and x.endswith('"'))
        or (x.startswith("'") and x.endswith("'"))
    )
    if quoted:
        return string[1:-1]
    else:
        return string


def get_dependencies_from_parse_tree(parse_tree):
    """
    Yield dependency mappings from a Pygmars parse tree.
    """
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
            if tree_node.label.startswith('OPERATOR'):
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
                yield dependency

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
                yield dependency

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
                yield dependency

            if tree_node.label == 'DEPENDENCY-3':
                dependency = {}
                for child_node in tree_node.leaves():
                    if TRACE:
                        logger_debug('DEPENDENCY-3:', child_node)
                    if child_node.label == 'NAME':
                        dependency['scope'] = child_node.value

                    elif is_literal_string(child_node.label):

                        value = child_node.value
                        value = remove_quotes(value)

                        # We are assuming `value` is in the form of "namespace:name:version"
                        split_dependency_string = value.split(':')
                        if TRACE:
                            logger_debug('DEPENDENCY-3: is_literal_string: value', value, 'split_dependency_string:', split_dependency_string)
                        length = len(split_dependency_string)
                        if length == 3:
                            namespace, name, version = split_dependency_string
                            dependency['namespace'] = namespace
                            dependency['name'] = name
                            dependency['version'] = version
                        elif length == 2:
                            namespace, name = split_dependency_string
                            dependency['namespace'] = namespace
                            dependency['name'] = name

                yield dependency

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
                yield dependency

            if tree_node.label == 'DEPENDENCY-VERSION-CATALOG':
                dependency = {}
                scope = None
                name_parts = []
                for child_node in tree_node.leaves():
                    if child_node.label == 'NAME':
                        if not scope:
                            scope = child_node.value
                        else:
                            name_parts.append(child_node.value)
                    elif child_node.label == 'NAME-ATTRIBUTE':
                        name_parts.append(child_node.value)
                if scope and name_parts:
                    full_name = '.'.join(name_parts)
                    dependency['scope'] = scope
                    dependency['name'] = full_name
                    dependency['namespace'] = ''
                    dependency['version'] = ''
                    yield dependency


def parse_version_catalog(build_gradle_location):
    """
    Parse gradle/libs.versions.toml and return a mapping of alias -> {group, name, version}.
    Returns empty dict if file not found.
    """
    gradle_dir = os.path.dirname(build_gradle_location)
    catalog_locations = [
        os.path.join(gradle_dir, 'gradle', 'libs.versions.toml'),
        os.path.join(os.path.dirname(gradle_dir), 'gradle', 'libs.versions.toml'),
    ]

    catalog_path = None
    for loc in catalog_locations:
        if os.path.exists(loc):
            catalog_path = loc
            break

    if not catalog_path:
        return {}

    with open(catalog_path, 'rb') as f:
        catalog = tomllib.load(f)

    libraries = catalog.get('libraries', {})
    versions = catalog.get('versions', {})
    alias_map = {}

    for alias, lib_spec in libraries.items():
        normalized_alias = alias.replace('-', '.')

        if isinstance(lib_spec, str):
            parts = lib_spec.split(':')
            if len(parts) >= 2:
                alias_map[normalized_alias] = {
                    'namespace': parts[0],
                    'name': parts[1],
                    'version': parts[2] if len(parts) > 2 else '',
                }

        elif isinstance(lib_spec, dict):
            module = lib_spec.get('module', '')
            if module:
                module_parts = module.split(':')
                group = module_parts[0] if len(module_parts) >= 1 else ''
                name = module_parts[1] if len(module_parts) >= 2 else ''
            else:
                group = lib_spec.get('group', '')
                name = lib_spec.get('name', '')

            version = lib_spec.get('version', '')
            if isinstance(version, dict) and 'ref' in version:
                version = versions.get(version['ref'], '')

            alias_map[normalized_alias] = {
                'namespace': group,
                'name': name,
                'version': version,
            }

    return alias_map


def get_dependencies(build_gradle_location):
    """
    Parse dependencies from build.gradle, resolving version catalog references.
    """
    parse_tree = get_parse_tree(build_gradle_location)
    raw_dependencies = list(get_dependencies_from_parse_tree(parse_tree))
    catalog = parse_version_catalog(build_gradle_location)

    resolved_dependencies = []
    for dep in raw_dependencies:
        name = dep.get('name', '')

        if name.startswith('libs.'):
            alias = name[5:]
            if alias in catalog:
                catalog_entry = catalog[alias]
                resolved_dependencies.append({
                    'namespace': catalog_entry['namespace'],
                    'name': catalog_entry['name'],
                    'version': catalog_entry['version'],
                    'scope': dep.get('scope', ''),
                })
                continue

        resolved_dependencies.append(dep)

    return resolved_dependencies


def build_package(cls, dependencies, package_only=False):
    """
    Yield PackageData from a ``dependencies`` list of mappings.
    """
    package_dependencies = []
    for dependency in dependencies:
        name = dependency.get('name', '')
        if not name:
            continue

        namespace = dependency.get('namespace', '')
        version = dependency.get('version', '')
        scope = dependency.get('scope', '')

        is_runtime = True
        is_optional = False
        if 'test' in scope.lower():
            is_runtime = False
            is_optional = True

        is_pinned = bool(version)

        resolved_package_data = {}
        if is_pinned:
            resolved_package = models.PackageData.from_data(
                dict(
                    datasource_id=cls.datasource_id,
                    type=cls.default_package_type,
                    namespace=namespace,
                    name=name,
                    version=version,
                ),
                package_only,
            )
            resolved_package_data = resolved_package.to_dict()

        package_dependencies.append(
            models.DependentPackage(
                purl=PackageURL(
                    type=cls.default_package_type,
                    namespace=namespace,
                    name=name,
                    version=version,
                ).to_string(),
                scope=scope,
                extracted_requirement=version,
                is_runtime=is_runtime,
                is_optional=is_optional,
                is_pinned=is_pinned,
                resolved_package=resolved_package_data,
            )
        )

    package_data = dict(
        datasource_id=cls.datasource_id,
        type=cls.default_package_type,
        primary_language=BuildGradleHandler.default_primary_language,
        dependencies=package_dependencies,
    )
    yield models.PackageData.from_data(package_data, package_only)

