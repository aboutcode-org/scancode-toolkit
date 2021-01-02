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
import utils_requirements


@click.command()

@click.option('--dev-requirement',
    type=click.Path(path_type=str, dir_okay=False),
    metavar='FILE',
    default='requirements-dev.txt',
    show_default=True,
    help='Path to the dev requirements file to update or create.',
)
@click.option('--main-requirement',
    type=click.Path(path_type=str, dir_okay=False),
    default='requirements.txt',
    metavar='FILE',
    show_default=True,
    help='Path to the main requirements file. Its requirements will be excluded '
    'from the generated dev requirements.',
)

@click.help_option('-h', '--help')
def gen_dev_requirements(dev_requirement, main_requirement):
    """
    Create or replace the `--requirement` FILE requirements file with all
    locally installed Python packages. Exclude package names listed in the
    --exclude-requirement FILE.
    """
    utils_requirements.lock_dev_requirements(
        dev_requirements_file=dev_requirement,
        main_requirements_file=main_requirement,
    )


if __name__ == '__main__':
    gen_dev_requirements()
