#!/bin/bash
#
# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# ScanCode release test script
# This script testss the installation of scancode in editable mode using the public PyPI

set -e

# un-comment to trace execution
set -x

echo "###  Installing ScanCode release with pip editable###"

mkdir -p tmp/pipedit
wget -O tmp/pipedit/virtualenv.pyz https://bootstrap.pypa.io/virtualenv/virtualenv.pyz
python3 tmp/pipedit/virtualenv.pyz tmp/pipedit

tmp/pipedit/bin/pip install -e .[full]

# perform a minimal check of the results for https://github.com/nexB/scancode-toolkit/issues/2201
if [ `tmp/pipedit/bin/scancode -i --json-pp - NOTICE | grep -c "scan_timings"` == 1 ]; then
   echo "Failed scan that includes timings"
   exit 1
else
   echo "pass"
fi

set +e
set +x
