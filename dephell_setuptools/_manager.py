# built-in
from logging import getLogger
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Union, Type

# app
from ._base import BaseReader
from ._cfg import CfgReader
from ._cmd import CommandReader
from ._pkginfo import PkgInfoReader
from ._static import StaticReader


logger = getLogger('dephell_setuptools')
ALL_READERS = (
    StaticReader,
    CfgReader,
    CommandReader,
    PkgInfoReader,
)


def read_setup(*,
               path: Union[str, Path],
               error_handler: Callable[[Exception], Any] = logger.exception,
               readers: Iterable[Type[BaseReader]] = ALL_READERS) -> Dict[str, Any]:
    result = dict()     # type: Dict[str, Any]
    for reader in readers:
        try:
            content = reader(path=path).content
        except Exception as e:
            error_handler(e)
        else:
            result.update(content)
    return result
