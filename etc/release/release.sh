#!/bin/bash
#
# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# ScanCode release script
# This script creates and tests release archives in the dist/ dir

set -e

# un-comment to trace execution
# set -x

echo "###  BUILDING ScanCode release ###"

PYPI_REPO=https://github.com/nexB/thirdparty-packages/releases/tag/pypi

echo "  RELEASE: Cleaning previous release archives, then setup and config: "
rm -rf dist/ build/

# backup dev manifests
cp MANIFEST.in MANIFEST.in.dev 

# backup thirdparty
cp -r thirdparty thirdparty_dev
rm -rf thirdparty

# install release manifests
cp etc/release/MANIFEST.in.release MANIFEST.in

python_version=`python -c "from sys import version_info as v;print(f'py{v.major}{v.minor}')`

# download all dependencies as per OS/arch/python 
python3 etc/release/deps_download.py --find-links $PYPI_REPO --requirement requirements.txt --dest thirdparty

if [ "$(uname -s)" == "Darwin" ]; then
    platform="mac"        
elif [ "$(uname -s)" == "Linux" ]; then
    platform="linux" 

# FIXME: This may only works on azure AND not elsewhere
elif [ "$(uname -s)" == "MINGW64_NT" ]; then
    platform="win64"
fi

#copy virtual env files
cp thirdparty_dev/{virtualenv.pyz,virtualenv.pyz.ABOUT} thirdparty

./configure --clean
CONFIGURE_QUIET=1 ./configure

# create requirements files as per OS/arch/python
source bin/activate
pip install -r etc/release/requirements.txt

python etc/release/freeze_and_update_reqs.py --find-links thirdparty --requirement requirements.txt


################################################################################
echo "  RELEASE: Building release archives..."
bin/python setup.py clean --all sdist --formats=bztar,zip bdist_wheel

# rename release archive as per os/arch/python
# See https://unix.stackexchange.com/questions/121570/rename-multiples-files-using-bash-scripting
for f in dist/scancode-toolkit*.tar.bz2
    do
        mv "$f" "${f%*.*.*}-"$python_version"_"$platform".tar.bz2"
    done

for f in dist/scancode-toolkit*.zip
    do
        mv "$f" "${f%*.*}-"$python_version"_"$platform".zip"
    done

# restore dev manifests
mv MANIFEST.in.dev MANIFEST.in

# restore thirdparty
rm -rf thirdparty
mv thirdparty_dev thirdparty

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
