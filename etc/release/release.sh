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

# backup thirdparty
cp -r thirdparty thirdparty_dev
rm -rf thirdparty

# install release manifests
cp etc/release/MANIFEST.in.release MANIFEST.in

python_version=`python -c "import sys;t='py{v[0]}{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)";`

# download all dependencies as per OS/arch/python 
python3 etc/scripts/deps_download.py --find-links https://github.com/Abhishek-Dev09/thirdparty/releases/tag/v2.0 --requirement etc/conf/requirements-"$python_version"_all.txt --dest thirdparty

if [ "$(uname -s)" == "Darwin" ]; then
    platform="mac"        
elif [ "$(uname -s)" == "Linux" ]; then
    platform="linux" 
elif [ "$(uname -s)" == "MINGW32_NT" ]; then
    platform="win32"
elif [ "$(uname -s)" == "MINGW64_NT" ]; then
    platform="win64"
fi

#copy virtual env files
cp thirdparty_dev/{virtualenv.pyz,virtualenv.pyz.ABOUT} thirdparty

./configure --clean
export CONFIGURE_QUIET=1
./configure etc/conf

# create requirements files as per OS/arch/python
source bin/activate
pip install -r etc/scripts/req_tools.txt
python etc/scripts/freeze_and_update_reqs.py --find-links thirdparty --requirement etc/conf/requirement-"$python_version"_"$platform".txt

echo "  RELEASE: Building release archives..."

# build a zip and tar.bz2
bin/python setup.py --quiet --use-default-version clean --all sdist --formats=bztar,zip bdist_wheel #--plat-name "$platform" --python-tag "$python_version"

#rename release archive as per os/arch/python
for f in dist/scancode-toolkit*.tar.bz2; do mv "$f" "${f%*.*.*}-"$python_version"_"$platform".tar.bz2"; done
for f in dist/scancode-toolkit*.zip; do mv "$f" "${f%*.*}-"$python_version"_"$platform".zip"; done

# restore dev manifests
mv MANIFEST.in.dev MANIFEST.in

#restore thirdparty
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
