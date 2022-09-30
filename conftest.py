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

TRACE = False

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
PLUGINS_TEST = 'scanplugins'


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        SLOW_TEST +
        ': Mark a ScanCode test as a slow, long running test.',
    )

    config.addinivalue_line(
        'markers',
        VALIDATION_TEST +
        ': Mark a ScanCode test as a validation test, super slow, long running test.',
    )

    config.addinivalue_line(
        'markers',
        PLUGINS_TEST +
        ': Mark a ScanCode test as a special CI test to tests installing additional plugins.',
    )


TEST_SUITES = ('standard', 'all', 'validate', 'plugins',)


def pytest_addoption(parser):
    """
    Add options used for ScanCode tests customization.
    """
    group = parser.getgroup('scancode', 'Test suite options for ScanCode')

    group.addoption(
        '--test-suite',
        action='store',
        choices=TEST_SUITES,
        dest='test_suite',
        default='standard',
        help='Select which test suite to run: '
             '"standard" runs the standard test suite designed to run reasonably fast. '
             '"all" runs "standard" and "slow" (long running) tests. '
             '"validate" runs all the tests, except the "plugins" tests. '
             '"plugins" runs special plugins tests. Needs extra setup, and is used only in the CI. '
             'Use the @pytest.mark.scanslow marker to mark a test as "slow" test. '
             'Use the @pytest.mark.scanvalidate marker to mark a test as a "validate" test.'
             'Use the @pytest.mark.scanplugins marker to mark a test as a "plugins" test.'
        )

################################################################################
# Filter which tests  to collect based on our CLI options and our custom markers
################################################################################


@pytest.mark.trylast
def pytest_collection_modifyitems(config, items):
    test_suite = config.getvalue('test_suite')
    run_everything = test_suite == 'validate'
    run_slow_test = test_suite in ('all', 'validate')
    run_only_plugins = test_suite == 'plugins'

    tests_to_run = []
    tests_to_skip = []

    for item in items:
        is_validate = bool(item.get_closest_marker(VALIDATION_TEST))
        is_slow = bool(item.get_closest_marker(SLOW_TEST))
        is_plugins = bool(item.get_closest_marker(PLUGINS_TEST))

        if is_plugins and not run_only_plugins:
            tests_to_skip.append(item)
            continue

        if is_validate and not run_everything:
            tests_to_skip.append(item)
            continue

        if is_slow and not run_slow_test:
            tests_to_skip.append(item)
            continue

        tests_to_run.append(item)

    print()
    print('{} tests selected, {} tests skipped.'.format(len(tests_to_run), len(tests_to_skip)))

    items[:] = tests_to_run
    config.hook.pytest_deselected(items=tests_to_skip)
