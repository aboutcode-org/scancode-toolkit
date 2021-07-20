#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import bashparse
from packagedcode.bashparse import ShellVariable

from packages_test_utils  import build_tests
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
            "Token(value='\\n', label='TEXT-WS-LF', start_line=1, pos=0)",
            "Token(value='# Contributor: Natanael Copa <ncopa@alpinelinux.org>', label='COMMENT', start_line=2, pos=1)",
            "Token(value='\\n', label='TEXT-WS-LF', start_line=2, pos=53)",
            "Token(value='pkgname', label='NAME-VARIABLE', start_line=3, pos=54)",
            "Token(value='=', label='OPERATOR-EQUAL', start_line=3, pos=61)",
            "Token(value='gcc', label='TEXT', start_line=3, pos=62)",
            "Token(value='\\n\\n', label='TEXT-WS-LF', start_line=3, pos=65)",
            "Token(value='pkgname', label='NAME-VARIABLE', start_line=5, pos=67)",
            "Token(value='=', label='OPERATOR-EQUAL', start_line=5, pos=74)",
            'Token(value=\'"$pkgname$_target"\', label=\'LITERAL-STRING-DOUBLE\', start_line=5, pos=75)',
            "Token(value='\\n', label='TEXT-WS-LF', start_line=5, pos=93)",
            "Token(value='foo', label='NAME-VARIABLE', start_line=6, pos=94)",
            "Token(value='=', label='OPERATOR-EQUAL', start_line=6, pos=97)",
            "Token(value='bar', label='TEXT', start_line=6, pos=98)",
            "Token(value='\\n', label='TEXT-WS-LF', start_line=6, pos=101)",
            "Token(value='baz', label='NAME-VARIABLE', start_line=7, pos=102)",
            "Token(value='=', label='OPERATOR-EQUAL', start_line=7, pos=105)",
            "Token(value='$foo', label='TEXT', start_line=7, pos=106)",
            "Token(value='\\n', label='TEXT-WS-LF', start_line=7, pos=110)",
            "Token(value='bez', label='NAME-VARIABLE', start_line=8, pos=111)",
            "Token(value='=', label='OPERATOR-EQUAL', start_line=8, pos=114)",
            "Token(value='${foo}', label='TEXT', start_line=8, pos=115)",
            "Token(value='\\n', label='TEXT-WS-LF', start_line=8, pos=121)",
            "Token(value='gnat()', label='TEXT', start_line=9, pos=122)",
            "Token(value=' ', label='TEXT-WS', start_line=9, pos=128)",
            "Token(value='{', label='TEXT', start_line=9, pos=129)",
            "Token(value='\\n', label='TEXT-WS-LF', start_line=9, pos=130)",
            "Token(value='    ', label='TEXT-WS', start_line=10, pos=131)",
            'Token(value=\'pkgdesc="Ada\', label=\'TEXT\', start_line=10, pos=135)',
            "Token(value=' ', label='TEXT-WS', start_line=10, pos=147)",
            "Token(value='support', label='TEXT', start_line=10, pos=148)",
            "Token(value=' ', label='TEXT-WS', start_line=10, pos=155)",
            "Token(value='for', label='TEXT', start_line=10, pos=156)",
            "Token(value=' ', label='TEXT-WS', start_line=10, pos=159)",
            'Token(value=\'GCC"\', label=\'TEXT\', start_line=10, pos=160)',
            "Token(value='\\n', label='TEXT-WS-LF', start_line=10, pos=164)",
            "Token(value='}', label='TEXT', start_line=11, pos=165)",
            "Token(value='\\n', label='TEXT-WS-LF', start_line=11, pos=166)",
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
            "Token(value='\\n', label='TEXT-WS-LF', start_line=1, pos=0)",
            "Token(value='foo', label='NAME-VARIABLE', start_line=2, pos=1)",
            "Token(value='=', label='OPERATOR-EQUAL', start_line=2, pos=4)",
            "Token(value='bar', label='TEXT', start_line=2, pos=5)",
            "Token(value='\\n', label='TEXT-WS-LF', start_line=2, pos=8)",
            "Token(value='baz', label='NAME-VARIABLE', start_line=3, pos=9)",
            "Token(value='=', label='OPERATOR-EQUAL', start_line=3, pos=12)",
            "Token(value='$foo', label='TEXT', start_line=3, pos=13)",
            "Token(value='\\n', label='TEXT-WS-LF', start_line=3, pos=17)",
            "Token(value='bez', label='NAME-VARIABLE', start_line=4, pos=18)",
            "Token(value='=', label='OPERATOR-EQUAL', start_line=4, pos=21)",
            "Token(value='${foo}', label='TEXT', start_line=4, pos=22)",
            "Token(value='\\n', label='TEXT-WS-LF', start_line=4, pos=28)",
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

    def test_collect_shell_variables_from_text_can_parse_var_at_start(self):
        text = "foo=bar"
        result, errors = bashparse.collect_shell_variables_from_text(text)
        expected = [
            ShellVariable(name='foo', value='bar'),
        ]
        assert result == expected
        expected = []
        assert errors == expected

    def test_collect_shell_variables_from_text_can_parse_empty_var(self):
        text = "foo=\nbar=baz\nlicense=\n"
        result, errors = bashparse.collect_shell_variables_from_text(text)
        expected = [
            ShellVariable(name='foo', value=''),
            ShellVariable(name='bar', value='baz'),
            ShellVariable(name='license', value=''),
        ]
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
source="https://cairographics.org/releases/cairo-$pkgver.tar.xz"
"""
        result, errors = bashparse.collect_shell_variables_from_text_as_dict(text, resolve=True)
        expected = []
        assert errors == expected
        expected = {
            'depends': '',
            'depends_dev':
                'fontconfig-dev freetype-dev libxrender-dev pixman-dev\n    '
                'xcb-util-dev libxext-dev cairo-tools',
            'makedepends':
                'fontconfig-dev freetype-dev libxrender-dev pixman-dev\n    '
                'xcb-util-dev libxext-dev cairo-tools zlib-dev expat-dev '
                'glib-dev libpng-dev autoconf automake libtool',
            'pkgname': 'cairo',
            'pkgver': '1.16.0',
            'source': 'https://cairographics.org/releases/cairo-1.16.0.tar.xz',
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
        expected = ["Duplicate variable name: 'options' value: 'duplicate' existing value: '!check'"]
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
        assert errors == ["Duplicate variable name: 'pkgname' value: '$pkgname$_target' existing value: 'gcc'"]


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

EXPECTED_SIMPLE = '''(label='ROOT', children=(
  (label='TEXT-WS-LF', value='\\n')
  (label='COMMENT', value='# Contributor: Natanael Copa <ncopa@alpinelinux.org>')
    (label='SHELL-VARIABLE', children=(
    (label='TEXT-WS-LF', value='\\n')
    (label='NAME-VARIABLE', value='pkgname')
    (label='OPERATOR-EQUAL', value='=')
    (label='TEXT', value='gcc')
  ))
    (label='SHELL-VARIABLE', children=(
    (label='TEXT-WS-LF', value='\\n\\n')
    (label='NAME-VARIABLE', value='pkgname')
    (label='OPERATOR-EQUAL', value='=')
    (label='LITERAL-STRING-DOUBLE', value='"$pkgname$_target"')
  ))
    (label='SHELL-VARIABLE', children=(
    (label='TEXT-WS-LF', value='\\n')
    (label='NAME-VARIABLE', value='pkgrel')
    (label='OPERATOR-EQUAL', value='=')
    (label='TEXT', value='2')
  ))
    (label='SHELL-VARIABLE', children=(
    (label='TEXT-WS-LF', value='\\n')
    (label='NAME-VARIABLE', value='license')
    (label='OPERATOR-EQUAL', value='=')
    (label='LITERAL-STRING-DOUBLE', value='"GPL-2.0-or-later\\n LGPL-2.1-or-later"')
  ))
  (label='TEXT-WS-LF', value='\\n')
  (label='TEXT-WS', value='    ')
  (label='TEXT', value='license="GPL-2.0-or-later')
  (label='TEXT-WS-LF', value='\\n')
  (label='TEXT-WS', value='     ')
  (label='TEXT', value='LGPL-2.1-or-later"')
  (label='TEXT-WS-LF', value='\\n\\n')
  (label='TEXT', value='gnat()')
  (label='TEXT-WS', value=' ')
  (label='TEXT', value='{')
  (label='TEXT-WS-LF', value='\\n')
  (label='TEXT-WS', value='    ')
  (label='TEXT', value='pkgdesc="Ada')
  (label='TEXT-WS', value=' ')
  (label='TEXT', value='support')
  (label='TEXT-WS', value=' ')
  (label='TEXT', value='for')
  (label='TEXT-WS', value=' ')
  (label='TEXT', value='GCC"')
  (label='TEXT-WS-LF', value='\\n')
  (label='TEXT', value='}')
  (label='TEXT-WS-LF', value='\\n')
))
'''
