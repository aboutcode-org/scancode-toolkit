# built-in
import ast
from typing import Any, Dict, Optional

# app
from ._base import BaseReader
from ._cached_property import cached_property


class StaticReader(BaseReader):
    @cached_property
    def content(self) -> Dict[str, Any]:
        if not self.call:
            raise LookupError('cannot find setup()')
        result = self._get_call_kwargs(self.call)
        return self._clean(result)

    @cached_property
    def tree(self) -> tuple:
        return tuple(ast.parse(self.path.read_text(encoding='utf8')).body)

    @cached_property
    def call(self) -> Optional[ast.Call]:
        return self._get_call(self.tree)

    @cached_property
    def body(self) -> tuple:
        return tuple(self._get_body(self.tree))

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

    def _get_call(self, elements) -> Optional[ast.Call]:
        for element in self._get_body(elements):
            if not isinstance(element, ast.Call):
                continue
            if not isinstance(element.func, ast.Name):
                continue
            if element.func.id != 'setup':
                continue
            return element
        return None

    def _node_to_value(self, node):
        if node is None:
            return None
        if hasattr(ast, 'Constant'):
            if isinstance(node, ast.Constant):
                return node.value
        if isinstance(node, ast.Str):
            return node.s
        if isinstance(node, ast.Num):
            return node.n

        if isinstance(node, ast.List):
            return [self._node_to_value(subnode) for subnode in node.elts]
        if isinstance(node, ast.Dict):
            result = dict()
            for key, value in zip(node.keys, node.values):
                result[self._node_to_value(key)] = self._node_to_value(value)
            return result

        if isinstance(node, ast.Name):
            variable = self._find_variable_in_body(self.body, node.id)
            if variable is not None:
                return self._node_to_value(variable)

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                return None
            if node.func.id != 'dict':
                return None
            return self._get_call_kwargs(node)
        return None

    def _find_variable_in_body(self, body, name):
        for elem in body:
            if not isinstance(elem, ast.Assign):
                continue
            for target in elem.targets:
                if not isinstance(target, ast.Name):
                    continue
                if target.id == name:
                    return elem.value
        return None

    def _get_call_kwargs(self, node: ast.Call) -> Dict[str, Any]:
        result = dict()
        for keyword in node.keywords:
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
