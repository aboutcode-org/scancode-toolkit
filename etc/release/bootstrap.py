#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

import itertools

import click

import utils_thirdparty
from utils_thirdparty import Environment
from utils_thirdparty import PypiPackage


@click.command()

@click.option('-r', '--requirements-file',
    type=click.Path(exists=True, readable=True, path_type=str, dir_okay=False),
    metavar='FILE',
    multiple=True,
    default=['requirements.txt'],
    show_default=True,
    help='Path to the requirements file(s) to use for thirdparty packages.',
)
@click.option('-t', '--thirdparty-dir',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    metavar='DIR',
    default=utils_thirdparty.THIRDPARTY_DIR,
    show_default=True,
    help='Path to the thirdparty directory where wheels are built and '
         'sources, ABOUT and LICENSE files fetched.',
)
@click.option('-p', '--python-version',
    type=click.Choice(utils_thirdparty.PYTHON_VERSIONS),
    metavar='PYVER',
    default=utils_thirdparty.PYTHON_VERSIONS,
    show_default=True,
    multiple=True,
    help='Python version(s) to use for this build.',
)
@click.option('-o', '--operating-system',
    type=click.Choice(utils_thirdparty.PLATFORMS_BY_OS),
    metavar='OS',
    default=tuple(utils_thirdparty.PLATFORMS_BY_OS),
    multiple=True,
    show_default=True,
    help='OS(ses) to use for this build: one of linux, mac or windows.',
)
@click.option('--sync-dejacode',
    is_flag=True,
    help='Synchronize packages with DejaCode.',
)
@click.help_option('-h', '--help')
def bootstrap(
    requirements_file,
    thirdparty_dir,
    python_version,
    operating_system,
    sync_dejacode,
):
    """
    Boostrap a thirdparty Python packages directory using pip requirements file(s).

    Fetch or build to THIRDPARTY_DIR all the wheels and source distributions for
    the pip `--requirement-file` requirements file(s). Build wheels compatible
    with all the provided `--python-version` and `--operating_system`
    defaulting to all supported combinations. Create or fetch .ABOUT and
    .LICENSE files.

    Sources and wheels are first fetched from PyPI, then our remote repository.
    If missing wheels are built as needed.
    """
    # rename variables for clarity since these are lists
    requirements_files = requirements_file
    python_versions = python_version
    operating_systems = operating_system

    # create the environments we need
    evts = itertools.product(python_versions, operating_systems)
    environments = [Environment.from_pyver_and_os(pyv, os) for pyv, os in evts]

    # collect all packages to process from requirements files
    # this will fail with an exception if there are packages we cannot find

    required_name_versions = set()

    for req_file in requirements_files:
        nvs = utils_thirdparty.load_requirements(requirements_file=req_file)
        required_name_versions.update(nvs)

    # list of all the wheel filenames either pre-existing, fetched or built
    # updated as we progress
    available_wheel_filenames = []

    local_packages_by_namever = {
        (p.name, p.version): p
        for p in utils_thirdparty.get_local_packages(directory=thirdparty_dir)
    }

    # fetch all available wheels, keep track of missing
    # start with local, then remote, then PyPI

    print('\n===========> COLLECTING ALREADY LOCALLY AVAILABLE REQUIRED WHEELS')

    # list of (name, version, environment) not local and to fetch
    name_version_envt_to_fetch = []

    # start with a local check
    for (name, version), envt in itertools.product(required_name_versions, environments):
        local_pack = local_packages_by_namever.get((name, version,))
        if local_pack:
            supported_wheels = list(local_pack.get_supported_wheels(environment=envt))
            if supported_wheels:
                available_wheel_filenames.extend(w.filename for w in supported_wheels)
                print(f'=============================> No fetch or build needed. Local wheel already available for {name}=={version} '
                      f'on os: {envt.operating_system} for Python: {envt.python_version}')
            else:
                name_version_envt_to_fetch.append((name, version, envt,))

    print(f'\n===========> TRYING TO FETCH #{len(name_version_envt_to_fetch)} REQUIRED WHEELS')

    # list of (name, version, environment) not fetch and to build
    name_version_envt_to_build = []

    # then check if the wheel can be fetched without building from remote and Pypi
    for name, version, envt in name_version_envt_to_fetch:

        fetched_fwn = utils_thirdparty.fetch_package_wheel(name=name, version=version, environment=envt)

        if fetched_fwn:
            available_wheel_filenames.append(fetched_fwn)
        else:
            name_version_envt_to_build.append((name, version, envt,))

    # At this stage we have all the wheels we could obtain without building
    for name, version, envt in name_version_envt_to_build:
        print(f'Need to build wheels for {name}=={version} '
              f'on os: {envt.operating_system} for Python: {envt.python_version}')

    packages_and_envts_to_build = [
        (PypiPackage(name, version), envt)
        for name, version, envt in name_version_envt_to_build
    ]

    # First attempt to build locally as plain/pure python wheel
    print(f'\n===========> BUILDING #{len(packages_and_envts_to_build)} MISSING WHEELS locally as pure Python')

    package_envts_not_built_as_pure, wheel_filenames_built = utils_thirdparty.build_missing_wheels(
        packages_and_envts=packages_and_envts_to_build,
        build_remotely=False,
        dest_dir=thirdparty_dir,
)
    if wheel_filenames_built:
        available_wheel_filenames.extend(available_wheel_filenames)

    for pack, envt in package_envts_not_built_as_pure:
        print(
            f'=============================> No PURE Python wheel build possible for {pack.name}=={pack.version} '
            f'on os: {envt.operating_system} for Python: {envt.python_version}'
        )

    # Second attempt to build remotely for wheels with native code
    print(f'\n===========> BUILDING #{len(package_envts_not_built_as_pure)} MISSING WHEELS with native remotely')

    package_envts_not_built, wheel_filenames_built = utils_thirdparty.build_missing_wheels(
        packages_and_envts=package_envts_not_built_as_pure,
        build_remotely=False,
        dest_dir=thirdparty_dir,
    )
    if wheel_filenames_built:
        available_wheel_filenames.extend(available_wheel_filenames)

    for pack, envt in package_envts_not_built:
        print(
            f'=============================> FAILED to build any wheel for {pack.name}=={pack.version} '
            f'on os: {envt.operating_system} for Python: {envt.python_version}'
        )

    print(f'\n===========> FETCHING SOURCE DISTRIBUTIONS')
    # fetch all sources, keep track of missing
    # This is a list of (name, version)
    missing_sdists = utils_thirdparty.add_missing_sources(
        dest_dir=thirdparty_dir)

    for name, version in missing_sdists:
        print(f'No sdist found for {name}=={version}')

    print(f'\n===========> FETCHING ABOUT AND LICENSE FILES')
    # fetch all ABOUT, NOTICE LICENSE keep track of missing
    # fetch all missing licenses
    utils_thirdparty.fetch_and_save_about_data(dest_dir=thirdparty_dir)
    utils_thirdparty.add_referenced_licenses_and_notices(dest_dir=thirdparty_dir)


    ############################################################################
    if sync_dejacode:
        print(f'\n===========> SYNC WITH DEJACODE')
        # try to fetch from DejaCode any missing ABOUT
        # create all missing DejaCode packages
        pass

    utils_thirdparty.add_or_update_about_files(dest_dir=thirdparty_dir)
    utils_thirdparty.fix_about_files_checksums(dest_dir=thirdparty_dir)


if __name__ == '__main__':
    bootstrap()
