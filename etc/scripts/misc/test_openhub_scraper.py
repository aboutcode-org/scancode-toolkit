# -*- coding: utf-8 -*-
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

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
