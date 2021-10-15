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
import itertools

import click

import utils_thirdparty


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
@click.option('-s', '--with-sources',
    is_flag=True,
    help='Fetch the corresponding source distributions.',
)
@click.option('-a', '--with-about',
    is_flag=True,
    help='Fetch the corresponding ABOUT and LICENSE files.',
)
@click.option('--allow-unpinned',
    is_flag=True,
    help='Allow requirements without pinned versions.',
)
@click.option('-s', '--only-sources',
    is_flag=True,
    help='Fetch only the corresponding source distributions.',
)
@click.option('-u', '--remote-links-url',
    type=str,
    metavar='URL',
    default=utils_thirdparty.REMOTE_LINKS_URL,
    show_default=True,
    help='URL to a PyPI-like links web site. '
         'Or local path to a directory with wheels.',
)

@click.help_option('-h', '--help')
def fetch_requirements(
    requirements_file,
    thirdparty_dir,
    python_version,
    operating_system,
    with_sources,
    with_about,
    allow_unpinned,
    only_sources,
    remote_links_url=utils_thirdparty.REMOTE_LINKS_URL,
):
    """
    Fetch and save to THIRDPARTY_DIR all the required wheels for pinned
    dependencies found in the `--requirement` FILE requirements file(s). Only
    fetch wheels compatible with the provided `--python-version` and
    `--operating-system`.
    Also fetch the corresponding .ABOUT, .LICENSE and .NOTICE files together
    with a virtualenv.pyz app.

    Use exclusively wheel not from PyPI but rather found in the PyPI-like link
    repo ``remote_links_url`` if this is a URL. Treat this ``remote_links_url``
    as a local directory path to a wheels directory if this is not a a URL.
    """

    # fetch wheels
    python_versions = python_version
    operating_systems = operating_system
    requirements_files = requirements_file

    if not only_sources:
        envs = itertools.product(python_versions, operating_systems)
        envs = (utils_thirdparty.Environment.from_pyver_and_os(pyv, os) for pyv, os in envs)

        for env, reqf in itertools.product(envs, requirements_files):

            for package, error in utils_thirdparty.fetch_wheels(
                environment=env,
                requirements_file=reqf,
                allow_unpinned=allow_unpinned,
                dest_dir=thirdparty_dir,
                remote_links_url=remote_links_url,
            ):
                if error:
                    print('Failed to fetch wheel:', package, ':', error)

    # optionally fetch sources
    if with_sources or only_sources:

        for reqf in requirements_files:
            for package, error in utils_thirdparty.fetch_sources(
                requirements_file=reqf,
                allow_unpinned=allow_unpinned,
                dest_dir=thirdparty_dir,
                remote_links_url=remote_links_url,
            ):
                if error:
                    print('Failed to fetch source:', package, ':', error)

    if with_about:
        utils_thirdparty.add_fetch_or_update_about_and_license_files(dest_dir=thirdparty_dir)
        utils_thirdparty.find_problems(
            dest_dir=thirdparty_dir,
            report_missing_sources=with_sources or only_sources,
            report_missing_wheels=not only_sources,
        )


if __name__ == '__main__':
    fetch_requirements()
