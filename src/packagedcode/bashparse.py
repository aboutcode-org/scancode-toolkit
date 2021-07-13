#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import attr
from parameter_expansion import pe
from pygmars import parse
from pygmars import Token
from pygmars import tree

from packagedcode.bashlex import BashShellLexer

"""
Extract and resolve variable from a Bash or shell script.
"""

# Tracing flags
TRACE = False or os.environ.get('SCANCODE_DEBUG_BASHPARSE', False)
if TRACE:
    TRACE = int(TRACE)

VALIDATE = False or os.environ.get('SCANCODE_DEBUG_BASHPARSE_VALIDATE', False)


# Tracing flags
def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

#
# a pygmars minimal grammar to collect bash/shell variables
variables_grammar = '''

# variable like: \\n pkgname="gcc  compiler"
SHELL-VARIABLE:  <TOKEN-TEXT-NEWLINE> <TOKEN-NAME-VARIABLE> <TOKEN-OPERATOR-EQUAL> <TOKEN-LITERAL-STRING-DOUBLE|TOKEN-LITERAL-STRING-SINGLE>

# with the TOKEN-TEXT-NEWLINE at the start we ensure we get only things that
# start on a new line, e.g. should be top level rather than inside a function

# variable like: \\n pkgname=gcc \\n
SHELL-VARIABLE:  <TOKEN-TEXT-NEWLINE> <TOKEN-NAME-VARIABLE> <TOKEN-OPERATOR-EQUAL> <TOKEN-TEXT>
'''


@attr.s
class ShellVariable:

    name = attr.ib()
    value = attr.ib()

    def is_resolved(self):
        """
        Return True if this variable is fully resolved and does not need further
        shell expansion.
        """
        return not any(c in self.value for c in '${}')

    @classmethod
    def from_node(cls, node):
        """
        Return a ShellVariable built from a parse tree node or None.
        """
        if 'SHELL-VARIABLE' not in node.label:
            return

        # removes space nodes
        filtered = [
            token for token in node.leaves()
            if token.label not in ('TOKEN-TEXT-NEWLINE', 'TOKEN-TEXT-WHITESPACE',)
        ]
        # we should be left with three elements
        assert len(filtered) == 3, f'Unknown ShellVaribale node: {node}'
        name_token, _equal, value_token = filtered
        value = dequote(value_token)
        return cls(name=name_token.value, value=value)

    @classmethod
    def validate(cls, variables):
        """
        Return a list of error messrage if some variables in a ``variables``
        list of ShellVariable are not valid.
        """
        seen = set()
        errors = []
        for var in variables:
            if var.name in seen:
                errors.append(f'Duplicate varibale name: {var.name}: {var.value}')
            else:
                seen.add(var.name)
        return errors

    @classmethod
    def resolve(cls, variables):
        """
        Resolve each variables in a ``variables`` list of ShellVariable.
        Return a tuple of (list with updated variables, list of error messages).
        """

        # mapping of variables that we use for resolution
        # the mappings and values are updated as resolution progresses
        environment = {}
        errors = []
        for var in variables:
            if not environment:
                if not var.is_resolved():
                    errors.append(f'Unresolvable first variable: {var}')
                environment[var.name] = var.value
                continue
            if var.is_resolved():
                environment[var.name] = var.value
                continue
            try:
                expanded = pe.expand(var.value, env=environment)
                if TRACE:
                    logger_debug(
                        f'Resolved variable: {var} to: {expanded} with envt: {environment} ')
                var.value = expanded
                environment[var.name] = expanded
                if not var.is_resolved():
                    errors.append(
                        f'Partially resolved variable: {var} envt: {environment}')
            except Exception as e:
                errors.append(f'Failed to expand variable: {var} error: {e}')

        return variables, errors


def dequote(token):
    """
    Return a token value stripped from quotes based on its token label.
    """
    quote_style_by_token_label = {
        'TOKEN-LITERAL-STRING-DOUBLE':'"',
        'TOKEN-LITERAL-STRING-SINGLE': "'",
    }
    qs = quote_style_by_token_label.get(token.label)
    if qs:
        return token.value.strip(qs)
    else:
        return token.value


def collect_shell_variables(location, resolve=False):
    """
    Return a tuple of (variables, errors) from collecting top-level variables
    defined in bash script at ``location``.
    """
    with open(location) as inp:
        text = inp.read()
    return collect_shell_variables_from_text(text, resolve)


def collect_shell_variables_from_text(text, resolve=False):
    """
    Return a tuple of (variables, errors) from collecting top-level variables
    defined in bash script ``text`` string.
    """
    parse_tree = parse_shell(text)
    variables = []
    # then walk the parse parse_tree to get variables
    for node in parse_tree:
        if TRACE: logger_debug(f'collect_shell_variables: parse_tree node: {node}')
        if not isinstance(node, tree.Tree):
            if TRACE: logger_debug(f'   skipped: {node}')
            continue

        variable = ShellVariable.from_node(node)
        if TRACE: logger_debug(f'   variable: {variable}')
        if variable:
            variables.append(variable)

    errors = []
    if resolve:
        errors = ShellVariable.validate(variables)
        variables, rerrors = ShellVariable.resolve(variables)
        errors.extend(rerrors)
    return variables, errors


def get_tokens(text):
    """
    Return a Tokens from ``text``.
    """
    lexer = BashShellLexer()
    pygtokens = lexer.get_tokens_unprocessed(text)
    return list(Token.from_pygments_tokens(pygtokens))


def parse_shell(text, grammar=variables_grammar, trace=TRACE, validate=VALIDATE):
    """
    Return a pygmars parse Tree built from a ``text`` string.
    """
    tokens = get_tokens(text)

    # then build a parse parse_tree based on tagged tokens
    parser = parse.Parser(
        grammar=grammar,
        trace=trace,
        validate=validate,
    )

    parse_tree = parser.parse(tokens)

    if TRACE:
        logger_debug(f'parse_shell: parse_tree: {parse_tree}')

    return parse_tree
