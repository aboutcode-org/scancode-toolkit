"""
Generated lexer tests
~~~~~~~~~~~~~~~~~~~~~

Checks that lexers output the expected tokens for each sample
under snippets/ and examplefiles/.

After making a change, rather than updating the samples manually,
run `pytest --update-goldens <changed file>`.

To add a new sample, create a new file matching this pattern.
The directory must match the alias of the lexer to be used.
Populate only the input, then just `--update-goldens`.

Derived from Pygments testsuite for pygments.lexers.shell and significantly modified
copyright: Copyright 2006-2021 by the Pygments team, see bashlex.py.AUTHORS.
SPDX-License-Identifier: BSD-2-Clause
"""

from pathlib import Path

import pytest

from pygments.token import Error


def pytest_collect_file(parent, path):
    if str(path).endswith(('.sh', 'APKBUILD',)):
        return LexerTestFile.from_parent(parent, fspath=path)


class LexerTestFile(pytest.File):

    def collect(self):
        yield LexerSeparateTestItem.from_parent(self, name='')


def pytest_addoption(parser):
    parser.addoption(
        '--update-goldens',
        action='store_true',
        help='reset golden master benchmarks',
    )


class LexerTestItem(pytest.Item):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.lexer = Path(str(self.fspath)).parent.name
        self.actual = None

    @classmethod
    def _prettyprint_tokens(cls, tokens):
        for tok, val in tokens:
            if tok is Error and not cls.allow_errors:
                raise ValueError('generated Error token at {!r}'.format(val))
            yield '{!r:<13} {}'.format(val, str(tok)[6:])
            if val.endswith('\n'):
                yield ''

    def runtest(self):
        from packagedcode import bashlex
        lexer = bashlex.BashShellLexer()
        tokens = lexer.get_tokens(self.input)
        self.actual = '\n'.join(self._prettyprint_tokens(tokens)).rstrip('\n') + '\n'
        if not self.config.getoption('--update-goldens'):
            assert self.actual == self.expected

    def _test_file_rel_path(self):
        pth = Path(str(self.fspath)).relative_to(Path(__file__).parent.parent)
        return pth

    def _prunetraceback(self, excinfo):
        excinfo.traceback = excinfo.traceback.cut(__file__).filter()

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, AssertionError):
            rel_path = self._test_file_rel_path()
            message = (
                'The tokens produced by the "{}" lexer differ from the '
                'expected ones in the file "{}".\n'
                'Run `pytest {} --update-goldens` to update it.'
            ).format(self.lexer, rel_path, Path(*rel_path.parts[:2]))
            diff = str(excinfo.value).split('\n', 1)[-1]
            return message + '\n\n' + diff
        else:
            return pytest.Item.repr_failure(self, excinfo)

    def reportinfo(self):
        return self.fspath, None, str(self._test_file_rel_path())

    def maybe_overwrite(self):
        if self.actual is not None and self.config.getoption('--update-goldens'):
            self.overwrite()


class LexerSeparateTestItem(LexerTestItem):
    allow_errors = False

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.input = self.fspath.read_text('utf-8')
        output_path = self.fspath + '.output'
        if output_path.check():
            self.expected = output_path.read_text(encoding='utf-8')
        else:
            self.expected = ''

    def overwrite(self):
        output_path = self.fspath + '.output'
        output_path.write_text(self.actual, encoding='utf-8')


def pytest_runtest_teardown(item, nextitem):
    if isinstance(item, LexerTestItem):
        item.maybe_overwrite()
