#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
#  Copyright (c) nexB Inc. and others http://www.nexb.com/. All rights reserved.
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
from os import path
from subprocess import check_output
from subprocess import STDOUT
import sys

import pytest


TRACE = True

"""
A pytest conftest.py for scancode-toolkit to control which tests to run and when.

We use custom markers and command line options to determine which test suite to run.

To retest only code impacted by a change, it tries to find which code modules
have changed using git, and selectively runs only the tests for the impacted
modules when running in a feature branch. When running on the develop or master
branches all the tests run: none are skipped.
"""



################################################################################
# pytest custom markers and CLI options
################################################################################
SLOW_TEST = 'scanslow'
VALIDATION_TEST = 'scanvalidate'


def pytest_configure(config):
    config.addinivalue_line('markers', SLOW_TEST + ': Mark a ScanCode test as a slow, long running test.')
    config.addinivalue_line('markers', VALIDATION_TEST + ': Mark a ScanCode test as a validation test, super slow, long running test.')


TEST_SUITES = 'standard', 'all', 'validate'


def pytest_addoption(parser):
    """
    Add options used for ScanCode tests customization.
    """
    group = parser.getgroup('scancode', 'Test suite options for ScanCode')

    group.addoption(
        '--force-py3',
        dest='force_py3',
        action='store_true',
        default=False,
        help='[DEPRECATED and ignored] Python 3 port is completed.',
    )

    group.addoption(
        '--test-suite',
        action='store',
        choices=TEST_SUITES,
        dest='test_suite',
        default='standard',
        help='Select which test suite to run: '
             '"standard" runs the standard test suite designed to run reasonably fast. '
             '"all" runs "standard" and "slow" (long running) tests. '
             '"validate" runs all the tests. '
             'Use the @pytest.mark.scanslow marker to mark a test as "slow" test. '
             'Use the @pytest.mark.scanvalidate marker to mark a test as a "validate" test.'
        )

    group.addoption(
        '--changed-only',
        dest='changed_only',
        action='store_true',
        default=False,
        help='Run only the subset of tests impacted by your changes.'
             'If selected, you can provide an optional --base-branch  and the '
             'changes are checked against that branch. '
             'Otherwise, a git diff is made against the current branch.',
    )

    group.addoption(
        '--base-branch',
        dest='base_branch',
        action='store',
        default=None,
        help='Optional name branch  of the branch diff against to find what has '
             'changed if --changed-only is selected.',
    )

    group.addoption(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        default=False,
        help='Only print selected and deselected tests. Do not run anything.',
    )

################################################################################
# Filter whcih tests  to collect based on our CLI options and our custom markers
################################################################################

@pytest.mark.trylast
def pytest_collection_modifyitems(config, items):
    test_suite = config.getvalue('test_suite')
    changed_only = config.getoption('changed_only')
    base_branch = config.getoption('base_branch')
    dry_run = config.getoption('dry_run')

    run_everything = test_suite == 'validate'
    run_slow_test = test_suite in ('all', 'validate')

    tests_to_run = []
    tests_to_skip = []

    if changed_only:
        base_branch = base_branch or get_git_branch()
        impacted_modules = get_impacted_modules(base_branch) or set()
        all_is_changed = not(impacted_modules)
        impacted_modules_paths = ['/{}/'.format(m) for m in impacted_modules]
        print()
        if not impacted_modules:
            print('All modules impacted')
        else:
            print('Run tests only in these changed modules:', ', '.join(sorted(impacted_modules)))

    for item in items:
        is_validate = bool(item.get_closest_marker(VALIDATION_TEST))
        is_slow = bool(item.get_closest_marker(SLOW_TEST))

        if is_validate and not run_everything:
            tests_to_skip.append(item)
            continue

        if is_slow and not run_slow_test:
            tests_to_skip.append(item)
            continue

        if changed_only and not all_is_changed:
            if not is_changed(item.fspath, impacted_modules_paths):
                tests_to_skip.append(item)
                continue

        tests_to_run.append(item)

    print()
    print('{} tests selected, {} tests skipped.'.format(len(tests_to_run), len(tests_to_skip)))

    if dry_run:
        if config.getvalue('verbose'):
            print()
            print('The following tests will run: ')
            for test in tests_to_run:
                print(test.nodeid)

            print('The following tests are skipped: ')
            for test in tests_to_skip:
                print(test.nodeid)

        tests = items[:]
        items[:] = []
        config.hook.pytest_deselected(items=tests)
        return


    items[:] = tests_to_run
    config.hook.pytest_deselected(items=tests_to_skip)


################################################################################
# Retest only tests for changed modules
################################################################################


def is_changed(path_string, impacted_module_paths, _cache={}):
    """
    Return True if a `path_string` is for a path that has changed.
    """
    path_string = str(path_string).replace('\\', '/')
    cached = _cache.get(path_string)
    if cached is not None:
        return cached

    if path_string.endswith(('setup.py', 'conftest.py')):
        return False
    changed = any(p in path_string for p in impacted_module_paths)
    if TRACE and changed:
        print('is_changed:', path_string, changed)
    _cache[path_string] = changed
    return changed


def get_all_modules():
    """
    Return a set of top level modules.
    """
    all_modules = set([p for p in os.listdir('src') if p.endswith('code')])
    if TRACE:
        print()
        print('get_all_modules:', all_modules)
    return all_modules


def get_impacted_modules(base_branch=None):
    """
    Return a set of impacted top level modules under tests or src.
    Return None if all modules are impacted and should be re-tested.
    """
    try:
        base_branch = base_branch or get_git_branch()
        changed_files = get_changed_files(base_branch)
        locally_changed_files = get_changed_files(None)
        changed_files.extend(locally_changed_files)
    except Exception as e:
        # we test it all if we cannot get proper git information
        print(e)
        return

    changed_modules = set()
    for changed_file in changed_files:
        segments = [s for s in changed_file.split('/') if s]

        if segments[0] == 'thirdparty':
            # test it all when changing thirdparty deps
            return

        if segments[0] not in ('src', 'tests'):
            # test none on changes to other files
            continue

        module = segments[1]
        changed_modules.add(module)

    force_full_test = [
        'scancode',
        'commoncode',
        'typecode',
        'textcode',
        'plugincode',
    ]

    if any(m in changed_modules for m in force_full_test):
        # test it all when certain widely dependended modules
        return

    # add dependencies
    if 'licensedcode' in changed_modules:
        changed_modules.add('packagedcode')
        changed_modules.add('summarycode')
        changed_modules.add('formattedcode')
        changed_modules.add('scancode')

    if 'cluecode' in changed_modules:
        changed_modules.add('summarycode')
        changed_modules.add('formattedcode')
        changed_modules.add('scancode')

    if TRACE:
        print()
        print('get_impacted_modules:', changed_modules)
    return changed_modules


def get_changed_files(base_branch='develop'):
    """
    Return a list of changed file paths against the `base_branch`.
    Or locally only if `base_branch` is None.
    Raise an exception on errors.
    """
    # this may fail with exceptions
    cmd = 'git', 'diff', '--name-only',
    if base_branch:
        cmd += base_branch + '...',
    changed_files = check_output(cmd, stderr=STDOUT)
    changed_files = changed_files.replace('\\', '/')
    changed_files = changed_files.splitlines(False)
    changed_files = [cf for cf in changed_files if cf.strip()]
    if TRACE:
        print()
        print('get_changed_files:', changed_files)
    return changed_files


def get_git_branch():
    """
    Return the current branch or raise an exception.
    """
    from subprocess import check_output, STDOUT
    # this may fail with exceptions
    cmd = 'git', 'status',
    branch = check_output(cmd, stderr=STDOUT).splitlines(False)[0]
    _, _, branch = branch.partition('On branch')
    branch = branch.strip()
    if TRACE:
        print()
        print('get_git_branch:', branch)
    return branch
