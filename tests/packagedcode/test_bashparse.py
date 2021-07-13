#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from functools import partial
import os.path

from commoncode import text
from packagedcode import bashparse
from packagedcode.bashparse import ShellVariable

from packages_test_utils import check_result_equals_expected_json
from packages_test_utils import get_test_files
from packages_test_utils import PackageTester

test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def create_test_function(test_file_loc, tested_function, test_name, regen=False):
    """
    Return a test function closed on test arguments to run
    `tested_function(test_file_loc)`.
    """

    def test_package(self):
        test_loc = self.get_test_loc(test_file_loc, must_exist=True)
        result = tested_function(test_loc)
        check_result_equals_expected_json(
            result=result,
            expected_loc=test_loc + '-expected.json',
            regen=regen,
        )

    test_package.__name__ = test_name
    return test_package


def build_tests(
    test_dir,
    test_file_suffix,
    clazz,
    tested_function,
    test_method_prefix,
    regen=False,
):
    """
    Dynamically build test methods from files in ``test_dir`` ending with
    ``test_file_suffix`` and attach a test method to the ``clazz`` test class.

    For each method:
    - run ``tested_function`` with a test file with``test_file_suffix``
      ``tested_function`` should return a JSON-serializable object.
    - set the name prefixed with ``test_method_prefix``.
    - check that a test expected file named <test_file_name>-expected.json`
      has content matching the results of the ``tested_function`` returned value.
    """
    assert issubclass(clazz, PackageTester)

    # loop through all items and attach a test method to our test class
    for test_file_path in get_test_files(test_dir, test_file_suffix):
        test_name = test_method_prefix + text.python_safe_name(test_file_path)
        test_file_loc = os.path.join(test_dir, test_file_path)

        test_method = create_test_function(
            test_file_loc=test_file_loc,
            tested_function=tested_function,
            test_name=test_name,
            regen=regen,
        )
        setattr(clazz, test_name, test_method)


class TestBashParserDatadriven(PackageTester):
    test_data_dir = test_data_dir


build_tests(
    test_dir=os.path.join(test_data_dir, 'bashparse'),
    test_file_suffix='.sh',
    clazz=TestBashParserDatadriven,
    tested_function=lambda loc: list(bashparse.collect_shell_variables(loc, resolve=True)),
    test_method_prefix='test_collect_shell_variables_',
    regen=False,
)


def clean_spaces(s):
    lines = (l.rstrip() for l in s.splitlines())
    return '\n'.join(lines)


class TestBashParser(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_tokens(self):
        text = '''
# Contributor: Natanael Copa <ncopa@alpinelinux.org>
pkgname=gcc

pkgname="$pkgname$_target"
foo=bar
baz=$foo
bez=${foo}
gnat() {
    pkgdesc="Ada support for GCC"
}
'''

        result = [str(t) for t in bashparse.get_tokens(text)]
        expected = [
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 1, 0)",
            "Token('# Contributor: Natanael Copa <ncopa@alpinelinux.org>\\n', 'TOKEN-COMMENT-SINGLE', 2, 1)",
            "Token('pkgname', 'TOKEN-NAME-VARIABLE', 3, 54)",
            "Token('=', 'TOKEN-OPERATOR-EQUAL', 3, 61)",
            "Token('gcc', 'TOKEN-TEXT', 3, 62)",
            "Token('\\n\\n', 'TOKEN-TEXT-NEWLINE', 3, 65)",
            "Token('pkgname', 'TOKEN-NAME-VARIABLE', 5, 67)",
            "Token('=', 'TOKEN-OPERATOR-EQUAL', 5, 74)",
            'Token(\'"$pkgname$_target"\', \'TOKEN-LITERAL-STRING-DOUBLE\', 5, 75)',
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 5, 93)",
            "Token('foo', 'TOKEN-NAME-VARIABLE', 6, 94)",
            "Token('=', 'TOKEN-OPERATOR-EQUAL', 6, 97)",
            "Token('bar', 'TOKEN-TEXT', 6, 98)",
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 6, 101)",
            "Token('baz', 'TOKEN-NAME-VARIABLE', 7, 102)",
            "Token('=', 'TOKEN-OPERATOR-EQUAL', 7, 105)",
            "Token('$foo', 'TOKEN-TEXT', 7, 106)",
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 7, 110)",
            "Token('bez', 'TOKEN-NAME-VARIABLE', 8, 111)",
            "Token('=', 'TOKEN-OPERATOR-EQUAL', 8, 114)",
            "Token('${foo}', 'TOKEN-TEXT', 8, 115)",
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 8, 121)",
            "Token('gnat()', 'TOKEN-TEXT', 9, 122)",
            "Token(' ', 'TOKEN-TEXT-WHITESPACE', 9, 128)",
            "Token('{', 'TOKEN-TEXT', 9, 129)",
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 9, 130)",
            "Token('    ', 'TOKEN-TEXT-WHITESPACE', 10, 131)",
            'Token(\'pkgdesc="Ada\', \'TOKEN-TEXT\', 10, 135)',
            "Token(' ', 'TOKEN-TEXT-WHITESPACE', 10, 147)",
            "Token('support', 'TOKEN-TEXT', 10, 148)",
            "Token(' ', 'TOKEN-TEXT-WHITESPACE', 10, 155)",
            "Token('for', 'TOKEN-TEXT', 10, 156)",
            "Token(' ', 'TOKEN-TEXT-WHITESPACE', 10, 159)",
            'Token(\'GCC"\', \'TOKEN-TEXT\', 10, 160)',
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 10, 164)",
            "Token('}', 'TOKEN-TEXT', 11, 165)",
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 11, 166)",
        ]

        assert result == expected

    def test_parse_shell_with_variables_grammar_can_parse(self):
        text = '''
# Contributor: Natanael Copa <ncopa@alpinelinux.org>
pkgname=gcc

pkgname="$pkgname$_target"
pkgrel=2
license="GPL-2.0-or-later
 LGPL-2.1-or-later"
    license="GPL-2.0-or-later
     LGPL-2.1-or-later"

gnat() {
    pkgdesc="Ada support for GCC"
}
'''

        result = repr(bashparse.parse_shell(text))
        assert clean_spaces(result) == clean_spaces(EXPECTED_SIMPLE)

    def test_get_tokens_simple(self):
        text = '''
foo=bar
baz=$foo
bez=${foo}
'''

        result = [str(t) for t in bashparse.get_tokens(text)]
        expected = [
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 1, 0)",
            "Token('foo', 'TOKEN-NAME-VARIABLE', 2, 1)",
            "Token('=', 'TOKEN-OPERATOR-EQUAL', 2, 4)",
            "Token('bar', 'TOKEN-TEXT', 2, 5)",
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 2, 8)",
            "Token('baz', 'TOKEN-NAME-VARIABLE', 3, 9)",
            "Token('=', 'TOKEN-OPERATOR-EQUAL', 3, 12)",
            "Token('$foo', 'TOKEN-TEXT', 3, 13)",
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 3, 17)",
            "Token('bez', 'TOKEN-NAME-VARIABLE', 4, 18)",
            "Token('=', 'TOKEN-OPERATOR-EQUAL', 4, 21)",
            "Token('${foo}', 'TOKEN-TEXT', 4, 22)",
            "Token('\\n', 'TOKEN-TEXT-NEWLINE', 4, 28)",
        ]

        assert result == expected

    def test_collect_shell_variables_from_text_can_resolve(self):
        text = '''
foo=bar
baz=$foo
bez=${baz}
'''
        result, errors = bashparse.collect_shell_variables_from_text(text)
        expected = [
            ShellVariable(name='foo', value='bar'),
            ShellVariable(name='baz', value='$foo'),
            ShellVariable(name='bez', value='${baz}'),
        ]
        assert result == expected

        expected = []
        assert errors == expected

        result, errors = bashparse.collect_shell_variables_from_text(text, resolve=True)
        expected = [
            ShellVariable(name='foo', value='bar'),
            ShellVariable(name='baz', value='bar'),
            ShellVariable(name='bez', value='bar'),
        ]
        assert result == expected

        expected = []
        assert errors == expected

    def test_collect_shell_variables_from_text_can_parse_single_quoted_vars(self):
        text = "\nlicense='AGPL3'"
        result, errors = bashparse.collect_shell_variables_from_text(text)
        expected = [ShellVariable(name='license', value='AGPL3')]
        assert result == expected
        expected = []
        assert errors == expected

    def test_collect_shell_variables_from_text_can_parse_trailing_comments(self):
        text = '\noptions="!check" # out of disk space (>35GB)'
        result, errors = bashparse.collect_shell_variables_from_text(text)
        expected = [ShellVariable(name='options', value='!check')]
        assert result == expected
        expected = []
        assert errors == expected

    def test_collect_shell_variables_from_text_can_parse_combo_single_quote_and_trailing_comments(self):
        text = '''
arch="x86_64 ppc64le aarch64"
options="!check" # out of disk space (>35GB)
license='AGPL3'
pkgusers="mongodb"
options='!baz' # out of disk space (>35GB)
'''
        result, errors = bashparse.collect_shell_variables_from_text(text)
        expected = [
            ShellVariable(name='arch', value='x86_64 ppc64le aarch64'),
            ShellVariable(name='options', value='!check'),
            ShellVariable(name='license', value='AGPL3'),
            ShellVariable(name='pkgusers', value='mongodb'),
            ShellVariable(name='options', value='!baz'),
        ]
        assert result == expected
        expected = []
        assert errors == expected

    def test_collect_shell_variables_from_text_simple(self):
        result, errors = bashparse.collect_shell_variables_from_text(TEST_TEXT1)
        expected = [
            ShellVariable(name='_pkgbase', value='10.3.1'),
            ShellVariable(name='pkgver', value='10.3.1_git20210424'),
            ShellVariable(name='pkgname', value='$pkgname$_target'),
            ShellVariable(name='pkgrel', value='2'),
            ShellVariable(name='pkgdesc', value='The GNU Compiler Collection'),
            ShellVariable(name='url', value='https://gcc.gnu.org'),
            ShellVariable(name='arch', value='all'),
            ShellVariable(name='license', value='GPL-2.0-or-later LGPL-2.1-or-later'),
            ShellVariable(name='_gccrel', value='$pkgver-r$pkgrel'),
            ShellVariable(name='depends', value='binutils$_target'),
            ShellVariable(name='makedepends_build', value='gcc$_cross g++$_cross bison flex texinfo gawk zip gmp-dev mpfr-dev mpc1-dev zlib-dev'),
            ShellVariable(name='makedepends_host', value='linux-headers gmp-dev mpfr-dev mpc1-dev isl-dev zlib-dev !gettext-dev libucontext-dev'),
            ShellVariable(name='makedepends', value='$makedepends_build $makedepends_host'),
            ShellVariable(name='source', value='https://dev.alpinelinux.org/~nenolod/gcc-${pkgver}.tar.xz\n    0001-posix_memalign.patch\n    '),
            ShellVariable(name='sha512sums', value='0ef281e6633b8bef7ce24d1448ec7b96aef66e414f90821a9  gcc-10.3.1_git20210424.tar.xz\nd1e10db83a04c02d99f9f6ce03f9  0001-posix_memalign.patch\n'),
        ]
        assert errors == []
        assert result == expected


TEST_TEXT1 = '''
# Contributor: Natanael Copa <ncopa@alpinelinux.org>
# Maintainer: Ariadne Conill <ariadne@dereferenced.org>
pkgname=gcc
_pkgbase=10.3.1
pkgver=10.3.1_git20210424
pkgname="$pkgname$_target"
pkgrel=2
pkgdesc="The GNU Compiler Collection"
url="https://gcc.gnu.org"
arch="all"
license="GPL-2.0-or-later LGPL-2.1-or-later"
_gccrel=$pkgver-r$pkgrel
depends="binutils$_target"
makedepends_build="gcc$_cross g++$_cross bison flex texinfo gawk zip gmp-dev mpfr-dev mpc1-dev zlib-dev"
makedepends_host="linux-headers gmp-dev mpfr-dev mpc1-dev isl-dev zlib-dev !gettext-dev libucontext-dev"

makedepends="$makedepends_build $makedepends_host"

source="https://dev.alpinelinux.org/~nenolod/gcc-${pkgver}.tar.xz
    0001-posix_memalign.patch
    "

gnat() {
    pkgdesc="Ada support for GCC"
    depends="gcc=$_gccrel"
}

sha512sums="0ef281e6633b8bef7ce24d1448ec7b96aef66e414f90821a9  gcc-10.3.1_git20210424.tar.xz
d1e10db83a04c02d99f9f6ce03f9  0001-posix_memalign.patch
"

'''

EXPECTED_SIMPLE = '''Tree('ROOT', [
/TOKEN-TEXT-NEWLINE, # Contributor: Natanael Copa <ncopa@alpinelinux.org>
/TOKEN-COMMENT-SINGLE, pkgname/TOKEN-NAME-VARIABLE, =/TOKEN-OPERATOR-EQUAL, gcc/TOKEN-TEXT, Tree('SHELL-VARIABLE', [

/TOKEN-TEXT-NEWLINE, pkgname/TOKEN-NAME-VARIABLE, =/TOKEN-OPERATOR-EQUAL, "$pkgname$_target"/TOKEN-LITERAL-STRING-DOUBLE]), Tree('SHELL-VARIABLE', [
/TOKEN-TEXT-NEWLINE, pkgrel/TOKEN-NAME-VARIABLE, =/TOKEN-OPERATOR-EQUAL, 2/TOKEN-TEXT]), Tree('SHELL-VARIABLE', [
/TOKEN-TEXT-NEWLINE, license/TOKEN-NAME-VARIABLE, =/TOKEN-OPERATOR-EQUAL, "GPL-2.0-or-later
 LGPL-2.1-or-later"/TOKEN-LITERAL-STRING-DOUBLE]),
/TOKEN-TEXT-NEWLINE,     /TOKEN-TEXT-WHITESPACE, license="GPL-2.0-or-later/TOKEN-TEXT,
/TOKEN-TEXT-NEWLINE,      /TOKEN-TEXT-WHITESPACE, LGPL-2.1-or-later"/TOKEN-TEXT,

/TOKEN-TEXT-NEWLINE, gnat()/TOKEN-TEXT,  /TOKEN-TEXT-WHITESPACE, {/TOKEN-TEXT,
/TOKEN-TEXT-NEWLINE,     /TOKEN-TEXT-WHITESPACE, pkgdesc="Ada/TOKEN-TEXT,  /TOKEN-TEXT-WHITESPACE, support/TOKEN-TEXT,  /TOKEN-TEXT-WHITESPACE, for/TOKEN-TEXT,  /TOKEN-TEXT-WHITESPACE, GCC"/TOKEN-TEXT,
/TOKEN-TEXT-NEWLINE, }/TOKEN-TEXT,
/TOKEN-TEXT-NEWLINE])'''
