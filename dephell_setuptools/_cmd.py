import json
import os
import subprocess
import sys
from contextlib import contextmanager
from distutils.core import Command
from pathlib import Path
from tempfile import NamedTemporaryFile

from ._base import BaseReader


@contextmanager
def cd(path: Path):
    old_path = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(old_path)


class CommandReader(BaseReader):
    @property
    def content(self):
        with cd(self.path.parent):
            # generate a temporary json file which contains the metadata
            output_json = NamedTemporaryFile()
            cmd = [
                sys.executable,
                self.path.name,
                '-q',
                '--command-packages', 'dephell_setuptools',
                'distutils_cmd',
                '-o', output_json.name,
            ]
            result = subprocess.run(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                env={'PYTHONPATH': str(Path(__file__).parent.parent)},
            )
            print(result.stderr.decode())
            print(result.stdout.decode())
            if result.returncode != 0:
                return None

            with open(output_json.name) as stream:
                return json.load(stream)


class JSONCommand(Command):
    """a distutils command to extract metadata
    """

    description = 'extract package metadata'
    user_options = [('output=', 'o', 'output for metadata json')]

    _exclude = {
        '_tmp_extras_require',
        'option_dict',
        'cmdclass',
        'metadata',
        'cmdline_options',
        'command_class',
        'command_obj',
    }

    def initialize_options(self):
        self.output = None

    def finalize_options(self):
        pass

    def run(self):
        data = dict()

        # attributes
        for key, value in vars(self.distribution).items():
            if key.startswith('get_'):
                continue
            if key in self._exclude:
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
            if name in self._exclude:
                continue
            value = getattr(self.distribution, func_name)()
            if value in ('UNKNOWN', None, ['UNKNOWN']):
                continue
            data[name] = value

        with open(self.output, 'w') as stream:
            print(json.dumps(data), file=stream)
