#!/bin/bash
#
# Copyright (c) 2018 nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# ScanCode release script
# This script builds wheels for plugins in the plugins-builtin/ directory

set -e

# un-comment to trace execution
# set -x


mkdir -p dist

for i in `ls plugins-builtin`
  do 
    pushd plugins-builtin/$i
    rm -rf dist build
    python setup.py release
    cp `find dist/ -type f` ../../thirdparty/
    cp `find dist/ -type f` ../../dist/
    popd
  done
