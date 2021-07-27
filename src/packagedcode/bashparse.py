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
        logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

#
# A simple and minimal pygmars grammar to collect bash/shell variables.
variables_grammar = (

    'SHELL-ARRAY: '
        '<ARRAYSEP-START>'
            '<TEXT-WS| TEXT-WS-LF | COMMENT |LITERAL-STRING-DOUBLE | LITERAL-STRING-SINGLE | TEXT>+'
        '<ARRAYSEP-END>'
        ' # An array'
    '\n'

    # This collects variables like: pkgname="gcc  compiler" or pkgname=gcc .
    # With the TEXT-WS-LF (newline) (not captured) at the start we ensure we get
    # only things that start on a new line, e.g. that should be top level
    # variable declaration rather than inside a function.
    'SHELL-VARIABLE: '
        '(?:<TEXT-WS-LF>|^)'
        '<NAME-VARIABLE>'
        '<OPERATOR-EQUAL>'
        '<LITERAL-STRING-DOUBLE | LITERAL-STRING-SINGLE | TEXT | SHELL-ARRAY>'
        ' # A Shell variable'

    '\n'

    'EMPTY-SHELL-VARIABLE: '
        '(?:<TEXT-WS-LF>|^)'
        '<NAME-VARIABLE>'
        '<OPERATOR-EQUAL>'
        '(?:<TEXT-WS-LF>?|$)'
        ' # Am empty Shell variable'

)


def collect_shell_variables(location, resolve=False, needed_variables=None):
    """
    Return a tuple of (``shell variables``, ``errors``) from collecting top-
    level variables defined in bash script at ``location``.

    ``shell variables`` is a mapping of {name: value}
    ``errors`` a list of error message strings.

    Optionally ``resolve`` the variables with emulated shell parameter
    expansion. If the set ``needed_variables`` is provided, only return
    variables with a named present in this set and only report errors for
    variables with a name listed in this set.
    """
    with open(location) as inp:
        text = inp.read()

    return collect_shell_variables_from_text_as_dict(
        text=text,
        resolve=resolve,
        needed_variables=needed_variables,
    )

#
# Convenience functions on parse tree labels


def is_shell_variable(node):
    return node.label.startswith('SHELL-VARIABLE')


def is_empty_shell_variable(node):
    return node.label.startswith('EMPTY-SHELL-VARIABLE')


def is_array(node):
    return node.label.startswith('SHELL-ARRAY')


def is_array_sep(node):
    return node.label.startswith('ARRAYSEP')


def is_whitespace(node):
    return node.label.startswith('TEXT-WS')


def is_comment(node):
    return node.label.startswith('COMMENT')


def is_ignorable(node):
    return is_whitespace(node) or is_comment(node)


def is_decoration(node):
    return is_ignorable(node) or is_array_sep(node)


@attr.s
class ShellVariable:

    name = attr.ib()
    value = attr.ib()
    is_array = attr.ib(default=False, repr=False)

    def is_resolved(self):
        """
        Return True if this variable is fully resolved and does not need further
        shell expansion.
        """
        if self.is_array:
            for item in self.value:
                return not any(c in item for c in '${}')
        return not any(c in self.value for c in '${}')

    @classmethod
    def from_node(cls, node):
        """
        Return a ShellVariable built from a parse tree node or None.
        """

        def get_content(_node, _length):
            _content = [n for n in _node if not is_ignorable(n)]
            assert len(_content) == _length, (
                f'Unknown shell assignment syntax: {_node}'
            )
            return _content

        if is_empty_shell_variable(node):
            # removes space nodes and comment nodes
            content = get_content(node, 2)
            # we should be left with two elements: name=
            name_token , _equal_token = content
            return cls(name=name_token.value, value='', is_array=False)

        if not is_shell_variable(node):
            return

        content = get_content(node, 3)
        # we should be left with three elements: name = value
        name_token , _equal_token , value_token = content

        if is_array(value_token):
            array = True
            items = [
                i for i in value_token.leaves()
                if not is_decoration(i)
            ]
            value = [dequote(vt) for vt in items]
        else:
            # a plain value string
            array = False

            value = dequote(value_token)
        sv = cls(name=name_token.value, value=value, is_array=array)
        return sv

    @classmethod
    def validate(cls, variables, needed_variables=None):
        """
        Return a list of error message if some variables in a ``variables``
        list of ShellVariable are not valid.
        """

        def reportable(v):
            if needed_variables:
                return v.name in needed_variables
            return True

        seen = dict()
        errors = []
        for var in variables:
            # check for duplicate names, but these could be redefinitions
            if reportable(var):
                if var.name in seen:
                    errors.append(
                        f'Duplicate variable name: {var.name!r} value: {var.value!r} '
                        f'existing value: {seen[var.name]!r}'
                    )
                else:
                    seen[var.name] = var.value
        return errors

    @classmethod
    def resolve(cls, variables, needed_variables=None):
        """
        Resolve each variables in a ``variables`` list of ShellVariable. Return
        a tuple of (list with updated variables, list of error messages). Do not
        report errors for variable with a name listed in the
        ``needed_variables`` set if provided.
        """

        def reportable(v):
            if needed_variables:
                return v.name in needed_variables
            return True

        # mapping of variables that we use for resolution
        # the mappings and values are updated as resolution progresses
        environment = {}
        errors = []
        for var in variables:

            if not environment:
                if reportable(var) and not var.is_resolved():
                    errors.append(f'Unresolvable first variable: {var}')

                if not var.is_array:
                    # we do not know how to expand an array
                    environment[var.name] = var.value
                continue

            if var.is_resolved():
                if not var.is_array:
                    # we do not know how to expand an array
                    environment[var.name] = var.value
                continue

            try:
                if var.is_array:
                    expanded = []
                    for item in var.value:
                        exp = pe.expand(item, env=environment)
                        if reportable(var) and ' ' in item and ' ' not in expanded:
                            errors.append(f'Expansion munged spaces in value: {item}')
                        expanded.append(exp)
                else:
                    expanded = pe.expand(var.value, env=environment)
                    if reportable(var) and ' ' in var.value and ' ' not in expanded:
                        errors.append(f'Expansion munged spaces in value: {var.value}')

                if TRACE:
                    logger_debug(
                        f'Resolved variable: {var} to: {expanded} '
                        f'with envt: {environment} '
                    )

                var.value = expanded

                if not var.is_array:
                    # we do not know how to expand an array
                    environment[var.name] = expanded

                if reportable(var) and not var.is_resolved():
                    errors.append(
                        f'Partially resolved variable: {var} envt: '
                        f'{environment}'
                    )

            except Exception as e:
                if reportable(var):
                    errors.append(f'Failed to expand variable: {var} error: {e}')

        return variables, errors

    def to_dict(self):
        return {self.name: self.value}


def dequote(token):
    """
    Return a token value stripped from quotes based on its token label.
    """
    quote_style_by_token_label = {
        'LITERAL-STRING-DOUBLE':'"',
        'LITERAL-STRING-SINGLE': "'",
    }
    qs = quote_style_by_token_label.get(token.label)
    s = token.value
    if qs and s.startswith(qs) and s.endswith(qs):
        return s[1:-1]
    return s


def collect_shell_variables_from_text_as_dict(text, resolve=False, needed_variables=None):
    """
    Return a tuple of (variables, errors) from collecting top-level variables
    defined in bash script ``text`` string. ``variables`` is a mapping of {name:
    value} and ``errors`` a list of error message strings.

    Optionally ``resolve`` the variables with emulated shell parameter
    expansion. If the set ``needed_variables`` is provided, only return
    variables with a named present in this set and only report errors for
    variables with a name listed in this set.
    """
    vrs, errs = collect_shell_variables_from_text(text, resolve, needed_variables)
    return {v.name: v.value for v in vrs}, errs


def collect_shell_variables_from_text(text, resolve=False, needed_variables=None):
    """
    Return a tuple of (variables, errors) from collecting top-level variables
    defined in bash script ``text`` string.``variables`` is a list of
    ShellVariable objects and ``errors`` a list of error message strings.

    Optionally ``resolve`` the variables with emulated shell parameter
    expansion. If the set ``needed_variables`` is provided, only return
    variables with a named present in this set and only report errors for
    variables with a name listed in this set.
    """
    parse_tree = parse_shell(text)
    variables = []
    # then walk the parse parse_tree to get variables
    for node in parse_tree:
        if TRACE:
            logger_debug(f'collect_shell_variables: parse_tree node: {node}')

        if not isinstance(node, tree.Tree):
            if TRACE: logger_debug(f'   skipped: {node}')
            continue

        variable = ShellVariable.from_node(node)
        if TRACE: logger_debug(f'   variable: {variable}')
        if variable:
            variables.append(variable)

    errors = ShellVariable.validate(variables, needed_variables)

    if resolve:
        variables, rerrors = ShellVariable.resolve(variables, needed_variables)
        errors.extend(rerrors)

    if needed_variables:
        variables = [v for v in variables if v.name in needed_variables]

    return variables, errors


def get_tokens(text):
    """
    Return a Tokens list from ``text``.
    """
    lexer = BashShellLexer()
    pygtokens = lexer.get_tokens_unprocessed(text)
    return list(Token.from_pygments_tokens(pygtokens))


def parse_shell(text, grammar=variables_grammar, loop=1, trace=TRACE, validate=VALIDATE):
    """
    Return a pygmars parse Tree built from a ``text`` string.
    """
    tokens = get_tokens(text)

    # then build a parse parse_tree based on tagged tokens
    parser = parse.Parser(
        grammar=grammar,
        trace=trace,
        validate=validate,
        loop=loop,
    )

    if TRACE:
        tokens = list(tokens)
        logger_debug(f'parse_shell: parsing tokens #: {len(tokens)}')

    if TRACE:
        logger_debug(f'parse_shell: calling parser.parse')

    parse_tree = parser.parse(tokens)

    if TRACE:
        logger_debug(f'parse_shell: got parse_tree: {parse_tree}')

    return parse_tree


if __name__ == '__main__':
    import json
    import sys  # NOQA
    test_file = sys.argv[1]
    results, errs = collect_shell_variables(test_file, resolve=True)
    print(json.dumps(dict(variables=results, errors=errs), indent=2))
