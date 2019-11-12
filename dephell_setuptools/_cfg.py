from configparser import ConfigParser
from typing import Dict, List, Optional, Union

from ._base import BaseReader


class CfgReader(BaseReader):
    @property
    def content(self) -> Optional[Dict[str, Union[List, Dict]]]:
        parser = ConfigParser()
        parser.read(str(self.path))

        name = None
        version = None
        if parser.has_option('metadata', 'name'):
            name = parser.get('metadata', 'name')

        if parser.has_option('metadata', 'version'):
            version = parser.get('metadata', 'version')

        install_requires = []
        extras_require = {}
        python_requires = None
        if parser.has_section('options'):
            if parser.has_option('options', 'install_requires'):
                for dep in parser.get('options', 'install_requires').split('\n'):
                    dep = dep.strip()
                    if not dep:
                        continue

                    install_requires.append(dep)

            if parser.has_option('options', 'python_requires'):
                python_requires = parser.get('options', 'python_requires')

        if parser.has_section('options.extras_require'):
            for group in parser.options('options.extras_require'):
                extras_require[group] = []
                deps = parser.get('options.extras_require', group)
                for dep in deps.split('\n'):
                    dep = dep.strip()
                    if not dep:
                        continue

                    extras_require[group].append(dep)

        return dict(
            name=name,
            version=version,
            install_requires=install_requires,
            extras_require=extras_require,
            python_requires=python_requires,
        )
