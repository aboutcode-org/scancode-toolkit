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

from pathlib import Path

import pytest

from textcode import markup

from scancode_config import SCANCODE_REGEN_TEST_FIXTURES
from textcode.markup import get_tags_and_entities

test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

markup_test_dir = Path(test_data_dir) / "markup"
markup_expected_dir = Path(test_data_dir) / "markup_expected"


def test_jsp_is_markup():
    test_file = markup_test_dir / 'java.jsp'
    assert markup.is_markup(str(test_file))


@pytest.mark.parametrize(
    "test_file",
    list(markup_test_dir.glob("*")),
)
def test_demarkup_files(test_file, regen=SCANCODE_REGEN_TEST_FIXTURES):
    result = list(markup.demarkup(test_file))
    expected_loc = markup_expected_dir / f"{test_file.name}.demarkup.json"
    if regen:
        expected_loc.write_text(json.dumps(result, indent=2))

    expected = expected_loc.read_text()

    assert json.dumps(result, indent=2) == expected


@pytest.mark.parametrize(
    "test_file",
    list(markup_test_dir.glob("*")),
)
def test_get_tags_and_entities(test_file):
    lines = test_file.read_text(errors=" ").splitlines(True)
    result = ["".join(get_tags_and_entities(l)) for l in lines]
    assert result == lines


@pytest.mark.parametrize(
    ["test_text", "expected_demarkup"],
    [
        (
            """<a href="https://licenses.nuget.org/Apache-2.0">Apache-2.0</a>""",
            '  ="https://licenses.nuget.org/Apache-2.0">Apache-2.0 ',

        ),
        (
            """<td width="30%">Copyright &copy; 2006 <a href="trolltech.html">Trolltech</a></td>""",
            ' width="30%">Copyright &copy; 2006   ="trolltech.html">Trolltech  ',
        ),
        (
            "<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>",
            " SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1 ",
        ),
        (
            "Copyright (C) 2009 Eric Paris <Red Hat Inc>",
            "Copyright (C) 2009 Eric Paris <Red Hat Inc>",
        )
    ],
)
def test_demarkup_text(test_text, expected_demarkup):
    assert markup.is_markup_text(test_text)
    assert markup.demarkup_text(test_text) == expected_demarkup

