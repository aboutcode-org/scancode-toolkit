
import ast
from configparser import ConfigParser
from copy import deepcopy
from pathlib import Path

from packagedcode.pypi_setuptools_config import ConfigMetadataHandler
from packagedcode.pypi_setuptools_config import ConfigOptionsHandler

# https://setuptools.readthedocs.io/en/latest/setuptools.html#metadata
FIELDS = {
    'author_email',
    'author',
    'classifiers',
    'dependency_links',
    'description',
    'download_url',
    'extras_require',
    'install_requires',
    'keywords',
    'license_file',
    'license',
    'long_description_content_type',
    'long_description',
    'maintainer_email',
    'maintainer',
    'metadata_version',
    'name',
    'obsoletes',
    'package_dir',
    'platforms',
    'project_urls',
    'provides',
    'python_requires',
    'requires',
    'setup_requires',
    'tests_require',
    'url',
    'version',
}

def is_setup_call(element):
    if (
        isinstance(element, ast.Call)
        and (
            hasattr(element, 'func')
            and isinstance(element.func, ast.Name)
            and getattr(element.func, 'id', None) == 'setup'
        ) or (
            hasattr(element, 'func')
            and isinstance(element.func, ast.Attribute)
            and getattr(element.func, 'attr', None) == 'setup'
            and isinstance(element.func.value, ast.Name)
            and getattr(element.func.value, 'id', None) == 'setuptools'
        )
    ):
        return True

class SetupPyReader:

    def __init__(self, path: Path):
        self.path = Path(path)

    def parse(self):
        self.tree = tuple(ast.parse(self.path.read_text(encoding='utf8')).body)
        self.body = tuple(self._get_body(self.tree))

        call = self._get_call(self.tree)
        result = self._get_call_kwargs(call)

        return clean_setup(result)

    @classmethod
    def _get_body(cls, elements):
        for element in elements:
            if isinstance(element, ast.FunctionDef):
                yield from cls._get_body(element.body)
                continue
            if isinstance(element, ast.If):
                yield from cls._get_body(element.body)
            if isinstance(element, ast.Expr):
                yield element.value
                continue
            yield element

    def _get_call(self, elements):
        for element in self._get_body(elements):
            if is_setup_call(element):
                return element
            elif isinstance(element, (ast.Assign, )):
                if isinstance(element.value, ast.Call):
                    if is_setup_call(element.value):
                        return element.value

    def _node_to_value(self, node):
        if node is None:
            return
        if hasattr(ast, 'Constant'):
            if isinstance(node, ast.Constant):
                return node.value

        if isinstance(node, ast.Str):
            return node.s

        if isinstance(node, ast.Num):
            return node.n

        if isinstance(node, (ast.List, ast.Tuple, ast.Set,)):
            return [self._node_to_value(subnode) for subnode in node.elts]

        if isinstance(node, ast.Dict):
            result = {}
            for key, value in zip(node.keys, node.values):
                result[self._node_to_value(key)] = self._node_to_value(value)
            return result

        if isinstance(node, ast.Name):
            variable = self._find_variable_in_body(self.body, node.id)
            if variable is not None:
                return self._node_to_value(variable)

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                return
            if node.func.id != 'dict':
                return
            return self._get_call_kwargs(node)
        return

    def _find_variable_in_body(self, body, name):
        for elem in body:
            if not isinstance(elem, ast.Assign):
                continue
            for target in elem.targets:
                if not isinstance(target, ast.Name):
                    continue
                if target.id == name:
                    return elem.value

    def _get_call_kwargs(self, node: ast.Call):
        """
        Return a mapping of setup() method call keyword arguments.
        """
        result = {}
        keywords = getattr(node, 'keywords', []) or []
        for keyword in keywords:
            # dict unpacking
            if keyword.arg is None:
                value = self._node_to_value(keyword.value)
                if isinstance(value, dict):
                    result.update(value)
                continue
            # keyword argument
            value = self._node_to_value(keyword.value)
            if value is None:
                continue
            result[keyword.arg] = value
        return result


class SetupCfgReader:

    def __init__(self, path):
        self.path = Path(path)

    def parse(self):
        parser = ConfigParser()
        parser.read(str(self.path))

        options = deepcopy(parser._sections)  # type: ignore
        for section, content in options.items():
            for k, v in content.items():
                options[section][k] = ('', v)

        container = type('container', (), dict.fromkeys(FIELDS))()
        ConfigOptionsHandler(container, options).parse()
        ConfigMetadataHandler(container, options).parse()

        return clean_setup(vars(container))


def clean_setup(data):
    """
    Return a cleaned mapping from setup ``data``.
    """
    result = {k: v
        for k, v in data.items()
        if (v and v is not False) and v != 'UNKNOWN'
        and k in FIELDS
    }

    # split keywords in words
    keywords = result.get('keywords')
    if keywords and isinstance(keywords, str):
        # some keywords are separated by coma, some by space or lines
        if ',' in keywords:
            keywords = [k.strip() for k in keywords.split(',')]
        else:
            keywords = keywords.split()
        result['keywords'] = keywords

    return result


def read_setup(path):

    READERS_BY_EXT = {
        '.py': SetupPyReader,
        '.cfg': SetupCfgReader,
    }

    for fname, reader in READERS_BY_EXT.items():
        if path.endswith(fname):
            return reader(path).parse()


def dumps_setup(path):
    import json
    print(json.dumps(read_setup(path), indent=2))
