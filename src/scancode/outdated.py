#
# Copyright (c) nexB Inc. and others. All rights reserved.
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
#
# This code was in part derived from the pip library:
# Copyright (c) 2008-2014 The pip developers (see outdated.NOTICE file)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from __future__ import absolute_import

from collections import OrderedDict
import datetime
import json
import logging
from os import path
import sys

from packaging import version as packaging_version
import requests
from requests.exceptions import ConnectionError
import yg.lockfile

from scancode_config import scancode_cache_dir
from scancode_config import __version__ as scancode_version


SELFCHECK_DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


logger = logging.getLogger(__name__)
# logging.basicConfig(stream=sys.stdout)
# logger.setLevel(logging.WARNING)


def total_seconds(td):
    if hasattr(td, 'total_seconds'):
        return td.total_seconds()
    else:
        val = td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6
        return val / 10 ** 6


class VersionCheckState(object):
    def __init__(self):
        self.statefile_path = path.join(
            scancode_cache_dir, 'scancode-version-check.json')
        self.lockfile_path = self.statefile_path + '.lockfile'
        # Load the existing state
        try:
            with open(self.statefile_path) as statefile:
                self.state = json.load(statefile)
        except (IOError, ValueError, KeyError):
            self.state = {}

    def save(self, latest_version, current_time):
        # Attempt to write out our version check file
        with yg.lockfile.FileLock(self.lockfile_path, timeout=10):
            state = {
                'last_check': current_time.strftime(SELFCHECK_DATE_FMT),
                'latest_version': latest_version,
            }
            with open(self.statefile_path, 'w') as statefile:
                json.dump(state, statefile, sort_keys=True,
                          separators=(',', ':'))


def check_scancode_version(installed_version=scancode_version,
                           new_version_url='https://pypi.org/pypi/scancode-toolkit/json',
                           force=False):
    """
    Check for an updated version of scancode-toolkit. Return a message to
    display if outdated or None. Limit the frequency of checks to once per week.
    State is stored in the scancode_cache_dir. If `force` is True, redo a PyPI
    remote check.
    """
    installed_version = packaging_version.parse(installed_version)
    latest_version = None
    msg = None

    try:
        state = VersionCheckState()

        current_time = datetime.datetime.utcnow()
        # Determine if we need to refresh the state
        if ('last_check' in state.state and 'latest_version' in state.state):
            last_check = datetime.datetime.strptime(
                state.state['last_check'],
                SELFCHECK_DATE_FMT
            )
            seconds_since_last_check = total_seconds(current_time - last_check)
            one_week = 7 * 24 * 60 * 60
            if seconds_since_last_check < one_week:
                latest_version = state.state['latest_version']

        if force:
            latest_version = None

        # Refresh the version if we need to or just see if we need to warn
        if latest_version is None:
            try:
                latest_version = get_latest_version(new_version_url)
                state.save(latest_version, current_time)
            except Exception:
                # save an empty version to avoid checking more than once a week
                state.save(None, current_time)
                raise

        latest_version = packaging_version.parse(latest_version)

        outdated_msg = ('WARNING: '
            'You are using ScanCode Toolkit version %s, however the newer '
            'version %s is available.\nYou should download and install the '
            'latest version of ScanCode with bug and security fixes and the '
            'latest license detection data for accurate scanning.\n'
            'Visit https://github.com/nexB/scancode-toolkit/releases for details.'
            % (installed_version, latest_version)
        )

        # Our git version string is not PEP 440 compliant, and thus improperly parsed via
        # most 3rd party version parsers. We handle this case by pulling out the "base"
        # release version by split()-ting on "post".
        # 
        # For example, "3.1.2.post351.850399ba3" becomes "3.1.2"
        if isinstance(installed_version, packaging_version.LegacyVersion):
            installed_version = installed_version.split('post')
            installed_version = installed_version[0]
            installed_version = packaging_version.parse(installed_version)

        # Determine if our latest_version is older
        if (installed_version < latest_version
        and installed_version.base_version != latest_version.base_version):
            return outdated_msg

    except Exception:
        msg = 'There was an error while checking for the latest version of ScanCode'
        logger.debug(msg, exc_info=True)


def get_latest_version(new_version_url='https://pypi.org/pypi/scancode-toolkit/json'):
    """
    Fetch `new_version_url` and return the latest version of scancode as a
    string.
    """
    requests_args = dict(
        timeout=10,
        verify=True,
        headers={'Accept': 'application/json'},
    )
    try:
        response = requests.get(new_version_url, **requests_args)
    except (ConnectionError) as e:
        logger.debug('get_latest_version: Download failed for %(url)r' % locals())
        raise

    status = response.status_code
    if status != 200:
        msg = 'get_latest_version: Download failed for %(url)r with %(status)r' % locals()
        logger.debug(msg)
        raise Exception(msg)

    # The check is done using python.org PyPI API
    payload = response.json(object_pairs_hook=OrderedDict)
    releases = [
        r for r in payload['releases'] if not packaging_version.parse(r).is_prerelease]
    releases = sorted(releases, key=packaging_version.parse)
    latest_version = releases[-1]

    return latest_version
