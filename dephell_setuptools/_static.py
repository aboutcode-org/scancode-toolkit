import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class StaticReader:
    def __init__(self, path: Union[str, Path]):
        if isinstance(path, str):
            path = Path(path)
        self.path = path

    @property
    def content(self) -> Optional[Dict[str, Union[List, Dict]]]:
        if not self.call:
            return None

        return dict(
            name=self._find_single_string('name'),
            version=self._find_single_string('version'),
            python_requires=self._find_single_string('python_requires'),

            install_requires=self._find_install_requires(),
            extras_require=self._find_extras_require(),
        )

    @property
    def tree(self):
        return ast.parse(self.path.read_text(encoding='utf8')).body

    @property
    def call(self) -> Optional[ast.Call]:
        return self._find_setup_call(self.tree)[0]

    @property
    def body(self) -> Optional[list]:
        return self._find_setup_call(self.tree)[1]

    def _find_setup_call(self, elements) -> Tuple[Optional[ast.Call], Optional[list]]:
        funcdefs = []
        for i, element in enumerate(elements):
            if isinstance(element, ast.If):
                # Checking if the last element is an if statement
                # and if it is 'if __name__ == '__main__'' which
                # could contain the call to setup()
                test = element.test
                if not isinstance(test, ast.Compare):
                    continue

                left = test.left
                if not isinstance(left, ast.Name):
                    continue

                if left.id != '__name__':
                    continue

                setup_call, body = self._find_sub_setup_call([element])
                if not setup_call:
                    continue

                return setup_call, body + elements
            if not isinstance(element, ast.Expr):
                if isinstance(element, ast.FunctionDef):
                    funcdefs.append(element)

                continue

            value = element.value
            if not isinstance(value, ast.Call):
                continue

            func = value.func
            if not isinstance(func, ast.Name):
                continue

            if func.id != 'setup':
                continue

            return value, elements

        # Nothing, we inspect the function definitions
        return self._find_sub_setup_call(funcdefs)

    def _find_sub_setup_call(
        self, elements
    ):  # type: (list) -> Tuple[Optional[ast.Call], Optional[list]]
        for element in elements:
            if not isinstance(element, (ast.FunctionDef, ast.If)):
                continue

            setup_call = self._find_setup_call(element.body)
            if setup_call != (None, None):
                setup_call, body = setup_call

                body = elements + body

                return setup_call, body

        return None, None

    def _find_install_requires(self):
        install_requires = []
        value = self._find_in_call(self.call, 'install_requires')
        if value is None:
            # Trying to find in kwargs
            kwargs = self._find_call_kwargs(self.call)

            if kwargs is None or not isinstance(kwargs, ast.Name):
                return install_requires

            variable = self._find_variable_in_body(self.body, kwargs.id)
            if not isinstance(variable, (ast.Dict, ast.Call)):
                return install_requires

            if isinstance(variable, ast.Call):
                if not isinstance(variable.func, ast.Name):
                    return install_requires

                if variable.func.id != 'dict':
                    return install_requires

                value = self._find_in_call(variable, 'install_requires')
            else:
                value = self._find_in_dict(variable, 'install_requires')

        if value is None:
            return install_requires

        if isinstance(value, ast.List):
            for el in value.elts:
                install_requires.append(el.s)
        elif isinstance(value, ast.Name):
            variable = self._find_variable_in_body(self.body, value.id)

            if variable is not None and isinstance(variable, ast.List):
                for el in variable.elts:
                    install_requires.append(el.s)

        return install_requires

    def _find_extras_require(self):
        extras_require = {}
        value = self._find_in_call(self.call, 'extras_require')
        if value is None:
            # Trying to find in kwargs
            kwargs = self._find_call_kwargs(self.call)

            if kwargs is None or not isinstance(kwargs, ast.Name):
                return extras_require

            variable = self._find_variable_in_body(self.body, kwargs.id)
            if not isinstance(variable, (ast.Dict, ast.Call)):
                return extras_require

            if isinstance(variable, ast.Call):
                if not isinstance(variable.func, ast.Name):
                    return extras_require

                if variable.func.id != 'dict':
                    return extras_require

                value = self._find_in_call(variable, 'extras_require')
            else:
                value = self._find_in_dict(variable, 'extras_require')

        if value is None:
            return extras_require

        if isinstance(value, ast.Dict):
            for key, val in zip(value.keys, value.values):
                if isinstance(val, ast.Name):
                    val = self._find_variable_in_body(self.body, val.id)

                if isinstance(val, ast.List):
                    extras_require[key.s] = [e.s for e in val.elts]
        elif isinstance(value, ast.Name):
            variable = self._find_variable_in_body(self.body, value.id)

            if variable is None or not isinstance(variable, ast.Dict):
                return extras_require

            for key, val in zip(variable.keys, variable.values):
                if isinstance(val, ast.Name):
                    val = self._find_variable_in_body(self.body, val.id)

                if isinstance(val, ast.List):
                    extras_require[key.s] = [e.s for e in val.elts]

        return extras_require

    def _find_single_string(self, name: str):
        value = self._find_in_call(self.call, name)
        if value is None:
            # Trying to find in kwargs
            kwargs = self._find_call_kwargs(self.call)

            if kwargs is None or not isinstance(kwargs, ast.Name):
                return

            variable = self._find_variable_in_body(self.body, kwargs.id)
            if not isinstance(variable, (ast.Dict, ast.Call)):
                return

            if isinstance(variable, ast.Call):
                if not isinstance(variable.func, ast.Name):
                    return

                if variable.func.id != 'dict':
                    return

                value = self._find_in_call(variable, name)
            else:
                value = self._find_in_dict(variable, name)

        if value is None:
            return

        if isinstance(value, ast.Str):
            return value.s
        elif isinstance(value, ast.Name):
            variable = self._find_variable_in_body(self.body, value.id)

            if variable is not None and isinstance(variable, ast.Str):
                return variable.s

    def _find_in_call(self, call, name):
        for keyword in call.keywords:
            if keyword.arg == name:
                return keyword.value

    def _find_call_kwargs(self, call):
        kwargs = None
        for keyword in call.keywords:
            if keyword.arg is None:
                kwargs = keyword.value

        return kwargs

    def _find_variable_in_body(self, body, name):
        found = None
        for elem in body:
            if found:
                break

            if not isinstance(elem, ast.Assign):
                continue

            for target in elem.targets:
                if not isinstance(target, ast.Name):
                    continue

                if target.id == name:
                    return elem.value

    def _find_in_dict(self, dict_, name):
        for key, val in zip(dict_.keys, dict_.values):
            if isinstance(key, ast.Str) and key.s == name:
                return val
