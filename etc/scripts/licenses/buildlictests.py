# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
from os import path
import sys

import click
from itertools import chain

import scancode_config


# hack to be able to load testxx utilities. The test code is not in the path otherwise
licensedcode_test_dir = path.join(scancode_config.scancode_root_dir, 'tests', 'licensedcode')
sys.path.append(licensedcode_test_dir)

import licensedcode_test_utils  # NOQA
from licensedcode_test_utils import LicenseTest  # NOQA


test_data_dir = path.join(licensedcode_test_dir, 'data')
test_gen_data_dir = path.join(test_data_dir, 'generated')


TRACE = True

def load_data(location='00-new-license-tests.txt'):
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


def find_test_file_loc(test_gen_data_dir=test_gen_data_dir):
    """
    Return a new, unique and non-existing base name location suitable to create
    a new license test.
    """
    template = 'license_{}.txt'
    idx = 1
    while True:
        test_file_loc = path.join(test_gen_data_dir, template.format(idx))
        if not path.exists(test_file_loc):
            return test_file_loc
        idx += 1


def get_all_tests():
    load_from = licensedcode_test_utils.LicenseTest.load_from
    return chain(
        load_from(test_gen_data_dir),
        load_from(path.join(test_data_dir, 'licenses')),
        load_from(path.join(test_data_dir, 'retro_licenses/OS-Licenses-master')),
        load_from(path.join(test_data_dir, 'spdx/licenses')),
        load_from(path.join(test_data_dir, 'license_tools')),
        load_from(path.join(test_data_dir, 'slic-tests/identification')),
        load_from(path.join(test_data_dir, 'more_licenses/licenses')),
        load_from(path.join(test_data_dir, 'more_licenses/tests')),
        load_from(path.join(test_data_dir, 'debian/licensecheck')),
    )


def build_dupe_index():
    """
    Return a set of existing license tests texts (to avoid duplication)
    """
    existing = set()
    for test in get_all_tests():
        existing.add(test.get_content())
    return existing


def build_test(text):
    """
    Build and return a LicenseTest object given a test text.
    """
    from licensedcode import cache

    test_file = find_test_file_loc()
    with io.open(test_file, 'w', encoding='utf-8') as tf:
        tf.write(text)

    idx = cache.get_index()
    matches = idx.match(query_string=text) or []
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
@click.argument('licenses_file', type=click.Path(), metavar='FILE',)
@click.help_option('-h', '--help')
def cli(licenses_file):
    """
    Create license tests from a text file that tests separated by one empty line.
    The expected license is computed from license detection.
    """
    from licensedcode_test_utils import LicenseTest  # NOQA

    existing = build_dupe_index()

    print()

    for text in load_data(licenses_file):
        slim = text.encode('utf-8')
        if slim in existing:
            print('--> License Test skipped, existing:', text[:80], '...')
            print()
            continue
        else:
            existing.add(slim)

        lt = build_test(text)
        lt.dump()
        existing.add(text)
        print('--> License Test added:', text[:80], '...')
        print()


if __name__ == '__main__':
    cli()
