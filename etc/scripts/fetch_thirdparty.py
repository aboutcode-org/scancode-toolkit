#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import itertools
import os
import sys

import click

import utils_thirdparty
import utils_requirements

TRACE = True


@click.command()
@click.option(
    "-r",
    "--requirements",
    "requirements_files",
    type=click.Path(exists=True, readable=True, path_type=str, dir_okay=False),
    metavar="REQUIREMENT-FILE",
    multiple=True,
    required=False,
    help="Path to pip requirements file(s) listing thirdparty packages.",
)
@click.option(
    "--spec",
    "--specifier",
    "specifiers",
    type=str,
    metavar="SPECIFIER",
    multiple=True,
    required=False,
    help="Thirdparty package name==version specification(s) as in django==1.2.3. "
    "With --latest-version a plain package name is also acceptable.",
)
@click.option(
    "-l",
    "--latest-version",
    is_flag=True,
    help="Get the latest version of all packages, ignoring any specified versions.",
)
@click.option(
    "-d",
    "--dest",
    "dest_dir",
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    metavar="DIR",
    default=utils_thirdparty.THIRDPARTY_DIR,
    show_default=True,
    help="Path to the detsination directory where to save downloaded wheels, "
    "sources, ABOUT and LICENSE files..",
)
@click.option(
    "-w",
    "--wheels",
    is_flag=True,
    help="Download wheels.",
)
@click.option(
    "-s",
    "--sdists",
    is_flag=True,
    help="Download source sdists tarballs.",
)
@click.option(
    "-p",
    "--python-version",
    "python_versions",
    type=click.Choice(utils_thirdparty.PYTHON_VERSIONS),
    metavar="PYVER",
    default=utils_thirdparty.PYTHON_VERSIONS,
    show_default=True,
    multiple=True,
    help="Python version(s) to use for wheels.",
)
@click.option(
    "-o",
    "--operating-system",
    "operating_systems",
    type=click.Choice(utils_thirdparty.PLATFORMS_BY_OS),
    metavar="OS",
    default=tuple(utils_thirdparty.PLATFORMS_BY_OS),
    multiple=True,
    show_default=True,
    help="OS(ses) to use for wheels: one of linux, mac or windows.",
)
@click.option(
    "--index-url",
    "index_urls",
    type=str,
    metavar="INDEX",
    default=utils_thirdparty.PYPI_INDEXES,
    show_default=True,
    multiple=True,
    help="PyPI index URL(s) to use for wheels and sources, in order of preferences.",
)
@click.help_option("-h", "--help")
def fetch_thirdparty(
    requirements_files,
    specifiers,
    latest_version,
    dest_dir,
    python_versions,
    operating_systems,
    wheels,
    sdists,
    index_urls,
):
    """
    Download to --dest-dir THIRDPARTY_DIR the PyPI wheels, source distributions,
    and their ABOUT metadata, license and notices files.

    Download the PyPI packages listed in the combination of:
    - the pip requirements --requirements REQUIREMENT-FILE(s),
    - the pip name==version --specifier SPECIFIER(s)
    - any pre-existing wheels or sdsists found in --dest-dir THIRDPARTY_DIR.

    Download wheels with the --wheels option for the ``--python-version`` PYVER(s)
    and ``--operating_system`` OS(s) combinations defaulting to all supported combinations.

    Download sdists tarballs with the --sdists option.

    Generate or Download .ABOUT, .LICENSE and .NOTICE files for all the wheels and sources fetched.

    Download wheels and sdists the provided PyPI simple --index-url INDEX(s) URLs.
    """
    print(f"COLLECTING REQUIRED NAMES & VERSIONS FROM {dest_dir}")
    existing_packages_by_nv = {
        (package.name, package.version): package
        for package in utils_thirdparty.get_local_packages(directory=dest_dir)
    }

    required_name_versions = set(existing_packages_by_nv.keys())

    for req_file in requirements_files:
        nvs = utils_requirements.load_requirements(
            requirements_file=req_file,
            with_unpinned=latest_version,
        )
        required_name_versions.update(nvs)

    for specifier in specifiers:
        nv = utils_requirements.get_name_version(
            requirement=specifier,
            with_unpinned=latest_version,
        )
        required_name_versions.add(nv)

    if not required_name_versions:
        print("Error: no requirements requested.")
        sys.exit(1)

    if not os.listdir(dest_dir) and not (wheels or sdists):
        print("Error: one or both of --wheels  and --sdists is required.")
        sys.exit(1)

    if latest_version:
        latest_name_versions = set()
        names = set(name for name, _version in sorted(required_name_versions))
        for name in sorted(names):
            latests = utils_thirdparty.PypiPackage.sorted(
                utils_thirdparty.get_package_versions(
                    name=name, version=None, index_urls=index_urls
                )
            )
            if not latests:
                print(f"No distribution found for: {name}")
            continue
            latest = latests[-1]
            latest_name_versions.add((latest.name, latest.version))
        required_name_versions = latest_name_versions

    if TRACE:
        print("required_name_versions:", required_name_versions)

    if wheels:
        # create the environments matrix we need for wheels
        evts = itertools.product(python_versions, operating_systems)
        environments = [utils_thirdparty.Environment.from_pyver_and_os(pyv, os) for pyv, os in evts]

    wheels_not_found = {}
    sdists_not_found = {}
    # iterate over requirements, one at a time
    for name, version in sorted(required_name_versions):
        nv = name, version
        existing_package = existing_packages_by_nv.get(nv)
        if wheels:
            for environment in environments:
                if existing_package:
                    existing_wheels = list(
                        existing_package.get_supported_wheels(environment=environment)
                    )
                else:
                    existing_wheels = None

                if existing_wheels:
                    if TRACE:
                        print(
                            f"====> Wheels already available: {name}=={version} on: {environment}: {existing_package.wheels!r}"
                        )
                    if all(w.is_pure() for w in existing_wheels):
                        break
                    else:
                        continue

                if TRACE:
                    print(f"Fetching wheel for: {name}=={version} on: {environment}")

                try:
                    (
                        fetched_wheel_filenames,
                        existing_wheel_filenames,
                    ) = utils_thirdparty.download_wheel(
                        name=name,
                        version=version,
                        environment=environment,
                        dest_dir=dest_dir,
                        index_urls=index_urls,
                    )
                    if TRACE:
                        if existing_wheel_filenames:
                            print(
                                f"    ====> Wheels already available: {name}=={version} on: {environment}"
                            )
                            for whl in existing_wheel_filenames:
                                print(f"        {whl}")
                        if fetched_wheel_filenames:
                            print(f"    ====> Wheels fetched: {name}=={version} on: {environment}")
                            for whl in fetched_wheel_filenames:
                                print(f"        {whl}")

                    fwfns = fetched_wheel_filenames + existing_wheel_filenames

                    if all(utils_thirdparty.Wheel.from_filename(f).is_pure() for f in fwfns):
                        break

                except utils_thirdparty.DistributionNotFound as e:
                    wheels_not_found[f"{name}=={version}"] = str(e)

        if sdists:
            if existing_package and existing_package.sdist:
                if TRACE:
                    print(
                        f"  ====> Sdist already available: {name}=={version}: {existing_package.sdist!r}"
                    )
                continue

            if TRACE:
                print(f"  Fetching sdist for: {name}=={version}")

            try:
                fetched = utils_thirdparty.download_sdist(
                    name=name,
                    version=version,
                    dest_dir=dest_dir,
                    index_urls=index_urls,
                )

                if TRACE:
                    if not fetched:
                        print(
                            f"    ====> Sdist already available: {name}=={version} on: {environment}"
                        )
                    else:
                        print(
                            f"    ====> Sdist fetched: {fetched} for {name}=={version} on: {environment}"
                        )

            except utils_thirdparty.DistributionNotFound as e:
                sdists_not_found[f"{name}=={version}"] = str(e)

    if wheels and wheels_not_found:
        print(f"==> MISSING WHEELS")
        for wh in wheels_not_found:
            print(f"  {wh}")

    if sdists and sdists_not_found:
        print(f"==> MISSING SDISTS")
        for sd in sdists_not_found:
            print(f"  {sd}")

    print(f"==> FETCHING OR CREATING ABOUT AND LICENSE FILES")
    utils_thirdparty.fetch_abouts_and_licenses(dest_dir=dest_dir)
    utils_thirdparty.clean_about_files(dest_dir=dest_dir)

    # check for problems
    print(f"==> CHECK FOR PROBLEMS")
    utils_thirdparty.find_problems(
        dest_dir=dest_dir,
        report_missing_sources=sdists,
        report_missing_wheels=wheels,
    )


if __name__ == "__main__":
    fetch_thirdparty()
