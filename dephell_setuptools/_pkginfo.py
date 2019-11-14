# built-in
import json
import subprocess
from typing import Any, Dict

# app
from ._base import BaseReader
from ._cached_property import cached_property


class PkgInfoReader(BaseReader):
    @cached_property
    def content(self) -> Dict[str, Any]:
        if self.path.is_file() and self.path.name != 'setup.py':
            raise NameError('cannot parse non setup.py named files')

        cmd = ['pkginfo', '--json', str(self.path)]
        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode().split('\n')[-1])
        content = json.loads(result.stdout.decode())
        return self._clean(content)
