#!/bin/bash
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

################################################################################
# ScanCode release build script for a Windows app archive
################################################################################

set -e
# Un-comment to trace execution
#set -x

release_dir=scancode-toolkit-$(git describe --tags)
rm -rf $release_dir
mkdir -p $release_dir

git describe --tags > $release_dir/SCANCODE_VERSION
thirdparty_dir=$release_dir/thirdparty
mkdir -p $thirdparty_dir

# build an sdist
./configure --dev
venv/bin/python setup.py --quiet sdist
mv dist/*.tar.gz $release_dir

./configure --dev

venv/bin/python etc/scripts/fetch_thirdparty.py \
  --requirements requirements.txt \
  --requirements requirements-native.txt \
  --requirements requirements-linux.txt \
  --wheel-only packagedcode-msitools \
  --wheel-only rpm-inspector-rpm \
  --wheel-only extractcode-7z \
  --wheel-only extractcode-libarchive \
  --wheel-only typecode-libmagic \
  --dest $thirdparty_dir \
  --sdists \
  --use-cached-index

mkdir -p $release_dir/etc
cp -r etc/thirdparty $release_dir/etc


cp -r \
  scancode.bat scancode extractcode extractcode.bat configure configure.bat \
  *.rst \
  docs \
  samples \
  *NOTICE *LICENSE *ABOUT \
  $release_dir

tarball=scancode-toolkit-$(git describe --tags)_sources.tar.gz
mkdir -p release
tar -cvzf release/$tarball $release_dir

set +e
set +x
