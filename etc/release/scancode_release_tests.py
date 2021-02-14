#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import hashlib
import os
import shutil
import subprocess
import sys

# TODO: also test a pip install with a find-links option to our new PyPI repo


def run_pypi_smoke_tests(pypi_archive):
    """
    Run basic install and "smoke" scancode tests for a PyPI archive.
    """
    # archive is either a wheel or an sdist as in
    # scancode_toolkit-21.1.21-py3-none-any.whl or scancode-toolkit-21.1.21.tar.gz
    run_command(['pip', 'install', pypi_archive + '[full]'])

    with open('some.file', 'w') as sf:
        sf.write('license: gpl-2.0')

    run_command(['scancode', '-clipeu', '--json-pp', '-', 'some.file'])


def run_app_smoke_tests(app_archive):
    """
    Run basic "smoke" scancode tests for the app release archive `app_archive`
    """
    # Extract app archive which has this namin pattern:
    # scancode-toolki-21.1.21_py36-linux.tar.xz
    # or scancode-toolkit-21.1.21_py36-windows.zip
    # We split the name on "_" to extract the laft hand side which is name of
    # the root directory inside the archive e.g. "scancode-toolkit-21.1.21"
    # where the archive gest extracted
    extract_dir, _, _py_ver_ext = app_archive.partition('_')
    shutil.unpack_archive(app_archive)
    print()
    print('cwd:', os.getcwd())

    extract_loc = os.path.normpath(os.path.abspath(os.path.expanduser(extract_dir)))
    print('extract_loc:', extract_loc)
    for f in os.listdir(extract_loc):
        print('  ', f)
    print()

    os.chdir(extract_loc)

    # minimal tests: update when new scans are available
    args = [
        os.path.join(extract_loc, 'scancode'),
        '-clipeu',
        '--classify',
        '--verbose',
        '--json', 'test_scan.json',
        '--csv', 'test_scan.csv',
        '--html', 'test_scan.html',
        '--spdx-tv', 'test_scan.spdx',
        '--json-pp', '-',
        os.path.join(extract_loc, 'apache-2.0.LICENSE'),
    ]

    print(f'Testing scancode release: {app_archive}')
    run_command(args)


def run_command(args):
    """
    Run a command list of `args` in a subprocess. Print the output. Exit on
    error.
    """
    cmd = ' '.join(args)
    print()
    print(f'Running command: {cmd}')
    try:
        on_windows = 'win32' in str(sys.platform).lower()
        output = subprocess.check_output(args, encoding='utf-8', shell=on_windows)
        print(f'Success to run command: {cmd}')
        print(output)

    except subprocess.CalledProcessError as cpe:
        print(f'Failure to run command: {cmd}')
        print(cpe.output)
        sys.exit(128)


if __name__ == '__main__':
    args = sys.argv[1:]
    action, archive, sha_arch, sha_py = args

    with open(archive, 'rb') as arch:
        current_sha_arch = hashlib.sha256(arch.read()).hexdigest()
        assert current_sha_arch == sha_arch

    with open(__file__, 'rb') as py:
        current_sha_py = hashlib.sha256(py.read()).hexdigest()
        assert current_sha_py == sha_py

    if action == 'pypi':
        run_pypi_smoke_tests(archive)
    else:
        # action =='app':
        run_app_smoke_tests(archive)
