#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path
from functools import partial

import attr

from packagedcode.bashlex import BashShellLexer
from packages_test_utils  import build_tests
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


@attr.s
class PygmentsToken:
    pos = attr.ib()
    type = attr.ib()
    value = attr.ib()

    def to_dict(self):
        return attr.asdict(self)

    @classmethod
    def lex(cls, lexer, text):
        """
        Return a list of token mappings by running the ``lexer`` on the ``text``
        string.
        """
        return [cls(*ts).to_dict() for ts in lexer().get_tokens_unprocessed(text)]


class TestBashlexDatadriven(PackageTester):
    test_data_dir = test_data_dir


def lexer_tester(location, lexer_class):
    with open(location) as inp:
        text = inp.read()
    return PygmentsToken.lex(lexer_class, text)


build_tests(
    test_dir=os.path.join(test_data_dir, 'bashlex'),
    test_file_suffix=('.sh', 'APKBUILD', 'PKGBUILD',),
    clazz=TestBashlexDatadriven,
    tested_function=partial(lexer_tester, lexer_class=BashShellLexer),
    test_method_prefix='test_collect_shell_variables_',
    regen=REGEN_TEST_FIXTURES,
)

