#!/bin/bash
#
# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#

################################################################################
# ScanCode release test script
################################################################################

set -e

# Un-comment to trace execution
#set -x


function run_test_scan {
    # Run a test scan for a given release archive
    # Note that for now, these tests run only on Linux
    # Arguments:
    #   file_extension: the file name suffix to consider for testing
    #   extract_command: the command to use to extract an archive

    file_extension=$1
    extract_command=$2
    for archive in *$file_extension;
        do
            echo "    RELEASE: Testing release archive: $archive ... "
            $($extract_command $archive)
            extract_dir=$(ls -d */)
            cd "$extract_dir"

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

            mkdir -p foo
            touch foo/bar
            tar -czf foo.tgz foo
            cmd="./extractcode --quiet foo.tgz"
            echo "RUNNING TEST: $cmd"
            $cmd
            echo "TEST PASSED"

            # cleanup
            cd ..
            rm -rf "$extract_dir"
            echo "    RELEASE: Success"
        done
}


cd release/archives
echo "  RELEASE: Testing built archives for LINUX only..."
run_test_scan "linux.tar.xz" "tar -xf"
cd ../..


set +e
set +x
