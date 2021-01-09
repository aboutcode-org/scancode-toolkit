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
import itertools


@click.command()

@click.option('-r', '--requirements-file',
    type=click.Path(exists=True, readable=True, path_type=str, dir_okay=False),
    metavar='FILE',
    multiple=True,
    default=['requirements.txt'],
    show_default=True,
    help='Path to the requirements file to use for thirdparty packages.',
)
@click.option('-d', '--thirdparty-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    metavar='DIR',
    default=utils_thirdparty.THIRDPARTY_DIR,
    show_default=True,
    help='Path to the thirdparty directory.',
)
@click.option('-p', '--python-version',
    type=click.Choice(utils_thirdparty.PYTHON_VERSIONS),
    metavar='INT',
    multiple=True,
    default=['36'],
    show_default=True,
    help='Python version to use for this build.',
)
@click.option('-o', '--operating-system',
    type=click.Choice(utils_thirdparty.PLATFORMS_BY_OS),
    metavar='OS',
    multiple=True,
    default=['linux'],
    show_default=True,
    help='OS to use for this build: one of linux, mac or windows.',
)
@click.help_option('-h', '--help')
def fetch_required_wheels(
    requirements_file,
    thirdparty_dir,
    python_version,
    operating_system,
):
    """
    Fetch and save to THIRDPARTY_DIR all the wheels for pinned dependencies
    found in the `--requirement` FILE requirements file(s). Only fetch wheels
    compatible with the provided `--python-version` and `--operating-system`.

    Use exclusively our remote repository.

    Also fetch the corresponding .ABOUT, .LICENSE and .NOTICE files together
    with a virtualenv.pyz app.
    """

    python_versions = python_version
    operating_systems = operating_system
    requirements_files = requirements_file

    envs = itertools.product(python_versions, operating_systems)
    envs = (utils_thirdparty.Environment.from_pyver_and_os(pyv, os) for pyv, os in envs)

    for env, reqf in itertools.product(envs, requirements_files):
        for package, error in utils_thirdparty.fetch_wheels(
            environment=env,
            requirements_file=reqf,
            dest_dir=thirdparty_dir,
        ):
            if error:
                print('Failed to fetch wheel:', package, ':', error)

    utils_thirdparty.fetch_and_save_about_data(dest_dir=thirdparty_dir)
    utils_thirdparty.add_referenced_licenses_and_notices(dest_dir=thirdparty_dir)


if __name__ == '__main__':
    fetch_required_wheels()
