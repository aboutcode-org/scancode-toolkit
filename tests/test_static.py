from pathlib import Path

from dephell_setuptools._static import StaticReader


def test_static():
    path = Path(__file__).parent / 'setups' / 'unpack_kwargs.py'
    actual = StaticReader(path).content
    assert actual['name'] == 'my-package'
    assert actual['install_requires'] == ['pendulum>=1.4.4', 'cachy[msgpack]>=0.2.0']
    assert actual['version'] == '0.1.2'
