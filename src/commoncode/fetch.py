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
from __future__ import print_function
from __future__ import unicode_literals

import logging

import requests
from requests.exceptions import ConnectionError
from requests.exceptions import InvalidSchema

from commoncode import fileutils
import os


logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


def download_url(url, file_name=None, verify=True, timeout=10):
    """
    Fetch `url` and return the temporary location where the fetched content was
    saved. Use `file_name` if provided or create a new `file_name` base on the last
    url segment. If `verify` is True, SSL certification is performed. Otherwise, no
    verification is done but a warning will be printed.
    `timeout` is the timeout in seconds.
    """
    requests_args = dict(timeout=timeout, verify=verify)
    file_name = file_name or fileutils.file_name(url)

    try:
        response = requests.get(url, **requests_args)
    except (ConnectionError, InvalidSchema) as e:
        logger.error('download_url: Download failed for %(url)r' % locals())
        raise

    status = response.status_code
    if status != 200:
        msg = 'download_url: Download failed for %(url)r with %(status)r' % locals()
        logger.error(msg)
        raise Exception(msg)

    tmp_dir = fileutils.get_temp_dir(base_dir='fetch')
    output_file = os.path.join(tmp_dir, file_name)
    with open(output_file, 'wb') as out:
        out.write(response.content)

    return output_file


def ping_url(url):
    """
    Returns True is `url` is reachable.
    """
    import urllib2

    # FIXME: if there is no 200 HTTP status, then the ULR may not be reachable.
    try:
        urllib2.urlopen(url)
    except Exception:
        return False
    else:
        return True
