# built-in
from pathlib import Path

# project
from dephell_setuptools import StaticReader


def test_unpack_kwargs():
    path = Path(__file__).parent / 'setups' / 'unpack_kwargs.py'
    actual = StaticReader(path).content
    assert actual['name'] == 'my-package'
    assert actual['version'] == '0.1.2'
    assert actual['install_requires'] == ['pendulum>=1.4.4', 'cachy[msgpack]>=0.2.0']


def test_sqlalchemy():
    path = Path(__file__).parent / 'setups' / 'sqlalchemy.py'
    actual = StaticReader(path).content
    assert actual['name'] == 'SQLAlchemy'
    assert 'version' not in actual
    assert 'install_requires' not in actual

    extras = {
        'mysql': ['mysqlclient'],
        'pymysql': ['pymysql'],
        'postgresql': ['psycopg2'],
        'postgresql_pg8000': ['pg8000'],
        'postgresql_psycopg2cffi': ['psycopg2cffi'],
        'oracle': ['cx_oracle'],
        'mssql_pyodbc': ['pyodbc'],
        'mssql_pymssql': ['pymssql'],
    }
    assert actual['extras_require'] == extras


def test_requests():
    path = Path(__file__).parent / 'setups' / 'requests.py'
    actual = StaticReader(path).content
    assert 'name' not in actual
    assert 'version' not in actual

    requires = [
        'chardet>=3.0.2,<3.1.0',
        'idna>=2.5,<2.8',
        'urllib3>=1.21.1,<1.25',
        'certifi>=2017.4.17',
    ]
    assert actual['install_requires'] == requires

    extras = {
        'security': ['pyOpenSSL >= 0.14', 'cryptography>=1.3.4', 'idna>=2.0.0'],
        'socks': ['PySocks>=1.5.6, !=1.5.7'],
        'socks:sys_platform == "win32" and python_version == "2.7"': ['win_inet_pton'],
    }
    assert actual['extras_require'] == extras
