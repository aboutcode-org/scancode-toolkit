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

@click.option('--thirdparty-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    default=release_utils.THIRDPARTY_DIR,
    help='Path to the thirdparty directory to fix.',
)
@click.option('--python-version',
    type=click.Choice(release_utils.PYTHON_VERSIONS),
    default=['36'],
    multiple=True,
    show_default=True,
    help='Python version to use for this build. Repeat for multiple versions',
)
@click.option('--operating-system',
    type=click.Choice(release_utils.PLATFORMS_BY_OS),
    default=['linux'],
    multiple=True,
    show_default=True,
    help='OS to use for this build: one of linux, mac or windows. Repeat for multiple OSes',
)
@click.option('--repo-url',
    type=str,
    metavar='URL',
    default=release_utils.REMOTE_LINKS_URL,
    show_default=True,
    help='Remote repository URL to HTML page index listing repo files.',
)
@click.help_option('-h', '--help')
def fix_thirdparty_dir(
    thirdparty_dir,
    python_version,
    operating_system,
    repo_url,
):
    """
    Fix a thirdparty directory of dependent package wheels and sdist.

    Multiple fixes are applied:
    - fetch or build missing binary wheels
    - fetch missing source distributions
    - derive, fetch or add missing ABOUT files
    - fetch missing .LICENSE and .NOTICE files
    - remove outdated package versions and the ABOUT, .LICENSE and .NOTICE files

    Using the provided `--python-version` and `--operating_system` to add or
    build missing binary wheels for specific OS and Python version combos.
    """

    # these are really lists, so we rename these
    python_version = python_version 
    operating_systems = operating_system

    remote_repo = release_utils.get_remote_repo(repo_url)
    paths_or_urls = remote_repo.get_links()

    release_utils.add_missing_sources(dest_dir=thirdparty_dir)
    return
    
    list(release_utils.fetch_wheels(
#         environment=environment,
#         requirement=requirement,
        dest_dir=thirdparty_dir,
        paths_or_urls=paths_or_urls,
    ))

    release_utils.fetch_abouts(
        dest_dir=thirdparty_dir,
        paths_or_urls=paths_or_urls,
    )

    release_utils.fetch_license_texts_and_notices(
        dest_dir=thirdparty_dir,
        paths_or_urls=paths_or_urls,
    )


if __name__ == '__main__':
    fix_thirdparty_dir()
