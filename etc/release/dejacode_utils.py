#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

import os

import requests

"""
Utility to create and retrieve package and ABOUT file data from DejaCode.
"""

DEJACODE_API_URL_PACKAGES = 'https://enterprise.dejacode.com/api/v2/packages/'
DEJACODE_API_KEY = os.environ.get('DEJACODE_API_KEY')
DEJACODE_API_HEADERS = {
    'Authorization': 'Token {}'.format(DEJACODE_API_KEY),
    'Accept': 'application/json; indent=4',
}


def can_do_api_calls():
    if not DEJACODE_API_KEY:
        print('DejaCode DEJACODE_API_KEY not configured. Doing nothing')
        return False
    else:
        return True


def get_package_data(download_url):
    """
    Return a mapping of package data given a package `download_url`.
    """
    if not can_do_api_calls():
        return

    response = requests.get(
        DEJACODE_API_URL_PACKAGES,
        params=dict(download_url=download_url),
        headers=DEJACODE_API_HEADERS,
    )
    response_count = response.json()['count']

    if response_count == 1:
        package_data = response.json()['results'][0]
        return package_data

    elif response_count > 1:
        print(f'More than 1 entry exists, review at: {DEJACODE_API_URL_PACKAGES}')
    else:
        print('Could not find package:', download_url)


def fetch_about_text_for_package(download_url):
    """
    Fetch and return an .ABOUT YAML text given a package `download_url`.
    """
    if not can_do_api_calls():
        return

    package_data = get_package_data(download_url=download_url)
    if not package_data:
        raise Exception(f'No package found for: {download_url}')

    package_api_url = package_data['api_url']
    about_url = f'{package_api_url}about/'
    response = requests.get(about_url, headers=DEJACODE_API_HEADERS)

    # note that this is YAML-formatted
    return response.json()['about_data']


def new_package_from_existing_package(
    existing_download_url,
    new_download_url,
):
    """
    Create a new DejaCode Package from existing package data at
    `existing_download_url` using the `new_download_url`.

    Return the new package data.

    If the package already exists, return its package data. If
    `existing_download_url` does not exist, create package with minimal data.
    """
    if not can_do_api_calls():
        return

    new_package_data = get_package_data(download_url=new_download_url)
    if new_package_data:
        return new_package_data

    print(f'Creating new DejaCode package for: {new_download_url}')
    existing_package_data = get_package_data(download_url=existing_download_url)

    new_package_payload = {
        'download_url': new_download_url,
        # Trigger data collection, scan, and purl
        'collect_data': 1,
    }

    if existing_package_data:
        fields_to_carry_over = [
            'license_expression',
            'copyright',
            'description',
            'homepage_url',
            'primary_language',
            'author',
            'holder',
            'notice_text',
        ]

        for field in fields_to_carry_over:
            value = existing_package_data.get(field)
            if value:
                new_package_payload[field] = value

    response = requests.post(
        DEJACODE_API_URL_PACKAGES,
        data=new_package_payload,
        headers=DEJACODE_API_HEADERS,
    )
    new_package_data = response.json()
    if response.status_code != 201:
        raise Exception(f'Error, cannot create {new_download_url}: {new_package_data}')

    print(f'New Package created at: {new_package_data["absolute_url"]}')
    return new_package_data
