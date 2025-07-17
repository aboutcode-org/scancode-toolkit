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
# ScanCode release build script for a macOS app archive
################################################################################

set -e
# Un-comment to trace execution
#set -x


operating_system=macos
python_dot_version=$1
python_version=${python_dot_version//.}
python_exe="python3"
release_dir=scancode-toolkit-$(git describe --tags)

rm -rf $release_dir
mkdir -p $release_dir

echo -n "$python_exe" > $release_dir/PYTHON_EXECUTABLE
git describe --tags > $release_dir/SCANCODE_VERSION
thirdparty_dir=$release_dir/thirdparty
thirdparty_src_dir=$release_dir/thirdparty-src
mkdir -p $thirdparty_dir
mkdir -p $thirdparty_src_dir

./configure --dev

venv/bin/python etc/scripts/fetch_thirdparty.py \
  --requirements requirements-native.txt \
  --wheel-only packagedcode-msitools \
  --wheel-only rpm-inspector-rpm \
  --wheel-only extractcode-7z \
  --wheel-only extractcode-libarchive \
  --wheel-only typecode-libmagic \
  --dest $thirdparty_src_dir \
  --sdists \
  --use-cached-index

venv/bin/python etc/scripts/fetch_thirdparty.py \
  --requirements requirements.txt \
  --dest $thirdparty_dir \
  --operating-system=$operating_system \
  --python-version=$python_version \
  --wheels \
  --use-cached-index

mv $thirdparty_src_dir/* $thirdparty_dir/
rm -rf $thirdparty_src_dir

mkdir -p $release_dir/etc
cp -r etc/thirdparty $release_dir/etc

# Build the wheel
./configure --dev
venv/bin/scancode-reindex-licenses
venv/bin/python setup.py --quiet bdist_wheel --python-tag cp$python_version

cp -r \
  dist/scancode_*.whl \
  scancode extractcode configure \
  *.rst \
  samples \
  *NOTICE *LICENSE *ABOUT \
  $release_dir

tarball=scancode-toolkit-$(git describe --tags)_py$python_dot_version-$operating_system.tar.gz
mkdir -p release
tar -cvzf release/$tarball $release_dir

set +e
set +x
