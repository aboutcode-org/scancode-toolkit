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
                'json',
                '-o', output_json.name,
            ]
            result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if result.returncode != 0:
                return None

            with open(output_json.name) as stream:
                return json.load(stream)


class JSONCommand(Command):
    """a distutils command to extract metadata
    """

    description = 'extract package metadata'
    user_options = [('output=', 'o', 'output for metadata json')]

    def initialize_options(self):
        self.output = sys.stdout

    def finalize_options(self):
        pass

    def run(self):
        data = dict()

        # attributes
        for key, value in vars(self.distribution):
            if type(data[key]).__name__ == 'dict_items':
                value = list(data[key])
            if key == 'entry_points' and isinstance(data[key], dict):
                for k, v in value.items():
                    if isinstance(v, set):
                        value[k] = list(v)
            data[key] = value

        # methods
        for func_name in dir(self.distribution):
            if not func_name.startswith('get_'):
                continue
            name = func_name[4:]
            data[name] = getattr(self.distribution, func_name)()

        print(json.dumps(data), file=self.output)
