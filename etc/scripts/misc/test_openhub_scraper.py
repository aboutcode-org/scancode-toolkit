# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import openhub_scraper

def test_scraping_unicode_and_ascii():
    license_result = openhub_scraper.extract_openhub_licenses(
                                                            start_pg=15,
                                                            end_pg=15,
                                                            write_to_file=False,
                                                            parse_website=False)
    observed_result_1 = (item for item in
                         license_result if item['name'] ==
                         u'Культурный центр Союза Десантников России').next()
    expected_result_1 = {
        'openhub_url': u'https://www.openhub.net/licenses/sdrvdvkc',
        'name': u'Культурный центр Союза Десантников России'
    }
    assert observed_result_1 == expected_result_1

    observed_result_2 = (item for item in
                         license_result if item['name'] ==
                         'Sleepycat License').next()
    expected_result_2 = {
        'openhub_url': 'https://www.openhub.net/licenses/sleepycat',
        'name': 'Sleepycat License'
    }
    assert observed_result_2 == expected_result_2

    observed_result_3 = (item for item in
                         license_result if item['name'] ==
                         'Sun Public License v1.0').next()
    expected_result_3 = {
        'openhub_url': u'https://www.openhub.net/licenses/sun_public',
        'name': u'Sun Public License v1.0'
    }
    assert observed_result_3 == expected_result_3
