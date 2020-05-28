# built-in
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from distutils.core import Command
from pathlib import Path
from tempfile import mkstemp
from typing import Any, Dict

# app
from ._base import BaseReader
from ._cached_property import cached_property
from ._constants import FIELDS


@contextmanager
def cd(path: Path):
    old_path = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def tmpfile():
    fd, path = mkstemp()
    os.close(fd)
    try:
        yield Path(path)
    finally:
        os.unlink(path)


class CommandReader(BaseReader):
    @cached_property
    def content(self) -> Dict[str, Any]:
        # generate a temporary json file which contains the metadata
        with tmpfile() as output_json:
            cmd = [
                sys.executable,
                self.path.name,
                '-q',
                '--command-packages', 'dephell_setuptools',
                'distutils_cmd',
                '-o', str(output_json),
            ]
            with cd(self.path.parent):
                env = {'PYTHONPATH': str(Path(__file__).parent.parent)}
                if sys.platform == 'win32':
                    env['SystemRoot'] = os.environ['SystemRoot']

                result = subprocess.run(
                    cmd,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    env=env,
                )
            if result.returncode != 0:
                raise RuntimeError('Command {!r} failed in {} with RC={}: {}'.format(
                    cmd,
                    os.getcwd(),
                    result.returncode,
                    result.stderr.decode('utf-8').strip().split('\n')[-1],
                ))

            with output_json.open() as stream:
                content = json.load(stream)

        return self._clean(content)


class JSONCommand(Command):
    """a distutils command to extract metadata
    """

    description = 'extract package metadata'
    user_options = [('output=', 'o', 'output for metadata json')]

    def initialize_options(self):
        self.output = None

    def finalize_options(self):
        pass

    def run(self):
        data = dict()

        # attributes
        for key, value in vars(self.distribution).items():
            if key not in FIELDS:
                continue
            if key == 'entry_points' and isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, set):
                        value[k] = list(v)
            if value in ('UNKNOWN', None, ['UNKNOWN']):
                continue
            data[key] = value

        # methods
        for func_name in dir(self.distribution):
            if not func_name.startswith('get_'):
                continue
            name = func_name[4:]
            if name not in FIELDS:
                continue
            value = getattr(self.distribution, func_name)()
            if value in ('UNKNOWN', None, ['UNKNOWN']):
                continue
            data[name] = value

        with open(self.output, 'w') as stream:
            print(json.dumps(data), file=stream)
