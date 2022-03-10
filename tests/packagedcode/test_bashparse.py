#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

import pygmars

from packagedcode import bashparse
from packagedcode.bashparse import ShellVariable
from packages_test_utils  import build_tests
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


class TestBashParserDatadriven(PackageTester):
    test_data_dir = test_data_dir


def tree_to_dict(o):
    if isinstance(o, pygmars.Token):
        return dict(label=o.label, value=o.value, start_line=o.start_line, pos=o.pos)
    elif isinstance(o, pygmars.tree.Tree):
        return {o.label: [tree_to_dict(child) for child in o]}


build_tests(
    test_dir=os.path.join(test_data_dir, 'bashparse'),
    test_file_suffix='.sh',
    clazz=TestBashParserDatadriven,
    tested_function=lambda loc: list(bashparse.collect_shell_variables(loc, resolve=True)),
    test_method_prefix='test_collect_shell_variables_',
    regen=REGEN_TEST_FIXTURES,
)


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

        expected = [
            {'label': 'TEXT-WS-LF',
             'pos': 0,
             'start_line': 1,
             'value': '\n'},
            {'label': 'COMMENT',
             'pos': 1,
             'start_line': 2,
             'value': '# Contributor: Natanael Copa <ncopa@alpinelinux.org>'},
            {'label': 'TEXT-WS-LF',
             'pos': 53,
             'start_line': 2,
             'value': '\n'},
            {'label': 'NAME-VARIABLE',
             'pos': 54,
             'start_line': 3,
             'value': 'pkgname'},
            {'label': 'OPERATOR-EQUAL',
             'pos': 61,
             'start_line': 3,
             'value': '='},
            {'label': 'TEXT',
             'pos': 62,
             'start_line': 3,
             'value': 'gcc'},
            {'label': 'TEXT-WS-LF',
             'pos': 65,
             'start_line': 3,
             'value': '\n'
                      '\n'},
            {'label': 'NAME-VARIABLE',
             'pos': 67,
             'start_line': 5,
             'value': 'pkgname'},
            {'label': 'OPERATOR-EQUAL',
             'pos': 74,
             'start_line': 5,
             'value': '='},
            {'label': 'LITERAL-STRING-DOUBLE',
             'pos': 75,
             'start_line': 5,
             'value': '"$pkgname$_target"'},
            {'label': 'TEXT-WS-LF',
             'pos': 93,
             'start_line': 5,
             'value': '\n'},
            {'label': 'NAME-VARIABLE',
             'pos': 94,
             'start_line': 6,
             'value': 'foo'},
            {'label': 'OPERATOR-EQUAL',
             'pos': 97,
             'start_line': 6,
             'value': '='},
            {'label': 'TEXT',
             'pos': 98,
             'start_line': 6,
             'value': 'bar'},
            {'label': 'TEXT-WS-LF',
             'pos': 101,
             'start_line': 6,
             'value': '\n'},
            {'label': 'NAME-VARIABLE',
             'pos': 102,
             'start_line': 7,
             'value': 'baz'},
            {'label': 'OPERATOR-EQUAL',
             'pos': 105,
             'start_line': 7,
             'value': '='},
            {'label': 'TEXT',
             'pos': 106,
             'start_line': 7,
             'value': '$foo'},
            {'label': 'TEXT-WS-LF',
             'pos': 110,
             'start_line': 7,
             'value': '\n'},
            {'label': 'NAME-VARIABLE',
             'pos': 111,
             'start_line': 8,
             'value': 'bez'},
            {'label': 'OPERATOR-EQUAL',
             'pos': 114,
             'start_line': 8,
             'value': '='},
            {'label': 'TEXT',
             'pos': 115,
             'start_line': 8,
             'value': '${foo}'},
            {'label': 'TEXT-WS-LF',
             'pos': 121,
             'start_line': 8,
             'value': '\n'},
            {'label': 'TEXT',
             'pos': 122,
             'start_line': 9,
             'value': 'gnat()'},
            {'label': 'TEXT-WS',
             'pos': 128,
             'start_line': 9,
             'value': ' '},
            {'label': 'TEXT',
             'pos': 129,
             'start_line': 9,
             'value': '{'},
            {'label': 'TEXT-WS-LF',
             'pos': 130,
             'start_line': 9,
             'value': '\n'},
            {'label': 'TEXT-WS',
             'pos': 131,
             'start_line': 10,
             'value': '    '},
            {'label': 'TEXT',
             'pos': 135,
             'start_line': 10,
             'value': 'pkgdesc="Ada'},
            {'label': 'TEXT-WS',
             'pos': 147,
             'start_line': 10,
             'value': ' '},
            {'label': 'TEXT',
             'pos': 148,
             'start_line': 10,
             'value': 'support'},
            {'label': 'TEXT-WS',
             'pos': 155,
             'start_line': 10,
             'value': ' '},
            {'label': 'TEXT',
             'pos': 156,
             'start_line': 10,
             'value': 'for'},
            {'label': 'TEXT-WS',
             'pos': 159,
             'start_line': 10,
             'value': ' '},
            {'label': 'TEXT',
             'pos': 160,
             'start_line': 10,
             'value': 'GCC"'},
            {'label': 'TEXT-WS-LF',
             'pos': 164,
             'start_line': 10,
             'value': '\n'},
            {'label': 'TEXT',
             'pos': 165,
             'start_line': 11,
             'value': '}'},
            {'label': 'TEXT-WS-LF',
             'pos': 166,
             'start_line': 11,
             'value': '\n'},
        ]

        result = [tree_to_dict(o) for o in bashparse.get_tokens(text)]
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

        result = tree_to_dict(bashparse.parse_shell(text))
        assert result == EXPECTED_SIMPLE

    def test_get_tokens_simple(self):
        text = '''
foo=bar
baz=$foo
bez=${foo}
'''

        expected = [
            {'label': 'TEXT-WS-LF',
             'pos': 0,
             'start_line': 1,
             'value': '\n'},
            {'label': 'NAME-VARIABLE',
             'pos': 1,
             'start_line': 2,
             'value': 'foo'},
            {'label': 'OPERATOR-EQUAL',
             'pos': 4,
             'start_line': 2,
             'value': '='},
            {'label': 'TEXT',
             'pos': 5,
             'start_line': 2,
             'value': 'bar'},
            {'label': 'TEXT-WS-LF',
             'pos': 8,
             'start_line': 2,
             'value': '\n'},
            {'label': 'NAME-VARIABLE',
             'pos': 9,
             'start_line': 3,
             'value': 'baz'},
            {'label': 'OPERATOR-EQUAL',
             'pos': 12,
             'start_line': 3,
             'value': '='},
            {'label': 'TEXT',
             'pos': 13,
             'start_line': 3,
             'value': '$foo'},
            {'label': 'TEXT-WS-LF',
             'pos': 17,
             'start_line': 3,
             'value': '\n'},
            {'label': 'NAME-VARIABLE',
             'pos': 18,
             'start_line': 4,
             'value': 'bez'},
            {'label': 'OPERATOR-EQUAL',
             'pos': 21,
             'start_line': 4,
             'value': '='},
            {'label': 'TEXT',
             'pos': 22,
             'start_line': 4,
             'value': '${foo}'},
            {'label': 'TEXT-WS-LF',
             'pos': 28,
             'start_line': 4,
             'value': '\n'},
        ]

        result = [tree_to_dict(o) for o in bashparse.get_tokens(text)]
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

    def test_collect_shell_variables_from_text_filters_on_needed_variables(self):
        text = '''
arch="x86_64"
options="foo"
license='AGPL3'
options=duplicate
'''

        result, errors = bashparse.collect_shell_variables_from_text(
            text=text,
            needed_variables=set(['license']),
        )
        expected = [
            ShellVariable(name='license', value='AGPL3'),
        ]
        assert result == expected
        expected = []
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

EXPECTED_SIMPLE = {
'ROOT': [{'label': 'TEXT-WS-LF',
          'pos': 0,
          'start_line': 1,
          'value': '\n'},
         {'label': 'COMMENT',
          'pos': 1,
          'start_line': 2,
          'value': '# Contributor: Natanael Copa <ncopa@alpinelinux.org>'},
         {'SHELL-VARIABLE': [{'label': 'TEXT-WS-LF',
                              'pos': 53,
                              'start_line': 2,
                              'value': '\n'},
                             {'label': 'NAME-VARIABLE',
                              'pos': 54,
                              'start_line': 3,
                              'value': 'pkgname'},
                             {'label': 'OPERATOR-EQUAL',
                              'pos': 61,
                              'start_line': 3,
                              'value': '='},
                             {'label': 'TEXT',
                              'pos': 62,
                              'start_line': 3,
                              'value': 'gcc'}]},
         {'SHELL-VARIABLE': [{'label': 'TEXT-WS-LF',
                              'pos': 65,
                              'start_line': 3,
                              'value': '\n'
                                       '\n'},
                             {'label': 'NAME-VARIABLE',
                              'pos': 67,
                              'start_line': 5,
                              'value': 'pkgname'},
                             {'label': 'OPERATOR-EQUAL',
                              'pos': 74,
                              'start_line': 5,
                              'value': '='},
                             {'label': 'LITERAL-STRING-DOUBLE',
                              'pos': 75,
                              'start_line': 5,
                              'value': '"$pkgname$_target"'}]},
         {'SHELL-VARIABLE': [{'label': 'TEXT-WS-LF',
                              'pos': 93,
                              'start_line': 5,
                              'value': '\n'},
                             {'label': 'NAME-VARIABLE',
                              'pos': 94,
                              'start_line': 6,
                              'value': 'pkgrel'},
                             {'label': 'OPERATOR-EQUAL',
                              'pos': 100,
                              'start_line': 6,
                              'value': '='},
                             {'label': 'TEXT',
                              'pos': 101,
                              'start_line': 6,
                              'value': '2'}]},
         {'SHELL-VARIABLE': [{'label': 'TEXT-WS-LF',
                              'pos': 102,
                              'start_line': 6,
                              'value': '\n'},
                             {'label': 'NAME-VARIABLE',
                              'pos': 103,
                              'start_line': 7,
                              'value': 'license'},
                             {'label': 'OPERATOR-EQUAL',
                              'pos': 110,
                              'start_line': 7,
                              'value': '='},
                             {'label': 'LITERAL-STRING-DOUBLE',
                              'pos': 111,
                              'start_line': 7,
                              'value': '"GPL-2.0-or-later\n'
                                       ' LGPL-2.1-or-later"'}]},
         {'label': 'TEXT-WS-LF',
          'pos': 148,
          'start_line': 8,
          'value': '\n'},
         {'label': 'TEXT-WS',
          'pos': 149,
          'start_line': 9,
          'value': '    '},
         {'label': 'TEXT',
          'pos': 153,
          'start_line': 9,
          'value': 'license="GPL-2.0-or-later'},
         {'label': 'TEXT-WS-LF',
          'pos': 178,
          'start_line': 9,
          'value': '\n'},
         {'label': 'TEXT-WS',
          'pos': 179,
          'start_line': 10,
          'value': '     '},
         {'label': 'TEXT',
          'pos': 184,
          'start_line': 10,
          'value': 'LGPL-2.1-or-later"'},
         {'label': 'TEXT-WS-LF',
          'pos': 202,
          'start_line': 10,
          'value': '\n'
                   '\n'},
         {'label': 'TEXT',
          'pos': 204,
          'start_line': 12,
          'value': 'gnat()'},
         {'label': 'TEXT-WS',
          'pos': 210,
          'start_line': 12,
          'value': ' '},
         {'label': 'TEXT',
          'pos': 211,
          'start_line': 12,
          'value': '{'},
         {'label': 'TEXT-WS-LF',
          'pos': 212,
          'start_line': 12,
          'value': '\n'},
         {'label': 'TEXT-WS',
          'pos': 213,
          'start_line': 13,
          'value': '    '},
         {'label': 'TEXT',
          'pos': 217,
          'start_line': 13,
          'value': 'pkgdesc="Ada'},
         {'label': 'TEXT-WS',
          'pos': 229,
          'start_line': 13,
          'value': ' '},
         {'label': 'TEXT',
          'pos': 230,
          'start_line': 13,
          'value': 'support'},
         {'label': 'TEXT-WS',
          'pos': 237,
          'start_line': 13,
          'value': ' '},
         {'label': 'TEXT',
          'pos': 238,
          'start_line': 13,
          'value': 'for'},
         {'label': 'TEXT-WS',
          'pos': 241,
          'start_line': 13,
          'value': ' '},
         {'label': 'TEXT',
          'pos': 242,
          'start_line': 13,
          'value': 'GCC"'},
         {'label': 'TEXT-WS-LF',
          'pos': 246,
          'start_line': 13,
          'value': '\n'},
         {'label': 'TEXT',
          'pos': 247,
          'start_line': 14,
          'value': '}'},
         {'label': 'TEXT-WS-LF',
          'pos': 248,
          'start_line': 14,
          'value': '\n'}],
}
