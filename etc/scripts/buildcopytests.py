# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import io
from os import path
import sys

import click
click.disable_unicode_literals_warning = True

import scancode_config


# hack to be able to load testxx utilities. The test code is not in the path otherwise
cluecode_test_dir = path.join(scancode_config.scancode_root_dir, 'tests', 'cluecode')
sys.path.append(cluecode_test_dir)

import cluecode_test_utils  # NOQA


TRACE = True

def load_data(location='00-new-copyright-tests.txt'):
    with io.open(location, encoding='utf-8') as o:
        data = [l.strip() for l in o.read().splitlines(False)]
    lines = []
    for line in data:
        if not line:
            if lines:
                yield '\n'.join(lines)
                lines = []
        else:
            lines.append(line)
    if lines:
        yield '\n'.join(lines)


def find_test_file_loc(test_data_dir):
    """
    Return a new, unique and non-existing base name location suitable to create
    a new copyright test.
    """
    template = 'copyright_{}.txt'
    idx = 1
    while True:
        test_file_loc = path.join(test_data_dir, template.format(idx))
        if not path.exists(test_file_loc):
            return test_file_loc
        idx += 1


def build_dupe_index():
    """
    Return a set of existing generated copyright tests (to avoid duplication)
    """
    existing = set()
    for test in cluecode_test_utils.load_copyright_tests():
        try:
            with io.open(test.test_file) as tf:
                existing.add(tf.read().strip())
        except UnicodeDecodeError:
            with io.open(test.test_file, 'rb') as tf:
                existing.add(tf.read().strip())
    return existing


@click.command()
@click.argument('copyrights_file', type=click.Path(), metavar='FILE', )
@click.help_option('-h', '--help')
def cli(copyrights_file):
    """
    Create copyright and holder tests rules from a text file that has one line per test.
    The expected holder and copyright are from detection.
    For instance:
        Copyright (c) All the Raige Dog Salon
    """
    from cluecode.copyrights import detect_copyrights
    from cluecode_test_utils import CopyrightTest  # NOQA

    test_data_dir = path.join(cluecode_test_utils.test_env.test_data_dir, 'generated')

    existing = build_dupe_index()

    print()

    for text in load_data(copyrights_file):
        if text in existing:
            print('Copyright Test skipped, existing:', text)
            print()
            continue

        test_file_loc = find_test_file_loc(test_data_dir)
        with io.open(test_file_loc, 'w') as tf:
            tf.write(text)

        # collect expected values
        copyrights = []
        holders = []
        authors = []
        for dtype, value, _start, _end in detect_copyrights([text]):
            if dtype == 'copyrights':
                copyrights.append(value)
            elif dtype == 'holders':
                holders.append(value)
            elif dtype == 'authors':
                authors.append(value)

        test = CopyrightTest(
            what=['holders', 'copyrights', 'authors'],
            copyrights=copyrights,
            holders=holders,
            authors=authors,
        )
        test.test_file = test_file_loc
        test.data_file = test_file_loc + '.yml'
        test.dump()
        existing.add(text)
        print('Copyright Test added:', text)
        print()


if __name__ == '__main__':
    cli()
