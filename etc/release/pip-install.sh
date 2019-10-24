#!/bin/bash
#
# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# ScanCode release script
# This script creates and tests release archives in the dist/ dir

set -e

# un-comment to trace execution
set -x

echo "###  Installing ScanCode release with pip ###"

mkdir -p tmp/pip
python -m venv tmp/pip
source tmp/pip/bin/activate
pip install dist/scancode_toolkit*.whl

set +e
set +x
