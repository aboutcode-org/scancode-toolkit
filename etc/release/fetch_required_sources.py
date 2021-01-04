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

import utils_thirdparty


@click.command()

@click.option('--requirement-file',
    type=click.Path(exists=True, readable=True, path_type=str, dir_okay=False),
    metavar='FILE',
    multiple=True,
    default=['requirements.txt'],
    show_default=True,
    help='Path to the requirements file to use for thirdparty packages.',
)
@click.option('--thirdparty-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    metavar='DIR',
    default=utils_thirdparty.THIRDPARTY_DIR,
    show_default=True,
    help='Path to the thirdparty directory.',
)
@click.help_option('-h', '--help')
def fetch_required_sources(
    requirement_file,
    thirdparty_dir,
):
    """
    Fetch and save to THIRDPARTY_DIR all the source distributions for pinned
    dependencies found in the `--requirement-file` FILE requirements file(s). Use
    exclusively our remote repository.

    Also fetch the corresponding .ABOUT, .LICENSE and .NOTICE files and a
    virtualenv.pyz app.
    """
    requirement_files = requirement_file
    # this set the cache of our remote_repo to repo_url as a side effect
    _ = utils_thirdparty.get_remote_repo()
    for reqf in requirement_files:
        for package, error in utils_thirdparty.fetch_sources(
            requirement_file=reqf,
            dest_dir=thirdparty_dir,
        ):
            if error:
                print('Failed to fetch source:', package, ':', error)

    utils_thirdparty.fetch_venv_abouts_and_licenses()


if __name__ == '__main__':
    fetch_required_sources()
