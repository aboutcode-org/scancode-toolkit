import os
import sys
import logging
import re
import traceback
from packageurl import PackageURL

from luaparser import ast
from packagedcode import models

# Debug configuration - set via environment variables
SCANCODE_DEBUG_PACKAGE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)
TRACE = SCANCODE_DEBUG_PACKAGE


def logger_debug(*args):
    """Dummy function that does nothing by default."""
    pass


logger = logging.getLogger(__name__)

# Configure logging when debug is enabled
if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        """Redefine to actually log debug messages."""
        return logger.debug(
            ' '.join(isinstance(a, str) and a or repr(a) for a in args)
        )


class RockspecHandler(models.DatafileHandler):
    datasource_id = 'luarocks_rockspec'
    path_patterns = ('*.rockspec',)
    default_package_type = 'luarocks'
    default_primary_language = 'Lua'
    description = 'LuaRocks rockspec file'
    documentation_url = 'https://github.com/luarocks/luarocks/blob/main/docs/rockspec_format.md'

    @classmethod
    def parse(cls, location, package_only=False):
        """Parse rockspec file and yield PackageData object."""
        parser = RockspecParser(location)
        parsed_data = parser.parse()

        # mandatory fields in rockspec files
        name = parsed_data.get('package')
        version = parsed_data.get('version')
        vcs_url = parsed_data.get('vcs_url')

        # Extract optional fields
        description = parsed_data.get('description')
        homepage_url = parsed_data.get('homepage_url')
        extracted_license_statement = parsed_data.get('license')

        parsed_dependencies = parsed_data.get('dependencies') or []

        if parsed_dependencies:
            dependencies = cls._build_dependent_packages(parsed_dependencies)
        else:
            dependencies = []

        extra_data = cls._build_extra_data(parsed_data)

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            primary_language=cls.default_primary_language,
            description=description,
            homepage_url=homepage_url,
            vcs_url=vcs_url,
            extracted_license_statement=extracted_license_statement,
            dependencies=dependencies,
            extra_data=extra_data,
        )

        yield models.PackageData.from_data(package_data, package_only)

    @classmethod
    def _build_dependent_packages(cls, parsed_dependencies):
        """Convert parsed dependency dicts to DependentPackage objects."""
        dependencies = []

        for dep_dict in parsed_dependencies:
            dep_obj = cls._create_dependent_package(dep_dict)
            dependencies.append(dep_obj)

        return dependencies

    @classmethod
    def _create_dependent_package(cls, dep_components):
        """Create DependentPackage from parsed dependency components dict."""
        name = dep_components.get('name')
        version_number = dep_components.get('version_number')
        version_spec = dep_components.get('version_spec')

        purl_str = cls._create_purl_string(name, version_number)
        # Determine if pinned (exact version with == operator)
        is_pinned = bool(version_spec and '==' in str(version_spec))

        return models.DependentPackage(
            purl=purl_str,
            extracted_requirement=version_spec,
            scope='dependencies',
            is_runtime=True,
            is_optional=False,
            is_pinned=is_pinned,
            is_direct=True,
        )

    @classmethod
    def _build_extra_data(cls, parsed_data):
        """Extract optional rockspec metadata into extra_data dict."""
        extra_data = {}

        rockspec_format = parsed_data.get('rockspec_format')
        if rockspec_format:
            extra_data['rockspec_format'] = rockspec_format

        platforms = parsed_data.get('supported_platforms')
        if platforms:
            extra_data['supported_platforms'] = platforms

        # TODO: Extract build table fields and add to extra_data
        # - build.type: the build system type (e.g., "builtin", "cmake", "make")
        # - build.copy_directories: directories to include in installation
        # - build.platforms: platform-specific build configurations

        return extra_data

    @classmethod
    def _create_purl_string(cls, package_name, package_version):
        """Return PURL string for luarocks package. Raises ValueError if package_name is empty."""
        if not package_name:
            raise ValueError('Package name is required for PURL creation')

        purl = PackageURL(
            type=cls.default_package_type,
            name=package_name,
            version=package_version
        )
        return purl.to_string()



class ParseError:
    """Structured error representation."""

    ERROR_MANDATORY_FIELD_MISSING = 'mandatory_field_missing'
    ERROR_PARSE_FAILED = 'parse_failed'
    ERROR_TABLE_EXTRACTION = 'table_extraction_failed'

    def __init__(self, error_type, field, message):
        self.error_type = error_type
        self.field = field
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"ParseError({self.error_type}, {self.field}: {self.message})"


class RockspecParser:
    """Parse LuaRocks rockspec files using Lua AST."""

    def __init__(self, rockspec_path):
        self.rockspec_path = rockspec_path
        self.ast_tree = None
        self.errors = []

    def parse(self):
        """Read file, parse AST, extract all rockspec fields and return data dict."""
        try:
            code = self._read_file()
            self.ast_tree = self._parse_lua(code)

            data = {
                'package': self._extract_package(),
                'version': self._extract_version(),
                'rockspec_format': self._extract_rockspec_format(),
                'supported_platforms': self._extract_supported_platforms(),
                'vcs_url': self._extract_source_url(),
                'description': self._extract_description(),
                'license': self._extract_license(),
                'homepage_url': self._extract_homepage(),
                'dependencies': self._extract_dependencies(),
            }
            return data
        except Exception as e:
            self.errors.append(ParseError(ParseError.ERROR_PARSE_FAILED, 'parse', str(e)))
            traceback.print_exc()
            return {}

    def _read_file(self):
        """Read and return rockspec file content as string."""
        try:
            with open(self.rockspec_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.rockspec_path}")
        except IOError as e:
            raise IOError(f"Error reading file: {e}")

    def _parse_lua(self, code):
        """Parse Lua code string into AST tree."""
        try:
            return ast.parse(code)
        except Exception as e:
            raise RuntimeError(f"Lua parse error: {e}")

    def _find_assignment(self, var_name):
        """Return (target_node, value_node) tuple for variable assignment or None."""
        if not self.ast_tree:
            return None

        for node in ast.walk(self.ast_tree):
            # Skip nodes that aren't assignments
            if not hasattr(node, 'targets') or not hasattr(node, 'values'):  # type: ignore
                continue

            # Skip if no targets in this assignment
            if not node.targets:  # type: ignore
                continue

            # Check each target to find our variable
            for idx, target in enumerate(node.targets):  # type: ignore
                # Skip if target doesn't have an id attribute
                if not hasattr(target, 'id'):
                    continue

                # Found the variable we're looking for
                if target.id == var_name:  # type: ignore
                    # Get the corresponding value (or first value if not enough values)
                    value = node.values[idx] if idx < len(node.values) else (node.values[0] if node.values else None)  # type: ignore
                    return (target, value)

        return None


    def _extract_string_value(self, node):
        """Extract and return string value from String AST node."""
        if not node or type(node).__name__ != 'String':
            return None

        s_val = node.s if hasattr(node, 's') else None
        if isinstance(s_val, bytes):
            return s_val.decode('utf-8')
        return str(s_val) if s_val else None

    def _extract_table_values(self, table_node):
        """Extract and return dict of key-value pairs from Table AST node."""
        result = {}

        if not table_node or type(table_node).__name__ != 'Table':
            return result

        if not hasattr(table_node, 'fields'):
            return result

        try:
            for field in table_node.fields:
                field_type = type(field).__name__

                # Only process Field type nodes because they represent key-value pairs or array entries
                if field_type != 'Field':
                    continue

                key_node = field.key if hasattr(field, 'key') else None
                value_node = field.value if hasattr(field, 'value') else None

                # Skip fields without values
                if not value_node:
                    continue

                # Extract value (works for both hash-style and array-style)
                extracted_value = self._extract_value(value_node)
                if extracted_value is None:
                    continue

                # Hash-style field: {key = value}
                if key_node:
                    key = self._extract_key(key_node)
                    if key is not None:
                        result[key] = extracted_value
                # Array-style field: {value}
                else:
                    result[len(result)] = extracted_value

        except Exception as e:
            error_msg = f'Error extracting table values: {e}'
            self.errors.append(ParseError(ParseError.ERROR_TABLE_EXTRACTION, 'table', error_msg))

        return result

    def _extract_key(self, key_node):
        """Extract and return key from field key node."""
        if not key_node:
            return None

        node_type = type(key_node).__name__

        if node_type == 'String':
            return self._extract_string_value(key_node)
        elif node_type == 'Name' or node_type == 'Id':
            return key_node.id if hasattr(key_node, 'id') else None
        elif node_type == 'Number':
            n_val = key_node.n if hasattr(key_node, 'n') else None
            return str(n_val) if n_val is not None else None

        return None

    def _extract_value(self, node):
        """Extract and return value from any AST node type."""
        if node is None:
            return None

        node_type = type(node).__name__

        # Handle each node type
        if node_type == 'String':
            return self._extract_string_value(node)

        elif node_type == 'Number':
            number_value = node.n if hasattr(node, 'n') else None
            return number_value

        elif node_type == 'Boolean':
            bool_value = node.value if hasattr(node, 'value') else None
            return bool_value

        elif node_type == 'Table':
            return self._extract_table_values(node)
        # special concat case found in the some rockspec files in the wild
        elif node_type == 'Concat':
            return self._extract_concat(node)

        elif node_type == 'Name':
            var_name = node.id if hasattr(node, 'id') else None
            if var_name:
                return self._get_variable_value(var_name)

        # Unknown node type
        return None

    def _get_variable_value(self, var_name):
        """Look up variable by name and return its extracted value."""
        assignment = self._find_assignment(var_name)
        if not assignment:
            return None

        _, value = assignment
        return self._extract_value(value)

    def _extract_concat(self, concat_node):
        """Extract and return concatenated string from Concat AST node."""
        if not concat_node or type(concat_node).__name__ != 'Concat':
            return None

        left_node = concat_node.left if hasattr(concat_node, 'left') else None
        right_node = concat_node.right if hasattr(concat_node, 'right') else None

        # Recursively extract values from both sides
        left_value = self._extract_value(left_node)
        right_value = self._extract_value(right_node)

        # Build result from available values
        has_left = left_value is not None
        has_right = right_value is not None

        if has_left and has_right:
            return str(left_value) + str(right_value)
        elif has_left:
            return str(left_value)
        elif has_right:
            return str(right_value)
        else:
            return None

    def _extract_package(self):
        """Extract and return mandatory package name field."""
        assignment = self._find_assignment('package')
        if not assignment:
            self.errors.append(ParseError(ParseError.ERROR_MANDATORY_FIELD_MISSING, 'package', 'Missing mandatory field: package'))
            return None

        _, value = assignment
        result = self._extract_value(value)
        return str(result) if result else None

    def _extract_version(self):
        """Extract and return mandatory version field."""
        assignment = self._find_assignment('version')
        if not assignment:
            self.errors.append(ParseError(ParseError.ERROR_MANDATORY_FIELD_MISSING, 'version', 'Missing mandatory field: version'))
            return None

        _, value = assignment
        result = self._extract_value(value)
        return str(result) if result else None

    def _extract_rockspec_format(self):
        """Extract and return optional rockspec_format field."""
        assignment = self._find_assignment('rockspec_format')
        if not assignment:
            return None

        _, value = assignment
        result = self._extract_value(value)
        return str(result) if result else None

    def _extract_supported_platforms(self):
        """Extract and return supported_platforms as sorted string list. (optional table)"""
        assignment = self._find_assignment('supported_platforms')
        if not assignment:
            return []

        _, platform_table_node = assignment
        platform_dict = self._extract_table_values(platform_table_node)

        # Sort platforms by numeric index order
        return self._sort_by_numeric_index(platform_dict)

    def _extract_source_url(self):
        """Extract and return mandatory source.url field."""
        assignment = self._find_assignment('source')
        if not assignment:
            self.errors.append(ParseError(ParseError.ERROR_MANDATORY_FIELD_MISSING, 'source', 'Missing mandatory field: source'))
            return None

        _, value = assignment
        source_table = self._extract_table_values(value)

        source_url = source_table.get('url')
        if not source_url:
            self.errors.append(ParseError(ParseError.ERROR_MANDATORY_FIELD_MISSING, 'source.url', 'Missing mandatory field: source.url'))
            return None

        return str(source_url)

    def _extract_description(self):
        """Extract and return optional description.summary field."""
        assignment = self._find_assignment('description')
        if not assignment:
            return None

        _, value = assignment
        desc_table = self._extract_table_values(value)

        summary = desc_table.get('summary')
        return str(summary) if summary else None

    def _extract_license(self):
        """Extract and return optional license field from description table."""
        assignment = self._find_assignment('description')
        if not assignment:
            return None

        _, value = assignment
        desc_table = self._extract_table_values(value)

        license_val = desc_table.get('license')
        return str(license_val) if license_val else None

    def _extract_homepage(self):
        """Extract and return optional homepage URL from description table."""
        assignment = self._find_assignment('description')
        if not assignment:
            return None

        _, value = assignment
        desc_table = self._extract_table_values(value)

        homepage = desc_table.get('homepage')
        return str(homepage) if homepage else None

    def _extract_dependencies(self):
        """Extract dependencies and return list of parsed dependency dicts."""
        assignment = self._find_assignment('dependencies')
        if not assignment:
            return []

        _, dependency_table_node = assignment
        dependency_strings = self._extract_table_values(dependency_table_node)

        if not dependency_strings:
            return []

        sorted_strings = self._sort_by_numeric_index(dependency_strings)

        return [
            parsed
            for parsed in (self.parse_dependency(dep_string) for dep_string in sorted_strings)
            if parsed is not None
        ]

    def _sort_by_numeric_index(self, table_dict):
        """Return values from table dict sorted by numeric keys as string list."""
        try:
            # Sort by numeric key index
            sorted_items = sorted(
                table_dict.items(),
                key=lambda x: self._numeric_key_value(x[0])
            )
            return [str(value) for _, value in sorted_items]
        except Exception:
            # Fallback: return values in dict order
            return [str(v) for v in table_dict.values()]

    def _numeric_key_value(self, key):
        """Return numeric sort key for dict key; non-numeric keys sort last."""
        if isinstance(key, int):
            return key
        if isinstance(key, str) and key.isdigit():
            return int(key)
        return float('inf')  # Non-numeric keys sort to the end

    def parse_dependency(self, dep_string):
        """Parse dependency string and return dict with name, version_number, and version_spec. Returns None if parsing fails."""
        if not dep_string:
            return None

        dep_string = str(dep_string).strip()
        pattern = r'([a-zA-Z0-9_-]+)\s*(?:([>=<~=]+)\s*)?(.+)?'
        match = re.match(pattern, dep_string)

        if not match:
            return None

        name = match.group(1)
        operator = match.group(2)
        version_raw = match.group(3)

        version_number = None
        version_spec = None

        if version_raw:
            version_raw = version_raw.strip()
            version_match = re.search(r'([0-9][0-9.]*)', version_raw)
            if version_match:
                version_number = version_match.group(1)
                if operator:
                    version_spec = operator + ' ' + version_number
                else:
                    version_spec = version_number

        return {
            'name': name,
            'version_number': version_number,
            'version_spec': version_spec,
        }



