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

mkdir -p tmp/pipinst
wget -O tmp/pipinst/virtualenv.pyz https://bootstrap.pypa.io/virtualenv/virtualenv.pyz
python3 tmp/pipinst/virtualenv.pyz tmp/pipinst

archive_to_test=$(find dist -type f -name "*.whl")

tmp/pipinst/bin/pip install release/pypi/$archive_to_test[full]

# perform a minimal check of the results for https://github.com/nexB/scancode-toolkit/issues/2201
if [ `tmp/pipinst/bin/scancode -i --json-pp - NOTICE | grep -c "scan_timings"` == 1 ]; then
   echo "Failed scan that includes timings"
   exit 1
else
   echo "pass"
fi

set +e
set +x
