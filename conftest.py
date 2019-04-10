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

from __future__ import absolute_import
from __future__ import print_function

import os
from os import path
from subprocess import check_output
from subprocess import STDOUT

import pytest
import six


"""
A pytest conftest.py for scancode-toolkit to speed test runs. 
It tries to find which code modules have changed using git, and selectively runs
only the tests for the impacted modules when running in a feature branch. When
running on the develop or master branches all the tests run: none are skipped.
"""


def get_all_modules():
    """
    Return a set of top level modules.
    """
    return set([p for p in os.listdir('src') if p.endswith('code')])


def get_impacted_modules(base_branch='develop'):
    """
    Return a set of impacted top level modules under tests or src.
    Return None if all modules are impacted and should be re-tested.
    """
    try:
        current_branch = get_git_branch()
        changed_files = get_changed_files(base_branch)
        locally_changed_files = get_changed_files(None)
        changed_files.extend(locally_changed_files)
    except Exception as e:
        # we test it all if we cannot get proper git information
        print(e)
        return

    if current_branch in ('develop', 'master'):
        # test it all when merging
        return

    changed_modules = set()
    for changed_file in changed_files:
        segments = [s for s in changed_file.split('/') if s]

        if (len(segments) == 1 or segments[0] == 'etc' 
        or segments[1] == 'scancode_config.py'):
            # test it all when changing root or etc/config files
            return

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
    return branch


################################################################################
# py test collection configuration

impacted_modules = get_impacted_modules() or set()
all_modules = get_all_modules() or set()
ignorable_modules = all_modules.difference(impacted_modules)
ignorable_module_paths = set(['/{}/'.format(m) for m in ignorable_modules])

base_dir = path.dirname(__file__)

print('====> ALL MODULES      :', ', '.join(sorted(all_modules)))
print('====> IMPACTED MODULES :', ', '.join(sorted(impacted_modules)))
print('====> IGNORED MODULES  :', ', '.join(sorted(ignorable_modules)))


def pytest_ignore_collect(path, config):
    """
    Return True to skip this path for tests collection.
    This is a pytest hook.
    """
    pth = path.strpath
    skip = should_skip(pth)
    return skip


def should_skip(path_string):
    """
    Return True if a `path_string` should be skipped.
    """
    path_string = path_string.replace('\\', '/')
    if six.PY3:
        # skip testing on Python 3 for now until we tag these modules
        # as testable . See #295 for details
        return True

    if path_string.endswith('setup.py'):
        return True

    if not impacted_modules:
        # everything is impacted and we ignore nothing
        return False
    else:
        return any(p in path_string for p in ignorable_module_paths)
