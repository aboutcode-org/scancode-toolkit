from logging import getLogger
from pathlib import Path

from ._cfg import CfgReader
from ._cmd import CommandReader
from ._pkginfo import PkgInfoReader
from ._static import StaticReader
from ._constants import FIELDS


logger = getLogger('dephell_setuptools')


class ReadersManager:
    error_handler = logger.exception
    readers = (
        StaticReader,
        CfgReader,
        CommandReader,
        PkgInfoReader,
    )

    def __call__(self, path: Path):
        result = dict()
        for reader in self.readers:
            try:
                content = reader(path=path).content
            except Exception as e:
                self.error_handler(str(e))
            else:
                result.update(content)
        exclude = (None, 0, [])
        result = {k: v for k, v in result.items() if k in FIELDS and v not in exclude}
        return result
