"""
    Generated lexer tests
    ~~~~~~~~~~~~~~~~~~~~~

    Checks that lexers output the expected tokens for each sample
    under lexers/*/test_*.txt.

    After making a change, rather than updating the samples manually,
    run `pytest --update-goldens tests/examplefiles`.

    To add a new sample, create a new file matching this pattern.
    The directory must match the alias of the lexer to be used.
    Populate only the input, then just `--update-goldens`.

    :copyright: Copyright 2021 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import pytest

from tests.conftest import LexerSeparateTestItem


def pytest_collect_file(parent, path):
    if path.ext != '.output' and path.basename != 'conftest.py':
        return LexerTestFile.from_parent(parent, fspath=path)


class LexerTestFile(pytest.File):
    def collect(self):
        yield LexerSeparateTestItem.from_parent(self, name='')
