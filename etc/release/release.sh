#!/bin/bash
#
# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# ScanCode release script
# This script creates and tests release archives in the dist/ dir

set -e

# un-comment to trace execution
set -x

echo "###  BUILDING ScanCode release ###"

echo "  RELEASE: Cleaning previous release archives, then setup and config: "
rm -rf dist/ build/

# backup dev manifests
cp MANIFEST.in MANIFEST.in.dev 

# install release manifests
cp etc/release/MANIFEST.in.release MANIFEST.in

./configure --clean
export CONFIGURE_QUIET=1
./configure etc/conf

echo "  RELEASE: Building release archives..."

# build a zip and tar.bz2
bin/python setup.py --quiet --use-default-version clean --all sdist --formats=bztar,zip bdist_wheel

# restore dev manifests
mv MANIFEST.in.dev MANIFEST.in


function test_scan {
    # run a test scan for a given archive
    file_extension=$1
    extract_command=$2
    for archive in *.$file_extension;
        do
            echo "    RELEASE: Testing release archive: $archive ... "
            $($extract_command $archive)
            extract_dir=$(ls -d */)
            cd $extract_dir

            # this is needed for the zip
            chmod o+x scancode extractcode

            # minimal tests: update when new scans are available
            cmd="./scancode --quiet -lcip apache-2.0.LICENSE --json test_scan.json"
            echo "RUNNING TEST: $cmd"
            $cmd
            echo "TEST PASSED"

            cmd="./scancode --quiet -clipeu  apache-2.0.LICENSE --json-pp test_scan.json"
            echo "RUNNING TEST: $cmd"
            $cmd
            echo "TEST PASSED"

            cmd="./scancode --quiet -clipeu  apache-2.0.LICENSE --csv test_scan.csv"
            echo "RUNNING TEST: $cmd"
            $cmd
            echo "TEST PASSED"

            cmd="./scancode --quiet -clipeu apache-2.0.LICENSE --html test_scan.html"
            echo "RUNNING TEST: $cmd"
            $cmd
            echo "TEST PASSED"

            cmd="./scancode --quiet -clipeu apache-2.0.LICENSE --spdx-tv test_scan.spdx"
            echo "RUNNING TEST: $cmd"
            $cmd
            echo "TEST PASSED"

            cmd="./extractcode --quiet samples/arch"
            echo "RUNNING TEST: $cmd"
            $cmd
            echo "TEST PASSED"

            # cleanup
            cd ..
            rm -rf $extract_dir
            echo "    RELEASE: Success"
        done
}

cd dist
if [ "$1" != "--no-tests" ]; then
    echo "  RELEASE: Testing..."
    test_scan bz2 "tar -xf"
    test_scan zip "unzip -q"
else
    echo "  RELEASE: !!!!NOT Testing..."
fi


echo "###  RELEASE is ready for publishing  ###"

set +e
set +x
