#!/bin/bash
#
# Copyright (c) 2018 nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# ScanCode release script
# This script builds wheels for plugins in the plugins/ directory

set -e

# un-comment to trace execution
# set -x

for i in `ls plugins`
  do 
    pushd plugins/$i
    rm -rf dist build
    python setup.py release
    cp `find dist/ -type f` ../../thirdparty/
    popd
  done
