# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import openhub_scraper


def test_scraping_unicode_and_ascii():
    test_file = os.path.join(
        os.path.dirname(__file__), "testdata/openhub_html.html"
    )
    with open(test_file, "r") as f:
        test_content = f.read()

    licenses = list(openhub_scraper.list_licenses_on_page(test_content))

    result = [i for i in licenses if i["name"] == "Sleepycat License"]
    expected = [{
        "url": "https://www.openhub.net/licenses/sleepycat",
        "name": "Sleepycat License",
    }]
    assert result == expected

    result = [i for i in licenses if i["name"] == "Sun Public License v1.0"]
    expected = [{
        "url": "https://www.openhub.net/licenses/sun_public",
        "name": "Sun Public License v1.0",
    }]
    assert result == expected
