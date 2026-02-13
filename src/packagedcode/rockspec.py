import os
import sys
import logging
import re
import traceback
from packageurl import PackageURL

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
        """
        Parse a rockspec file and return a PackageData object.
        """
        pass


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
        """Main parsing orchestration. Reads file, parses AST, extracts all fields."""
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
        """Read rockspec file and return content."""
        try:
            with open(self.rockspec_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.rockspec_path}")
        except IOError as e:
            raise IOError(f"Error reading file: {e}")

    def _parse_lua(self, code):
        """Parse Lua code to AST."""
        try:
            return ast.parse(code)
        except Exception as e:
            raise RuntimeError(f"Lua parse error: {e}")

    def _find_assignment(self, var_name):
        """Find assignment node for a variable, return (target_node, value_node)."""
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
        """Extract string value from String node."""
        if not node or type(node).__name__ != 'String':
            return None

        s_val = node.s if hasattr(node, 's') else None
        if isinstance(s_val, bytes):
            return s_val.decode('utf-8')
        return str(s_val) if s_val else None

    def _extract_table_values(self, table_node):
        """Extract key-value pairs from Table node."""
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
        """Extract key from field key node."""
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
        """Extract value from any AST node."""
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
        """Look up a variable and return its value."""
        assignment = self._find_assignment(var_name)
        if not assignment:
            return None

        _, value = assignment
        return self._extract_value(value)

    def _extract_concat(self, concat_node):
        """
        Extract value from Concat node (string concatenation).
        Recursively processes: left .. right
        """
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
        """Extract package name (mandatory)."""
        assignment = self._find_assignment('package')
        if not assignment:
            self.errors.append(ParseError(ParseError.ERROR_MANDATORY_FIELD_MISSING, 'package', 'Missing mandatory field: package'))
            return None

        _, value = assignment
        result = self._extract_value(value)
        return str(result) if result else None

    def _extract_version(self):
        """Extract version (mandatory)."""
        assignment = self._find_assignment('version')
        if not assignment:
            self.errors.append(ParseError(ParseError.ERROR_MANDATORY_FIELD_MISSING, 'version', 'Missing mandatory field: version'))
            return None

        _, value = assignment
        result = self._extract_value(value)
        return str(result) if result else None

    def _extract_rockspec_format(self):
        """Extract rockspec_format (optional)."""
        assignment = self._find_assignment('rockspec_format')
        if not assignment:
            return None

        _, value = assignment
        result = self._extract_value(value)
        return str(result) if result else None

    def _extract_supported_platforms(self):
        """Extract supported_platforms as list (optional table)."""
        assignment = self._find_assignment('supported_platforms')
        if not assignment:
            return []

        _, platform_table_node = assignment
        platform_dict = self._extract_table_values(platform_table_node)

        # Sort platforms by numeric index order
        return self._sort_by_numeric_index(platform_dict)

    def _extract_source_url(self):
        """Extract VCS URL from source table (url is mandatory)."""
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
        """Extract description summary from description table (optional)."""
        assignment = self._find_assignment('description')
        if not assignment:
            return None

        _, value = assignment
        desc_table = self._extract_table_values(value)

        summary = desc_table.get('summary')
        return str(summary) if summary else None

    def _extract_license(self):
        """Extract license from description table (optional)."""
        assignment = self._find_assignment('description')
        if not assignment:
            return None

        _, value = assignment
        desc_table = self._extract_table_values(value)

        license_val = desc_table.get('license')
        return str(license_val) if license_val else None

    def _extract_homepage(self):
        """Extract homepage URL from description table (optional)."""
        assignment = self._find_assignment('description')
        if not assignment:
            return None

        _, value = assignment
        desc_table = self._extract_table_values(value)

        homepage = desc_table.get('homepage')
        return str(homepage) if homepage else None

    def _extract_dependencies(self):
        """Extract dependencies as list of parsed dicts (optional table)."""
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
        """Sort a table dict by numeric keys and return values as strings."""
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
        """Convert key to numeric value for sorting. Non-numeric keys sort to end."""
        if isinstance(key, int):
            return key
        if isinstance(key, str) and key.isdigit():
            return int(key)
        return float('inf')  # Non-numeric keys sort to the end

    def parse_dependency(self, dep_string):
        """
        Parse a Lua dependency string into name and version spec.

        Lua RockSpecs format: "package_name [operator version]"
        Examples:
            "inspect == 3.1.3"
            "luasec == 1.3.1"
            "binaryheap >= 0.4"
            "somedep" (no version)

        Returns dict with keys:
            - name: Package name
            - version_number: Clean version number (e.g. "3.1.3") or None
            - version_spec: Full version specification with operator (e.g. "== 3.1.3") or None
            - raw: Original input string
        """
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
            'raw': dep_string
        }



