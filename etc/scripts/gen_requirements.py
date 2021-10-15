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
import utils_requirements


@click.command()

@click.option('-s', '--site-packages-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False, resolve_path=True),
    required=True,
    metavar='DIR',
    help='Path to the "site-packages" directory where wheels are installed such as lib/python3.6/site-packages',
)
@click.option('-r', '--requirements-file',
    type=click.Path(path_type=str, dir_okay=False),
    metavar='FILE',
    default='requirements.txt',
    show_default=True,
    help='Path to the requirements file to update or create.',
)
@click.help_option('-h', '--help')
def gen_requirements(site_packages_dir, requirements_file):
    """
    Create or replace the `--requirements-file` file FILE requirements file with all
    locally installed Python packages.all Python packages found installed in `--site-packages-dir`
    """
    utils_requirements.lock_requirements(
        requirements_file=requirements_file,
        site_packages_dir=site_packages_dir,
    )


if __name__ == '__main__':
    gen_requirements()
