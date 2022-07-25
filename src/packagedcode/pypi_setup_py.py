#
# Copyright (c) Gram and others.
# This code is copied and modified from dephell_setuptools https://github.com/dephell/dephell_setuptools
# SPDX-License-Identifier: MIT
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#


import ast
from pathlib import Path

"""
Parse setup.py files.
"""

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
    """
    Return if the AST ``element`` is a call to the setup() function.
    Note: this is derived from the code in packagedcode.pypi.py
    """
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


def parse_setup_py(location):
    """
    Return a mapping of setuptools.setup() call argument found in a setup.py
    file at ``location`` or an empty mapping.
    """
    path = Path(location)
    tree = tuple(ast.parse(path.read_text(encoding='utf8')).body)
    body = tuple(get_body(tree))

    call = get_setup_call(tree)
    result = get_call_kwargs(call, body)

    return clean_setup(result)


def get_body(elements):
    """
    Yield the body from ``elements`` as a single iterable.
    """
    for element in elements:
        if isinstance(element, ast.FunctionDef):
            yield from get_body(element.body)
            continue
        if isinstance(element, ast.If):
            yield from get_body(element.body)
        if isinstance(element, ast.Expr):
            yield element.value
            continue
        yield element


def get_setup_call(elements):
    """
    Return a setup() method call found in the ``elements`` or None.
    """
    for element in get_body(elements):
        if is_setup_call(element):
            return element
        elif isinstance(element, (ast.Assign,)):
            if isinstance(element.value, ast.Call):
                if is_setup_call(element.value):
                    return element.value


def node_to_value(node, body):
    """
    Return the extracted and converted value of a node or None
    """
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
        return [node_to_value(subnode, body) for subnode in node.elts]

    if isinstance(node, ast.Dict):
        result = {}
        for key, value in zip(node.keys, node.values):
            result[node_to_value(key, body)] = node_to_value(value, body)
        return result

    if isinstance(node, ast.Name):
        variable = find_variable_in_body(body, node.id)
        if variable is not None:
            return node_to_value(variable, body)

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            return
        if node.func.id != 'dict':
            return
        return get_call_kwargs(node, body)
    return


def find_variable_in_body(body, name):
    """
    Return the value of the variable ``name`` found in the ``body`` ast tree or None.
    """
    for elem in body:
        if not isinstance(elem, ast.Assign):
            continue
        for target in elem.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id == name:
                return elem.value


def get_call_kwargs(node: ast.Call, body):
    """
    Return a mapping of setup() method call keyword arguments.
    """
    result = {}
    keywords = getattr(node, 'keywords', []) or []
    for keyword in keywords:
        # dict unpacking
        if keyword.arg is None:
            value = node_to_value(keyword.value, body)
            if isinstance(value, dict):
                result.update(value)
            continue
        # keyword argument
        value = node_to_value(keyword.value, body)
        if value is None:
            continue
        result[keyword.arg] = value
    return result


def clean_setup(data):
    """
    Return a cleaned mapping from a setup ``data`` mapping.
    """
    result = {k: v
        for k, v in data.items()
        if k in FIELDS
        and (v and v is not False)
        and str(v) != 'UNKNOWN'
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
