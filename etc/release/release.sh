#!/bin/bash
#
# Copyright (c) 2015 nexB Inc. http://www.nexb.com/ - All rights reserved.
#

# A minimal release script

set -e
#RELEASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#cd "$RELEASE_DIR"

rm -rf dist/
cp etc/release/MANIFEST.in.release MANIFEST.in
cp etc/release/setup.cfg.release setup.cfg

./configure --clean
source configure etc/conf
python setup.py sdist --formats=bztar,zip

cp etc/release/MANIFEST.in.dev MANIFEST.in
cp etc/release/setup.cfg.dev setup.cfg

set +e
