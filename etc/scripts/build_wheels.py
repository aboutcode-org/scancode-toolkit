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

@click.option('-n', '--name',
    type=str,
    metavar='PACKAGE_NAME',
    required=True,
    help='Python package name to add or build.',
)
@click.option('-v', '--version',
    type=str,
    default=None,
    metavar='VERSION',
    help='Python package version to add or build.',
)
@click.option('-d', '--thirdparty-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    metavar='DIR',
    default=utils_thirdparty.THIRDPARTY_DIR,
    show_default=True,
    help='Path to the thirdparty directory where wheels are built.',
)
@click.option('-p', '--python-version',
    type=click.Choice(utils_thirdparty.PYTHON_VERSIONS),
    metavar='PYVER',
    default=utils_thirdparty.PYTHON_VERSIONS,
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
@click.option('--build-remotely',
    is_flag=True,
    help='Build missing wheels remotely.',
)
@click.option('--with-deps',
    is_flag=True,
    help='Also include all dependent wheels.',
)
@click.option('--verbose',
    is_flag=True,
    help='Provide verbose output.',
)
@click.help_option('-h', '--help')
def build_wheels(
    name,
    version,
    thirdparty_dir,
    python_version,
    operating_system,
    with_deps,
    build_remotely,
    verbose,
):
    """
    Build to THIRDPARTY_DIR all the wheels for the Python PACKAGE_NAME and
    optional VERSION. Build wheels compatible with all the `--python-version`
    PYVER(s) and `--operating_system` OS(s).

    Build native wheels remotely if needed when `--build-remotely` and include
    all dependencies with `--with-deps`.
    """
    utils_thirdparty.add_or_upgrade_built_wheels(
        name=name,
        version=version,
        python_versions=python_version,
        operating_systems=operating_system,
        dest_dir=thirdparty_dir,
        build_remotely=build_remotely,
        with_deps=with_deps,
        verbose=verbose,
    )


if __name__ == '__main__':
    build_wheels()
