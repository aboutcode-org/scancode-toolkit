#!/usr/bin/python2
#
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

import io
import json
import os

try:
    from urlib.request import urlopen
except ImportError:
    from urllib2 import urlopen

from bs4 import BeautifulSoup


def write_license_info_to_file(license_list):
    """
    Neatly format all the scrapped license information in the json format and
    write it to a file.
    """
    with io.open('openhub_licenses.json', 'wb') as f:
        f.write(json.dumps(license_list, indent=4))


def parse_local_file():
    """
    Parses the given file using 'BeautifulSoup' and returns html content of
    that file.
    """
    local_test_file = os.path.join(os.path.dirname(__file__),
                                   'testdata/openhub_scraper/openhub_html.html')
    with open(local_test_file, 'r') as f:
        parsed_page = BeautifulSoup(f.read(), 'html.parser')
    return parsed_page


def parse_webpage(url, page_no):
    """
    Parses the given webpage using 'BeautifulSoup' and returns html content of
    that webpage.
    """
    page = urlopen(url + page_no)
    parsed_page = BeautifulSoup(page, 'html.parser')
    return parsed_page


def extract_openhub_licenses(start_pg, end_pg, write_to_file,
                             parse_website):
    """
    Extract openhub license names, their urls, and save it in a json file or
    return the list of the license dictionary.
    """
    license_dict = {}
    license_list = []

    for i in range(start_pg, end_pg + 1):
        if parse_website:
            parsed_page = parse_webpage(url='https://www.openhub.net/licenses?page=',
                                        page_no=str(i))
        else:
            parsed_page = parse_local_file()
        all_licenses = parsed_page.find(
            id='license').select('table.table-condensed.table-striped.table')
        license_rows = all_licenses[0].find_all('a', href=True)
        for license in license_rows:  # NOQA
            license_dict['openhub_url'] = license['href']
            license_dict['name'] = license.get_text()
            license_list.append(license_dict.copy())

    if write_to_file:
        write_license_info_to_file(license_list)
    else:
        return license_list


if __name__ == '__main__':
    extract_openhub_licenses(start_pg=1, end_pg=17, write_to_file=True,
                             parse_website=True)
