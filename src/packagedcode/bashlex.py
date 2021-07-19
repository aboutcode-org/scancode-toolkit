"""
Minimal lexer for POSIX and Bash shells.
Derived from pygments.lexers.shell and significantly modified
copyright: Copyright 2006-2021 by the Pygments team, see bashlex.py.AUTHORS.
SPDX-License-Identifier: BSD-2-Clause
"""

from pygments.lexer import (
    RegexLexer,
    bygroups,
    include
)

from pygments.token import (
    Token,
    Text,
    Comment,
    Operator,
    Name,
    String,
)

# White spaces
WS = Text.WS  # NOQA
# new lines
LF = WS.LF

ArrayStart = Token.ArraySep.Start
ArrayEnd = Token.ArraySep.End
Equal = Operator.Equal  # NOQA


class BashShellLexer(RegexLexer):
    """
    A Pygments shell lexer to lex shell scripts used as package build scripts
    and package manifests such as autotools, ebuild, PKGBUILD or APKBUILD.
    This used as an input to further parse and extract metadata.
    """

    name = 'Shell'
    aliases = ['shell']
    # for info, as this is not used here otherwise
    filenames = ['*.ebuild', 'PKGBUILD', 'APKBUILD', ]
    mimetypes = []

    tokens = {
        'root': [
            include('basic'),
            include('data'),
        ],
        'basic': [
            (r'#.*$', Comment),
            # variable declaration and assignment
            (r'^(\b\w+)(\+?=)', bygroups(Name.Variable, Equal)),
        ],
        'data': [
            (r'\(', ArrayStart),
            (r'\)', ArrayEnd),
            # (?s) is re.DOTALL e.g. across lines
            (r'(?s)"(\\.|[^"])*"', String.Double),
            (r"(?s)'(\\.|[^'])*'", String.Single),
            (r'\n+', LF),
            (r'\s+', WS),
            (r'\S+', Text),
        ],
    }
