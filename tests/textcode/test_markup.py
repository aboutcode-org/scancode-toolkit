# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os

from commoncode.testcase import FileBasedTesting

from textcode import markup
import pytest


class TestMarkup(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_jsp_is_markup(self):
        test_file = self.get_test_loc(u'markup/java.jsp')
        assert markup.is_markup(test_file)

    def test_jsp_demarkup(self, regen=False):
        test_file = self.get_test_loc(u'markup/java.jsp')
        result = list(markup.demarkup(test_file))
        expected_loc = self.get_test_loc(u'markup/java.jsp-expected.json')

        if regen:
            with open(expected_loc, 'w') as out:
                out.write(json.dumps(result, indent=2))

        with open(expected_loc) as inp:
            expected = json.load(inp)
        assert result == expected


@pytest.mark.parametrize(
    ["test_text", "expected_demarkup"],
    [
        (
            """<a href="https://licenses.nuget.org/Apache-2.0">Apache-2.0</a>""",
            '  ="https://licenses.nuget.org/Apache-2.0">Apache-2.0 ',

        ),
        (
            """<td width="30%">Copyright &copy; 2006 <a href="trolltech.html">Trolltech</a></td>""",
            ' width="30%">Copyright  &copy;  2006   ="trolltech.html">Trolltech  ',
        ),
        (
            "<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>",
            " SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1 ",
        )
    ],
)
def test_demarkup_text(test_text, expected_demarkup):
    assert markup.is_markup_text(test_text)
    assert markup.demarkup_text(test_text) == expected_demarkup

