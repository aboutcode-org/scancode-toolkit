#!/bin/bash
#
# Copyright (c) 2015 nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# ScanCode release script
# This script creates and tests release archives in the dist/ dir

set -e

# un-comment to trace execution
# set -x

echo "###  BUILDING ScanCode release ###"

echo -n "  RELEASE: Cleaning previous release archives, then setup and config: "
rm -rf dist/

cp etc/release/MANIFEST.in.release MANIFEST.in
cp etc/release/setup.cfg.release setup.cfg
./configure --clean
export CONFIGURE_QUIET=1
./configure etc/conf

echo "  RELEASE: Building release archives..."

# build a zip and tar.bz2
bin/python setup.py --quiet release


# Restoring initial dev setup and config...
cp etc/release/MANIFEST.in.dev MANIFEST.in
cp etc/release/setup.cfg.dev setup.cfg


function test_scan {
    # run a test scan for a given archive
    file_extension=$1
    extract_command=$2
    for archive in *.$file_extension;
        do
            echo -n "    RELEASE: Testing release archive: $archive ... "
            $($extract_command $archive)
            extract_dir=$(ls -d */)
            cd $extract_dir

            # this is needed for the zip
            chmod o+x scancode extractcode

            # minimal test: update when new scans are available
            ./scancode --quiet -lcip apache-2.0.LICENSE test_scan.json
            echo "TEST JSON passed: ./scancode --quiet -lcip apache-2.0.LICENSE test_scan.json"
            ./scancode --quiet -lcip --format html apache-2.0.LICENSE test_scan.html
            echo "TEST HTML passed: ./scancode --quiet -lcip --format html apache-2.0.LICENSE test_scan.html"
            ./scancode --quiet -lcip --format html-app apache-2.0.LICENSE test_scan_app.html
            echo "TEST HTML-APP passed: ./scancode --quiet -lcip --format html-app apache-2.0.LICENSE test_scan_app.html"
            ./extractcode --quiet samples/arch
            echo "TEST EXTRACTCODE passed: ./extractcode --quiet samples/arch"

            # cleanup
            cd ..
            rm -rf $extract_dir
            echo "    RELEASE: Success"
        done
}

cd dist
echo "  RELEASE: Testing..."
test_scan gz "tar -xf"
test_scan bz2 "tar -xf"
test_scan zip "unzip -q"

echo "###  RELEASE is ready for publishing ###"

set +e
set +x
