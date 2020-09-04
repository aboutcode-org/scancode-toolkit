#!/bin/bash
#
# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# ScanCode release script
# This script creates and tests release archives in the dist/ dir

set -e

# un-comment to trace execution
set -x

echo "###  Installing ScanCode release with pip editable###"

mkdir -p tmp/pipe
python -m venv tmp/pipe
tmp/pipe/bin/pip install -e .

# perform a minimal check of the results for https://github.com/nexB/scancode-toolkit/issues/2201
if [ `tmp/pipe/bin/scancode -i --json-pp - NOTICE | grep -c "scan_timings"` == 1 ]; then
   echo "Failed scan that includes timings"
   exit 1
else
   echo "pass"
fi

set +e
set +x
