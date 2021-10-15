#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import click

import utils_thirdparty


@click.command()

@click.option('-d', '--thirdparty-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    required=True,
    help='Path to the thirdparty directory to fix.',
)
@click.option('--build-wheels',
    is_flag=True,
    help='Build all missing wheels .',
)
@click.option('--build-remotely',
    is_flag=True,
    help='Build missing wheels remotely.',
)
@click.help_option('-h', '--help')
def fix_thirdparty_dir(
    thirdparty_dir,
    build_wheels,
    build_remotely,
):
    """
    Fix a thirdparty directory of dependent package wheels and sdist.

    Multiple fixes are applied:
    - fetch or build missing binary wheels
    - fetch missing source distributions
    - derive, fetch or add missing ABOUT files
    - fetch missing .LICENSE and .NOTICE files
    - remove outdated package versions and the ABOUT, .LICENSE and .NOTICE files

    Optionally build missing binary wheels for all supported OS and Python
    version combos locally or remotely.
    """
    print('***FETCH*** MISSING WHEELS')
    package_envts_not_fetched = utils_thirdparty.fetch_missing_wheels(dest_dir=thirdparty_dir)
    print('***FETCH*** MISSING SOURCES')
    src_name_ver_not_fetched = utils_thirdparty.fetch_missing_sources(dest_dir=thirdparty_dir)

    package_envts_not_built = []
    if build_wheels:
        print('***BUILD*** MISSING WHEELS')
        package_envts_not_built, _wheel_filenames_built = utils_thirdparty.build_missing_wheels(
            packages_and_envts=package_envts_not_fetched,
            build_remotely=build_remotely,
            dest_dir=thirdparty_dir,
        )

    print('***ADD*** ABOUT AND LICENSES')
    utils_thirdparty.add_fetch_or_update_about_and_license_files(dest_dir=thirdparty_dir)

    # report issues
    for name, version in src_name_ver_not_fetched:
        print(f'{name}=={version}: Failed to fetch source distribution.')

    for package, envt in package_envts_not_built:
        print(
            f'{package.name}=={package.version}: Failed to build wheel '
            f'on {envt.operating_system} for Python {envt.python_version}')

    print('***FIND PROBLEMS***')
    utils_thirdparty.find_problems(dest_dir=thirdparty_dir)


if __name__ == '__main__':
    fix_thirdparty_dir()
