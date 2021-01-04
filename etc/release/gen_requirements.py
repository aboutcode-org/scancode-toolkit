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

@click.option('--requirement-file',
    type=click.Path(path_type=str, dir_okay=False),
    metavar='FILE',
    default='requirements.txt',
    show_default=True,
    help='Path to the requirements file to update or create.',
)
@click.option('--lib-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False, resolve_path=True),
    metavar='DIR',
    default='lib',
    show_default=True,
    help='Path to the "lib" directory where wheels are installed.',
)
@click.help_option('-h', '--help')
def gen_requirements(requirement_file, lib_dir):
    """
    Create or replace the `--requirement-file` file FILE requirements file with all
    locally installed Python packages.all Python packages found installed in `--lib-dir`
    """
    utils_requirements.lock_requirements(
        requirements_file=requirement_file,
        lib_dir=lib_dir,
    )


if __name__ == '__main__':
    gen_requirements()
