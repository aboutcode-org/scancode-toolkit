#!/bin/bash
#
# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# ScanCode release script
# This script uses bumpversion to update the version of plugins in the plugins-builtin/ directory

set -e

# un-comment to trace execution
# set -x


for i in `ls plugins-builtin`
  do 
    echo "Bumping $i"
    pushd plugins-builtin/$i
    bumpversion patch
    popd
  done
