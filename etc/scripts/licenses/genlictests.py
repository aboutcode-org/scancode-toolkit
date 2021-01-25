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
from os import path
import sys

import click
click.disable_unicode_literals_warning = True
from commoncode import fileutils

import scancode_config
# hack to be able to load testxx utilities. The test code is not in the path otherwise
licensedcode_test_dir = path.join(scancode_config.scancode_root_dir, 'tests', 'licensedcode')
sys.path.append(licensedcode_test_dir)

import licensedcode_test_utils  # NOQA
from licensedcode_test_utils import LicenseTest  # NOQA

"""
Generate license tests for each file in a directory tree.
The generated expected licenses are based on the detection of the licenses
in the files.
"""


def build_test(test_file):
    """
    Build and return a LicenseTest object given a test text.
    """
    from licensedcode import cache

    idx = cache.get_index()
    matches = idx.match(location=test_file) or []
    detected_expressions = [match.rule.license_expression for match in matches]
    notes = ''
    if not detected_expressions:
        notes = 'No license should be detected'

    lt = LicenseTest(
        test_file=test_file,
        license_expressions=detected_expressions,
        notes=notes
    )

    lt.data_file = test_file + '.yml'
    return lt


@click.command()
@click.argument('test_directory', type=click.Path(), metavar='DIR',)
@click.help_option('-h', '--help')
def cli(test_directory):
    """
    Generate license tests YAML data files for each file in a directory tree.
    The expected license is computed from license detection.
    """
    from licensedcode_test_utils import LicenseTest  # NOQA

    print()
    for test_file in fileutils.resource_iter(test_directory, with_dirs=False):
        lt = build_test(test_file)
        lt.dump()
        print('--> License Test added:', lt)
        print()


if __name__ == '__main__':
    cli()
