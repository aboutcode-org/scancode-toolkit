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
from textcode.markup import split_on_tags_and_entities

test_data_dir = os.path.join(os.path.dirname(__file__), "data")

markup_test_dir = Path(test_data_dir) / "markup"
markup_expected_dir = Path(test_data_dir) / "markup_expected"

MARKUP_TEST_FILES = list(markup_test_dir.glob("*"))


def test_jsp_is_markup():
    test_file = markup_test_dir / "java.jsp"
    assert markup.is_markup(str(test_file))


@pytest.mark.parametrize(
    "test_file",
    MARKUP_TEST_FILES,
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
    MARKUP_TEST_FILES,
)
def test_strip_known_markup_from_text_files(test_file, regen=SCANCODE_REGEN_TEST_FIXTURES):

    result = list(markup.demarkup(location=test_file, stripper=markup.strip_known_markup_from_text))
    expected_loc = markup_expected_dir / f"{test_file.name}.stripmarkup.json"
    if regen:
        expected_loc.write_text(json.dumps(result, indent=2))

    expected = expected_loc.read_text()

    assert json.dumps(result, indent=2) == expected


@pytest.mark.parametrize(
    "test_file",
    MARKUP_TEST_FILES,
)
def test_strip_markup_legacy_files(test_file, regen=SCANCODE_REGEN_TEST_FIXTURES):

    result = list(markup.demarkup(location=test_file, stripper=markup.strip_markup_text_legacy))
    expected_loc = markup_expected_dir / f"{test_file.name}.stripmarkup-legacy.json"
    if regen:
        expected_loc.write_text(json.dumps(result, indent=2))

    expected = expected_loc.read_text()

    assert json.dumps(result, indent=2) == expected


@pytest.mark.parametrize("test_file", MARKUP_TEST_FILES)
def test_get_tags_and_entities(test_file):
    lines = test_file.read_text(errors=" ").splitlines(True)
    result = ["".join(split_on_tags_and_entities(l)) for l in lines]
    assert result == lines


demarkup_tests = [
    (
        """<a href="https://licenses.nuget.org/Apache-2.0">Apache-2.0</a>""",
        '="https://licenses.nuget.org/Apache-2.0">Apache-2.0',
    ),
    (
        """<td width="30%">Copyright &copy; 2006 <a href="trolltech.html">Trolltech</a></td>""",
        'width="30%">Copyright &copy; 2006 ="trolltech.html">Trolltech',
    ),
    (
        "<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>",
        "SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1",
    ),
    (
        "Copyright (C) 2009 Eric Paris <Red Hat Inc>",
        "Copyright (C) 2009 Eric Paris <Red Hat Inc>",
    ),
    (
        "(c) 2007-2008 Cyril Brulebois <kibi@debian.org>",
        "(c) 2007-2008 Cyril Brulebois <kibi@debian.org>",
    ),
    (
        "<s>Foo Bar</s>",
        "<s>Foo Bar</s>",
    ),
]


@pytest.mark.parametrize(["test_text", "expected_demarkup"], demarkup_tests)
def test_demarkup_text(test_text, expected_demarkup):
    assert markup.demarkup_text(test_text) == expected_demarkup


is_markup_tests = [
    (
        """<a href="https://licenses.nuget.org/Apache-2.0">Apache-2.0</a>""",
        True,
    ),
    (
        """<td width="30%">Copyright &copy; 2006 <a href="trolltech.html">Trolltech</a></td>""",
        True,
    ),
    (
        "<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>",
        True,
    ),
    (
        "<s>Foo Bar</s>",
        True,
    ),
    (
        "Philip Hazel <ph10@cam.ac.uk> University of Cambridge",
        False,
    ),
    (
        "(c) 2007-2008 Cyril Brulebois <kibi@debian.org>",
        False,
    ),
    (
        "Copyright (C) 2009 Eric Paris <Red Hat Inc>",
        True,
    ),
    (
        "<dd>Marks the token value as a part of an error traceback.</dd>\n",
        True,
    ),
]


@pytest.mark.parametrize(["test_text", "is_markup"], is_markup_tests)
def test_is_markup(test_text, is_markup):
    assert markup.is_markup_text(test_text) == is_markup


legacy_stripmarkup_tests = [
    (
        """<a href="https://licenses.nuget.org/Apache-2.0">Apache-2.0</a>""",
        "Apache-2.0</a>",
    ),
    (
        """<td width="30%">Copyright &copy; 2006 <a href="trolltech.html">Trolltech</a></td>""",
        "Copyright &copy; 2006  Trolltech</a>",
    ),
    (
        "<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>",
        "<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>",
    ),
    (
        "<br>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</br>",
        "SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1",
    ),
    (
        "<br>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1<br/>",
        "SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1",
    ),
    (
        "<s>Foo Bar</s>",
        "<s>Foo Bar</s>",
    ),
    (
        "Philip Hazel <ph10@cam.ac.uk> University of Cambridge",
        "Philip Hazel <ph10@cam.ac.uk> University of Cambridge",
    ),
    (
        "(c) 2007-2008 Cyril Brulebois <kibi@debian.org>",
        "(c) 2007-2008 Cyril Brulebois <kibi@debian.org>",
    ),
    (
        "Copyright (C) 2009 Eric Paris <Red Hat Inc>",
        "Copyright (C) 2009 Eric Paris",
    ),
    (
        "<dd>Marks the token value as a part of an error traceback.</dd>\n",
        "Marks the token value as a part of an error traceback.",
    ),
    (
        "Copyright (c) 2012 Rod Vagg [@rvagg](https://twitter.com/rvagg)",
        "Copyright (c) 2012 Rod Vagg [@rvagg](https://twitter.com/rvagg)",
    ),
]


@pytest.mark.parametrize(["test_text", "expected_demarkup"], legacy_stripmarkup_tests)
def test_strip_markup_text_legacy(test_text, expected_demarkup):
    assert markup.strip_markup_text_legacy(test_text) == expected_demarkup


new_stripmarkup_tests = [
    (
        """<a href="https://licenses.nuget.org/Apache-2.0">Apache-2.0</a>""",
        "Apache-2.0",
    ),
    (
        """<td width="30%">Copyright &copy; 2006 <a href="trolltech.html">Trolltech</a></td>""",
        "Copyright &copy; 2006 Trolltech",
    ),
    (
        "<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>",
        "<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>",
    ),
    (
        "<br>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</br>",
        "SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1",
    ),
    (
        "<br>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1<br/>",
        "SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1",
    ),
    (
        "Jason Hunter <jhunter AT jdom DOT org>",
        "Jason Hunter <jhunter AT jdom DOT org",
    ),
    (
        "<s>Foo Bar</s>",
        "Foo Bar",
    ),
    (
        "Philip Hazel <ph10@cam.ac.uk> University of Cambridge",
        "Philip Hazel <ph10@cam.ac.uk> University of Cambridge",
    ),
    (
        "(c) 2007-2008 Cyril Brulebois <kibi@debian.org>",
        "(c) 2007-2008 Cyril Brulebois <kibi@debian.org>",
    ),
    (
        "Copyright (C) 2009 Eric Paris <Red Hat Inc>",
        "Copyright (C) 2009 Eric Paris <Red Hat Inc",
    ),
    (
        "<dd>Marks the token value as a part of an error traceback.</dd>\n",
        "Marks the token value as a part of an error traceback.",
    ),
    (
        "(c) 2007-2008 Cyril Brulebois <kibi@debian.org> @end group @group",
        "(c) 2007-2008 Cyril Brulebois <kibi@debian.org> group",
    ),
    (
        "Copyright (c) 2012 Rod Vagg [@rvagg](https://twitter.com/rvagg)",
        "Copyright (c) 2012 Rod Vagg [@rvagg](https://twitter.com/rvagg)",
    ),
    (
        """for <span class="application">AMOR</span>, and also the one with """
        """the most “<span class="quote">tricks</span>”.  This theme was """
        """created by <span class="firstname">Martin</span> <span class="othername">R.</span> """
        """<span class="surname">Jones</span>.  The jet-pack, beaming, and fire animations were """
        """contributed by <span class="firstname">Mark</span> <span class="surname">Grant</span>.""",
        (
            "for AMOR , and also the one with the most “ tricks ”. This theme was "
            "created by Martin R. Jones . The jet-pack, beaming, and fire "
            "animations were contributed by Mark Grant ."
        ),
    ),
]


@pytest.mark.parametrize(["test_text", "expected_demarkup"], new_stripmarkup_tests)
def test_strip_markup_text_tagset(test_text, expected_demarkup):
    assert markup.strip_known_markup_from_text(test_text) == expected_demarkup


split_tests = [
    (
        """<a href="https://licenses.nuget.org/Apache-2.0">Apache-2.0</a>""",
        [
            "<a ",
            'href="https://licenses.nuget.org/Apache-2.0"',
            ">",
            "Apache-2.0",
            "</a>",
        ],
    ),
    (
        "Copyright (c) 1992 Free Software Foundation <https://www.fsf.org/>",
        [
            "Copyright",
            " ",
            "(c)",
            " ",
            "1992",
            " ",
            "Free",
            " ",
            "Software",
            " ",
            "Foundation",
            " ",
            "<https://www.fsf.org/>",
        ],
    ),
    (
        "Copyright (c) 1992 Free Software Foundation <www.fsf.org/>",
        [
            "Copyright",
            " ",
            "(c)",
            " ",
            "1992",
            " ",
            "Free",
            " ",
            "Software",
            " ",
            "Foundation",
            " ",
            "<www.fsf.org/>",
        ],
    ),
    (
        '<a href="mailto:joen@foo.com"> bla dasdasd</a>',
        [
            "<a ",
            'href="',
            "mailto:",
            'joen@foo.com"',
            ">",
            " ",
            "bla",
            " ",
            "dasdasd",
            "</a>",
        ],
    ),
    (
        """<td width="30%">Copyright &copy; 2006 <a href="trolltech.html">Trolltech</a></td>""",
        [
            "<td ",
            'width="30%"',
            ">",
            "Copyright",
            " ",
            "&copy;",
            " ",
            "2006",
            " ",
            "<a ",
            'href="trolltech.html"',
            ">",
            "Trolltech",
            "</a>",
            "</td>",
        ],
    ),
    (
        "<p>SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1</p>",
        [
            "<p>",
            "SPDX-License-Identifier:",
            " ",
            "Apache-2.0",
            " ",
            "WITH",
            " ",
            "SHL-2.1",
            "</p>",
        ],
    ),
    (
        "Copyright (C) 2009 Eric Paris <Red Hat Inc>",
        [
            "Copyright",
            " ",
            "(C)",
            " ",
            "2009",
            " ",
            "Eric",
            " ",
            "Paris",
            " ",
            "<Red ",
            "Hat",
            " ",
            "Inc",
            ">",
        ],
    ),
    (
        "<s>Foo Bar</s>",
        [
            "<s>",
            "Foo",
            " ",
            "Bar",
            "</s>",
        ],
    ),
    (
        "(c) 2007-2008 Cyril Brulebois <kibi@debian.org> @end group @group",
        [
            "(c)",
            " ",
            "2007-2008",
            " ",
            "Cyril",
            " ",
            "Brulebois",
            " ",
            "<kibi@debian.org>",
            " ",
            "@end",
            " ",
            "group",
            " ",
            "@group",
        ],
    ),
    (
        '<span class="application">AMOR</span>, and ',
        ["<span ", 'class="application"', ">", "AMOR", "</span>", ",", " ", "and", " "],
    ),
    (
        "Parts Copyright (c) 1992 <s>Uri Blumentha<s>l, I</s>BM</s>",
        [
            "Parts",
            " ",
            "Copyright",
            " ",
            "(c)",
            " ",
            "1992",
            " ",
            "<s>",
            "Uri",
            " ",
            "Blumentha",
            "<s>",
            "l,",
            " ",
            "I",
            "</s>",
            "BM",
            "</s>",
        ],
    ),
]


@pytest.mark.parametrize(["test_text", "expected_splits"], split_tests)
def test_split_tags(test_text, expected_splits):
    assert [s for s in markup.split_on_tags(test_text) if s] == expected_splits


tag_keeper_tests = [
    (
        [
            "<a ",
            'href="https://licenses.nuget.org/Apache-2.0"',
            ">",
            "Apache-2.0",
            "</a>",
        ],
        ["Apache-2.0"],
    ),
    (
        [
            "Copyright",
            " ",
            "(c)",
            "1992",
            "Foundation",
            "<https://www.fsf.org/>",
            "<www.fsf.org/>",
        ],
        [
            "Copyright",
            " ",
            "(c)",
            "1992",
            "Foundation",
            "<https://www.fsf.org/>",
            "<www.fsf.org/>",
        ],
    ),
    (
        [
            "<a ",
            'href="',
            "mailto:",
            'joen@foo.com"',
            ">",
            "dasdasd",
            "</a>",
        ],
        ['joen@foo.com"', "dasdasd"],
    ),
    (
        [
            "<td ",
            'width="30%"',
            ">",
            "&copy;",
            "</a>",
            "</td>",
        ],
        ["&copy;"],
    ),
    (
        [
            "<p>",
            "SPDX-License-Identifier:",
            "</p>",
        ],
        ["<p>", "SPDX-License-Identifier:", "</p>"],
    ),
    (
        [
            "<Red ",
            "Hat",
            " ",
            "Inc",
            ">",
        ],
        ["<Red ", "Hat", " ", "Inc"],
    ),
    (
        [
            "<s>",
            "Bar",
            "</s>",
        ],
        ["Bar"],
    ),
    (
        [
            "<kibi@debian.org>",
            " ",
            "@end",
            " ",
            "group",
            " ",
            "@group",
        ],
        ["<kibi@debian.org>", " ", " ", "group", " "],
    ),
    (
        ["<span ", 'class="application"', ">", "AMOR", "</span>", ",", " ", "and", " "],
        ["AMOR", ",", " ", "and", " "],
    ),
]


@pytest.mark.parametrize(["test_tokens", "expected_tokens"], tag_keeper_tests)
def test_tag_keeper(test_tokens, expected_tokens):
    kept = [token for token in test_tokens if markup.keep_tag(token)]
    assert kept == expected_tokens
