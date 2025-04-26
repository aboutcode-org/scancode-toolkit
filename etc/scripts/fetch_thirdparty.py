#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import itertools
import os
import sys
from collections import defaultdict

import click

import utils_thirdparty
import utils_requirements

TRACE = False
TRACE_DEEP = False


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
    type=click.Path(exists=True, readable=True,
                    path_type=str, file_okay=False),
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
    default=utils_thirdparty.PYPI_INDEX_URLS,
    show_default=True,
    multiple=True,
    help="PyPI index URL(s) to use for wheels and sources, in order of preferences.",
)
@click.option(
    "--use-cached-index",
    is_flag=True,
    help="Use on disk cached PyPI indexes list of packages and versions and do not refetch if present.",
)
@click.option(
    "--sdist-only",
    "sdist_only",
    type=str,
    metavar="SDIST",
    default=tuple(),
    show_default=False,
    multiple=True,
    help="Package name(s) that come only in sdist format (no wheels). "
         "The command will not fail and exit if no wheel exists for these names",
)
@click.option(
    "--wheel-only",
    "wheel_only",
    type=str,
    metavar="WHEEL",
    default=tuple(),
    show_default=False,
    multiple=True,
    help="Package name(s) that come only in wheel format (no sdist). "
         "The command will not fail and exit if no sdist exists for these names",
)
@click.option(
    "--no-dist",
    "no_dist",
    type=str,
    metavar="DIST",
    default=tuple(),
    show_default=False,
    multiple=True,
    help="Package name(s) that do not come either in wheel or sdist format. "
         "The command will not fail and exit if no distribution exists for these names",
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
    use_cached_index,
    sdist_only,
    wheel_only,
    no_dist,
):
    """
    Download to --dest THIRDPARTY_DIR the PyPI wheels, source distributions,
    and their ABOUT metadata, license and notices files.

    Download the PyPI packages listed in the combination of:
    - the pip requirements --requirements REQUIREMENT-FILE(s),
    - the pip name==version --specifier SPECIFIER(s)
    - any pre-existing wheels or sdsists found in --dest-dir THIRDPARTY_DIR.

    Download wheels with the --wheels option for the ``--python-version``
    PYVER(s) and ``--operating_system`` OS(s) combinations defaulting to all
    supported combinations.

    Download sdists tarballs with the --sdists option.

    Generate or Download .ABOUT, .LICENSE and .NOTICE files for all the wheels
    and sources fetched.

    Download from the provided PyPI simple --index-url INDEX(s) URLs.
    """
    if not (wheels or sdists):
        print("Error: one or both of --wheels  and --sdists is required.")
        sys.exit(1)

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
        nv = utils_requirements.get_required_name_version(
            requirement=specifier,
            with_unpinned=latest_version,
        )
        required_name_versions.add(nv)

    if latest_version:
        names = set(name for name, _version in sorted(required_name_versions))
        required_name_versions = {(n, None) for n in names}

    if not required_name_versions:
        print("Error: no requirements requested.")
        sys.exit(1)

    if TRACE_DEEP:
        print("required_name_versions:")
        for n, v in required_name_versions:
            print(f"    {n} @ {v}")

    # create the environments matrix we need for wheels
    environments = None
    if wheels:
        evts = itertools.product(python_versions, operating_systems)
        environments = [utils_thirdparty.Environment.from_pyver_and_os(
            pyv, os) for pyv, os in evts]

    # Collect PyPI repos
    repos = []
    for index_url in index_urls:
        index_url = index_url.strip("/")
        existing = utils_thirdparty.DEFAULT_PYPI_REPOS_BY_URL.get(index_url)
        if existing:
            existing.use_cached_index = use_cached_index
            repos.append(existing)
        else:
            repo = utils_thirdparty.PypiSimpleRepository(
                index_url=index_url,
                use_cached_index=use_cached_index,
            )
            repos.append(repo)

    wheels_or_sdist_not_found = defaultdict(list)

    for name, version in sorted(required_name_versions):
        nv = name, version
        print(f"Processing: {name} @ {version}")
        if wheels:
            for environment in environments:

                if TRACE:
                    print(f"  ==> Fetching wheel for envt: {environment}")

                fetched = utils_thirdparty.download_wheel(
                    name=name,
                    version=version,
                    environment=environment,
                    dest_dir=dest_dir,
                    repos=repos,
                )
                if not fetched:
                    wheels_or_sdist_not_found[f"{name}=={version}"].append(
                        environment)
                    if TRACE:
                        print(f"      NOT FOUND")

        if (sdists or
            (f"{name}=={version}" in wheels_or_sdist_not_found and name in sdist_only)
            ):
            if TRACE:
                print(f"  ==> Fetching sdist: {name}=={version}")

            fetched = utils_thirdparty.download_sdist(
                name=name,
                version=version,
                dest_dir=dest_dir,
                repos=repos,
            )
            if not fetched:
                wheels_or_sdist_not_found[f"{name}=={version}"].append("sdist")
                if TRACE:
                    print(f"      NOT FOUND")

    mia = []
    for nv, dists in wheels_or_sdist_not_found.items():
        name, _, version = nv.partition("==")
        if name in no_dist:
            continue
        sdist_missing = sdists and "sdist" in dists and not name in wheel_only
        if sdist_missing:
            mia.append(f"SDist missing: {nv} {dists}")
        wheels_missing = wheels and any(
            d for d in dists if d != "sdist") and not name in sdist_only
        if wheels_missing:
            mia.append(f"Wheels missing: {nv} {dists}")

    if mia:
        for m in mia:
            print(m)
        raise Exception(mia)

    print(f"==> FETCHING OR CREATING ABOUT AND LICENSE FILES")
    utils_thirdparty.fetch_abouts_and_licenses(
        dest_dir=dest_dir, use_cached_index=use_cached_index)
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
