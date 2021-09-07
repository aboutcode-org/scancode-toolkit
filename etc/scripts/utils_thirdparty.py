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
from collections import defaultdict
import email
import itertools
import operator
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib

import attr
import license_expression
import packageurl
import utils_pip_compatibility_tags
import utils_pypi_supported_tags
import requests
import saneyaml

from commoncode import fileutils
from commoncode.hash import multi_checksums
from packaging import tags as packaging_tags
from packaging import version as packaging_version
from utils_requirements import load_requirements

"""
Utilities to manage Python thirparty libraries source, binaries and metadata in
local directories and remote repositories.

- update pip requirement files from installed packages for prod. and dev.
- build and save wheels for all required packages
- also build variants for wheels with native code for all each supported
  operating systems (Linux, macOS, Windows) and Python versions (3.x)
  combinations using remote Ci jobs
- collect source distributions for all required packages
- keep in sync wheels, distributions, ABOUT and LICENSE files to a PyPI-like
  repository (using GitHub)
- create, update and fetch ABOUT, NOTICE and LICENSE metadata for all distributions


Approach
--------

The processing is organized around these key objects:

- A PyPiPackage represents a PyPI package with its name and version. It tracks
  the downloadable Distribution objects for that version:

  - one Sdist source Distribution object
  - a list of Wheel binary Distribution objects

- A Distribution (either a Wheel or Sdist) is identified by and created from its
  filename. It also has the metadata used to populate an .ABOUT file and
  document origin and license. A Distribution can be fetched from Repository.
  Metadata can be loaded from and dumped to ABOUT files and optionally from
  DejaCode package data.

- An Environment is a combination of a Python version and operating system.
  A Wheel Distribution also has Python/OS tags is supports and these can be
  supported in a given Environment.

- Paths or URLs to "filenames" live in a Repository, either a plain
  LinksRepository (an HTML page listing URLs or a local directory) or a
  PypiRepository (a PyPI simple index where each package name has an HTML page
  listing URLs to all distribution types and versions).
  Repositories and Distributions are related through filenames.


 The Wheel models code is partially derived from the mit-licensed pip and the
 Distribution/Wheel/Sdist design has been heavily inspired by the packaging-
 dists library https://github.com/uranusjr/packaging-dists by Tzu-ping Chung
"""

TRACE = False

# Supported environments
PYTHON_VERSIONS = '36', '37', '38', '39',

ABIS_BY_PYTHON_VERSION = {
    '36':['cp36', 'cp36m'],
    '37':['cp37', 'cp37m'],
    '38':['cp38', 'cp38m'],
    '39':['cp39', 'cp39m'],
}

PLATFORMS_BY_OS = {
    'linux': [
        'linux_x86_64',
        'manylinux1_x86_64',
        'manylinux2014_x86_64',
        'manylinux2010_x86_64',
    ],
    'macos': [
        'macosx_10_6_intel', 'macosx_10_6_x86_64',
        'macosx_10_9_intel', 'macosx_10_9_x86_64',
        'macosx_10_10_intel', 'macosx_10_10_x86_64',
        'macosx_10_11_intel', 'macosx_10_11_x86_64',
        'macosx_10_12_intel', 'macosx_10_12_x86_64',
        'macosx_10_13_intel', 'macosx_10_13_x86_64',
        'macosx_10_14_intel', 'macosx_10_14_x86_64',
        'macosx_10_15_intel', 'macosx_10_15_x86_64',
    ],
    'windows': [
        'win_amd64',
    ],
}

THIRDPARTY_DIR = 'thirdparty'
CACHE_THIRDPARTY_DIR = '.cache/thirdparty'

REMOTE_LINKS_URL = 'https://thirdparty.aboutcode.org/pypi'

EXTENSIONS_APP = '.pyz',
EXTENSIONS_SDIST = '.tar.gz', '.tar.bz2', '.zip', '.tar.xz',
EXTENSIONS_INSTALLABLE = EXTENSIONS_SDIST + ('.whl',)
EXTENSIONS_ABOUT = '.ABOUT', '.LICENSE', '.NOTICE',
EXTENSIONS = EXTENSIONS_INSTALLABLE + EXTENSIONS_ABOUT + EXTENSIONS_APP

PYPI_SIMPLE_URL = 'https://pypi.org/simple'

LICENSEDB_API_URL = 'https://scancode-licensedb.aboutcode.org'

LICENSING = license_expression.Licensing()

################################################################################
#
# Fetch remote wheels and sources locally
#
################################################################################


def fetch_wheels(
    environment=None,
    requirements_file='requirements.txt',
    allow_unpinned=False,
    dest_dir=THIRDPARTY_DIR,
    remote_links_url=REMOTE_LINKS_URL,
):
    """
    Download all of the wheel of packages listed in the ``requirements_file``
    requirements file into ``dest_dir`` directory.

    Only get wheels for the ``environment`` Enviromnent constraints. If the
    provided ``environment`` is None then the current Python interpreter
    environment is used implicitly.

    Only accept pinned requirements (e.g. with a version) unless
    ``allow_unpinned`` is True.

    Use exclusively direct downloads from a remote repo  at URL
    ``remote_links_url``. If ``remote_links_url`` is a path, use this as a
    directory of links instead of a URL.

    Yield tuples of (PypiPackage, error) where is None on success.
    """
    missed = []

    if not allow_unpinned:
        force_pinned = True
    else:
        force_pinned = False

    rrp = list(get_required_remote_packages(
        requirements_file=requirements_file,
        force_pinned=force_pinned,
        remote_links_url=remote_links_url,
    ))

    fetched_filenames = set()
    for name, version, package in rrp:
        if not package:
            missed.append((name, version,))
            nv = f'{name}=={version}' if version else name
            yield None, f'fetch_wheels: Missing package in remote repo: {nv}'

        else:
            fetched_filename = package.fetch_wheel(
                environment=environment,
                fetched_filenames=fetched_filenames,
                dest_dir=dest_dir,
            )

            if fetched_filename:
                fetched_filenames.add(fetched_filename)
                error = None
            else:
                if fetched_filename in fetched_filenames:
                    error = None
                else:
                    error = f'Failed to fetch'
            yield package, error

    if missed:
        rr = get_remote_repo()
        print()
        print(f'===> fetch_wheels: Missed some packages')
        for n, v in missed:
            nv = f'{n}=={v}' if v else n
            print(f'Missed package {nv} in remote repo, has only:')
            for pv in rr.get_versions(n):
                print('  ', pv)


def fetch_sources(
    requirements_file='requirements.txt',
    allow_unpinned=False,
    dest_dir=THIRDPARTY_DIR,
    remote_links_url=REMOTE_LINKS_URL,
):
    """
    Download all of the dependent package sources listed in the
    ``requirements_file`` requirements file into ``dest_dir`` destination
    directory.

    Use direct downloads to achieve this (not pip download). Use exclusively the
    packages found from a remote repo at URL ``remote_links_url``. If
    ``remote_links_url`` is a path, use this as a directory of links instead of
    a URL.

    Only accept pinned requirements (e.g. with a version) unless
    ``allow_unpinned`` is True.

    Yield tuples of (PypiPackage, error message) for each package where error
    message will empty on success.
    """
    missed = []

    if not allow_unpinned:
        force_pinned = True
    else:
        force_pinned = False

    rrp = list(get_required_remote_packages(
        requirements_file=requirements_file,
        force_pinned=force_pinned,
        remote_links_url=remote_links_url,
    ))

    for name, version, package in rrp:
        if not package:
            missed.append((name, name,))
            nv = f'{name}=={version}' if version else name
            yield None, f'fetch_sources: Missing package in remote repo: {nv}'

        elif not package.sdist:
            yield package, f'Missing sdist in links'

        else:
            fetched = package.fetch_sdist(dest_dir=dest_dir)
            error = f'Failed to fetch' if not fetched else None
            yield package, error

################################################################################
#
# Core models
#
################################################################################


@attr.attributes
class NameVer:
    name = attr.ib(
        type=str,
        metadata=dict(help='Python package name, lowercase and normalized.'),
    )

    version = attr.ib(
        type=str,
        metadata=dict(help='Python package version string.'),
    )

    @property
    def normalized_name(self):
        return NameVer.normalize_name(self.name)

    @staticmethod
    def normalize_name(name):
        """
        Return a normalized package name per PEP503, and copied from
        https://www.python.org/dev/peps/pep-0503/#id4
        """
        return name and re.sub(r"[-_.]+", "-", name).lower() or name

    @staticmethod
    def standardize_name(name):
        """
        Return a standardized package name, e.g. lowercased and using - not _
        """
        return name and re.sub(r"[-_]+", "-", name).lower() or name

    @property
    def name_ver(self):
        return f'{self.name}-{self.version}'

    def sortable_name_version(self):
        """
        Return a tuple of values to sort by name, then version.
        This method is a suitable to use as key for sorting NameVer instances.
        """
        return self.normalized_name, packaging_version.parse(self.version)

    @classmethod
    def sorted(cls, namevers):
        return sorted(namevers, key=cls.sortable_name_version)


@attr.attributes
class Distribution(NameVer):

    # field names that can be updated from another dist of mapping
    updatable_fields = [
        'license_expression',
        'copyright',
        'description',
        'homepage_url',
        'primary_language',
        'notice_text',
        'extra_data',
    ]

    filename = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='File name.'),
    )

    path_or_url = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='Path or download URL.'),
    )

    sha256 = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='SHA256 checksum.'),
    )

    sha1 = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='SHA1 checksum.'),
    )

    md5 = attr.ib(
        repr=False,
        type=int,
        default=0,
        metadata=dict(help='MD5 checksum.'),
    )

    type = attr.ib(
        repr=False,
        type=str,
        default='pypi',
        metadata=dict(help='Package type'),
    )

    namespace = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='Package URL namespace'),
    )

    qualifiers = attr.ib(
        repr=False,
        type=dict,
        default=attr.Factory(dict),
        metadata=dict(help='Package URL qualifiers'),
    )

    subpath = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='Package URL subpath'),
    )

    size = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='Size in bytes.'),
    )

    primary_language = attr.ib(
        repr=False,
        type=str,
        default='Python',
        metadata=dict(help='Primary Programming language.'),
    )

    description = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='Description.'),
    )

    homepage_url = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='Homepage URL'),
    )

    notes = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='Notes.'),
    )

    copyright = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='Copyright.'),
    )

    license_expression = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='License expression'),
    )

    licenses = attr.ib(
        repr=False,
        type=list,
        default=attr.Factory(list),
        metadata=dict(help='List of license mappings.'),
    )

    notice_text = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='Notice text'),
    )

    extra_data = attr.ib(
        repr=False,
        type=dict,
        default=attr.Factory(dict),
        metadata=dict(help='Extra data'),
    )

    @property
    def package_url(self):
        """
        Return a Package URL string of self.
        """
        return str(packageurl.PackageURL(**self.purl_identifiers()))

    @property
    def download_url(self):
        if self.path_or_url and self.path_or_url.startswith('https://'):
            return self.path_or_url
        else:
            return self.get_best_download_url()

    @property
    def about_filename(self):
        return f'{self.filename}.ABOUT'

    def has_about_file(self, dest_dir=THIRDPARTY_DIR):
        return os.path.exists(os.path.join(dest_dir, self.about_filename))

    @property
    def about_download_url(self):
        return self.build_remote_download_url(self.about_filename)

    @property
    def notice_filename(self):
        return f'{self.filename}.NOTICE'

    @property
    def notice_download_url(self):
        return self.build_remote_download_url(self.notice_filename)

    @classmethod
    def from_path_or_url(cls, path_or_url):
        """
        Return a distribution built from the data found in the filename of a
        `path_or_url` string. Raise an exception if this is not a valid
        filename.
        """
        filename = os.path.basename(path_or_url.strip('/'))
        dist = cls.from_filename(filename)
        dist.path_or_url = path_or_url
        return dist

    @classmethod
    def get_dist_class(cls, filename):
        if filename.endswith('.whl'):
            return Wheel
        elif filename.endswith(('.zip', '.tar.gz',)):
            return Sdist
        raise InvalidDistributionFilename(filename)

    @classmethod
    def from_filename(cls, filename):
        """
        Return a distribution built from the data found in a `filename` string.
        Raise an exception if this is not a valid filename
        """
        clazz = cls.get_dist_class(filename)
        return clazz.from_filename(filename)

    @classmethod
    def from_data(cls, data, keep_extra=False):
        """
        Return a distribution built from a `data` mapping.
        """
        filename = data['filename']
        dist = cls.from_filename(filename)
        dist.update(data, keep_extra=keep_extra)
        return dist

    @classmethod
    def from_dist(cls, data, dist):
        """
        Return a distribution built from a `data` mapping and update it with data
        from another dist Distribution. Return None if it cannot be created
        """
        # We can only create from a dist of the same package
        has_same_key_fields = all(data.get(kf) == getattr(dist, kf, None)
            for kf in ('type', 'namespace', 'name')
        )
        if not has_same_key_fields:
            print(f'Missing key fields: Cannot derive a new dist from data: {data} and dist: {dist}')
            return

        has_key_field_values = all(data.get(kf) for kf in ('type', 'name', 'version'))
        if not has_key_field_values:
            print(f'Missing key field values: Cannot derive a new dist from data: {data} and dist: {dist}')
            return

        data = dict(data)
        # do not overwrite the data with the other dist
        # only supplement
        data.update({k: v for k, v in dist.get_updatable_data().items() if not data.get(k)})
        return cls.from_data(data)

    @classmethod
    def build_remote_download_url(cls, filename, base_url=REMOTE_LINKS_URL):
        """
        Return a direct download URL for a file in our remote repo
        """
        return f'{base_url}/{filename}'

    def get_best_download_url(self):
        """
        Return the best download URL for this distribution where best means that
        PyPI is better and our own remote repo URLs are second.
        If none is found, return a synthetic remote URL.
        """
        name = self.normalized_name
        version = self.version
        filename = self.filename

        pypi_package = get_pypi_package(name=name, version=version)
        if pypi_package:
            pypi_url = pypi_package.get_url_for_filename(filename)
            if pypi_url:
                return pypi_url

        remote_package = get_remote_package(name=name, version=version)
        if remote_package:
            remote_url = remote_package.get_url_for_filename(filename)
            if remote_url:
                return remote_url
        else:
            # the package may not have been published yet, so we craft a URL
            # using our remote base URL
            return self.build_remote_download_url(self.filename)

    def purl_identifiers(self, skinny=False):
        """
        Return a mapping of non-empty identifier name/values for the purl
        fields. If skinny is True, only inlucde type, namespace and name.
        """
        identifiers = dict(
            type=self.type,
            namespace=self.namespace,
            name=self.name,
        )

        if not skinny:
            identifiers.update(
                version=self.version,
                subpath=self.subpath,
                qualifiers=self.qualifiers,
            )

        return {k: v for k, v in sorted(identifiers.items()) if v}

    def identifiers(self, purl_as_fields=True):
        """
        Return a mapping of non-empty identifier name/values.
        Return each purl fields separately if purl_as_fields is True.
        Otherwise return a package_url string for the purl.
        """
        if purl_as_fields:
            identifiers = self.purl_identifiers()
        else:
            identifiers = dict(package_url=self.package_url)

        identifiers.update(
            download_url=self.download_url,
            filename=self.filename,
            md5=self.md5,
            sha1=self.sha1,
            package_url=self.package_url,
        )

        return {k: v for k, v in sorted(identifiers.items()) if v}

    def has_key_metadata(self):
        """
        Return True if this distribution has key metadata required for basic attribution.
        """
        if self.license_expression == 'public-domain':
            # copyright not needed
            return True
        return self.license_expression and self.copyright and self.path_or_url

    def to_about(self):
        """
        Return a mapping of ABOUT data from this distribution fields.
        """
        about_data = dict(
            about_resource=self.filename,
            checksum_md5=self.md5,
            checksum_sha1=self.sha1,
            copyright=self.copyright,
            description=self.description,
            download_url=self.download_url,
            homepage_url=self.homepage_url,
            license_expression=self.license_expression,
            name=self.name,
            namespace=self.namespace,
            notes=self.notes,
            notice_file=self.notice_filename if self.notice_text else '',
            package_url=self.package_url,
            primary_language=self.primary_language,
            qualifiers=self.qualifiers,
            size=self.size,
            subpath=self.subpath,
            type=self.type,
            version=self.version,
        )

        about_data.update(self.extra_data)
        about_data = {k: v for k, v in sorted(about_data.items()) if v}
        return about_data

    def to_dict(self):
        """
        Return a mapping data from this distribution.
        """
        return {k: v for k, v in  attr.asdict(self).items() if v}

    def save_about_and_notice_files(self, dest_dir=THIRDPARTY_DIR):
        """
        Save a .ABOUT file to `dest_dir`. Include a .NOTICE file if there is a
        notice_text.
        """

        def save_if_modified(location, content):
            if os.path.exists(location):
                with open(location) as fi:
                    existing_content = fi.read()
                if existing_content == content:
                    return False

            if TRACE: print(f'Saving ABOUT (and NOTICE) files for: {self}')
            with open(location, 'w') as fo:
                fo.write(content)
            return True

        save_if_modified(
            location=os.path.join(dest_dir, self.about_filename),
            content=saneyaml.dump(self.to_about()),
        )

        notice_text = self.notice_text and self.notice_text.strip()
        if notice_text:
            save_if_modified(
                location=os.path.join(dest_dir, self.notice_filename),
                content=notice_text,
            )

    def load_about_data(self, about_filename_or_data=None, dest_dir=THIRDPARTY_DIR):
        """
        Update self with ABOUT data loaded from an `about_filename_or_data`
        which is either a .ABOUT file in `dest_dir` or an ABOUT data mapping.
        `about_filename_or_data` defaults to this distribution default ABOUT
        filename if not provided. Load the notice_text if present from dest_dir.
        """
        if not about_filename_or_data:
            about_filename_or_data = self.about_filename

        if isinstance(about_filename_or_data, str):
            # that's an about_filename
            about_path = os.path.join(dest_dir, about_filename_or_data)
            if os.path.exists(about_path):
                with open(about_path) as fi:
                    about_data = saneyaml.load(fi.read())
            else:
                return False
        else:
            about_data = about_filename_or_data

        md5 = about_data.pop('checksum_md5', None)
        if md5:
            about_data['md5'] = md5
        sha1 = about_data.pop('checksum_sha1', None)
        if sha1:
            about_data['sha1'] = sha1
        sha256 = about_data.pop('checksum_sha256', None)
        if sha256:
            about_data['sha256'] = sha256

        about_data.pop('about_resource', None)
        notice_text = about_data.pop('notice_text', None)
        notice_file = about_data.pop('notice_file', None)
        if notice_text:
            about_data['notice_text'] = notice_text
        elif notice_file:
            notice_loc = os.path.join(dest_dir, notice_file)
            if os.path.exists(notice_loc):
                with open(notice_loc) as fi:
                    about_data['notice_text'] = fi.read()
        return self.update(about_data, keep_extra=True)

    def load_remote_about_data(self):
        """
        Fetch and update self with "remote" data Distribution ABOUT file and
        NOTICE file if any. Return True if the data was updated.
        """
        try:
            about_text = fetch_content_from_path_or_url_through_cache(self.about_download_url)
        except RemoteNotFetchedException:
            return False

        if not about_text:
            return False

        about_data = saneyaml.load(about_text)
        notice_file = about_data.pop('notice_file', None)
        if notice_file:
            try:
                notice_text = fetch_content_from_path_or_url_through_cache(self.notice_download_url)
                if notice_text:
                    about_data['notice_text'] = notice_text
            except RemoteNotFetchedException:
                print(f'Failed to fetch NOTICE file: {self.notice_download_url}')
        return self.load_about_data(about_data)

    def get_checksums(self, dest_dir=THIRDPARTY_DIR):
        """
        Return a mapping of computed checksums for this dist filename is
        `dest_dir`.
        """
        dist_loc = os.path.join(dest_dir, self.filename)
        if os.path.exists(dist_loc):
            return multi_checksums(dist_loc, checksum_names=('md5', 'sha1', 'sha256'))
        else:
            return {}

    def set_checksums(self, dest_dir=THIRDPARTY_DIR):
        """
        Update self with checksums computed for this dist filename is `dest_dir`.
        """
        self.update(self.get_checksums(dest_dir), overwrite=True)

    def validate_checksums(self, dest_dir=THIRDPARTY_DIR):
        """
        Return True if all checksums that have a value in this dist match
        checksums computed for this dist filename is `dest_dir`.
        """
        real_checksums = self.get_checksums(dest_dir)
        for csk in ('md5', 'sha1', 'sha256'):
            csv = getattr(self, csk)
            rcv = real_checksums.get(csk)
            if csv and rcv and csv != rcv:
                return False
        return True

    def get_pip_hash(self):
        """
        Return a pip hash option string as used in requirements for this dist.
        """
        assert self.sha256, f'Missinh SHA256 for dist {self}'
        return f'--hash=sha256:{self.sha256}'

    def get_license_keys(self):
        try:
            keys = LICENSING.license_keys(self.license_expression, unique=True, simple=True)
        except license_expression.ExpressionParseError:
            return ['unknown']
        return keys

    def fetch_license_files(self, dest_dir=THIRDPARTY_DIR):
        """
        Fetch license files is missing in `dest_dir`.
        Return True if license files were fetched.
        """
        paths_or_urls = get_remote_repo().links
        errors = []
        extra_lic_names = [l.get('file') for l in self.extra_data.get('licenses', {})]
        extra_lic_names += [self.extra_data.get('license_file')]
        extra_lic_names = [ln for ln in extra_lic_names  if ln]
        lic_names = [ f'{key}.LICENSE' for key in self.get_license_keys()]
        for filename  in lic_names + extra_lic_names:
            floc = os.path.join(dest_dir, filename)
            if os.path.exists(floc):
                continue

            try:
                # try remotely first
                lic_url = get_link_for_filename(
                    filename=filename, paths_or_urls=paths_or_urls)

                fetch_and_save_path_or_url(
                    filename=filename,
                    dest_dir=dest_dir,
                    path_or_url=lic_url,
                    as_text=True,
                )
                if TRACE: print(f'Fetched license from remote: {lic_url}')

            except:
                try:
                    # try licensedb second
                    lic_url = f'{LICENSEDB_API_URL}/{filename}'
                    fetch_and_save_path_or_url(
                        filename=filename,
                        dest_dir=dest_dir,
                        path_or_url=lic_url,
                        as_text=True,
                    )
                    if TRACE: print(f'Fetched license from licensedb: {lic_url}')

                except:
                    msg = f'No text for license {filename} in expression "{self.license_expression}" from {self}'
                    print(msg)
                    errors.append(msg)

        return errors

    def extract_pkginfo(self, dest_dir=THIRDPARTY_DIR):
        """
        Return the text of the first PKG-INFO or METADATA file found in the
        archive of this Distribution in `dest_dir`. Return None if not found.
        """
        fmt = 'zip' if self.filename.endswith('.whl') else None
        dist = os.path.join(dest_dir, self.filename)
        with tempfile.TemporaryDirectory(prefix='pypi-tmp-extract') as td:
            shutil.unpack_archive(filename=dist, extract_dir=td, format=fmt)
            # NOTE: we only care about the first one found in the dist
            # which may not be 100% right
            for pi in fileutils.resource_iter(location=td, with_dirs=False):
                if pi.endswith(('PKG-INFO', 'METADATA',)):
                    with open(pi) as fi:
                        return fi.read()

    def load_pkginfo_data(self, dest_dir=THIRDPARTY_DIR):
        """
        Update self with data loaded from the PKG-INFO file found in the
        archive of this Distribution in `dest_dir`.
        """
        pkginfo_text = self.extract_pkginfo(dest_dir=dest_dir)
        if not pkginfo_text:
            print(f'!!!!PKG-INFO not found in {self.filename}')
            return
        raw_data = email.message_from_string(pkginfo_text)

        classifiers = raw_data.get_all('Classifier') or []

        declared_license = [raw_data['License']] + [c for c in classifiers if c.startswith('License')]
        license_expression = compute_normalized_license_expression(declared_license)
        other_classifiers = [c for c in classifiers if not c.startswith('License')]

        holder = raw_data['Author']
        holder_contact=raw_data['Author-email']
        copyright = f'Copyright (c) {holder} <{holder_contact}>'

        pkginfo_data = dict(
            name=raw_data['Name'],
            declared_license=declared_license,
            version=raw_data['Version'],
            description=raw_data['Summary'],
            homepage_url=raw_data['Home-page'],
            copyright=copyright,
            license_expression=license_expression,
            holder=holder,
            holder_contact=holder_contact,
            keywords=raw_data['Keywords'],
            classifiers=other_classifiers,
        )

        return self.update(pkginfo_data, keep_extra=True)

    def update_from_other_dist(self, dist):
        """
        Update self using data from another dist
        """
        return self.update(dist.get_updatable_data())

    def get_updatable_data(self, data=None):
        data = data or self.to_dict()
        return {
            k: v for k, v in data.items()
            if v and k in self.updatable_fields
        }

    def update(self, data, overwrite=False, keep_extra=True):
        """
        Update self with a mapping of `data`. Keep unknown data as extra_data if
        `keep_extra` is True. If `overwrite` is True, overwrite self with `data`
        Return True if any data was updated, False otherwise. Raise an exception
        if there are key data conflicts.
        """
        package_url = data.get('package_url')
        if package_url:
            purl_from_data = packageurl.PackageURL.from_string(package_url)
            purl_from_self = packageurl.PackageURL.from_string(self.package_url)
            if purl_from_data != purl_from_self:
                print(
                    f'Invalid dist update attempt, no same same purl with dist: '
                    f'{self} using data {data}.')
                return

        data.pop('about_resource', None)
        dl = data.pop('download_url', None)
        if dl:
            data['path_or_url'] = dl

        updated = False
        extra = {}
        for k, v in data.items():
            if isinstance(v, str):
                v = v.strip()
            if not v:
                continue

            if hasattr(self, k):
                value = getattr(self, k, None)
                if not value or (overwrite and value != v):
                    try:
                        setattr(self, k, v)
                    except Exception as e:
                        raise Exception(f'{self}, {k}, {v}') from e
                    updated = True

            elif keep_extra:
                # note that we always overwrite extra
                extra[k] = v
                updated = True

        self.extra_data.update(extra)

        return updated


class InvalidDistributionFilename(Exception):
    pass


@attr.attributes
class Sdist(Distribution):

    extension = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='File extension, including leading dot.'),
    )

    @classmethod
    def from_filename(cls, filename):
        """
        Return a Sdist object built from a filename.
        Raise an exception if this is not a valid sdist filename
        """
        name_ver = None
        extension = None

        for ext in EXTENSIONS_SDIST:
            if filename.endswith(ext):
                name_ver, extension, _ = filename.rpartition(ext)
                break

        if not extension or not name_ver:
            raise InvalidDistributionFilename(filename)

        name, _, version = name_ver.rpartition('-')

        if not name or not version:
            raise InvalidDistributionFilename(filename)

        return cls(
            type='pypi',
            name=name,
            version=version,
            extension=extension,
            filename=filename,
        )

    def to_filename(self):
        """
        Return an sdist filename reconstructed from its fields (that may not be
        the same as the original filename.)
        """
        return f'{self.name}-{self.version}.{self.extension}'


@attr.attributes
class Wheel(Distribution):

    """
    Represents a wheel file.

    Copied and heavily modified from pip-20.3.1 copied from pip-20.3.1
    pip/_internal/models/wheel.py

    name: pip compatibility tags
    version: 20.3.1
    download_url: https://github.com/pypa/pip/blob/20.3.1/src/pip/_internal/models/wheel.py
    copyright: Copyright (c) 2008-2020 The pip developers (see AUTHORS.txt file)
    license_expression: mit
    notes: copied from pip-20.3.1 pip/_internal/models/wheel.py

    Copyright (c) 2008-2020 The pip developers (see AUTHORS.txt file)

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    """

    get_wheel_from_filename = re.compile(
        r"""^(?P<namever>(?P<name>.+?)-(?P<ver>.*?))
        ((-(?P<build>\d[^-]*?))?-(?P<pyvers>.+?)-(?P<abis>.+?)-(?P<plats>.+?)
        \.whl)$""",
        re.VERBOSE
    ).match

    build = attr.ib(
        type=str,
        default='',
        metadata=dict(help='Python wheel build.'),
    )

    python_versions = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help='List of wheel Python version tags.'),
    )

    abis = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help='List of wheel ABI tags.'),
    )

    platforms = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help='List of wheel platform tags.'),
    )

    tags = attr.ib(
        repr=False,
        type=set,
        default=attr.Factory(set),
        metadata=dict(help='Set of all tags for this wheel.'),
    )

    @classmethod
    def from_filename(cls, filename):
        """
        Return a wheel object built from a filename.
        Raise an exception if this is not a valid wheel filename
        """
        wheel_info = cls.get_wheel_from_filename(filename)
        if not wheel_info:
            raise InvalidDistributionFilename(filename)

        name = wheel_info.group('name').replace('_', '-')
        # we'll assume "_" means "-" due to wheel naming scheme
        # (https://github.com/pypa/pip/issues/1150)
        version = wheel_info.group('ver').replace('_', '-')
        build = wheel_info.group('build')
        python_versions = wheel_info.group('pyvers').split('.')
        abis = wheel_info.group('abis').split('.')
        platforms = wheel_info.group('plats').split('.')

        # All the tag combinations from this file
        tags = {
            packaging_tags.Tag(x, y, z) for x in python_versions
            for y in abis for z in platforms
        }

        return cls(
            filename=filename,
            type='pypi',
            name=name,
            version=version,
            build=build,
            python_versions=python_versions,
            abis=abis,
            platforms=platforms,
            tags=tags,
        )

    def is_supported_by_tags(self, tags):
        """
        Return True is this wheel is compatible with one of a list of PEP 425 tags.
        """
        return not self.tags.isdisjoint(tags)

    def is_supported_by_environment(self, environment):
        """
        Return True if this wheel is compatible with the Environment
        `environment`.
        """
        return  not self.is_supported_by_tags(environment.tags)

    def to_filename(self):
        """
        Return a wheel filename reconstructed from its fields (that may not be
        the same as the original filename.)
        """
        build = f'-{self.build}' if self.build else ''
        pyvers = '.'.join(self.python_versions)
        abis = '.'.join(self.abis)
        plats = '.'.join(self.platforms)
        return f'{self.name}-{self.version}{build}-{pyvers}-{abis}-{plats}.whl'

    def is_pure(self):
        """
        Return True if wheel `filename` is for a "pure" wheel e.g. a wheel that
        runs on all Pythons 3 and all OSes.

        For example::

        >>> Wheel.from_filename('aboutcode_toolkit-5.1.0-py2.py3-none-any.whl').is_pure()
        True
        >>> Wheel.from_filename('beautifulsoup4-4.7.1-py3-none-any.whl').is_pure()
        True
        >>> Wheel.from_filename('beautifulsoup4-4.7.1-py2-none-any.whl').is_pure()
        False
        >>> Wheel.from_filename('bitarray-0.8.1-cp36-cp36m-win_amd64.whl').is_pure()
        False
        >>> Wheel.from_filename('extractcode_7z-16.5-py2.py3-none-macosx_10_13_intel.whl').is_pure()
        False
        >>> Wheel.from_filename('future-0.16.0-cp36-none-any.whl').is_pure()
        False
        >>> Wheel.from_filename('foo-4.7.1-py3-none-macosx_10_13_intel.whl').is_pure()
        False
        >>> Wheel.from_filename('future-0.16.0-py3-cp36m-any.whl').is_pure()
        False
        """
        return (
            'py3' in self.python_versions
            and 'none' in self.abis
            and 'any' in self.platforms
        )


def is_pure_wheel(filename):
    try:
        return Wheel.from_filename(filename).is_pure()
    except:
        return False


@attr.attributes
class PypiPackage(NameVer):
    """
    A Python package with its "distributions", e.g. wheels and source
    distribution , ABOUT files and licenses or notices.
    """
    sdist = attr.ib(
        repr=False,
        type=str,
        default='',
        metadata=dict(help='Sdist source distribution for this package.'),
    )

    wheels = attr.ib(
        repr=False,
        type=list,
        default=attr.Factory(list),
        metadata=dict(help='List of Wheel for this package'),
    )

    @property
    def specifier(self):
        """
        A requirement specifier for this package
        """
        if self.version:
            return f'{self.name}=={self.version}'
        else:
            return self.name

    @property
    def specifier_with_hashes(self):
        """
        Return a requirement specifier for this package with --hash options for
        all its distributions
        """
        items = [self.specifier]
        items += [d.get_pip_hashes() for d in self.get_distributions()]
        return ' \\\n    '.join(items)

    def get_supported_wheels(self, environment):
        """
        Yield all the Wheel of this package supported and compatible with the
        Environment `environment`.
        """
        envt_tags = environment.tags()
        for wheel in self.wheels:
            if wheel.is_supported_by_tags(envt_tags):
                yield wheel

    @classmethod
    def package_from_dists(cls, dists):
        """
        Return a new PypiPackage built from an iterable of Wheels and Sdist
        objects all for the same package name and version.

        For example:
        >>> w1 = Wheel(name='bitarray', version='0.8.1', build='',
        ...    python_versions=['cp36'], abis=['cp36m'],
        ...    platforms=['linux_x86_64'])
        >>> w2 = Wheel(name='bitarray', version='0.8.1', build='',
        ...    python_versions=['cp36'], abis=['cp36m'],
        ...    platforms=['macosx_10_9_x86_64', 'macosx_10_10_x86_64'])
        >>> sd = Sdist(name='bitarray', version='0.8.1')
        >>> package = PypiPackage.package_from_dists(dists=[w1, w2, sd])
        >>> assert package.name == 'bitarray'
        >>> assert package.version == '0.8.1'
        >>> assert package.sdist == sd
        >>> assert package.wheels == [w1, w2]
        """
        dists = list(dists)
        if not dists:
            return

        reference_dist = dists[0]
        normalized_name = reference_dist.normalized_name
        version = reference_dist.version

        package = PypiPackage(name=normalized_name, version=version)

        for dist in dists:
            if dist.normalized_name != normalized_name or dist.version != version:
                if TRACE:
                    print(
                        f'  Skipping inconsistent dist name and version: {dist} '
                        f'Expected instead package name: {normalized_name} and version: "{version}"'
                    )
                continue

            if isinstance(dist, Sdist):
                package.sdist = dist

            elif isinstance(dist, Wheel):
                package.wheels.append(dist)

            else:
                raise Exception(f'Unknown distribution type: {dist}')

        return package

    @classmethod
    def packages_from_one_path_or_url(cls, path_or_url):
        """
        Yield PypiPackages built from files found in at directory path or the
        URL to an HTML page (that will be fetched).
        """
        extracted_paths_or_urls = get_paths_or_urls(path_or_url)
        return cls.packages_from_many_paths_or_urls(extracted_paths_or_urls)

    @classmethod
    def packages_from_many_paths_or_urls(cls, paths_or_urls):
        """
        Yield PypiPackages built from a list of paths or URLs.
        """
        dists = cls.get_dists(paths_or_urls)
        dists = NameVer.sorted(dists)

        for _projver, dists_of_package in itertools.groupby(
            dists, key=NameVer.sortable_name_version,
        ):
            yield PypiPackage.package_from_dists(dists_of_package)

    @classmethod
    def get_versions_from_path_or_url(cls, name, path_or_url):
        """
        Return a subset list from a list of PypiPackages version at `path_or_url`
        that match PypiPackage `name`.
        """
        packages = cls.packages_from_one_path_or_url(path_or_url)
        return cls.get_versions(name, packages)

    @classmethod
    def get_versions(cls, name, packages):
        """
        Return a subset list of package versions from a list of `packages` that
        match PypiPackage `name`.
        The list is sorted by version from oldest to most recent.
        """
        norm_name = NameVer.normalize_name(name)
        versions = [p for p in packages if p.normalized_name == norm_name]
        return cls.sorted(versions)

    @classmethod
    def get_latest_version(cls, name, packages):
        """
        Return the latest version of PypiPackage `name` from a list of `packages`.
        """
        versions = cls.get_versions(name, packages)
        if not versions:
            return
        return versions[-1]

    @classmethod
    def get_outdated_versions(cls, name, packages):
        """
        Return all versions except the latest version of PypiPackage `name` from a
        list of `packages`.
        """
        versions = cls.get_versions(name, packages)
        return versions[:-1]

    @classmethod
    def get_name_version(cls, name, version, packages):
        """
        Return the PypiPackage with `name` and `version` from a list of `packages`
        or None if it is not found.
        If `version` is None, return the latest version found.
        """
        if version is None:
            return cls.get_latest_version(name, packages)

        nvs = [p for p in cls.get_versions(name, packages) if p.version == version]

        if not nvs:
            return

        if len(nvs) == 1:
            return nvs[0]

        raise Exception(f'More than one PypiPackage with {name}=={version}')

    def fetch_wheel(
        self,
        environment=None,
        fetched_filenames=None,
        dest_dir=THIRDPARTY_DIR,
    ):
        """
        Download a binary wheel of this package matching the ``environment``
        Enviromnent constraints into ``dest_dir`` directory.

        Return the wheel filename if it was fetched, None otherwise.

        If the provided ``environment`` is None then the current Python
        interpreter environment is used implicitly. Do not refetch wheel if
        their name is in a provided ``fetched_filenames`` set.
        """
        fetched_wheel_filename = None
        if fetched_filenames is not None:
            fetched_filenames = fetched_filenames
        else:
            fetched_filenames = set()

        for wheel in self.get_supported_wheels(environment):

            if wheel.filename not in fetched_filenames:
                fetch_and_save_path_or_url(
                    filename=wheel.filename,
                    path_or_url=wheel.path_or_url,
                    dest_dir=dest_dir,
                    as_text=False,
                )
                fetched_filenames.add(wheel.filename)
                fetched_wheel_filename = wheel.filename

                # TODO: what if there is more than one?
                break

        return fetched_wheel_filename

    def fetch_sdist(self, dest_dir=THIRDPARTY_DIR):
        """
        Download the source distribution into `dest_dir` directory. Return the
        fetched filename if it was fetched, False otherwise.
        """
        if self.sdist:
            assert self.sdist.filename
            if TRACE: print('Fetching source for package:', self.name, self.version)
            fetch_and_save_path_or_url(
                filename=self.sdist.filename,
                dest_dir=dest_dir,
                path_or_url=self.sdist.path_or_url,
                as_text=False,
            )
            if TRACE: print(' --> file:', self.sdist.filename)
            return self.sdist.filename
        else:
            print(f'Missing sdist for: {self.name}=={self.version}')
            return False

    def delete_files(self, dest_dir=THIRDPARTY_DIR):
        """
        Delete all PypiPackage files from `dest_dir` including wheels, sdist and
        their ABOUT files. Note that we do not delete licenses since they can be
        shared by several packages: therefore this would be done elsewhere in a
        function that is aware of all used licenses.
        """
        for to_delete in self.wheels + [self.sdist]:
            if not to_delete:
                continue
            tdfn = to_delete.filename
            for deletable in [tdfn, f'{tdfn}.ABOUT', f'{tdfn}.NOTICE']:
                target = os.path.join(dest_dir, deletable)
                if os.path.exists(target):
                    print(f'Deleting outdated {target}')
                    fileutils.delete(target)

    @classmethod
    def get_dists(cls, paths_or_urls):
        """
        Return a list of Distribution given a list of
        `paths_or_urls` to wheels or source distributions.

        Each Distribution receives two extra attributes:
            - the path_or_url it was created from
            - its filename

        For example:
        >>> paths_or_urls ='''
        ...     /home/foo/bitarray-0.8.1-cp36-cp36m-linux_x86_64.whl
        ...     bitarray-0.8.1-cp36-cp36m-macosx_10_9_x86_64.macosx_10_10_x86_64.whl
        ...     bitarray-0.8.1-cp36-cp36m-win_amd64.whl
        ...     httsp://example.com/bar/bitarray-0.8.1.tar.gz
        ...     bitarray-0.8.1.tar.gz.ABOUT bit.LICENSE'''.split()
        >>> result = list(PypiPackage.get_dists(paths_or_urls))
        >>> for r in results:
        ...    r.filename = ''
        ...    r.path_or_url = ''
        >>> expected = [
        ...     Wheel(name='bitarray', version='0.8.1', build='',
        ...         python_versions=['cp36'], abis=['cp36m'],
        ...         platforms=['linux_x86_64']),
        ...     Wheel(name='bitarray', version='0.8.1', build='',
        ...         python_versions=['cp36'], abis=['cp36m'],
        ...         platforms=['macosx_10_9_x86_64', 'macosx_10_10_x86_64']),
        ...     Wheel(name='bitarray', version='0.8.1', build='',
        ...         python_versions=['cp36'], abis=['cp36m'],
        ...         platforms=['win_amd64']),
        ...     Sdist(name='bitarray', version='0.8.1')
        ... ]
        >>> assert expected == result
        """
        installable = [f for f in paths_or_urls if f.endswith(EXTENSIONS_INSTALLABLE)]
        for path_or_url in installable:
            try:
                yield Distribution.from_path_or_url(path_or_url)
            except InvalidDistributionFilename:
                if TRACE:
                    print(f'Skipping invalid distribution from: {path_or_url}')
                continue

    def get_distributions(self):
        """
        Yield all distributions available for this PypiPackage
        """
        if self.sdist:
            yield self.sdist
        for wheel in self.wheels:
            yield wheel

    def get_url_for_filename(self, filename):
        """
        Return the URL for this filename or None.
        """
        for dist in self.get_distributions():
            if dist.filename == filename:
                return dist.path_or_url


@attr.attributes
class Environment:
    """
    An Environment describes a target installation environment with its
    supported Python version, ABI, platform, implementation and related
    attributes. We can use these to pass as `pip download` options and force
    fetching only the subset of packages that match these Environment
    constraints as opposed to the current running Python interpreter
    constraints.
    """

    python_version = attr.ib(
        type=str,
        default='',
        metadata=dict(help='Python version supported by this environment.'),
    )

    operating_system = attr.ib(
        type=str,
        default='',
        metadata=dict(help='operating system supported by this environment.'),
    )

    implementation = attr.ib(
        type=str,
        default='cp',
        metadata=dict(help='Python implementation supported by this environment.'),
    )

    abis = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help='List of  ABI tags supported by this environment.'),
    )

    platforms = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help='List of platform tags supported by this environment.'),
    )

    @classmethod
    def from_pyver_and_os(cls, python_version, operating_system):
        if '.' in python_version:
            python_version = ''.join(python_version.split('.'))

        return cls(
            python_version=python_version,
            implementation='cp',
            abis=ABIS_BY_PYTHON_VERSION[python_version],
            platforms=PLATFORMS_BY_OS[operating_system],
            operating_system=operating_system,
        )

    def get_pip_cli_options(self):
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

    def tags(self):
        """
        Return a set of all the PEP425 tags supported by this environment.
        """
        return set(utils_pip_compatibility_tags.get_supported(
            version=self.python_version or None,
            impl=self.implementation or None,
            platforms=self.platforms or None,
            abis=self.abis or None,
        ))

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

    packages_by_normalized_name = attr.ib(
        type=dict,
        default=attr.Factory(lambda: defaultdict(list)),
        metadata=dict(help=
            'Mapping of {package name: [package objects]} available in this repo'),
    )

    packages_by_normalized_name_version = attr.ib(
        type=dict,
        default=attr.Factory(dict),
        metadata=dict(help=
            'Mapping of {(name, version): package object} available in this repo'),
    )

    def get_links(self, *args, **kwargs):
        raise NotImplementedError()

    def get_versions(self, name):
        """
        Return a list of all available PypiPackage version for this package name.
        The list may be empty.
        """
        raise NotImplementedError()

    def get_package(self, name, version):
        """
        Return the PypiPackage with name and version or None.
        """
        raise NotImplementedError()

    def get_latest_version(self, name):
        """
        Return the latest PypiPackage version for this package name or None.
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
        if not self.packages_by_normalized_name:
            for p in PypiPackage.packages_from_many_paths_or_urls(paths_or_urls=self.links):
                normalized_name = p.normalized_name
                self.packages_by_normalized_name[normalized_name].append(p)
                self.packages_by_normalized_name_version[(normalized_name, p.version)] = p

    def get_links(self, *args, **kwargs):
        return self.links or []

    def get_versions(self, name):
        name = name and NameVer.normalize_name(name)
        return self.packages_by_normalized_name.get(name, [])

    def get_latest_version(self, name):
        return PypiPackage.get_latest_version(name, self.get_versions(name))

    def get_package(self, name, version):
        return PypiPackage.get_name_version(name, version, self.get_versions(name))


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

    links_by_normalized_name = attr.ib(
        type=dict,
        default=attr.Factory(lambda: defaultdict(list)),
        metadata=dict(help='Mapping of {package name: [links]} available in this repo'),
    )

    def _fetch_links(self, name):
        name = name and NameVer.normalize_name(name)
        return find_pypi_links(name=name, simple_url=self.simple_url)

    def _populate_links_and_packages(self, name):
        name = name and NameVer.normalize_name(name)
        if name in self.links_by_normalized_name:
            return

        links = self._fetch_links(name)
        self.links_by_normalized_name[name] = links

        packages = list(PypiPackage.packages_from_many_paths_or_urls(paths_or_urls=links))
        self.packages_by_normalized_name[name] = packages

        for p in packages:
            name = name and NameVer.normalize_name(p.name)
            self.packages_by_normalized_name_version[(name, p.version)] = p

    def get_links(self, name, *args, **kwargs):
        name = name and NameVer.normalize_name(name)
        self._populate_links_and_packages(name)
        return  self.links_by_normalized_name.get(name, [])

    def get_versions(self, name):
        name = name and NameVer.normalize_name(name)
        self._populate_links_and_packages(name)
        return self.packages_by_normalized_name.get(name, [])

    def get_latest_version(self, name):
        return PypiPackage.get_latest_version(name, self.get_versions(name))

    def get_package(self, name, version):
        return PypiPackage.get_name_version(name, version, self.get_versions(name))

################################################################################
# Globals for remote repos to be lazily created and cached on first use for the
# life of the session together with some convenience functions.
################################################################################


def get_local_packages(directory=THIRDPARTY_DIR):
    """
    Return the list of all PypiPackage objects built from a local directory. Return
    an empty list if the package cannot be found.
    """
    return list(PypiPackage.packages_from_one_path_or_url(path_or_url=directory))


def get_local_repo(directory=THIRDPARTY_DIR):
    return LinksRepository(path_or_url=directory)


_REMOTE_REPO = None


def get_remote_repo(remote_links_url=REMOTE_LINKS_URL):
    global _REMOTE_REPO
    if not _REMOTE_REPO:
        _REMOTE_REPO = LinksRepository(path_or_url=remote_links_url)
    return _REMOTE_REPO


def get_remote_package(name, version, remote_links_url=REMOTE_LINKS_URL):
    """
    Return a PypiPackage or None.
    """
    try:
        return get_remote_repo(remote_links_url).get_package(name, version)
    except RemoteNotFetchedException as e:
        print(f'Failed to fetch remote package info: {e}')


_PYPI_REPO = None


def get_pypi_repo(pypi_simple_url=PYPI_SIMPLE_URL):
    global _PYPI_REPO
    if not _PYPI_REPO:
        _PYPI_REPO = PypiRepository(simple_url=pypi_simple_url)
    return _PYPI_REPO


def get_pypi_package(name, version, pypi_simple_url=PYPI_SIMPLE_URL):
    """
    Return a PypiPackage or None.
    """
    try:
        return get_pypi_repo(pypi_simple_url).get_package(name, version)
    except RemoteNotFetchedException as e:
        print(f'Failed to fetch remote package info: {e}')

################################################################################
#
# Basic file and URL-based operations using a persistent file-based Cache
#
################################################################################


@attr.attributes
class Cache:
    """
    A simple file-based cache based only on a filename presence.
    This is used to avoid impolite fetching from remote locations.
    """

    directory = attr.ib(type=str, default=CACHE_THIRDPARTY_DIR)

    def __attrs_post_init__(self):
        os.makedirs(self.directory, exist_ok=True)

    def clear(self):
        shutil.rmtree(self.directory)

    def get(self, path_or_url, as_text=True):
        """
        Get a file from a `path_or_url` through the cache.
        `path_or_url` can be a path or a URL to a file.
        """
        filename = os.path.basename(path_or_url.strip('/'))
        cached = os.path.join(self.directory, filename)

        if not os.path.exists(cached):
            content = get_file_content(path_or_url=path_or_url, as_text=as_text)
            wmode = 'w' if as_text else 'wb'
            with open(cached, wmode) as fo:
                fo.write(content)
            return content
        else:
            return get_local_file_content(path=cached, as_text=as_text)

    def put(self, filename, content):
        """
        Put in the cache the `content` of `filename`.
        """
        cached = os.path.join(self.directory, filename)
        wmode = 'wb' if isinstance(content, bytes) else 'w'
        with open(cached, wmode) as fo:
            fo.write(content)


def get_file_content(path_or_url, as_text=True):
    """
    Fetch and return the content at `path_or_url` from either a local path or a
    remote URL. Return the content as bytes is `as_text` is False.
    """
    if (path_or_url.startswith('file://')
        or (path_or_url.startswith('/') and os.path.exists(path_or_url))
    ):
        return get_local_file_content(path=path_or_url, as_text=as_text)

    elif path_or_url.startswith('https://'):
        if TRACE: print(f'Fetching: {path_or_url}')
        _headers, content = get_remote_file_content(url=path_or_url, as_text=as_text)
        return content

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


class RemoteNotFetchedException(Exception):
    pass


def get_remote_file_content(url, as_text=True, headers_only=False, headers=None, _delay=0,):
    """
    Fetch and return a tuple of (headers, content) at `url`. Return content as a
    text string if `as_text` is True. Otherwise return the content as bytes.

    If `header_only` is True, return only (headers, None). Headers is a mapping
    of HTTP headers.
    Retries multiple times to fetch if there is a HTTP 429 throttling response
    and this with an increasing delay.
    """
    time.sleep(_delay)
    headers = headers or {}
    # using a GET with stream=True ensure we get the the final header from
    # several redirects and that we can ignore content there. A HEAD request may
    # not get us this last header
    with requests.get(url, allow_redirects=True, stream=True, headers=headers) as response:
        status = response.status_code
        if status != requests.codes.ok:  # NOQA
            if status == 429 and _delay < 20:
                # too many requests: start some exponential delay
                increased_delay = (_delay * 2) or 1

                return get_remote_file_content(
                    url,
                    as_text=as_text,
                    headers_only=headers_only,
                    _delay=increased_delay,
                )

            else:
                raise RemoteNotFetchedException(f'Failed HTTP request from {url} with {status}')

        if headers_only:
            return response.headers, None

        return response.headers, response.text if as_text else response.content


def get_url_content_if_modified(url, md5, _delay=0,):
    """
    Return fetched content bytes at `url` or None if the md5 has not changed.
    Retries multiple times to fetch if there is a HTTP 429 throttling response
    and this with an increasing delay.
    """
    time.sleep(_delay)
    headers = None
    if md5:
        etag = f'"{md5}"'
        headers = {'If-None-Match': f'{etag}'}

    # using a GET with stream=True ensure we get the the final header from
    # several redirects and that we can ignore content there. A HEAD request may
    # not get us this last header
    with requests.get(url, allow_redirects=True, stream=True, headers=headers) as response:
        status = response.status_code
        if status == requests.codes.too_many_requests and _delay < 20:  # NOQA
            # too many requests: start waiting with some exponential delay
            _delay = (_delay * 2) or 1
            return get_url_content_if_modified(url=url, md5=md5, _delay=_delay)

        elif status == requests.codes.not_modified:  # NOQA
            # all is well, the md5 is the same
            return None

        elif status != requests.codes.ok:  # NOQA
            raise RemoteNotFetchedException(f'Failed HTTP request from {url} with {status}')

        return response.content


def get_remote_headers(url):
    """
    Fetch and return a mapping of HTTP headers of `url`.
    """
    headers, _content = get_remote_file_content(url, headers_only=True)
    return headers


def fetch_and_save_filename_from_paths_or_urls(
    filename,
    paths_or_urls,
    dest_dir=THIRDPARTY_DIR,
    as_text=True,
):
    """
    Return the content from fetching the `filename` file name found in the
    `paths_or_urls` list of URLs or paths and save to `dest_dir`. Raise an
    Exception on errors. Treats the content as text if `as_text` is True
    otherwise as binary.
    """
    path_or_url = get_link_for_filename(
        filename=filename,
        paths_or_urls=paths_or_urls,
    )

    return fetch_and_save_path_or_url(
        filename=filename,
        dest_dir=dest_dir,
        path_or_url=path_or_url,
        as_text=as_text,
    )


def fetch_content_from_path_or_url_through_cache(path_or_url, as_text=True, cache=Cache()):
    """
    Return the content from fetching at path or URL. Raise an Exception on
    errors. Treats the content as text if as_text is True otherwise as treat as
    binary. Use the provided file cache. This is the main entry for using the
    cache.

    Note: the `cache` argument is a global, though it does not really matter
    since it does not hold any state which is only kept on disk.
    """
    if cache:
        return cache.get(path_or_url=path_or_url, as_text=as_text)
    else:
        return get_file_content(path_or_url=path_or_url, as_text=as_text)


def fetch_and_save_path_or_url(filename, dest_dir, path_or_url, as_text=True, through_cache=True):
    """
    Return the content from fetching the `filename` file name at URL or path
    and save to `dest_dir`. Raise an Exception on errors. Treats the content as
    text if as_text is True otherwise as treat as binary.
    """
    if through_cache:
        content = fetch_content_from_path_or_url_through_cache(path_or_url, as_text)
    else:
        content = fetch_content_from_path_or_url_through_cache(path_or_url, as_text, cache=None)

    output = os.path.join(dest_dir, filename)
    wmode = 'w' if as_text else 'wb'
    with open(output, wmode) as fo:
        fo.write(content)
    return content

################################################################################
#
# Sync and fix local thirdparty directory for various issues and gaps
#
################################################################################


def fetch_missing_sources(dest_dir=THIRDPARTY_DIR):
    """
    Given a thirdparty dir, fetch missing source distributions from our remote
    repo or PyPI. Return a list of (name, version) tuples for source
    distribution that were not found
    """
    not_found = []
    local_packages = get_local_packages(directory=dest_dir)
    remote_repo = get_remote_repo()
    pypi_repo = get_pypi_repo()

    for package in local_packages:
        if not package.sdist:
            print(f'Finding sources for: {package.name}=={package.version}: ', end='')
            try:
                pypi_package = pypi_repo.get_package(
                    name=package.name, version=package.version)

                if pypi_package and pypi_package.sdist:
                    print(f'Fetching sources from Pypi')
                    pypi_package.fetch_sdist(dest_dir=dest_dir)
                    continue
                else:
                    remote_package = remote_repo.get_package(
                        name=package.name, version=package.version)

                    if remote_package and remote_package.sdist:
                        print(f'Fetching sources from Remote')
                        remote_package.fetch_sdist(dest_dir=dest_dir)
                        continue

            except RemoteNotFetchedException as e:
                print(f'Failed to fetch remote package info: {e}')

            print(f'No sources found')
            not_found.append((package.name, package.version,))

    return not_found


def fetch_missing_wheels(
    python_versions=PYTHON_VERSIONS,
    operating_systems=PLATFORMS_BY_OS,
    dest_dir=THIRDPARTY_DIR,
):
    """
    Given a thirdparty dir fetch missing wheels for all known combos of Python
    versions and OS. Return a list of tuple (Package, Environment) for wheels
    that were not found locally or remotely.
    """
    local_packages = get_local_packages(directory=dest_dir)
    evts = itertools.product(python_versions, operating_systems)
    environments = [Environment.from_pyver_and_os(pyv, os) for pyv, os in evts]
    packages_and_envts = itertools.product(local_packages, environments)

    not_fetched = []
    fetched_filenames = set()
    for package, envt in packages_and_envts:

        filename = package.fetch_wheel(
            environment=envt,
            fetched_filenames=fetched_filenames,
            dest_dir=dest_dir,
        )

        if filename:
            fetched_filenames.add(filename)
        else:
            not_fetched.append((package, envt,))

    return not_fetched


def build_missing_wheels(
    packages_and_envts,
    build_remotely=False,
    with_deps=False,
    dest_dir=THIRDPARTY_DIR,
):
    """
    Build all wheels in a list of tuple (Package, Environment) and save in
    `dest_dir`. Return a list of tuple (Package, Environment), and a list of
    built wheel filenames.
    """

    not_built = []
    built_filenames = []

    packages_and_envts = itertools.groupby(
        sorted(packages_and_envts), key=operator.itemgetter(0))

    for package, pkg_envts in packages_and_envts:

        envts = [envt for _pkg, envt in pkg_envts]
        python_versions = sorted(set(e.python_version for e in envts))
        operating_systems = sorted(set(e.operating_system for e in envts))
        built = None
        try:
            built = build_wheels(
                requirements_specifier=package.specifier,
                with_deps=with_deps,
                build_remotely=build_remotely,
                python_versions=python_versions,
                operating_systems=operating_systems,
                verbose=False,
                dest_dir=dest_dir,
            )
            print('.')
        except Exception as e:
            import traceback
            print('#############################################################')
            print('#############     WHEEL BUILD FAILED   ######################')
            traceback.print_exc()
            print()
            print('#############################################################')

        if not built:
            for envt in pkg_envts:
                not_built.append((package, envt))
        else:
            for bfn in built:
                print(f'   --> Built wheel: {bfn}')
                built_filenames.append(bfn)

    return not_built, built_filenames

################################################################################
#
# Functions to handle remote or local repo used to "find-links"
#
################################################################################


def get_paths_or_urls(links_url):
    if links_url.startswith('https:'):
        paths_or_urls = find_links_from_release_url(links_url)
    else:
        paths_or_urls = find_links_from_dir(links_url)
    return paths_or_urls


def find_links_from_dir(directory=THIRDPARTY_DIR):
    """
    Return a list of path to files in `directory` for any file that ends with
    any of the extension in the list of `extensions` strings.
    """
    base = os.path.abspath(directory)
    files = [os.path.join(base, f) for f in os.listdir(base) if f.endswith(EXTENSIONS)]
    return files


get_links = re.compile('href="([^"]+)"').findall


def find_links_from_release_url(links_url=REMOTE_LINKS_URL):
    """
    Return a list of download link URLs found in the HTML page at `links_url`
    URL that starts with the `prefix` string and ends with any of the extension
    in the list of `extensions` strings. Use the `base_url` to prefix the links.
    """
    if TRACE: print(f'Finding links for {links_url}')

    plinks_url = urllib.parse.urlparse(links_url)

    base_url = urllib.parse.SplitResult(
        plinks_url.scheme, plinks_url.netloc, '', '', '').geturl()

    if TRACE: print(f'Base URL {base_url}')

    _headers, text = get_remote_file_content(links_url)
    links = []
    for link in get_links(text):
        if not link.endswith(EXTENSIONS):
            continue

        plink = urllib.parse.urlsplit(link)

        if plink.scheme:
            # full URL kept as-is
            url = link

        if plink.path.startswith('/'):
            # absolute link
            url = f'{base_url}{link}'

        else:
            # relative link
            url = f'{links_url}/{link}'

        if TRACE: print(f'Adding URL: {url}')

        links.append(url)

    if TRACE: print(f'Found {len(links)} links at {links_url}')
    return links


def find_pypi_links(name, simple_url=PYPI_SIMPLE_URL):
    """
    Return a list of download link URLs found in a PyPI simple index for package name.
    with the list of `extensions` strings. Use the `simple_url` PyPI url.
    """
    if TRACE: print(f'Finding links for {simple_url}')

    name = name and NameVer.normalize_name(name)
    simple_url = simple_url.strip('/')
    simple_url = f'{simple_url}/{name}'

    _headers, text = get_remote_file_content(simple_url)
    links = get_links(text)
    # TODO: keep sha256
    links = [l.partition('#sha256=') for l in links]
    links = [url for url, _, _sha256 in links]
    links = [l for l in links if l.endswith(EXTENSIONS)]
    return  links


def get_link_for_filename(filename, paths_or_urls):
    """
    Return a link for `filename` found in the `links` list of URLs or paths. Raise an
    exception if no link is found or if there are more than one link for that
    file name.
    """
    path_or_url = [l for l in paths_or_urls if l.endswith(f'/{filename}')]
    if not path_or_url:
        raise Exception(f'Missing link to file: {filename}')
    if not len(path_or_url) == 1:
        raise Exception(f'Multiple links to file: {filename}: \n' + '\n'.join(path_or_url))
    return path_or_url[0]

################################################################################
#
# Requirements processing
#
################################################################################


class MissingRequirementException(Exception):
    pass


def get_required_packages(required_name_versions):
    """
    Return a tuple of (remote packages, PyPI packages) where each is a mapping
    of {(name, version): PypiPackage}  for packages listed in the
    `required_name_versions` list of (name, version) tuples. Raise a
    MissingRequirementException with a list of missing (name, version) if a
    requirement cannot be satisfied remotely or in PyPI.
    """
    remote_repo = get_remote_repo()

    remote_packages = {(name, version): remote_repo.get_package(name, version)
        for name, version in required_name_versions}

    pypi_repo = get_pypi_repo()
    pypi_packages = {(name, version):  pypi_repo.get_package(name, version)
        for name, version in required_name_versions}

    # remove any empty package (e.g. that do not exist in some place)
    remote_packages = {nv: p for nv, p in remote_packages.items() if p}
    pypi_packages = {nv: p for nv, p in pypi_packages.items() if p}

    # check that we are not missing any
    repos_name_versions = set(remote_packages.keys()) | set(pypi_packages.keys())
    missing_name_versions = required_name_versions.difference(repos_name_versions)
    if missing_name_versions:
        raise MissingRequirementException(sorted(missing_name_versions))

    return remote_packages, pypi_packages


def get_required_remote_packages(
    requirements_file='requirements.txt',
    force_pinned=True,
    remote_links_url=REMOTE_LINKS_URL,
):
    """
    Yield tuple of (name, version, PypiPackage) for packages listed in the
    `requirements_file` requirements file and found in the PyPI-like link repo
    ``remote_links_url`` if this is a URL. Treat this ``remote_links_url`` as a
    local directory path to a wheels directory if this is not a a URL.
    """
    required_name_versions = load_requirements(
        requirements_file=requirements_file,
        force_pinned=force_pinned,
    )

    if remote_links_url.startswith('https://'):
        repo = get_remote_repo(remote_links_url=remote_links_url)
    else:
        # a local path
        assert os.path.exists(remote_links_url)
        repo = get_local_repo(directory=remote_links_url)

    for name, version in required_name_versions:
        if version:
            yield name, version, repo.get_package(name, version)
        else:
            yield name, version, repo.get_latest_version(name)


def update_requirements(name, version=None, requirements_file='requirements.txt'):
    """
    Upgrade or add `package_name` with `new_version` to the `requirements_file`
    requirements file. Write back requirements sorted with name and version
    canonicalized. Note: this cannot deal with hashed or unpinned requirements.
    Do nothing if the version already exists as pinned.
    """
    normalized_name = NameVer.normalize_name(name)

    is_updated = False
    updated_name_versions = []
    for existing_name, existing_version in load_requirements(requirements_file, force_pinned=False):

        existing_normalized_name = NameVer.normalize_name(existing_name)

        if normalized_name == existing_normalized_name:
            if version != existing_version:
                is_updated = True
            updated_name_versions.append((existing_normalized_name, existing_version,))

    if is_updated:
        updated_name_versions = sorted(updated_name_versions)
        nvs = '\n'.join(f'{name}=={version}' for name, version in updated_name_versions)

        with open(requirements_file, 'w') as fo:
            fo.write(nvs)


def hash_requirements(dest_dir=THIRDPARTY_DIR, requirements_file='requirements.txt'):
    """
    Hash all the requirements found in the `requirements_file`
    requirements file based on distributions available in `dest_dir`
    """
    local_repo = get_local_repo(directory=dest_dir)
    packages_by_normalized_name_version = local_repo.packages_by_normalized_name_version
    hashed = []
    for name, version in load_requirements(requirements_file, force_pinned=True):
        package = packages_by_normalized_name_version.get((name, version))
        if not package:
            raise Exception(f'Missing required package {name}=={version}')
        hashed.append(package.specifier_with_hashes)

    with open(requirements_file, 'w') as fo:
        fo.write('\n'.join(hashed))

################################################################################
#
# Functions to update or fetch ABOUT and license files
#
################################################################################


def add_fetch_or_update_about_and_license_files(dest_dir=THIRDPARTY_DIR, include_remote=True):
    """
    Given a thirdparty dir, add missing ABOUT. LICENSE and NOTICE files using
    best efforts:

    - use existing ABOUT files
    - try to load existing remote ABOUT files
    - derive from existing distribution with same name and latest version that
      would have such ABOUT file
    - extract ABOUT file data from distributions PKGINFO or METADATA files
    - TODO: make API calls to fetch package data from DejaCode

    The process consists in load and iterate on every package distributions,
    collect data and then acsk to save.
    """

    local_packages = get_local_packages(directory=dest_dir)
    local_repo = get_local_repo(directory=dest_dir)

    remote_repo = get_remote_repo()

    def get_other_dists(_package, _dist):
        """
        Return a list of all the dists from package that are not the `dist` object
        """
        return [d for d in _package.get_distributions() if d != _dist]

    for local_package in local_packages:
        for local_dist in local_package.get_distributions():
            local_dist.load_about_data(dest_dir=dest_dir)
            local_dist.set_checksums(dest_dir=dest_dir)

            # if has key data we may look to improve later, but we can move on
            if local_dist.has_key_metadata():
                local_dist.save_about_and_notice_files(dest_dir=dest_dir)
                local_dist.fetch_license_files(dest_dir=dest_dir)
                continue

            # lets try to get from another dist of the same local package
            for otherd in get_other_dists(local_package, local_dist):
                updated = local_dist.update_from_other_dist(otherd)
                if updated and local_dist.has_key_metadata():
                    break

            # if has key data we may look to improve later, but we can move on
            if local_dist.has_key_metadata():
                local_dist.save_about_and_notice_files(dest_dir=dest_dir)
                local_dist.fetch_license_files(dest_dir=dest_dir)
                continue

            # try to get a latest version of the same package that is not our version
            other_local_packages = [
                p for p in local_repo.get_versions(local_package.name)
                if p.version != local_package.version
            ]

            latest_local_version = other_local_packages and other_local_packages[-1]
            if latest_local_version:
                latest_local_dists = list(latest_local_version.get_distributions())
                for latest_local_dist in latest_local_dists:
                    latest_local_dist.load_about_data(dest_dir=dest_dir)
                    if not latest_local_dist.has_key_metadata():
                        # there is not much value to get other data if we are missing the key ones
                        continue
                    else:
                        local_dist.update_from_other_dist(latest_local_dist)
                        # if has key data we may look to improve later, but we can move on
                        if local_dist.has_key_metadata():
                            break

                # if has key data we may look to improve later, but we can move on
                if local_dist.has_key_metadata():
                    local_dist.save_about_and_notice_files(dest_dir=dest_dir)
                    local_dist.fetch_license_files(dest_dir=dest_dir)
                    continue

            if include_remote:
                # lets try to fetch remotely
                local_dist.load_remote_about_data()

                # if has key data we may look to improve later, but we can move on
                if local_dist.has_key_metadata():
                    local_dist.save_about_and_notice_files(dest_dir=dest_dir)
                    local_dist.fetch_license_files(dest_dir=dest_dir)
                    continue

                # try to get a latest version of the same package that is not our version
                other_remote_packages = [
                    p for p in remote_repo.get_versions(local_package.name)
                    if p.version != local_package.version
                ]

                latest_version = other_remote_packages and other_remote_packages[-1]
                if latest_version:
                    latest_dists = list(latest_version.get_distributions())
                    for remote_dist in latest_dists:
                        remote_dist.load_remote_about_data()
                        if not remote_dist.has_key_metadata():
                            # there is not much value to get other data if we are missing the key ones
                            continue
                        else:
                            local_dist.update_from_other_dist(remote_dist)
                            # if has key data we may look to improve later, but we can move on
                            if local_dist.has_key_metadata():
                                break

                    # if has key data we may look to improve later, but we can move on
                    if local_dist.has_key_metadata():
                        local_dist.save_about_and_notice_files(dest_dir=dest_dir)
                        local_dist.fetch_license_files(dest_dir=dest_dir)
                        continue

            # try to get data from pkginfo (no license though)
            local_dist.load_pkginfo_data(dest_dir=dest_dir)

            # FIXME: save as this is the last resort for now in all cases
            # if local_dist.has_key_metadata() or not local_dist.has_key_metadata():
            local_dist.save_about_and_notice_files(dest_dir)

            lic_errs = local_dist.fetch_license_files(dest_dir)

            # TODO: try to get data from dejacode

            if not local_dist.has_key_metadata():
                print(f'Unable to add essential ABOUT data for: {local_dist}')
            if lic_errs:
                lic_errs = '\n'.join(lic_errs)
                print(f'Failed to fetch some licenses:: {lic_errs}')

################################################################################
#
# Functions to build new Python wheels including native on multiple OSes
#
################################################################################


def call(args):
    """
    Call args in a subprocess and display output on the fly.
    Return or raise stdout, stderr, returncode
    """
    if TRACE: print('Calling:', ' '.join(args))
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
            if TRACE: print(line.rstrip(), flush=True)

        stdout, stderr = process.communicate()
        returncode = process.returncode
        if returncode == 0:
            return returncode, stdout, stderr
        else:
            raise Exception(returncode, stdout, stderr)


def add_or_upgrade_built_wheels(
    name,
    version=None,
    python_versions=PYTHON_VERSIONS,
    operating_systems=PLATFORMS_BY_OS,
    dest_dir=THIRDPARTY_DIR,
    build_remotely=False,
    with_deps=False,
    verbose=False,
):
    """
    Add or update package `name` and `version` as a binary wheel saved in
    `dest_dir`. Use the latest version if `version` is None. Return the a list
    of the collected, fetched or built wheel file names or an empty list.

    Use the provided lists of `python_versions` (e.g. "36", "39") and
    `operating_systems` (e.g. linux, windows or macos) to decide which specific
    wheel to fetch or build.

    Include wheels for all dependencies if `with_deps` is True.
    Build remotely is `build_remotely` is True.
    """
    assert name, 'Name is required'
    ver = version and f'=={version}' or ''
    print(f'\nAdding wheels for package: {name}{ver}')

    wheel_filenames = []
    # a mapping of {req specifier: {mapping build_wheels kwargs}}
    wheels_to_build = {}
    for python_version, operating_system in itertools.product(python_versions, operating_systems):
        print(f'  Adding wheels for package: {name}{ver} on {python_version,} and {operating_system}')
        environment = Environment.from_pyver_and_os(python_version, operating_system)

        # Check if requested wheel already exists locally for this version
        local_repo = get_local_repo(directory=dest_dir)
        local_package = local_repo.get_package(name=name, version=version)

        has_local_wheel = False
        if version and local_package:
            for wheel in local_package.get_supported_wheels(environment):
                has_local_wheel = True
                wheel_filenames.append(wheel.filename)
                break
        if has_local_wheel:
            print(f'    local wheel exists: {wheel.filename}')
            continue

        if not version:
            pypi_package = get_pypi_repo().get_latest_version(name)
            version = pypi_package.version

        # Check if requested wheel already exists remotely or in Pypi for this version
        wheel_filename = fetch_package_wheel(
            name=name, version=version, environment=environment, dest_dir=dest_dir)
        if wheel_filename:
            wheel_filenames.append(wheel_filename)

        # the wheel is not available locally, remotely or in Pypi
        # we need to build binary from sources
        requirements_specifier = f'{name}=={version}'
        to_build = wheels_to_build.get(requirements_specifier)
        if to_build:
            to_build['python_versions'].append(python_version)
            to_build['operating_systems'].append(operating_system)
        else:
            wheels_to_build[requirements_specifier] = dict(
                requirements_specifier=requirements_specifier,
                python_versions=[python_version],
                operating_systems=[operating_system],
                dest_dir=dest_dir,
                build_remotely=build_remotely,
                with_deps=with_deps,
                verbose=verbose,
            )

    for build_wheels_kwargs in wheels_to_build.values():
        bwheel_filenames = build_wheels(**build_wheels_kwargs)
        wheel_filenames.extend(bwheel_filenames)

    return sorted(set(wheel_filenames))


def build_wheels(
    requirements_specifier,
    python_versions=PYTHON_VERSIONS,
    operating_systems=PLATFORMS_BY_OS,
    dest_dir=THIRDPARTY_DIR,
    build_remotely=False,
    with_deps=False,
    verbose=False,
):
    """
    Given a pip `requirements_specifier` string (such as package names or as
    name==version), build the corresponding binary wheel(s) for all
    `python_versions` and `operating_systems` combinations and save them
    back in `dest_dir` and return a list of built wheel file names.

    Include wheels for all dependencies if `with_deps` is True.

    First try to build locally to process pure Python wheels, and fall back to
    build remotey on all requested Pythons and operating systems.
    """
    all_pure, builds = build_wheels_locally_if_pure_python(
        requirements_specifier=requirements_specifier,
        with_deps=with_deps,
        verbose=verbose,
        dest_dir=dest_dir,
    )
    for local_build in builds:
        print(f'Built wheel: {local_build}')

    if all_pure:
        return builds

    if build_remotely:
        remote_builds = build_wheels_remotely_on_multiple_platforms(
            requirements_specifier=requirements_specifier,
            with_deps=with_deps,
            python_versions=python_versions,
            operating_systems=operating_systems,
            verbose=verbose,
            dest_dir=dest_dir,
        )
        builds.extend(remote_builds)

    return builds


def build_wheels_remotely_on_multiple_platforms(
    requirements_specifier,
    with_deps=False,
    python_versions=PYTHON_VERSIONS,
    operating_systems=PLATFORMS_BY_OS,
    verbose=False,
    dest_dir=THIRDPARTY_DIR,
):
    """
    Given pip `requirements_specifier` string (such as package names or as
    name==version), build the corresponding binary wheel(s) including wheels for
    all dependencies for all `python_versions` and `operating_systems`
    combinations and save them back in `dest_dir` and return a list of built
    wheel file names.
    """
    check_romp_is_configured()
    pyos_options = get_romp_pyos_options(python_versions, operating_systems)
    deps = '' if with_deps else '--no-deps'
    verbose = '--verbose' if verbose else ''

    romp_args = ([
        'romp',
        '--interpreter', 'cpython',
        '--architecture', 'x86_64',
        '--check-period', '5',  # in seconds

    ] + pyos_options + [

        '--artifact-paths', '*.whl',
        '--artifact', 'artifacts.tar.gz',
        '--command',
            # create a virtualenv, upgrade pip
#            f'python -m ensurepip --user --upgrade; '
            f'python -m pip {verbose} install  --user --upgrade pip setuptools wheel; '
            f'python -m pip {verbose} wheel {deps} {requirements_specifier}',
    ])

    if verbose:
        romp_args.append('--verbose')

    print(f'Building wheels for: {requirements_specifier}')
    print(f'Using command:', ' '.join(romp_args))
    call(romp_args)

    wheel_filenames = extract_tar('artifacts.tar.gz', dest_dir)
    for wfn in wheel_filenames:
        print(f' built wheel: {wfn}')
    return wheel_filenames


def get_romp_pyos_options(
    python_versions=PYTHON_VERSIONS,
    operating_systems=PLATFORMS_BY_OS,
):
    """
    Return a list of CLI options for romp
    For example:
    >>> expected = ['--version', '3.6', '--version', '3.7', '--version', '3.8',
    ... '--version', '3.9', '--platform', 'linux', '--platform', 'macos',
    ... '--platform', 'windows']
    >>> assert get_romp_pyos_options() == expected
    """
    python_dot_versions = ['.'.join(pv) for pv in sorted(set(python_versions))]
    pyos_options = list(itertools.chain.from_iterable(
        ('--version', ver) for ver in python_dot_versions))

    pyos_options += list(itertools.chain.from_iterable(
        ('--platform' , plat) for plat in sorted(set(operating_systems))))

    return pyos_options


def check_romp_is_configured():
    # these environment variable must be set before
    has_envt = (
        os.environ.get('ROMP_BUILD_REQUEST_URL') and
        os.environ.get('ROMP_DEFINITION_ID') and
        os.environ.get('ROMP_PERSONAL_ACCESS_TOKEN') and
        os.environ.get('ROMP_USERNAME')
    )

    if not has_envt:
        raise Exception(
            'ROMP_BUILD_REQUEST_URL, ROMP_DEFINITION_ID, '
            'ROMP_PERSONAL_ACCESS_TOKEN and ROMP_USERNAME '
            'are required enironment variables.')


def build_wheels_locally_if_pure_python(
    requirements_specifier,
    with_deps=False,
    verbose=False,
    dest_dir=THIRDPARTY_DIR,
):
    """
    Given pip `requirements_specifier` string (such as package names or as
    name==version), build the corresponding binary wheel(s) locally.

    If all these are "pure" Python wheels that run on all Python 3 versions and
    operating systems, copy them back in `dest_dir` if they do not exists there

    Return a tuple of (True if all wheels are "pure", list of built wheel file names)
    """
    deps = [] if with_deps else ['--no-deps']
    verbose = ['--verbose'] if verbose else []

    wheel_dir = tempfile.mkdtemp(prefix='scancode-release-wheels-local-')
    cli_args = [
        'pip', 'wheel',
        '--wheel-dir', wheel_dir,
    ] + deps + verbose + [
        requirements_specifier
    ]

    print(f'Building local wheels for: {requirements_specifier}')
    print(f'Using command:', ' '.join(cli_args))
    call(cli_args)

    built = os.listdir(wheel_dir)
    if not built:
        return []

    all_pure = all(is_pure_wheel(bwfn) for bwfn in built)

    if not all_pure:
        print(f'  Some wheels are not pure')

    print(f'  Copying local wheels')
    pure_built = []
    for bwfn in built:
        owfn = os.path.join(dest_dir, bwfn)
        if not os.path.exists(owfn):
            nwfn = os.path.join(wheel_dir, bwfn)
            fileutils.copyfile(nwfn, owfn)
        pure_built.append(bwfn)
        print(f'    Built local wheel: {bwfn}')
    return all_pure, pure_built


# TODO: Use me
def optimize_wheel(wheel_filename, dest_dir=THIRDPARTY_DIR):
    """
    Optimize a wheel named `wheel_filename` in `dest_dir` such as renaming its
    tags for PyPI compatibility and making it smaller if possible. Return the
    name of the new wheel if renamed or the existing new name otherwise.
    """
    if is_pure_wheel(wheel_filename):
        print(f'Pure wheel: {wheel_filename}, nothing to do.')
        return wheel_filename

    original_wheel_loc = os.path.join(dest_dir, wheel_filename)
    wheel_dir = tempfile.mkdtemp(prefix='scancode-release-wheels-')
    awargs = [
        'auditwheel',
        'addtag',
        '--wheel-dir', wheel_dir,
       original_wheel_loc
    ]
    call(awargs)

    audited = os.listdir(wheel_dir)
    if not audited:
        # cannot optimize wheel
        return wheel_filename

    assert len(audited) == 1
    new_wheel_name = audited[0]

    new_wheel_loc = os.path.join(wheel_dir, new_wheel_name)

    # this needs to go now
    os.remove(original_wheel_loc)

    if new_wheel_name == wheel_filename:
        os.rename(new_wheel_loc, original_wheel_loc)
        return wheel_filename

    new_wheel = Wheel.from_filename(new_wheel_name)
    non_pypi_plats = utils_pypi_supported_tags.validate_platforms_for_pypi(new_wheel.platforms)
    new_wheel.platforms = [p for p in new_wheel.platforms if p not in non_pypi_plats]
    if not new_wheel.platforms:
        print(f'Cannot make wheel PyPI compatible: {original_wheel_loc}')
        os.rename(new_wheel_loc, original_wheel_loc)
        return wheel_filename

    new_wheel_cleaned_filename = new_wheel.to_filename()
    new_wheel_cleaned_loc = os.path.join(dest_dir, new_wheel_cleaned_filename)
    os.rename(new_wheel_loc, new_wheel_cleaned_loc)
    return new_wheel_cleaned_filename


def extract_tar(location, dest_dir=THIRDPARTY_DIR,):
    """
    Extract a tar archive at `location` in the `dest_dir` directory. Return a
    list of extracted locations (either directories or files).
    """
    with open(location, 'rb') as fi:
        with tarfile.open(fileobj=fi) as tar:
            members = list(tar.getmembers())
            tar.extractall(dest_dir, members=members)

    return [os.path.basename(ti.name) for ti in members
            if ti.type == tarfile.REGTYPE]


def fetch_package_wheel(name, version, environment, dest_dir=THIRDPARTY_DIR):
    """
    Fetch the binary wheel for package `name` and `version` and save in
    `dest_dir`. Use the provided `environment` Environment to determine which
    specific wheel to fetch.

    Return the fetched wheel file name on success or None if it was not fetched.
    Trying fetching from our own remote repo, then from PyPI.
    """
    wheel_filename = None
    remote_package = get_remote_package(name=name, version=version)
    if remote_package:
        wheel_filename = remote_package.fetch_wheel(
            environment=environment, dest_dir=dest_dir)
        if wheel_filename:
            return wheel_filename

    pypi_package = get_pypi_package(name=name, version=version)
    if pypi_package:
        wheel_filename = pypi_package.fetch_wheel(
            environment=environment, dest_dir=dest_dir)
    return wheel_filename


def check_about(dest_dir=THIRDPARTY_DIR):
    try:
        subprocess.check_output(f'venv/bin/about check {dest_dir}'.split())
    except subprocess.CalledProcessError as cpe:
        print()
        print('Invalid ABOUT files:')
        print(cpe.output.decode('utf-8', errors='replace'))


def find_problems(
    dest_dir=THIRDPARTY_DIR,
    report_missing_sources=False,
    report_missing_wheels=False,
):
    """
    Print the problems found in `dest_dir`.
    """

    local_packages = get_local_packages(directory=dest_dir)

    for package in local_packages:
        if report_missing_sources and not package.sdist:
            print(f'{package.name}=={package.version}: Missing source distribution.')
        if report_missing_wheels and not package.wheels:
            print(f'{package.name}=={package.version}: Missing wheels.')

        for dist in package.get_distributions():
            dist.load_about_data(dest_dir=dest_dir)
            abpth = os.path.abspath(os.path.join(dest_dir, dist.about_filename))
            if not dist.has_key_metadata():
                print(f'   Missing key ABOUT data in file://{abpth}')
            if 'classifiers' in dist.extra_data:
                print(f'   Dangling classifiers data in file://{abpth}')
            if not dist.validate_checksums(dest_dir):
                print(f'   Invalid checksums in file://{abpth}')
            if not dist.sha1 and dist.md5:
                print(f'   Missing checksums in file://{abpth}')

    check_about(dest_dir=dest_dir)


def compute_normalized_license_expression(declared_licenses):
    if not declared_licenses:
        return
    try:
        from packagedcode import pypi
        return pypi.compute_normalized_license(declared_licenses)
    except ImportError:
        # Scancode is not installed, we join all license strings and return it
        return ' '.join(declared_licenses)
