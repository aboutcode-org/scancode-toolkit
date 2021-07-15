#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from commoncode import text
from packagedcode import bashparse
from packagedcode.bashparse import ShellVariable

from packages_test_utils  import build_tests
from packages_test_utils import check_result_equals_expected_json
from packages_test_utils import get_test_files
from packages_test_utils import PackageTester

test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


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
            "Token('\\n', 'TEXT-NEWLINE', 1, 0)",
            "Token('# Contributor: Natanael Copa <ncopa@alpinelinux.org>', 'COMMENT-SINGLE', 2, 1)",
            "Token('\\n', 'TEXT-NEWLINE', 2, 53)",
            "Token('pkgname', 'NAME-VARIABLE', 3, 54)",
            "Token('=', 'OPERATOR-EQUAL', 3, 61)",
            "Token('gcc', 'TEXT', 3, 62)",
            "Token('\\n\\n', 'TEXT-NEWLINE', 3, 65)",
            "Token('pkgname', 'NAME-VARIABLE', 5, 67)",
            "Token('=', 'OPERATOR-EQUAL', 5, 74)",
            'Token(\'"$pkgname$_target"\', \'LITERAL-STRING-DOUBLE\', 5, 75)',
            "Token('\\n', 'TEXT-NEWLINE', 5, 93)",
            "Token('foo', 'NAME-VARIABLE', 6, 94)",
            "Token('=', 'OPERATOR-EQUAL', 6, 97)",
            "Token('bar', 'TEXT', 6, 98)",
            "Token('\\n', 'TEXT-NEWLINE', 6, 101)",
            "Token('baz', 'NAME-VARIABLE', 7, 102)",
            "Token('=', 'OPERATOR-EQUAL', 7, 105)",
            "Token('$foo', 'TEXT', 7, 106)",
            "Token('\\n', 'TEXT-NEWLINE', 7, 110)",
            "Token('bez', 'NAME-VARIABLE', 8, 111)",
            "Token('=', 'OPERATOR-EQUAL', 8, 114)",
            "Token('${foo}', 'TEXT', 8, 115)",
            "Token('\\n', 'TEXT-NEWLINE', 8, 121)",
            "Token('gnat()', 'TEXT', 9, 122)",
            "Token(' ', 'TEXT-WHITESPACE', 9, 128)",
            "Token('{', 'TEXT', 9, 129)",
            "Token('\\n', 'TEXT-NEWLINE', 9, 130)",
            "Token('    ', 'TEXT-WHITESPACE', 10, 131)",
            'Token(\'pkgdesc="Ada\', \'TEXT\', 10, 135)',
            "Token(' ', 'TEXT-WHITESPACE', 10, 147)",
            "Token('support', 'TEXT', 10, 148)",
            "Token(' ', 'TEXT-WHITESPACE', 10, 155)",
            "Token('for', 'TEXT', 10, 156)",
            "Token(' ', 'TEXT-WHITESPACE', 10, 159)",
            'Token(\'GCC"\', \'TEXT\', 10, 160)',
            "Token('\\n', 'TEXT-NEWLINE', 10, 164)",
            "Token('}', 'TEXT', 11, 165)",
            "Token('\\n', 'TEXT-NEWLINE', 11, 166)",
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
            "Token('\\n', 'TEXT-NEWLINE', 1, 0)",
            "Token('foo', 'NAME-VARIABLE', 2, 1)",
            "Token('=', 'OPERATOR-EQUAL', 2, 4)",
            "Token('bar', 'TEXT', 2, 5)",
            "Token('\\n', 'TEXT-NEWLINE', 2, 8)",
            "Token('baz', 'NAME-VARIABLE', 3, 9)",
            "Token('=', 'OPERATOR-EQUAL', 3, 12)",
            "Token('$foo', 'TEXT', 3, 13)",
            "Token('\\n', 'TEXT-NEWLINE', 3, 17)",
            "Token('bez', 'NAME-VARIABLE', 4, 18)",
            "Token('=', 'OPERATOR-EQUAL', 4, 21)",
            "Token('${foo}', 'TEXT', 4, 22)",
            "Token('\\n', 'TEXT-NEWLINE', 4, 28)",
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

    def test_collect_shell_variables_from_text_as_dict_does_not_munge_spaces_on_expand(self):
        text = """
pkgname=cairo
pkgver=1.16.0
depends=
depends_dev="fontconfig-dev freetype-dev libxrender-dev pixman-dev
    xcb-util-dev libxext-dev $pkgname-tools"
makedepends="$depends_dev zlib-dev expat-dev glib-dev libpng-dev autoconf automake libtool"
subpackages="$pkgname-dev $pkgname-doc $pkgname-gobject $pkgname-tools $pkgname-dbg"
source="https://cairographics.org/releases/cairo-$pkgver.tar.xz
"""
        result, errors = bashparse.collect_shell_variables_from_text_as_dict(text, resolve=True)
        expected = []
        assert errors == expected
        expected = {
            'depends_dev':
                'fontconfig-dev freetype-dev libxrender-dev pixman-dev\n    '
                'xcb-util-dev libxext-dev cairo-tools',
            'makedepends':
                'fontconfig-dev freetype-dev libxrender-dev pixman-dev\n    '
                'xcb-util-dev libxext-dev cairo-tools zlib-dev expat-dev '
                'glib-dev libpng-dev autoconf automake libtool',
            'pkgname': 'cairo',
            'pkgver': '1.16.0',
            'subpackages': 'cairo-dev cairo-doc cairo-gobject cairo-tools cairo-dbg',
        }
        assert result == expected

    def test_collect_shell_variables_from_text_can_parse_combo_single_quote_and_trailing_comments(self):
        text = '''
arch="x86_64 ppc64le aarch64"
options="!check" # out of disk space (>35GB)
license='AGPL3'
pkgusers="mongodb"
option2s='!baz' # out of disk space (>35GB)
options=duplicate
'''
        result, errors = bashparse.collect_shell_variables_from_text(text)
        expected = [
            ShellVariable(name='arch', value='x86_64 ppc64le aarch64'),
            ShellVariable(name='options', value='!check'),
            ShellVariable(name='license', value='AGPL3'),
            ShellVariable(name='pkgusers', value='mongodb'),
            ShellVariable(name='option2s', value='!baz'),
            ShellVariable(name='options', value='duplicate'),
        ]
        assert result == expected
        expected = ['Duplicate variable name: options: duplicate']
        assert errors == expected

    def test_collect_shell_variables_from_text_simple(self):
        result, errors = bashparse.collect_shell_variables_from_text(TEST_TEXT1)
        expected = [
            ShellVariable(name='pkgname', value='gcc'),
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
        assert result == expected
        assert errors == ['Duplicate variable name: pkgname: $pkgname$_target']


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
/TEXT-NEWLINE, # Contributor: Natanael Copa <ncopa@alpinelinux.org>/COMMENT-SINGLE, Tree('SHELL-VARIABLE', [
/TEXT-NEWLINE, pkgname/NAME-VARIABLE, =/OPERATOR-EQUAL, gcc/TEXT]), Tree('SHELL-VARIABLE', [

/TEXT-NEWLINE, pkgname/NAME-VARIABLE, =/OPERATOR-EQUAL, "$pkgname$_target"/LITERAL-STRING-DOUBLE]), Tree('SHELL-VARIABLE', [
/TEXT-NEWLINE, pkgrel/NAME-VARIABLE, =/OPERATOR-EQUAL, 2/TEXT]), Tree('SHELL-VARIABLE', [
/TEXT-NEWLINE, license/NAME-VARIABLE, =/OPERATOR-EQUAL, "GPL-2.0-or-later
 LGPL-2.1-or-later"/LITERAL-STRING-DOUBLE]),
/TEXT-NEWLINE,     /TEXT-WHITESPACE, license="GPL-2.0-or-later/TEXT,
/TEXT-NEWLINE,      /TEXT-WHITESPACE, LGPL-2.1-or-later"/TEXT,

/TEXT-NEWLINE, gnat()/TEXT,  /TEXT-WHITESPACE, {/TEXT,
/TEXT-NEWLINE,     /TEXT-WHITESPACE, pkgdesc="Ada/TEXT,  /TEXT-WHITESPACE, support/TEXT,  /TEXT-WHITESPACE, for/TEXT,  /TEXT-WHITESPACE, GCC"/TEXT,
/TEXT-NEWLINE, }/TEXT,
/TEXT-NEWLINE])'''
