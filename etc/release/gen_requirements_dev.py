#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
@click.option('-d', '--dev-requirements-file',
    type=click.Path(path_type=str, dir_okay=False),
    metavar='FILE',
    default='requirements-dev.txt',
    show_default=True,
    help='Path to the dev requirements file to update or create.',
)
@click.option('-r', '--main-requirements-file',
    type=click.Path(path_type=str, dir_okay=False),
    default='requirements.txt',
    metavar='FILE',
    show_default=True,
    help='Path to the main requirements file. Its requirements will be excluded '
    'from the generated dev requirements.',
)
@click.help_option('-h', '--help')
def gen_dev_requirements(site_packages_dir, dev_requirements_file, main_requirements_file):
    """
    Create or overwrite the `--dev-requirements-file` pip requirements FILE with
    all Python packages found installed in `--site-packages-dir`. Exclude
    package names also listed in the --main-requirements-file pip requirements
    FILE (that are assume to the production requirements and therefore to always
    be present in addition to the development requirements).
    """
    utils_requirements.lock_dev_requirements(
        dev_requirements_file=dev_requirements_file,
        main_requirements_file=main_requirements_file,
        site_packages_dir=site_packages_dir
    )


if __name__ == '__main__':
    gen_dev_requirements()
