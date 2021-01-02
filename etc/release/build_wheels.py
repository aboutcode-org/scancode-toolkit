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

@click.option('--requirement',
    type=str,
    metavar='SPECIFIER',
    help='Pip package requirement specifier to add or build.',
)
@click.option('--thirdparty-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    metavar='DIR',
    default=utils_thirdparty.THIRDPARTY_DIR,
    show_default=True,
    help='Path to the thirdparty directory where wheels are built.',
)
@click.option('-p', '--python-dot-version',
    type=click.Choice(utils_thirdparty.PYTHON_DOT_VERSIONS),
    metavar='PYVER',
    default=utils_thirdparty.PYTHON_DOT_VERSIONS,
    show_default=True,
    multiple=True,
    help='Python version to use for this build.',
)
@click.option('-o', '--operating-system',
    type=click.Choice(utils_thirdparty.PLATFORMS_BY_OS),
    metavar='OS',
    default=tuple(utils_thirdparty.PLATFORMS_BY_OS),
    multiple=True,
    show_default=True,
    help='OS to use for this build: one of linux, mac or windows.',
)
@click.option('--with-deps',
    is_flag=True,
    help='Also include all dependent wheels.',
)
@click.option('--build-remotely',
    is_flag=True,
    help='Build missing wheels remotely.',
)
@click.help_option('-h', '--help')
def build_wheels(
    requirement,
    thirdparty_dir,
    python_dot_version,
    operating_system,
    with_deps,
    build_remotely,
):
    """
    Build to THIRDPARTY_DIR all the wheels for the pip `--requirement`
    requirements SPECIFIER. Build wheels compatible with all the provided
    `--python-dot-version` and `--operating_system`.
    """
    utils_thirdparty.build_wheels(
        requirements_specifier=requirement,
        python_dot_versions=python_dot_version,
        operating_systems=operating_system,
        dest_dir=thirdparty_dir,
        build_remotely=build_remotely,
        with_deps=with_deps,
        verbose=False,
    )


if __name__ == '__main__':
    build_wheels()
