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

from collections import defaultdict
import itertools
import operator
import os
import re
import subprocess
import time

import attr
import packaging_dists
import packaging
import pip_compatibility_tags
import pip_wheel
import requests
import saneyaml

from commoncode import fileutils
from packaging.utils import canonicalize_name
from packaging.utils import canonicalize_version
from requirements_utils import load_requirements

"""
Utilities to build scancode releases and manage Python thirparty libraries.

- create and update locked/pinned requirement files (optionally with hashes)

- build individual wheels for all supported OSes and Python combos and upload
  them all to a PyPI-like repository.

- use a public alternative PyPI-like repository to keep all dependent packages
  as pre-built wheels for each supported Python/OS combo, their source code and
  ABOUT and LICENSE files.

- build application release archives as plaform-specific tarballs with bundled
  pre-built dependencies.

"""

# Supported environments
PYTHON_VERSIONS = '36', '37', '38', '39'

PLATFORMS_BY_OS = {
    'linux': [
        'linux_x86_64',
        'manylinux1_x86_64',
        'manylinux2014_x86_64',
        'manylinux2010_x86_64',
    ],
    'macosx': [
        'macosx_10_6_intel', 'macosx_10_6_intel_x86_64', 'macosx_10_6_x86_64',
        'macosx_10_9_intel', 'macosx_10_9_intel_x86_64', 'macosx_10_9_x86_64',
        'macosx_10_10_intel', 'macosx_10_10_intel_x86_64', 'macosx_10_10_x86_64',
        'macosx_10_11_intel', 'macosx_10_11_intel_x86_64', 'macosx_10_11_x86_64',
        'macosx_10_12_intel', 'macosx_10_12_intel_x86_64', 'macosx_10_12_x86_64',
        'macosx_10_13_intel', 'macosx_10_13_intel_x86_64', 'macosx_10_13_x86_64',
    ],
    'windows': [
        'win_amd64',
    ],
}

THIRDPARTY_DIR = 'thirdparty'

REMOTE_BASE_URL = 'https://github.com'
REMOTE_LINKS_URL = 'https://github.com/nexB/thirdparty-packages/releases/pypi'
REMOTE_HREF_PREFIX = '/nexB/thirdparty-packages/releases/download/'
REMOTE_BASE_DOWNLOAD_URL = 'https://github.com/nexB/thirdparty-packages/releases/download/pypi'

EXTENSIONS_APP = '.pyz',
EXTENSIONS_INSTALLABLE = '.whl', '.tar.gz', '.tar.bz2', '.zip', '.tar.xz',
EXTENSIONS_ABOUT = '.ABOUT', '.LICENSE', '.NOTICE',
EXTENSIONS = EXTENSIONS_INSTALLABLE + EXTENSIONS_ABOUT + EXTENSIONS_APP

PYPI_SIMPLE_URL = 'https://pypi.org/simple'

LICENSEDB_API_URL = 'https://scancode-licensedb.aboutcode.org'

################################################################################
#
# main entry point
#
################################################################################


def fetch_wheels(environment=None, requirement='requirements.txt', dest_dir=THIRDPARTY_DIR):
    """
    Download all of the wheel of packages listed in the `requirement`
    requirements file into `dest_dir` directory.

    Only get wheels for the `environment` Enviromnent constraints. If the
    provided `environment` is None then the current Python interpreter
    environment is used implicitly.
    Use direct downloads from our remote repo exclusively.
    Yield tuples of (Package, error) where is None on success
    """
    missed = []
    rrp = list(get_required_remote_packages(requirement))
    for name, version, package in rrp:
        if not package:
            missed.append((name, version,))
            yield None, f'Missing package in remote repo: {name}=={version}'

        else:
            fetched = package.fetch_wheel(environment=environment, dest_dir=dest_dir)
            error = f'Failed to fetch' if not fetched else None
            yield package, error

    if missed:
        rr = get_remote_repo()
        print()
        print(f'===============> Missed some packages')
        for n, v in missed:
            print(f'Missed package in remote repo: {n}=={v} from:')
            for pv in rr.get_versions(n):
                print(pv)


def fetch_sources(requirement='requirements.txt', dest_dir=THIRDPARTY_DIR,):
    """
    Download all of the dependent package sources listed in the `requirement`
    requirements file into `dest_dir` directory.

    Use direct downloads to achieve this (not pip download). Use only the
    packages found in our remote repo. Yield tuples of
    (Package, error message) for each package where error message will empty on
    success
    """
    missed = []
    rrp = list(get_required_remote_packages(requirement))
    for name, version, package in rrp:
        if not package:
            missed.append((name, version,))
            yield None, f'Missing package in remote repo: {name}=={version}'

        elif not package.sdist:
            yield package, f'Missing sdist in links'

        else:
            fetched = package.fetch_sdist(dest_dir=dest_dir)
            error = f'Failed to fetch' if not fetched else None
            yield package, error


def fetch_venv_abouts_and_licenses(dest_dir=THIRDPARTY_DIR):
    """
    Download to `est_dir` a virtualenv.pyz app, and all .ABOUT, license and
    notice files for all packages in `dest_dir`
    """
    remote_repo = get_remote_repo()
    paths_or_urls = remote_repo.get_links()

    fetch_and_save_file_name_from_paths_or_urls(
        file_name='virtualenv.pyz',
        dest_dir=dest_dir,
        paths_or_urls=paths_or_urls,
        as_text=False,
    )

    fetch_abouts(dest_dir=dest_dir, paths_or_urls=paths_or_urls)
    fetch_license_texts_and_notices(dest_dir=dest_dir, paths_or_urls=paths_or_urls)


def fetch_package_wheel(name, version, environment, dest_dir=THIRDPARTY_DIR):
    """
    Fetch the binary wheel for package `name` and `version` and save in
    `dest_dir`. Use the provided `environment` Environment to determine which
    specific wheel to fetch.

    Return the fetched wheel file name on success or None if it was not fetched.
    Trying fetching from our own remote repo, then from PyPI.
    """
    wheel_file = None
    remote_package = get_remote_package(name, version)
    if remote_package:
        wheel_file = remote_package.fetch_wheel(environment, dest_dir)
    if not wheel_file:
        pypi_package = get_pypi_package(name, version)
        if pypi_package:
            wheel_file = pypi_package.fetch_wheel(environment, dest_dir)
    return wheel_file

################################################################################
#
# Core models
#
################################################################################


@attr.attributes
class Package:
    """
    A Python package with its "distributions", e.g. wheels and source
    distribution , ABOUT files and licenses or notices.
    """
    name = attr.ib(
        type=str,
        metadata=dict(help='Python package name, lowercase and normalized.'),
    )

    version = attr.ib(
        type=str,
        metadata=dict(help='Python package version.'),
    )

    sdist = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='packaging_dists.Sdist depicting a source distribution}'),
    )

    wheels = attr.ib(
        repr=False,
        type=list,
        default=attr.Factory(list),
        metadata=dict(help='List of packaging_dists.Wheel'),
    )

    def get_supported_wheels(self, environment):
        """
        Yield all wheels of this Package supported and compatible with the
        Environment `environment`.
        """
        envt_tags = set(pip_compatibility_tags.get_supported(
            version=environment and environment.python_version or None,
            platforms=environment and environment.platforms or None,
            impl=environment and environment.implementation or None,
            abis=environment and [environment.abi] or None,
        ))

        for wheel in self.wheels:
            pwhl = pip_wheel.Wheel(wheel.file_name)
            if pwhl.supported(envt_tags):
                yield wheel

    @classmethod
    def package_from_dists(cls, dists):
        """
        Return a new Package built from an iterable of Distribution objects all
        for the same package name and version.
        For example:
        >>> import packaging_dists as pd
        >>> from packaging.version import Version
        >>> w1 = pd.Wheel(project='bitarray', version=Version('0.8.1'), build='',
        ...        python='cp36', abi='cp36m', platform='linux_x86_64')
        >>> w2 = pd.Wheel(project='bitarray', version=Version('0.8.1'), build='',
        ...         python='cp36', abi='cp36m', platform='macosx_10_9_x86_64.macosx_10_10_x86_64')
        >>> sd = pd.Sdist(project='bitarray', version=Version('0.8.1'))
        >>> package = Package.package_from_dists(dists=[w1, w2, sd])
        >>> assert package.name == 'bitarray'
        >>> assert package.version == '0.8.1'
        >>> assert package.sdist == sd
        >>> assert package.wheels == [w1, w2]
        """
        dists = list(dists)
        if not dists:
            return
        base = dists[0]
        name = base.project
        version = str(base.version)
        name, version = canonicalize(name, version)
        package = Package(name=name, version=version)
        for dist in dists:
            dname, dversion = canonicalize(dist.project, str(dist.version))
            if dname != name or dversion != version:
                raise Exception(
                    'Inconsistent set of distributions: '
                    'must use all the same name and version.')
            if isinstance(dist, packaging_dists.Sdist):
                package.sdist = dist
            elif isinstance(dist, packaging_dists.Wheel):
                package.wheels.append(dist)
            else:
                raise Exception(f'Unknown distribution type: {dist}')
        return package

    @classmethod
    def packages_from_one_path_or_url(cls, path_or_url):
        """
        Yield Packages built from a files found in at directory path or URL to
        an HTML page (that will be fetched).
        """
        return cls.packages_from_many_paths_or_urls(get_paths_or_urls(path_or_url))

    @classmethod
    def packages_from_many_paths_or_urls(cls, paths_or_urls):
        """
        Yield Packages built from a list of of paths or URLs.
        """
        dists = cls.get_dists(paths_or_urls)
        key = operator.attrgetter('project', 'version')
        dists = sorted(dists, key=key)
        for _projver, package_dists in itertools.groupby(dists, key=key):
            yield Package.package_from_dists(package_dists)

    @classmethod
    def get_versions_from_path_or_url(cls, name, path_or_url):
        """
        Return a subset list from a list of Packages version at `path_or_url`
        that match Package `name`.
        """
        name = name and canonicalize_name(name)
        packages = cls.packages_from_one_path_or_url(path_or_url)
        return cls.get_versions(name, packages)

    @classmethod
    def get_versions(cls, name, packages):
        """
        Return a subset list of package versions from a list of `packages` that
        match Package `name`.
        The list is sorted by version from oldest to most recent.
        """
        name = name and canonicalize_name(name)
        versions = [p for p in packages if p.name == name]
        return cls.sort_by_version(versions)

    @classmethod
    def sort_by_version(cls, packages):
        key = lambda p: packaging.version.parse(p.version)
        return sorted(packages, key=key)

    @classmethod
    def sort_by_name_version(cls, packages):
        key = lambda p: (p.name, packaging.version.parse(p.version))
        return sorted(packages, key=key)

    @classmethod
    def get_latest_version(cls, name, packages):
        """
        Return the latest version of Package `name` from a list of `packages`.
        """
        name = name and canonicalize_name(name)
        versions = cls.get_versions(name, packages)
        return versions[-1]

    @classmethod
    def get_outdated_versions(cls, name, packages):
        """
        Return all versions except the latest version of Package `name` from a
        list of `packages`.
        """
        name = name and canonicalize_name(name)
        versions = cls.get_versions(name, packages)
        return versions[:-1]

    @classmethod
    def get_name_version(cls, name, version, packages):
        """
        Return the Package with `name` and `version` from a list of `packages`
        or None if it is not found.
        If `version` is None, return the latest version found.
        """
        name, version = canonicalize(name, version)
        if version is None:
            return cls.get_latest_version(name, packages)

        nvs = [p for p in cls.get_versions(name, packages) if p.version == version]
        if not nvs:
            return
        if len(nvs) == 1:
            return nvs[0]
        raise Exception(f'More than one Package with {name}=={version}')

    def fetch_wheel(self, environment=None, dest_dir=THIRDPARTY_DIR):
        """
        Download the `package` Package binary wheel matching the `environment`
        Enviromnent constraints into `dest_dir` directory.

        Return the wheel file name if was fetched, False otherwise.

        If the provided `environment` is None then the current Python interpreter
        environment is used implicitly.
        """
        fetched_wheel_file_name = False
        for wheel in self.get_supported_wheels(environment):
            print('Fetching wheel for package:', self.name, self.version, end='')
            fetch_and_save_path_or_url(
                file_name=wheel.file_name,
                path_or_url=wheel.path_or_url,
                dest_dir=dest_dir,
                as_text=False,
            )
            print(' --> file:', wheel.file_name)
            fetched_wheel_file_name = wheel.file_name
            # TODO: what if there is more than one?
            break

        if not fetched_wheel_file_name:
            msg = f'Missing wheels for: {self.name}=={self.version} and envt: {environment}'
            print(msg)

        return fetched_wheel_file_name

    def fetch_sdist(self, dest_dir=THIRDPARTY_DIR):
        """
        Download the source distribution into `dest_dir` directory.
        Return a True if it was fetched. False otherwise.
        """
        if self.sdist and self.sdist.file_name:
            print('Fetching source for package:', self.name, self.version, end='')
            fetch_and_save_path_or_url(
                file_name=self.sdist.file_name,
                dest_dir=dest_dir,
                path_or_url=self.sdist.path_or_url,
                as_text=False,
            )
            print(' --> file:', self.sdist.file_name)
            return self.sdist.file_name
        else:
            print(f'Missing sdist for: {self.name}=={self.version}')
            return False

    def delete_files(self, dest_dir=THIRDPARTY_DIR):
        """
        Delete all Package files from `dest_dir` including wheels, sdist and
        their ABOUT files. Note that we do not delete licenses since they can be
        shared by several packages: therefore this would be done elsewhere in a
        function that is aware of all used licenses.
        """
        for to_delete in self.wheels + [self.dist]:
            if not to_delete:
                continue
            for deletable in [to_delete, f'{to_delete}.ABOUT', f'{to_delete}.NOTICE']:
                target = os.path.join(dest_dir, deletable)
                if os.path.exists(target):
                    fileutils.delete(target)

    @classmethod
    def get_dists(cls, paths_or_urls):
        """
        Return a list of packaging_dists.Distribution given a list of
        `paths_or_urls` to wheels or source distributions.

        Each Distribution receives two extra attributes:
            - the path_or_url it was created from
            - its file_name

        For example:
        >>> import packaging_dists as pd
        >>> from packaging.version import Version
        >>> paths_or_urls ='''
        ...     bitarray-0.8.1-cp36-cp36m-linux_x86_64.whl
        ...     bitarray-0.8.1-cp36-cp36m-macosx_10_9_x86_64.macosx_10_10_x86_64.whl
        ...     bitarray-0.8.1-cp36-cp36m-win_amd64.whl
        ...     bitarray-0.8.1.tar.gz
        ...     bitarray-0.8.1.tar.gz.ABOUT bit.LICENSE'''.split()
        >>> result = list(Package.get_dists(paths_or_urls))
        >>> expected = [
        ...     pd.Wheel(project='bitarray', version=Version('0.8.1'), build='',
        ...        python='cp36', abi='cp36m', platform='linux_x86_64'),
        ...     pd.Wheel(project='bitarray', version=Version('0.8.1'), build='',
        ...         python='cp36', abi='cp36m', platform='macosx_10_9_x86_64.macosx_10_10_x86_64'),
        ...     pd.Wheel(project='bitarray', version=Version('0.8.1'), build='',
        ...         python='cp36', abi='cp36m', platform='win_amd64'),
        ...     pd.Sdist(project='bitarray', version=Version('0.8.1'))
        ... ]
        >>> assert expected == result
        """
        installable = [f for f in paths_or_urls if f .endswith(EXTENSIONS_INSTALLABLE)]
        for path_or_url in installable:
            file_name = get_file_name(path_or_url)
            dist = None
            try:
                dist = packaging_dists.parse(file_name)
            except packaging_dists.InvalidDistribution as e:
                print(f'Skipping invalid distribution with file_name: {path_or_url}')
                print(e)
                continue

            if dist:
                # always add these attributes
                dist.path_or_url = path_or_url
                dist.file_name = file_name
                yield dist

    def get_distributions(self):
        """
        Yield all distributions available for this Package
        """
        if self.sdist:
            yield self.sdist
        for wheel in self.wheels:
            yield wheel

    def get_url_for_file_name(self, file_name):
        """
        Return the URL for this file_name or None.
        """
        for dist in self.get_distributions():
            if dist.file_name == file_name:
                return dist.path_or_url


def get_best_download_url(file_name):
    """
    Given a package file `file_name` return the best download URL where best
    means that PyPI is better and our remote urls are second.
    """
    dist = packaging_dists.parse(file_name)
    name = dist.project
    version = str(dist.version)
    name, version = canonicalize(name, version)

    pypi_package = get_pypi_package(name=name, version=version)
    if pypi_package:
        pypi_url = pypi_package.get_url_for_file_name(file_name)
        if pypi_url:
            return pypi_url

    remote_package = get_remote_package(name=name, version=version)
    if remote_package:
        remote_url = remote_package.get_url_for_file_name(file_name)
        if remote_url:
            return remote_url


@attr.attributes(auto_attribs=True)
class Environment:
    """
    An Environment describes a target installation environment with its
    supported Python version, ABI, platform, implementation and related
    attributes. We can use these to pass as `pip download` options and force
    fetching only the subset of packages that match these Environment
    constraints as opposed to the current running Python constraints.
    """
    python_version: str
    implementation: str
    abi: str
    platforms: list

    @classmethod
    def from_pyos(cls, python_version, operating_system):
        return cls(
            python_version=python_version,
            implementation='cp',
            abi=f'cp{python_version}m',
            platforms=PLATFORMS_BY_OS[operating_system],
        )

    def pip_cli_options(self):
        """
        Return a list of pip command line options for this environment.
        """
        options = [
            '--python-version', self.python_version,
            '--implementation', self.implementation,
            '--abi', self.abi,
        ]
        for platform in self.platforms:
            options.extend(['--platform', platform])
        return options

################################################################################
#
# PyPI repo and link index for package wheels and sources
#
################################################################################


@attr.attributes
class Repository:
    """
    A PyPI or links Repository of Python packages: wheels, sdist, ABOUT, etc.
    """

    packages_by_name = attr.ib(
        type=dict,
        default=attr.Factory(lambda: defaultdict(list)),
        metadata=dict(help=
            'Mapping of {package name: [package objects]} available in this repo'),
    )

    packages_by_name_version = attr.ib(
        type=dict,
        default=attr.Factory(dict),
        metadata=dict(help=
            'Mapping of {(name, version): package object} available in this repo'),
    )

    def get_links(self, *args, **kwargs):
        raise NotImplementedError()

    def get_versions(self, name):
        """
        Return a list of all available Package version for this package name.
        The list may be empty.
        """
        raise NotImplementedError()

    def get_package(self, name, version):
        """
        Return the Package with name and version or None.
        """
        raise NotImplementedError()

    def get_latest_version(self, name):
        """
        Return the latest Package version for this package name or None.
        """
        raise NotImplementedError()


@attr.attributes
class LinksRepository(Repository):
    """
    Represents a simple links repository which is either a local directory with
    Python wheels and sdist or a remote URL to an HTML with links to these.
    (e.g. suitable for use with pip --find-links).
    """
    path_or_url = attr.ib(
        type=str,
        default='',
        metadata=dict(help='Package directory path or URL'),
    )

    links = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help='List of links available in this repo'),
    )

    def __attrs_post_init__(self):
        if not self.links:
            self.links = get_paths_or_urls(links_url=self.path_or_url)
        if not self.packages_by_name:
            for p in Package.packages_from_many_paths_or_urls(paths_or_urls=self.links):
                name, version = canonicalize(p.name, p.version)
                self.packages_by_name[name].append(p)
                self.packages_by_name_version[(name, version)] = p

    def get_links(self, *args, **kwargs):
        return self.links or []

    def get_versions(self, name):
        name = name and canonicalize_name(name)
        return self.packages_by_name.get(name, [])

    def get_latest_version(self, name):
        name = name and canonicalize_name(name)
        return Package.get_latest_version(name, self.get_versions(name))

    def get_package(self, name, version):
        name, version = canonicalize(name, version)
        if version is None:
            return self.get_latest_version(name)

        return Package.get_name_version(name, version, self.get_versions(name))


@attr.attributes
class PypiRepository(Repository):
    """
    Represents the public PyPI simple index.
    It is populated lazily based on requested packages names
    """
    simple_url = attr.ib(
        type=str,
        default=PYPI_SIMPLE_URL,
        metadata=dict(help='Base PyPI simple URL for this index.'),
    )

    links_by_name = attr.ib(
        type=dict,
        default=attr.Factory(lambda: defaultdict(list)),
        metadata=dict(help='Mapping of {package name: [links]} available in this repo'),
    )

    def _fetch_links(self, name):
        name = name and canonicalize_name(name)
        return find_pypi_links(name=name, simple_url=self.simple_url)

    def _populate_links_and_packages(self, name):
        name = name and canonicalize_name(name)
        if name in self.links_by_name:
            return

        links = self._fetch_links(name)
        self.links_by_name[name] = links

        packages = list(Package.packages_from_many_paths_or_urls(paths_or_urls=links))
        self.packages_by_name[name] = packages

        for p in packages:
            name, version = canonicalize(p.name, p.version)
            self.packages_by_name_version[(name, version)] = p

    def get_links(self, name, *args, **kwargs):
        name = name and canonicalize_name(name)
        self._populate_links_and_packages(name)
        return  self.links_by_name.get(name, [])

    def get_versions(self, name):
        name = name and canonicalize_name(name)
        self._populate_links_and_packages(name)
        return self.packages_by_name.get(name, [])

    def get_latest_version(self, name):
        name = name and canonicalize_name(name)
        return Package.get_latest_version(name, self.get_versions(name))

    def get_package(self, name, version):
        name, version = canonicalize(name, version)
        if version is None:
            return self.get_latest_version(name)

        return Package.get_name_version(name, version, self.get_versions(name))

################################################################################
# Globals for remote repos to be lazily created and cached on first use for the
# life of the session together with some convenience functions.
################################################################################


_REMOTE_REPO = None


def get_remote_repo(remote_links_url=REMOTE_LINKS_URL):
    global _REMOTE_REPO
    if not _REMOTE_REPO:
        _REMOTE_REPO = LinksRepository(path_or_url=remote_links_url)
    return _REMOTE_REPO


_PYPI_REPO = None


def get_pypi_repo(pypi_simple_url=PYPI_SIMPLE_URL):
    global _PYPI_REPO
    if not _PYPI_REPO:
        _PYPI_REPO = PypiRepository(simple_url=pypi_simple_url)
    return _PYPI_REPO


def get_local_packages(directory=THIRDPARTY_DIR):
    """
    Return the list of all Package objects built from a local directory. Return
    an empty list if the package cannot be found.
    """
    return list(Package.packages_from_one_path_or_url(path_or_url=directory))


def get_local_package(name, version, directory=THIRDPARTY_DIR):
    """
    Return the list of all Package objects built from a local directory. Return
    an empty list if the package cannot be found.
    """
    name, version = canonicalize(name, version)
    packages = get_local_packages(directory)
    return Package.get_name_version(name, version, packages)


def get_remote_package(name, version, remote_links_url=REMOTE_LINKS_URL):
    name, version = canonicalize(name, version)
    return get_remote_repo(remote_links_url).get_package(name, version)


def get_pypi_package(name, version, pypi_simple_url=PYPI_SIMPLE_URL):
    name, version = canonicalize(name, version)
    return get_pypi_repo(pypi_simple_url).get_package(name, version)

################################################################################
#
# Basic file and URL-based operations using a persistent file-based Cache
#
################################################################################


@attr.attributes
class Cache:
    """
    A simple file-based cache based only on a file_name presence.
    This is used to avoid impolite fetching from remote locations.
    """

    directory = attr.ib(type=str, default='.cache/thirdparty')

    def __attrs_post_init__(self):
        os.makedirs(self.directory, exist_ok=True)

    def clear(self):
        import shutil
        shutil.rmtree(self.directory)

    def get(self, path_or_url, as_text=True):
        """
        Get a file from a `path_or_url` through the cache.
        `path_or_url` can be a path or a URL to a file.
        """
        file_name = get_file_name(path_or_url)
        cached = os.path.join(self.directory, file_name)

        if not os.path.exists(cached):
            print(f'Fetching {path_or_url}')
            content = get_file_content(path_or_url=path_or_url, as_text=as_text)
            wmode = 'w' if as_text else 'wb'
            with open(cached, wmode) as fo:
                fo.write(content)
            return content
        else:
            return get_local_file_content(path=cached, as_text=as_text)

    def put(self, file_name, content):
        """
        Put in the cache the `content` of `file_name`.
        """
        cached = os.path.join(self.directory, file_name)
        wmode = 'wb' if isinstance(content, bytes) else 'w'
        with open(cached, wmode) as fo:
            fo.write(content)


def get_file_name(path_or_url):
    return os.path.basename(path_or_url.strip('/'))


def get_file_content(path_or_url, as_text=True):
    """
    Fetch and return the content at `path_or_url` from either a local path or a
    remote URL. Return the content as bytes is `as_text` is False.
    """
    if path_or_url.startswith('file://'):
        return get_local_file_content(path=path_or_url, as_text=as_text)
    elif path_or_url.startswith('https://'):
        return get_remote_file_content(url=path_or_url, as_text=as_text)
    else:
        raise Exception(f'Unsupported URL scheme: {path_or_url}')


def get_local_file_content(path, as_text=True):
    """
    Return the content at `url` as text. Return the content as bytes is
    `as_text` is False.
    """
    if path.startswith('file://'):
        path = path[7:]

    mode = 'r' if as_text else 'rb'
    with open(path, mode) as fo:
        return fo.read()


def get_remote_file_content(url, as_text=True, _delay=0):
    """
    Fetch and return the content at `url` as text. Return the content as bytes
    is `as_text` is False. Retries multiple times to fetch if there is a HTTP
    429 throttling response and this with an increasing delay.
    """
    time.sleep(_delay)
    response = requests.get(url)
    status = response.status_code
    if status != requests.codes.ok:  # NOQA
        if status == 429 and _delay < 20:
            # too many requests: start some exponential delay
            increased_delay = (_delay * 2) or 1
            return get_remote_file_content(url, as_text=True, _delay=increased_delay)
        else:
            raise Exception('Failed HTTP request for %(url)r: %(status)r' % locals())
    return response.text if as_text else response.content


def fetch_and_save_file_name_from_paths_or_urls(
    file_name,
    paths_or_urls,
    dest_dir=THIRDPARTY_DIR,
    as_text=True,
):
    """
    Return the content from fetching the `file_name` file name found in the
    `paths_or_urls` list of URLs or paths and save to `dest_dir`. Raise an
    Exception on errors. Treats the content as text if `as_text` is True
    otherwise as binary.
    """
    path_or_url = get_link_for_file_name(
        file_name=file_name,
        paths_or_urls=paths_or_urls,
    )

    return fetch_and_save_path_or_url(
        file_name=file_name,
        dest_dir=dest_dir,
        path_or_url=path_or_url,
        as_text=as_text,
    )


def fetch_path_or_url_through_cache(path_or_url, as_text=True, cache=Cache()):
    """
    Return the content from fetching at path or URL. Raise an Exception on
    errors. Treats the content as text if as_text is True otherwise as treat as
    binary. Use the provided file cache. This is the main entry for using the
    cache.

    Note: the `cache` argument is a global, though it does not really matter
    since it does not hold any state which is only kept on disk.
    """
    return cache.get(path_or_url=path_or_url, as_text=as_text)


def fetch_and_save_path_or_url(file_name, dest_dir, path_or_url, as_text=True):
    """
    Return the content from fetching the `file_name` file name at URL or path
    and save to `dest_dir`. Raise an Exception on errors. Treats the content as
    text if as_text is True otherwise as treat as binary.
    """
    content = fetch_path_or_url_through_cache(path_or_url, as_text)
    output = os.path.join(dest_dir, file_name)
    wmode = 'w' if as_text else 'wb'
    with open(output, wmode) as fo:
        fo.write(content)
    return content

################################################################################
#
# Sync and fix local thirdparty directory for various issues and gaps
#
################################################################################


def add_missing_sources(dest_dir=THIRDPARTY_DIR):
    """
    Given a thirdparty dir, fetch missing source distributions from our remote
    repo or PyPI.
    """
    not_found = []
    local_packages = get_local_packages(directory=dest_dir)
    remote_repo = get_remote_repo()
    pypi_repo = get_pypi_repo()

    for package in local_packages:
        if not package.sdist:
            print(f'Finding sources for: {package.name} {package.version}')
            pypi_package = pypi_repo.get_package(
                name=package.name, version=package.version)

            print(f' --> Try fetching sources from Pypi: {pypi_package}')
            if pypi_package and pypi_package.sdist:
                print(f' --> Fetching sources from Pypi: {pypi_package.sdist}')
                pypi_package.fetch_sdist(dest_dir=dest_dir)
            else:
                remote_package = remote_repo.get_package(
                    name=package.name, version=package.version)

                print(f' --> Try fetching sources from remote: {pypi_package}')
                if remote_package and remote_package.sdist:
                    print(f' --> Fetching sources from Remote: {remote_package.sdist}')
                    remote_package.fetch_sdist(dest_dir=dest_dir)

                else:
                    print(f' --> no sources found')
                    not_found.append((package.name, package.version,))

    if not_found:
        for name, version in not_found:
            print(f'sdist not found for {name}=={version}')


def add_missing_about_files(dest_dir=THIRDPARTY_DIR):
    """
    Given a thirdparty dir, add missing ANOUT files and licenses using best efforts:
    - fetch from our mote links
    - derive from existing packages of the same name and version that would have such ABOUT file
    - derive from existing packages of the same name and different version that would have such ABOUT file
    - attempt to make API calls to fetch package details and create ABOUT file
    - create a skinny ABOUT file as a last resort
    """
    # first get available ones from our remote repo
    remote_repo = get_remote_repo()
    paths_or_urls = remote_repo.get_links()
    fetch_abouts(dest_dir=dest_dir, paths_or_urls=paths_or_urls)

    # then derive or create
    existing_about_files = set(get_about_files(dest_dir))
    local_packages = get_local_packages(directory=dest_dir)

    pypi_repo = get_pypi_repo()

    for package in local_packages:
        pypi_packages = pypi_repo.get_versions(package.name)
        remote_package = remote_repo.get_package(package.name, package.version)
        for dist in package.get_distributions():
            file_name = dist.file_name
            download_url = get_best_download_url(
                file_name=file_name,
                pypi_packages=pypi_packages,
                remote_package=remote_package)

            about_file = f'{file_name}.ABOUT'
            if about_file not in existing_about_files:
                # TODO: also derive files from API calls
                about_file = create_or_derive_about_file(
                    remote_package=remote_package,
                    name=package.name,
                    version=package.version,
                    file_name=file_name,
                    download_url=download_url,
                    dest_dir=dest_dir,
                )
            if not about_file:
                print(f'Unable to derive/createfetch ABOUT file: {about_file}')


def fetch_missing_wheels(python_versions=(), operating_systems=(), dest_dir=THIRDPARTY_DIR):
    """
    Given a thirdparty dir build missing wheels for the provided
    python_versions and operating_systems lists.
    """

    not_found = []

    local_packages = get_local_packages(directory=dest_dir)
    combos = itertools.product(local_packages, python_versions, operating_systems)

    missing_to_fetch_or_build = []
    for local_package, python_version, operating_system in combos:
        pass

    for name, version, pyver, opsys in not_found:
        print(f'Wheel not found for {name}=={version} on python {pyver} and {opsys}')


def build_missing_wheels(python_versions=(), operating_systems=(), dest_dir=THIRDPARTY_DIR):
    """
    Given a thirdparty dir fetch missing wheels for the provided
    python_versions and operating_systems lists.
    """

    not_found = []

    local_packages = get_local_packages(directory=dest_dir)
    combos = itertools.product(local_packages, python_versions, operating_systems)

    for local_package, python_version, operating_system in combos:
        pass

    for name, version, pyver, opsys in not_found:
        print(f'Wheel not found for {name}=={version} on python {pyver} and {opsys}')


def add_missing_licenses_and_notices(dest_dir=THIRDPARTY_DIR):
    """
    Given a thirdparty dir that is assumed to be in sync with the
    REMOTE_FIND_LINKS repo, fetch missing license and notice files.
    """

    not_found = []

    # fetch any remote ones, then from licensedb
    paths_or_urls = get_paths_or_urls(links_url=REMOTE_BASE_DOWNLOAD_URL)
    errors = fetch_license_texts_and_notices(dest_dir, paths_or_urls)
    not_found.extend(errors)

    errors = fetch_license_texts_from_licensedb(dest_dir)
    not_found.extend(errors)

    # TODO: also make API calls

    for name, version, pyver, opsys in not_found:
        print(f'Not found wheel for {name}=={version} on python {pyver} and {opsys}')


def delete_outdated_package_files(dest_dir=THIRDPARTY_DIR):
    """
    Keep only the latest version of any Package found in `dest_dir`.
    Delete wheels, sdists and ABOUT files for older versions.
    """
    local_packages = get_local_packages(directory=dest_dir)
    key = operator.attrgetter('name')
    package_versions_by_name = itertools.groupby(local_packages, key=key)
    for name, package_versions in package_versions_by_name:
        for outdated in Package.get_outdated_versions(name, package_versions):
            outdated.delete_files(dest_dir)


def delete_unused_license_and_notice_files(dest_dir=THIRDPARTY_DIR):
    """
    Using .ABOUT files found in `dest_dir` remove any license file found in
    `dest_dir` that is not referenced in any .ABOUT file.
    """
    referenced_license_files = set()

    license_files = set([f for f in os.listdir(dest_dir) if f.endswith('.LICENSE')])

    for about_data in get_about_data(dest_dir):
        lfns = get_license_and_notice_file_names(about_data)
        referenced_license_files.update(lfns)

    unused_license_files = license_files.difference(referenced_license_files)
    for unused in unused_license_files:
        fileutils.delete(os.path.join(dest_dir, unused))

################################################################################
#
# Functions to handle remote or local repo used to "find-links"
#
################################################################################


def get_paths_or_urls(links_url):
    if links_url.startswith('https:'):
        paths_or_urls = find_links_from_url(links_url)
    else:
        paths_or_urls = find_links_from_dir(links_url)
    return paths_or_urls


def find_links_from_dir(directory=THIRDPARTY_DIR, extensions=EXTENSIONS):
    """
    Return a list of path to files in `directory` for any file that ends with
    any of the extension in the list of `extensions` strings.
    """
    base = os.path.abspath(directory)
    files = [os.path.join(base, f) for f in os.listdir(base) if f.endswith(extensions)]
    return files


def find_links_from_url(
    links_url=REMOTE_LINKS_URL,
    base_url=REMOTE_BASE_URL,
    prefix=REMOTE_HREF_PREFIX,
    extensions=EXTENSIONS,
):
    """
    Return a list of download link URLs found in the HTML page at `links_url`
    URL that starts with the `prefix` string and ends with any of the extension
    in the list of `extensions` strings. Use the `base_url` to prefix the links.
    """
    get_links = re.compile('href="([^"]+)"').findall

    text = get_remote_file_content(links_url)
    links = get_links(text)
    links = [l for l in links if l.startswith(prefix) and l.endswith(extensions)]
    links = [l if l.startswith('https://') else f'{base_url}{l}' for l in links]
    return links


def find_pypi_links(name, extensions=EXTENSIONS, simple_url=PYPI_SIMPLE_URL):
    """
    Return a list of download link URLs found in a PyPI simple index for package name.
    with the list of `extensions` strings. Use the `simple_url` PyPI url.
    """
    get_links = re.compile('href="([^"]+)"').findall

    name = name and canonicalize_name(name)
    simple_url = simple_url.strip('/')
    simple_url = f'{simple_url}/{name}'

    text = get_remote_file_content(simple_url)
    links = get_links(text)
    links = [l.partition('#sha256=') for l in links]
    links = [url for url, _, _sha256 in links]
    links = [l for l in links if l.endswith(extensions)]
    return  links


def get_link_for_file_name(file_name, paths_or_urls):
    """
    Return a link for `file_name` found in the `links` list of URLs or paths. Raise an
    exception if no link is found or if there are more than one link for that
    file name.
    """
    path_or_url = [l for l in paths_or_urls if l.endswith(f'/{file_name}')]
    if not path_or_url:
        raise Exception(f'Missing link to file: {file_name}')
    if not len(path_or_url) == 1:
        raise Exception(f'Multiple links to file: {file_name}: \n' + '\n'.join(path_or_url))
    return path_or_url[0]

################################################################################
#
# Requirements processing
#
################################################################################


def get_required_remote_packages(requirement='requirements.txt'):
    """
    Yield tuple of (name, version, Package) for packages listed in the
    `requirement` requirements file and found in our remote repo exclusively.
    """
    required_name_versions = load_requirements(requirements_file=requirement)
    remote_repo = get_remote_repo()
    return (
        (name, version, remote_repo.get_package(name, version))
        for name, version in required_name_versions
    )


def update_requirements(name, version=None, requirements_file='requirements.txt'):
    """
    Upgrade or add `package_name` with `new_version` to the `requirements_file`
    requirements file. Write back requirements sorted with name and version
    canonicalized. Note: this cannot deal with hashed or unpinned requirements.
    Do nothng if the version already exists as pinned.
    """
    name, version = canonicalize(name, version)

    is_updated = False
    updated_name_versions = []
    for existing_name, existing_version in load_requirements(requirements_file, force_pinned=False):
        existing_name, existing_version = canonicalize(existing_name, existing_version)

        if name == existing_name:
            if version != existing_version:
                is_updated = True
            updated_name_versions.append((existing_name, existing_version,))

    if is_updated:
        updated_name_versions = sorted(updated_name_versions)
        nvs = '\n'.join(f'{name}=={version}' for name, version in updated_name_versions)

        with open(requirements_file, 'w') as fo:
            fo.write(nvs)


def canonicalize(name, version=None):
    """
    Return a tuple of canonical name, canonical version
    """
    name = name and canonicalize_name(name)
    version = version and canonicalize_version(version)
    return name, version

################################################################################
#
# ABOUT and license files functions
#
################################################################################


def get_about_files(dest_dir=THIRDPARTY_DIR):
    """
    Return a list of ABOUT files found in `dest_dir`
    """
    return [f for f in os.listdir(dest_dir) if f.endswith('.ABOUT')]


def get_about_data(dest_dir=THIRDPARTY_DIR):
    """
    Yield ABOUT data mappings from ABOUT files found in `dest_dir`
    """
    for about_file in get_about_files(dest_dir):
        with open(os.path.join(dest_dir, about_file)) as fi:
            yield saneyaml.load(fi.read())


def create_or_derive_about_file(
    remote_package,
    name,
    version,
    file_name,
    download_url,
    dest_dir=THIRDPARTY_DIR,
):
    """
    Derive an ABOUT file from an existing remote package if possible. Otherwise,
    create a skinny ABOUT file using the provided name, version file_name and
    download_url. Return file_name on success or None.
    """
    name, version = canonicalize(name, version)

    about_file = None

    if remote_package:
        about_file = derive_about_file_from_package(
            remote_package=remote_package,
            name=name,
            version=version,
            file_name=file_name,
            download_url=download_url,
            dest_dir=dest_dir)

    if not about_file:
        about_file = create_and_save_skinny_about_file(
            about_resource=file_name,
            name=name,
            version=version,
            download_url=download_url,
            dest_dir=dest_dir)

    if not about_file:
        raise Exception(
            f'Failed to create an ABOUT file for: {file_name}')

    return about_file


def derive_about_file_from_package(
    remote_package,
    name,
    version,
    file_name,
    download_url=None,
    dest_dir=THIRDPARTY_DIR,
):
    """
    Derive an ABOUT file from existing ABOUT files if possible. Try an sdist ABOUT first,
    then any wheel. Use the provided name, version file_name and
    download_url to update the new ABOUT file. Return the ABOUT file_name on success or None on failure.
    """
    name, version = canonicalize(name, version)

    for dist in remote_package.get_distributions():
        about_file_name = derive_about_file_from_dist(
            dist, name, version, file_name, download_url, dest_dir)
        if about_file_name:
            return about_file_name


def build_remote_download_url(file_name, base_url=REMOTE_BASE_DOWNLOAD_URL):
    """
    Return a direct download URL for a file in our remote repo
    """
    return f'{base_url}/{file_name}'


def derive_about_file_from_dist(
    dist,
    name,
    version,
    file_name,
    download_url=None,
    dest_dir=THIRDPARTY_DIR,

):
    """
    Derive and save a new ABOUT file from dist for the provided argument.
    Return the ABOUT file name on success, None otherwise.
    """
    name, version = canonicalize(name, version)

    dist_about_url = f'{dist.path_or_url}.ABOUT'
    dist_about_content = fetch_path_or_url_through_cache(dist_about_url)
    if not dist_about_content:
        return

    if not download_url:
        # binary has been built from sources, therefore this is NOT from PyPI
        # so we raft a wheel URL assuming this will be later uploaded
        # to our PyPI-like repo
        download_url = build_remote_download_url(file_name)

    about_file_name = derive_new_about_file_from_about_content(
        about_content=dist_about_content,
        new_name=name,
        new_version=version,
        new_file_name=file_name,
        new_download_url=download_url,
        dest_dir=dest_dir,
    )

    if 'notice_file: ' in dist_about_content:
        # also fetch and rename the NOTICE
        dist_notice_file_name = f'{file_name}.NOTICE'
        dist_notice_url = build_remote_download_url(dist_notice_file_name)

        fetch_and_save_path_or_url(
            file_name=f'{file_name}.NOTICE',
            dest_dir=dest_dir,
            path_or_url=dist_notice_url,
            as_text=True,
        )

    return about_file_name


def derive_new_about_file_from_about_file(
    existing_about_file,
    new_name,
    new_version,
    new_file_name,
    new_download_url,
    dest_dir=THIRDPARTY_DIR,
):
    """
    Given an existing ABOUT file `existing_about_file` in `dest_dir`, create a
    new ABOUT file derived from that existing file and save it to `dest_dir`.
    Use new_name, new_version, new_file_name, new_download_url for the new ABOUT
    file.
    """
    new_name, new_version = canonicalize(new_name, new_version)

    with open(existing_about_file) as fi:
        about_content = fi.read()

    return derive_new_about_file_from_about_content(
        about_content,
        new_name,
        new_version,
        new_file_name,
        new_download_url,
        dest_dir=dest_dir,
    )


def derive_new_about_file_from_about_content(
    about_content,
    new_name,
    new_version,
    new_file_name,
    new_download_url,
    dest_dir=THIRDPARTY_DIR,
):
    """
    Given an existing ABOUT file `existing_about_file` in `dest_dir`, create a
    new ABOUT file derived from that existing file and save it to `dest_dir`.
    Use new_name, new_version, new_file_name, new_download_url for the new ABOUT
    file. Return the new ABOUT file name
    """
    new_name, new_version = canonicalize(new_name, new_version)

    new_about_content = derive_new_about_from_about_content(
        about_content,
        new_name,
        new_version,
        new_file_name,
        new_download_url,
    )

    new_about_file_name = os.path.join(dest_dir, f'{new_file_name}.ABOUT')

    with open(new_about_file_name, 'w') as fo:
        fo.write(saneyaml.dump(new_about_content))

    return new_about_file_name


def derive_new_about_from_about_content(
    about_content,
    new_name,
    new_version,
    new_file_name,
    new_download_url,
):
    """
    Given an ABOUT data YANL content`about_data` as text return a new ABOUT YAML text
    derived from that existing content . Use new_name,
    new_version, new_file_name, new_download_url for the new ABOUT file.
    Assumes (possibly incorrectly) that everything else stays the same.
    """
    new_name, new_version = canonicalize(new_name, new_version)

    about_data = saneyaml.load(about_content)
    # remove checksums if any
    for checksum in ('md5', 'sha1', 'sha256', 'sha512'):
        about_data.pop(checksum, None)
    old_about_resource = about_data['about_resource']
    about_data['about_resource'] = new_file_name
    about_data['name'] = new_name
    about_data['version'] = new_version
    about_data['download_url'] = new_download_url

    notice_file = about_data.get('notice_file')
    if notice_file:
        new_notice_file = notice_file.replace(old_about_resource, new_file_name)
        about_data['notice_file'] = new_notice_file

    return saneyaml.dump(about_data)


def create_and_save_skinny_about_file(
    about_resource,
    name,
    version,
    download_url,
    dest_dir=THIRDPARTY_DIR,
):
    """
    Create and save a skinny about filw with minimum known data
    """
    name, version = canonicalize(name, version)

    about_data = dict(
        about_resource=about_resource,
        name=name,
        version=version,
        download_url=download_url,
        primary_language='Python',
    )
    about_file = f'{about_resource}.ABOUT'
    with open(os.path.join(dest_dir, about_file), 'w') as fo:
        fo.write(saneyaml.dump(about_data))
    return about_file


def fetch_license_texts_and_notices(dest_dir, paths_or_urls):
    """
    Download to `dest_dir` all the .LICENSE and .NOTICE files referenced in all
    the .ABOUT files in `dest_dir` using URLs or path from the `paths_or_urls`
    list.
    """
    errors = []
    for about_data in get_about_data(dest_dir):
        for lic_file in get_license_and_notice_file_names(about_data):
            try:

                lic_url = get_link_for_file_name(
                    file_name=lic_file,
                    paths_or_urls=paths_or_urls,
                )

                fetch_and_save_path_or_url(
                    file_name=lic_file,
                    dest_dir=dest_dir,
                    path_or_url=lic_url,
                    as_text=True,
                )
            except Exception as e:
                errors.append(str(e))
                continue

    return errors


def fetch_license_texts_from_licensedb(
    dest_dir=THIRDPARTY_DIR,
    licensedb_api_url=LICENSEDB_API_URL,
):
    """
    Download to `dest_dir` all the .LICENSE files referenced in all the .ABOUT
    files in `dest_dir` using the licensedb `licensedb_api_url`.
    """
    errors = []
    for about_data in get_about_data(dest_dir):
        for license_key in get_license_keys(about_data):
            ltext = fetch_and_save_license_text_from_licensedb(
                license_key,
                dest_dir,
                licensedb_api_url,
            )
            if not ltext:
                errors.append(f'No text for license {license_key}')

    return errors


def fetch_abouts(dest_dir, paths_or_urls):
    """
    Download to `dest_dir` all the .ABOUT files for all the files in `dest_dir`
    that should have an .ABOUT file documentation using URLs or path from the
    `paths_or_urls` list.

    Documentable files (typically archives, sdists, wheels, etc.) should have a
    corresponding .ABOUT file named <archive_file_name>.ABOUT.
    """

    # these are the files that should have a matching ABOUT file
    aboutables = [fn for fn in os.listdir(dest_dir)
        if not fn.endswith(EXTENSIONS_ABOUT)
    ]

    errors = []
    for aboutable in aboutables:
        about_file = f'{aboutable}.ABOUT'
        try:
            about_url = get_link_for_file_name(
                file_name=about_file,
                paths_or_urls=paths_or_urls,
            )

            fetch_and_save_path_or_url(
                file_name=about_file,
                dest_dir=dest_dir,
                path_or_url=about_url,
                as_text=True,
            )

        except Exception as e:
            errors.append(str(e))

    return errors


def get_license_keys(about_data):
    """
    Return a list of license key found in the `about_data` .ABOUT data
    mapping.
    """
    # collect all the license and notice files
    # - first explicitly listed as licenses keys
    licenses = about_data.get('licenses', [])
    keys = [l.get('key') for l in licenses]
    # - then implied key from the license expression
    license_expression = about_data.get('license_expression', '')
    keys += keys_from_expression(license_expression)
    keys = [l for l in keys if l]
    return sorted(set(keys))


def get_license_file_names(about_data):
    """
    Return a list of license file names found in the `about_data` .ABOUT data
    mapping.
    """
    return [f'{l}.LICENSE' for l in get_license_keys(about_data)]


def get_notice_file_name(about_data):
    """
    Yield the notice file name found in the `about_data` .ABOUT data
    mapping.
    """
    notice_file = about_data.get('notice_file')
    if notice_file:
        yield notice_file


def get_license_and_notice_file_names(about_data):
    """
    Return a list of license file names found in the `about_data` .ABOUT data
    mapping.
    """

    license_files = get_license_file_names(about_data)

    licenses = about_data.get('licenses', [])
    license_files += [l.get('file') for l in licenses]

    license_files += list(get_notice_file_name(about_data))
    return sorted(set(f for f in license_files if f))


def keys_from_expression(license_expression):
    """
    Return a list of license keys from a `license_expression` string.
    """
    cleaned = (license_expression
        .lower()
        .replace('(', ' ')
        .replace(')', ' ')
        .replace(' and ', ' ')
        .replace(' or ', ' ')
        .replace(' with ', ' ')
    )
    return cleaned.split()


def fetch_and_save_license_text_from_licensedb(
    license_key,
    dest_dir=THIRDPARTY_DIR,
    licensedb_api_url=LICENSEDB_API_URL,
):
    """
    Fetch and save the license text for `license_key` from the `licensedb_api_url`
    """
    file_name = f'{license_key}.LICENSE'
    api_url = f'{licensedb_api_url}/{file_name}'
    return fetch_and_save_path_or_url(file_name, dest_dir, path_or_url=api_url, as_text=True)

################################################################################
#
# pip-based functions running pip as if called from the command line
#
################################################################################


def call(args):
    """
    Call args in a subprocess and display output on the fly.
    Return or raise stdout, stderr, returncode
    """
    print('Calling:', ' '.join(args))
    with subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8'
    ) as process:

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            print(line.rstrip(), flush=True)

        stdout, stderr = process.communicate()
        returncode = process.returncode
        if returncode == 0:
            return stdout, stderr, returncode
        else:
            raise Exception(stdout, stderr, returncode)


def fetch_wheels_using_pip(
        environment=None,
        requirement='requirements.txt',
        dest_dir=THIRDPARTY_DIR,
        links_url=REMOTE_LINKS_URL,
):
    """
    Download all dependent wheels for the `environment` Enviromnent constraints in
    the `requirement` requirements file or package requirement into `dest_dir`
    directory.

    Use only the packages found in the `links_url` HTML page ignoring PyPI
    packages unless `links_url` is None or empty in which case we use instead
    the public PyPI packages.

    If the provided `environment` is None then the current Python interpreter
    environment is used implicitly.
    """

    options = [
        'pip', 'download',
        '--requirement', requirement,
        '--dest', dest_dir,
        '--only-binary=:all:',
        '--no-deps',
    ]

    if links_url:
        find_link = [
            '--no-index',
            '--find-links', links_url,
        ]
        options += find_link

    if environment:
        options += environment.pip_cli_options()

    try:
        call(options)
    except:
        print('Failed to run:')
        print(' '.join(options))
        raise


def fetch_sources_using_pip(
        requirement='requirements.txt',
        dest_dir=THIRDPARTY_DIR,
        links_url=REMOTE_LINKS_URL,
):
    """
    Download all dependency source distributions for the `environment`
    Enviromnent constraints in the `requirement` requirements file or package
    requirement into `dest_dir` directory.

    Use only the source packages found in the `links_url` HTML page ignoring
    PyPI packages unless `links_url` is None or empty in which case we use
    instead the public PyPI packages.

    These items are fetched:
        - source distributions
    """

    options = [
        'pip', 'download',
        '--requirement', requirement,
        '--dest', dest_dir,
        '--no-binary=:all:'
        '--no-deps',
    ] + [
        # temporary workaround
        '--only-binary=extractcode-7z',
        '--only-binary=extractcode-libarchive',
        '--only-binary=typecode-libmagic',
    ]

    if links_url:
        options += [
            '--no-index',
            '--find-links', links_url,
        ]

    try:
        call(options)
    except:
        print('Failed to run:')
        print(' '.join(options))
        raise

################################################################################
# Utility to build new Python wheel.
################################################################################


def build_wheel(name, version, python_version, operating_system, dest_dir=THIRDPARTY_DIR):
    """
    Given a package `name` and `version`, build a binary wheel for
    `python_version` and `operating_system` into `dest_dir` and return the file
    name for the built wheel.
    """
    print('!!! build_wheel is NOT implemented:', name, version, python_version, operating_system)
    return None


def add_or_upgrade_package(
        name,
        version=None,
        python_version=None,
        operating_system=None,
        dest_dir=THIRDPARTY_DIR,
    ):
    """
    Add or update package `name` and `version` as a binary wheel saved in
    `dest_dir`. Use the latest version if `version` is None.
    Return the name of the built wheel or None.

    Use the provided `python_version` (e.g. "36") and `operating_system` (e.g.
    linux, windows or macos) to decide which specific wheel to fetch or build.
    """
    name, version = canonicalize(name, version)

    environment = Environment.from_pyos(python_version, operating_system)

    # Check if requested wheel already exists locally for this version
    local_package = get_local_package(name, version)
    if version and local_package:
        for wheel in local_package.get_supported_wheels(environment):
            # if requested version is there, there is nothing to do: just return
            return wheel.file_name

    if not version:
        # find latest version @ PyPI
        pypi_package = get_pypi_repo().get_latest_version(name)
        version = pypi_package.version

    # Check if requested wheel already exists remotely or in Pypi for this version
    wheel_file_name = fetch_package_wheel(name, version, environment, dest_dir)
    if wheel_file_name:
        return wheel_file_name

    # the wheel is not available locally, remotely or in Pypi
    # we need to build binary from sources
    wheel_file_name = build_wheel(
        name=name,
        version=version,
        python_version=python_version,
        operating_system=operating_system)

    return wheel_file_name
