# built-in
from pathlib import Path

# project
from dephell_setuptools import CommandReader


def test_cfg():
    path = Path(__file__).parent / 'setups' / 'ansible' / 'setup.py'
    actual = CommandReader(path).content
    assert actual['name'] == 'ansible'
    assert actual['version'] == '2.10.0.dev0'
    reqs = ['jinja2', 'PyYAML', 'paramiko', 'cryptography', 'setuptools']
    assert actual['install_requires'] == reqs
