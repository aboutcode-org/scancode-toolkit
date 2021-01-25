# -*- coding: utf-8 -*-
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
