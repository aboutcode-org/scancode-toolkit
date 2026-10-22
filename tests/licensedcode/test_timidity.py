# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

from scancode.api import get_licenses


TEST_DATA_DIR = Path(__file__).parent / "data" / "datadriven" / "lic1"
LICENSE_CHOICE = "gpl-1.0-plus OR lgpl-2.0-plus OR artistic-perl-1.0"


@pytest.mark.parametrize(
    "filename, expected_expression",
    [
        ("timidity-readme.txt", LICENSE_CHOICE),
        ("timidity-license-choice.txt", LICENSE_CHOICE),
        ("timidity-license-choice-short.txt", LICENSE_CHOICE),
        ("timidity-artistic-header.c", "artistic-perl-1.0"),
        ("timidity-copying.txt", "artistic-perl-1.0"),
        ("timidity-frontier-control.txt", "frontier-1.0"),
    ],
)
def test_timidity_api_reports_license_expression(filename, expected_expression):
    # An index match can become only a clue in the API when its coverage is low.
    # Assert on the public result, including for the shortened choice notice.
    result = get_licenses(str(TEST_DATA_DIR / filename))
    assert result["detected_license_expression"] == expected_expression
