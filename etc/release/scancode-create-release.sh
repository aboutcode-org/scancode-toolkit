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
OPERATING_SYSTEMS="linux macosx windows"

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
echo "### BUILDING on Python: $PYTHON_VERSIONS on OSes $OPERATING_SYSTEMS"


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
# Build OSes and Pythons-specific release archives
################################

function build_archives {
    # Build scancode release archives (zip and tarbal) for one target python
    # and operating_system
    # Arguments:
    #   python_version: only include wheels for this Python version. Example: 36
    #   operating_system: only include wheels for this operating_system. One of windows, linux or mac

    python_version=$1
    operating_system=$2

    echo "## RELEASE: Building archive for Python $python_version for operating_system $operating_system"

    clean_build
    mkdir -p thirdparty

    # collect thirdparty deps only for the subset for this Python/operating_system
    bin/python etc/release/fetch_required_wheels.py \
        --requirement=requirements.txt \
        --thirdparty-dir=thirdparty \
        --python-version=$python_version \
        --operating_system=$operating_system

    # Create tarball and zip.
    # For now as a shortcut we use the Python setup.py sdist to create a tarball.
    # This is hackish and we should instead use our own archiving code that
    # would take a distutils manifest-like input
    bin/python setup.py $QUIET $QUIET $QUIET sdist --formats=xztar,zip 
    bin/python etc/release/rename_archives.py dist/ $python_version $operating_system
    mkdir -p release/archives
    mv dist/* release/archives/
}


function build_archives_with_sources {
    # Build scancode release archives (zip and tarbal) for one target python
    # and operating_system, including all thirdparty source code.
    # Arguments:
    #   python_version: only include wheels for this Python version. Example: 36
    #   operating_system: only include wheels for this operating_system. One of windows, linux or mac

    python_version=$1
    operating_system=$2

    echo "## RELEASE: Building archive for Python $python_version for operating_system $operating_system"

    clean_build
    mkdir -p thirdparty

    # collect thirdparty deps only for the subset for this Python/operating_system
    bin/python etc/release/fetch_required_sources.py \
        --requirement=requirements.txt \
        --thirdparty-dir=thirdparty

    # Create tarball and zip.
    # For now as a shortcut we use the Python setup.py sdist to create a tarball.
    # This is hackish and we should instead use our own archiving code that
    # would take a distutils manifest-like input

    bin/python setup.py $QUIET $QUIET $QUIET sdist --formats=xztar

    bin/python etc/release/rename_archives.py dist/ $python_version $operating_system-sources
    mkdir -p release/archives
    mv dist/* release/archives/
}


# build all the combos
for python_version in $PYTHON_VERSIONS
    do
    for operating_system in $OPERATING_SYSTEMS
        do
        build_archives $python_version $operating_system
        build_archives_with_sources $python_version $operating_system
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
