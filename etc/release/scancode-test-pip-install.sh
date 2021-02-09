#!/bin/bash
#
# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# ScanCode release test script
# This script testss the installation of scancode from a wheel using the public PyPI

set -e

# un-comment to trace execution
set -x

echo "## Build a wheel"
./configure --dev
./scancode --reindex-licenses
bin/python setup.py bdist_wheel

echo "###  Installing ScanCode release with pip ###"

mkdir -p tmp/pip
python -m venv tmp/pip
tmp/pip/bin/pip install release/pypi/scancode_toolkit*.whl

# perform a minimal check of the results for https://github.com/nexB/scancode-toolkit/issues/2201
if [ `tmp/pip/bin/scancode -i --json-pp - NOTICE | grep -c "scan_timings"` == 1 ]; then
   echo "Failed scan that includes timings"
   exit 1
else
   echo "pass"
fi

set +e
set +x
