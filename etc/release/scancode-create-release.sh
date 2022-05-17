#!/bin/bash
#
# Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#

################################################################################
# ScanCode release build script
# Create, test and publish release archives, wheels and sdists.
# Use the --test to also run basic smoke tests of the built archives
#
# To use a local checkout of https://github.com/nexB/thirdparty-packages/ rather
# than https://thirdparty.aboutcode.org/ set the variable PYPI_LINKS to point
# to your thirdparty-packages/pypi local directory (this speeds up the release
# creation and allow to work mostly offline.
#
################################################################################

# Supported current app Python version and OS
# one archive or installer is built for each python x OS combo
PYTHON_APP_DOT_VERSIONS="3.8"

PYTHON_PYPI_TESTS_DOT_VERSIONS="3.8"

PYPI_LINKS=https://thirdparty.aboutcode.org/pypi

OPERATING_SYSTEMS="linux macos windows"

QUIET="--quiet"


################################################################################

set -e

# Un-comment to trace execution
#set -x


if [ "$(uname -s)" != "Linux" ]; then
    echo "Building is only supported on Linux. Aborting"
    exit 1
fi


CLI_ARGS=$1

BIN_DIR=venv/bin

echo "##########################################################################"
echo "### BUILDING App for Python: $PYTHON_APP_VERSIONS on OS: $OPERATING_SYSTEMS"


################################
# Setup
################################

echo "## RELEASE: Backup previous releases"

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


function clean_egg_info {
	rm -rf .eggs src/scancode_toolkit.egg-info src/scancode_toolkit_mini.egg-info
}


function clean_build {
    rm -rf build dist thirdparty PYTHON_EXECUTABLE
    clean_egg_info
}

################################
# PyPI wheels and sdist: these are not Python version- or OS-dependent
################################
function build_wheels {
    # Build scancode wheels and dist for PyPI
    # Arguments:

    echo " "
    echo "## RELEASE: Building a wheel and a source distribution"
    clean_egg_info
    $BIN_DIR/python setup.py $QUIET sdist bdist_wheel

    mv dist release/pypi

    echo " "
    echo "## RELEASE: Building a mini wheel and a source distribution"
    clean_egg_info
    mv setup.cfg setup-full.cfg
    cp setup-mini.cfg setup.cfg
    rm -rf build
    $BIN_DIR/python setup.py $QUIET sdist bdist_wheel
    mv setup-full.cfg setup.cfg

    cp dist/* release/pypi/

    clean_egg_info
    echo "## RELEASE: full and mini, wheel and source distribution(s) built and ready for PyPI upload"
    find release -ls

}

################################
# Build OSes and Pythons-specific release archives
################################

function build_app_archive {
    # Build scancode release archives (zip and tarbal) for the current app
    # python and a provided operating_system argument
    # Arguments:
    #   operating_system: only include wheels for this operating_system. 
    #                     One of windows, linux or macos
    #   python_app_dot_version: the python version to build (with dot)

    operating_system=$1
    python_app_dot_version=$2
    # remove dots
    python_app_version=${python_app_dot_version/./}

    echo " "
    echo "## RELEASE: Building archive for Python $python_app_version on operating system: $operating_system"

    if [ "$operating_system" == "windows" ]; then
        # create a zip only on Windows
        formats=zip
        formats_ext=.zip
    else
        formats=xztar
        formats_ext=.tar.xz
    fi

    if [ ! -f release/archives/scancode-toolkit-*_py$python_app_version-$operating_system$formats_ext ]; then
        clean_build
        mkdir -p thirdparty

        if [ "$operating_system" == "windows" ]; then
            echo -n "py -$python_app_dot_version" > PYTHON_EXECUTABLE
        else
            echo -n "python$python_app_dot_version" > PYTHON_EXECUTABLE
        fi

        # 1. Collect thirdparty deps only for the subset for this Python/operating_system
        $BIN_DIR/python etc/scripts/fetch_thirdparty.py \
            --requirements=requirements.txt \
            --dest=thirdparty \
            --python-version=$python_app_version \
            --operating-system=$operating_system \
            --wheels

        # 2. Collect thirdparty deps source for native
        $BIN_DIR/python etc/scripts/fetch_thirdparty.py \
            --requirements=requirements-native.txt \
            --dest=thirdparty \
            --sdists

        # 3. Create tarball or zip.
        # For now as a shortcut we use the Python setup.py sdist to create a tarball.
        # This is hackish and we should instead use our own archiving code that
        # would take a distutils manifest-like input
        $BIN_DIR/python setup.py $QUIET sdist --formats=$formats 
        $BIN_DIR/python etc/release/scancode_rename_archives.py dist/ _py$python_app_version-$operating_system
        mkdir -p release/archives
        mv dist/* release/archives/
    fi

}


function build_source_archive {
    # Build scancode source archive tarball including only thirdparty source
    # code, no wheels (and for any python and operating_system)

    echo " "
    echo "## RELEASE: Building archive with sources"

    clean_build
    mkdir -p thirdparty

    # 1. collect thirdparty deps sources
    $BIN_DIR/python etc/scripts/fetch_thirdparty.py \
        --requirements=requirements.txt \
        --dest=thirdparty \
        --sdists

    # 2. Create tarball
    # For now as a shortcut we use the Python setup.py sdist to create a tarball.
    # This is hackish and we should instead use our own archiving code that
    # would take a distutils manifest-like input

    $BIN_DIR/python setup.py $QUIET sdist --formats=xztar
    $BIN_DIR/python etc/release/scancode_rename_archives.py dist/ _sources
    mkdir -p release/archives
    mv dist/* release/archives/
}


if [ "$CLI_ARGS" != "--continue" ]; then
    echo "############# Reset release creation #############################"
    backup_previous_release
    clean_build
    mkdir release

    echo "## RELEASE: Setup environment"

    echo "## RELEASE: Clean and configure, then regen license index"
    ./configure --clean
    ./configure --local 
    source $BIN_DIR/activate
    scancode --reindex-licenses

    echo "## RELEASE: Install utilities requirements"
    # We do not need a full env for releasing
    $BIN_DIR/pip install $QUIET -r etc/scripts/requirements.txt
else
    echo "############# Continuing previous release creation #############################"
fi


# wheels
build_wheels

# build the app combos on the current App Python
for operating_system in $OPERATING_SYSTEMS
    do
    for pyver in $PYTHON_APP_DOT_VERSIONS
        do
        build_app_archive $operating_system $pyver
    done
done

build_source_archive

echo " "
echo "## RELEASE: archives built and ready for test and publishing"
find release -ls 



################################
# Publish release
################################

echo " "
echo "###  RELEASE is ready for publishing  ###"
# Upload wheels and sdist to PyPI
# They are found in release/pypi


# Create and upload release and pypi archives to GitHub
# They are found in release/archives and in release/pypi


################################
# Announce release
################################

# ping on chat and twitter
# send email

set +e
set +x
