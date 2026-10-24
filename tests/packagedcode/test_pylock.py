from os.path import join, dirname, abspath

from packagedcode.pypi import is_pylock_toml
from packagedcode.pypi import parse_pylock

TEST_DATA_DIR = join(abspath(dirname(__file__)), 'data')

def test_is_pylock_toml():
    assert is_pylock_toml("pylock.toml")

def test_parse_pylock():
    location = join(TEST_DATA_DIR, "pylock.toml")
    data = parse_pylock(location)
    assert "package" in data
    assert len(data["package"]) == 2
    assert data["package"][0]["name"] == "click"
    assert data["package"][1]["name"] == "setuptools"