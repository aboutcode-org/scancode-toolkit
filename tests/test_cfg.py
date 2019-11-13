# built-in
from pathlib import Path

# project
from dephell_setuptools import CfgReader


def test_cfg():
    path = Path(__file__).parent / 'setups' / 'setup.cfg'
    actual = CfgReader(path).content
    assert actual['name'] == 'with-setup-cfg'
    assert actual['install_requires'] == ['six', 'tomlkit']
    assert actual['version'] == '1.2.3'
