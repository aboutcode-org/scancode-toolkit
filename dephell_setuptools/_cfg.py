from copy import deepcopy
from configparser import ConfigParser
from typing import Dict, List, Optional, Union

from setuptools.config import ConfigOptionsHandler, ConfigMetadataHandler

from ._base import BaseReader


DEFAULT = dict(
    author_email=None,
    author=None,
    classifiers=None,
    description=None,
    download_url=None,
    extras_require=None,
    install_requires=None,
    keywords=None,
    license=None,
    long_description=None,
    maintainer_email=None,
    maintainer=None,
    metadata_version=None,
    name=None,
    obsoletes=None,
    package_dir=None,
    platforms=None,
    provides=None,
    requires=None,
    url=None,
    version=None,
)


class CfgReader(BaseReader):
    @property
    def content(self) -> Optional[Dict[str, Union[List, Dict]]]:
        path = self.path
        if path.name == 'setup.py':
            path = path.parent / 'setup.cfg'
            if not path.exists():
                raise FileNotFoundError(str(path))

        parser = ConfigParser()
        parser.read(str(path))

        options = deepcopy(parser._sections)
        for section, content in options.items():
            for k, v in content.items():
                options[section][k] = ('', v)

        container = type('container', (), DEFAULT.copy())()
        ConfigOptionsHandler(container, options).parse()
        ConfigMetadataHandler(container, options).parse()

        result = dict()
        for k, v in vars(container).items():
            if v is not None:
                result[k] = v
        return result
