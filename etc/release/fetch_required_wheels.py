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

import click

import release_utils


@click.command()

@click.option('--requirement',
    type=click.Path(exists=True, readable=True, path_type=str, dir_okay=False),
    metavar='FILE',
    default='requirements.txt',
    show_default=True,
    help='Path to the requirements file to use for thirdparty packages.',
)
@click.option('--thirdparty-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    metavar='DIR',
    default=release_utils.THIRDPARTY_DIR,
    show_default=True,
    help='Path to the thirdparty directory.',
)
@click.option('--python-version',
    type=click.Choice(release_utils.PYTHON_VERSIONS),
    metavar='INT',
    default='36',
    show_default=True,
    help='Python version to use for this build.',
)
@click.option('--operating-system',
    type=click.Choice(release_utils.PLATFORMS_BY_OS),
    metavar='OS',
    default='linux',
    show_default=True,
    help='OS to use for this build: one of linux, mac or windows.',
)
@click.option('--repo-url',
    type=str,
    metavar='URL',
    default=release_utils.REMOTE_LINKS_URL,
    show_default=True,
    help='Remote repository URL to HTML page index listing repo files.',
)
@click.help_option('-h', '--help')
def fetch_required_wheels(
    requirement,
    thirdparty_dir,
    python_version,
    operating_system,
    repo_url,
):
    """
    Fetch and save to THIRDPARTY_DIR all the wheels for pinned dependencies
    found in the `--requirement` FILE requirements file. Only fetch wheels
    compatible with the provided `--python- version` and `--operating_system`.

    Use exclusively our remote repository.

    Also fetch the corresponding .ABOUT, .LICENSE nad .NOTICE files and a
    virtualenv.pyz app.
    """
    # this set the cache of our remote_repo to repo_url as a side effect
    _ = release_utils.get_remote_repo(repo_url)

    environment = release_utils.Environment.from_pyos(
        python_version, operating_system)

    for package, error in release_utils.fetch_wheels(
        environment=environment,
        requirement=requirement,
        dest_dir=thirdparty_dir,
    ):
        if error:
            print('Failed to fetch wheel:', package, ':', error)

    release_utils.fetch_venv_abouts_and_licenses()


if __name__ == '__main__':
    fetch_required_wheels()
