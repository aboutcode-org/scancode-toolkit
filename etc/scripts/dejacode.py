# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import requests


"""
Script to fetch DejaCode license data and sync with ScanCode as needed.
"""


def license_keys(api_url, api_key):
    """
    Return license keys from a DejaCode instance using API calls.
    """
    headers = {'Authorization': api_key}
    keys = []
    while api_url:
        response = requests.get(api_url, headers=headers).json()
        keys.extend([result.get('key') for result in response['results']])
        # get next API page
        api_url = response.get('next')
    return keys


if __name__ == '__main__':
    import os, sys
    api_url = os.environ.get('DEJACODE_API_URL', None)
    api_key = os.environ.get('DEJACODE_API_KEY', None)
    if not api_url or api_url:
        print('You must set the DEJACODE_API_URL and DEJACODE_API_URL '
              'environment variables before running this script.')
        sys.exit(0)
    print(license_keys(api_url, api_key))
