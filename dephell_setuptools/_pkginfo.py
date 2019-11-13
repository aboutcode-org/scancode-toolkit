import json
import subprocess

from ._base import BaseReader


class PkgInfoReader(BaseReader):
    @property
    def content(self):
        if self.path.is_file() and self.path.name != 'setup.py':
            return None

        cmd = ['pkginfo', '--json', str(self.path)]
        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if result.returncode != 0:
            return None
        content = json.loads(result.stdout.decode())
        return self._clean(content)
