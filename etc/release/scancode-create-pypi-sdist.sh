#!/bin/bash
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

################################################################################
# ScanCode release build script for PyPI sdists
################################################################################

set -e
# Un-comment to trace execution
#set -x

./configure --dev
venv/bin/python setup.py --quiet sdist

rm -rf build .eggs src/scancode_toolkit*.egg-info src/scancode_toolkit_mini*.egg-info
cp setup.cfg setup-main.cfg
cp setup-mini.cfg setup.cfg

venv/bin/python setup.py --quiet sdist

cp setup-main.cfg setup.cfg
rm setup-main.cfg

venv/bin/twine check dist/*

set +e
set +x
