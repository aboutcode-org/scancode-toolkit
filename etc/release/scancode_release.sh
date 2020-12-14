#!/bin/bash
#
# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#

################################################################################
# ScanCode release build script
# Create, test and publish release archives, wheels and sdists.
# Use the --test to also run basic somke test of the built archives
#
################################################################################

# Supported Python versions and OS combos
# one archive or installer is built for each combo
PYTHON_VERSIONS="36"
PLATFORMS="linux macosx windows"

# an HTML page where we can find links to our pre-build wheels
LINKS_URL=https://github.com/nexB/thirdparty-packages/releases/pypi

#QUIET=""

QUIET="--quiet"

################################################################################

set -e

# Un-comment to trace execution
#set -x


#if [ "$(uname -s)" != "Linux" ]; then
#    echo "Building is only supported on Linux. Aborting"
#    exit 1
#fi


CLI_ARGS=$1


echo "##########################################################################"
echo "### BUILDING on Python: $PYTHON_VERSIONS on platforms $PLATFORMS"


################################
# Setup
################################

echo "## RELEASE: Setup environment"


function backup_previous_release {
    # Move any existing dist, build and release dirs to a release-backup-<timestamp> dir

    if [[ (-d "dist") || (-d "build") ||  (-d "release") ]]; then
        previous_release=release-backup-$(date --iso=seconds)
        mkdir $previous_release
        [[ (-d "dist") ]] && mv dist $previous_release
        [[ (-d "build") ]] && mv build $previous_release
        [[ (-d "release") ]] && mv release $previous_release
    fi
}

function clean_build {
    rm -rf build dist thirdparty
}

backup_previous_release
clean_build
mkdir release

source bin/activate
bin/pip install $QUIET -r etc/release/requirements.txt


################################
# PyPI wheels and sdist
################################

echo "## RELEASE: Building a wheel and a source distribution"
bin/python setup.py $QUIET $QUIET $QUIET sdist bdist_wheel
mv dist release/pypi

echo "## RELEASE: wheel and source distribution built and ready for PyPI upload"
find release/pypi -ls 


################################
# Build platforms and Pythons-specific release archives
################################

function build_archives {
    # Build scancode release archives (zip and tarbal) for one target python
    # and platform
    # Arguments:
    #   python_version: only include wheels for this Python version. Example: 36
    #   platform: only include wheels for this platform. One of windows, linux or mac

    python_version=$1
    platform=$2

    echo "## RELEASE: Building archive for Python $python_version for platform $platform"

    clean_build
    mkdir -p thirdparty

    # collect thirdparty deps only for the subset for this Python/platform
    bin/python etc/release/dependencies_fetch.py \
        --links-url=$LINKS_URL \
        --requirement=requirements.txt \
        --thirdparty-dir=thirdparty \
        --python-version=$python_version \
        --platform=$platform

    # Create tarball and zip.
    # For now as a shortcut we use the Python setup.py sdist to create a tarball.
    # This is hackish and we should instead use our own archiving code that
    # would take a distutils manifest-like input
    bin/python setup.py $QUIET $QUIET $QUIET sdist --formats=bztar,gztar,xztar,zip 
    bin/python etc/release/rename_archives.py dist/ $python_version $platform
    mkdir -p release/archives
    mv dist/* release/archives/
}


function build_archives_with_sources {
    # Build scancode release archives (zip and tarbal) for one target python
    # and platform, including all thirdparty source code.
    # Arguments:
    #   python_version: only include wheels for this Python version. Example: 36
    #   platform: only include wheels for this platform. One of windows, linux or mac

    python_version=$1
    platform=$2

    echo "## RELEASE: Building archive for Python $python_version for platform $platform"

    clean_build
    mkdir -p thirdparty

    # collect thirdparty deps only for the subset for this Python/platform
    bin/python etc/release/dependencies_fetch.py \
        --links-url=$LINKS_URL \
        --requirement=requirements.txt \
        --thirdparty-dir=thirdparty \
        --python-version=$python_version \
        --platform=$platform \
        --include-source

    # Create tarball and zip.
    # For now as a shortcut we use the Python setup.py sdist to create a tarball.
    # This is hackish and we should instead use our own archiving code that
    # would take a distutils manifest-like input

    bin/python setup.py $QUIET $QUIET $QUIET sdist --formats=xztar

    bin/python etc/release/rename_archives.py dist/ $python_version $platform-sources
    mkdir -p release/archives
    mv dist/* release/archives/
}


# build all the combos
for python_version in $PYTHON_VERSIONS
    do
    for platform in $PLATFORMS
        do
        build_archives $python_version $platform
        build_archives_with_sources $python_version $platform
        done
    done

echo "## RELEASE: archive built and ready for publishing"
find release/archives -ls 


################################
# Run optional smoke tests
################################



if [ "$CLI_ARGS" == "--test" ]; then
    ./scancode_release_tests.sh
else
    echo "  RELEASE: !!!!NOT Testing..."
fi


################################
# Publish release
################################

echo "###  RELEASE is ready for publishing  ###"
# Upload wheels and sdist to PyPI
# They are found in release/pypi


# Create and upload release archives to GitHub
# They are found in release/archives


# also upload wheels and sdist to GitHub
# They are found in release/pypi


################################
# Announce release
################################

# ping on chat and tweeter
# send email


set +e
set +x
