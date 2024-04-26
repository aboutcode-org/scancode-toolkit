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
# ScanCode release build script for PyPI ScanCode, license and other wheels.
################################################################################

set -e
# Un-comment to trace execution
#set -x

./configure --dev

venv/bin/scancode-reindex-licenses

# build license data packages
venv/bin/flot --pyproject pyproject-licensedcode-data.toml --wheel --sdist
venv/bin/flot --pyproject pyproject-licensedcode-index.toml --wheel --sdist

# build code packages
venv/bin/flot --pyproject pyproject.toml --wheel --sdist
venv/bin/flot --pyproject pyproject-mini.toml --wheel --sdist
venv/bin/flot --pyproject pyproject-packagedcode.toml --wheel --sdist

venv/bin/twine check dist/*

set +e
set +x
