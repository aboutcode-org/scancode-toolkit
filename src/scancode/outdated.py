#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0 AND MIT
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
# #
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

import datetime
import json
import logging
from os import path

from packvers import version as packaging_version
import requests
from requests.exceptions import ConnectionError

from scancode_config import scancode_cache_dir
from scancode_config import __version__ as scancode_version
from scancode_config import __release_date__ as scancode_release_date
from scancode import lockfile

"""
Utilities to check if the installed version of ScanCode is out of date.
The check is done either:
- locally based on elapsed time of 90 days
- remotely based on an API check for PyPI releases at the Python Software
  Foundation PyPI.org. At most once a week

This code is based on a pip module and heavilty modified for use here.
"""

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


class VersionCheckState:

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
        with lockfile.FileLock(self.lockfile_path).locked(timeout=10):
            state = {
                'last_check': current_time.strftime(SELFCHECK_DATE_FMT),
                'latest_version': latest_version,
            }
            with open(self.statefile_path, 'w') as statefile:
                json.dump(state, statefile, sort_keys=True,
                          separators=(',', ':'))


def build_outdated_message(installed_version, release_date, newer_version=''):
    """
    Return a message about outdated version for display.
    """
    rel_date, _, _ = release_date.isoformat().partition('T')

    newer_version = newer_version or ''
    newer_version = newer_version.strip()
    if newer_version:
        newer_version = f'{newer_version} '

    msg = (
        'WARNING: Outdated ScanCode Toolkit version! '
        f'You are using an outdated version of ScanCode Toolkit: {installed_version} '
        f'released on: {rel_date}. '
        f'A new version {newer_version}is available with important '
        f'improvements including bug and security fixes, updated license, '
        f'copyright and package detection, and improved scanning accuracy. '
        'Please download and install the latest version of ScanCode. '
        'Visit https://github.com/nexB/scancode-toolkit/releases for details.'
    )
    return msg


def check_scancode_version(
    installed_version=scancode_version,
    release_date=scancode_release_date,
    new_version_url='https://pypi.org/pypi/scancode-toolkit/json',
    force=False,
):
    """
    Check for an updated version of scancode-toolkit. Return a message to
    display if outdated or None. Limit the frequency of checks to once per week.
    State is stored in the scancode_cache_dir. If `force` is True, redo a PyPI
    remote check.
    """
    newer_version = fetch_newer_version(
        installed_version=installed_version,
        new_version_url=new_version_url,
        force=force,
    )
    if newer_version:
        return build_outdated_message(
                installed_version=installed_version,
                release_date=release_date,
                newer_version=newer_version,
            )


def fetch_newer_version(
    installed_version=scancode_version,
    new_version_url='https://pypi.org/pypi/scancode-toolkit/json',
    force=False,
):
    """
    Return a version string if there is an updated version of scancode-toolkit
    newer than the installed version and available on PyPI. Return None
    otherwise.
    Limit the frequency of update checks to once per week.
    State is stored in the scancode_cache_dir.
    If `force` is True, redo a PyPI remote check.
    """
    try:
        installed_version = packaging_version.parse(installed_version)
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
                latest_version = fetch_latest_version(new_version_url)
                state.save(latest_version, current_time)
            except Exception:
                # save an empty version to avoid checking more than once a week
                state.save(None, current_time)
                raise

        latest_version = packaging_version.parse(latest_version)

        # Determine if our latest_version is older
        if (installed_version < latest_version
        and installed_version.base_version != latest_version.base_version):
            return str(latest_version)

    except Exception:
        msg = 'There was an error while checking for the latest version of ScanCode'
        logger.debug(msg, exc_info=True)


def fetch_latest_version(new_version_url='https://pypi.org/pypi/scancode-toolkit/json'):
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
        logger.debug('fetch_latest_version: Download failed for %(url)r' % locals())
        raise

    status = response.status_code
    if status != 200:
        msg = 'fetch_latest_version: Download failed for %(url)r with %(status)r' % locals()
        logger.debug(msg)
        raise Exception(msg)

    # The check is done using python.org PyPI API
    payload = response.json()
    releases = [
        r for r in payload['releases'] if not packaging_version.parse(r).is_prerelease]
    releases = sorted(releases, key=packaging_version.parse)
    latest_version = releases[-1]

    return latest_version
