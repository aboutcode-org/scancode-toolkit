#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import re
import warnings
from shutil import which

from commoncode.command import execute
from commoncode.command import find_in_path
from commoncode.system import on_linux
from commoncode.version import VERSION_PATTERNS_REGEX
from packagedcode import models

MSIINFO_BIN_LOCATION = 'packagedcode_msitools.msiinfo'


def get_msiinfo_bin_location(_cache=[]):
    """
    Return the binary location for msiinfo from either:
    - a plugin-provided path,
    - the system PATH.
    Raise an Exception if no msiinfo command can be found.
    """
    if _cache:
        return _cache[0]

    from plugincode.location_provider import get_location

    # try a plugin-provided path first
    cmd_loc = get_location(MSIINFO_BIN_LOCATION)

    # try the PATH
    if not cmd_loc:
        cmd = 'msiinfo'
        cmd_loc = find_in_path(cmd)

        if not cmd_loc:
            cmd_loc = which(cmd)

        if cmd_loc:
            warnings.warn(
                'Using "msiinfo" command found in the PATH. '
                'Install instead a plugincode-msitools plugin for best support.'
            )

    if not cmd_loc or not os.path.isfile(cmd_loc):
        raise Exception(
            'CRITICAL: msiinfo not provided. '
            'Unable to continue: you need to install the plugin packagedcode-msitools'
        )
    _cache.append(cmd_loc)
    return cmd_loc


class MsiinfoException(Exception):
    pass


def parse_msiinfo_suminfo_output(output_string):
    """
    Return a dictionary containing information from the output of `msiinfo suminfo`
    """
    # Split lines by newline and place lines into a list
    output_list = output_string.splitlines()
    results = {}
    # Partition lines by the leftmost ":", use the string to the left of ":" as
    # the key and use the string to the right of ":" as the value
    for output in output_list:
        key, _, value = output.partition(':')
        if key:
            results[key] = value.strip()
    return results


def get_msi_info(location):
    """
    Run the command `msiinfo suminfo` on the file at `location` and return the
    results in a dictionary

    This function requires `msiinfo` to be installed on the system, either by
    installing the `packagedcode-msiinfo` plugin or by installing `msitools`
    through a package manager.
    """
    # FIXME: what about the return code? we ignore it?
    rc, stdout, stderr = execute(
        cmd_loc=get_msiinfo_bin_location(),
        args=[
            'suminfo',
            location,
        ],
    )
    if stderr or rc:
        error_message = f'Error encountered when reading MSI information from {location}: {stderr}'
        raise MsiinfoException(error_message)
    return parse_msiinfo_suminfo_output(stdout)


def get_version_from_subject_line(subject_line):
    """
    Return a version number from `subject_line`

    `subject_line` is the `Subject` field from the output of
    `msiinfo suminfo <msi installer file>`. This string sometimes contains
    the version number of the package contained in the MSI installer.
    """
    for pattern in VERSION_PATTERNS_REGEX():
        version = re.search(pattern, subject_line)
        if version:
            v = version.group(0)
            # prefix with v space
            if not v.lower().startswith('v'):
                v = f'v {v}'
            return v


def create_package_data_from_msiinfo_results(
    msiinfo_results,
    datasource_id='msi_installer',
    package_type='msi',
    purl_only=False,
):
    """
    Return PackageData from a mapping of `msiinfo_results`
    """
    subject = msiinfo_results.pop('Subject', '')
    name = subject
    version = get_version_from_subject_line(subject)
    pkg = models.PackageData(
        datasource_id=datasource_id,
        type=package_type,
        name=name,
        version=version,
    )
    if purl_only:
        return pkg

    author_name = msiinfo_results.pop('Author', '')
    parties = []
    if author_name:
        parties.append(
            models.Party(
                type=None,
                role='author',
                name=author_name
            )
        )

    # Currently, we use the contents `Subject` field from the msiinfo suminfo
    # results as the package name because it contains the package name most of
    # the time. Getting the version out of the `Subject` string is not
    # straightforward because the format of the string is usually different
    # between different MSIs

    pkg.description = msiinfo_results.pop('Comments', '')
    pkg.parties = parties
    pkg.keywords = msiinfo_results.pop('Keywords', [])
    pkg.extra_data = msiinfo_results
    return pkg


def msi_parse(location,
    datasource_id='msi_installer',
    package_type='msi',
    purl_only=False,
):
    """
    Return PackageData from ``location``
    """
    if on_linux:
        info = get_msi_info(location)
        return create_package_data_from_msiinfo_results(
            msiinfo_results=info,
            datasource_id=datasource_id,
            package_type=package_type,
            purl_only=purl_only,
        )
    else:
        return models.PackageData(
            datasource_id=datasource_id,
            type=package_type,
        )


class MsiInstallerHandler(models.DatafileHandler):
    datasource_id = 'msi_installer'
    filetypes = ('msi installer',)
    path_patterns = ('*.msi',)
    default_package_type = 'msi'
    description = 'Microsoft MSI installer'
    documentation_url = 'https://docs.microsoft.com/en-us/windows/win32/msi/windows-installer-portal'

    @classmethod
    def parse(cls, location, purl_only=False):
        yield msi_parse(location=location, purl_only=purl_only)
