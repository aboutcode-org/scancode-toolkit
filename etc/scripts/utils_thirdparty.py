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
import email
import itertools
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib
from collections import defaultdict
from urllib.parse import quote_plus

import attr
import license_expression
import packageurl
import requests
import saneyaml
from commoncode import fileutils
from commoncode.hash import multi_checksums
from commoncode.text import python_safe_name
from packvers import tags as packaging_tags
from packvers import version as packaging_version

import utils_pip_compatibility_tags

"""
Utilities to manage Python thirparty libraries source, binaries and metadata in
local directories and remote repositories.

- download wheels for packages for all each supported operating systems
  (Linux, macOS, Windows) and Python versions (3.x) combinations

- download sources for packages (aka. sdist)

- create, update and download ABOUT, NOTICE and LICENSE metadata for these
  wheels and source distributions

- update pip requirement files based on actually installed packages for
  production and development


Approach
--------

The processing is organized around these key objects:

- A PyPiPackage represents a PyPI package with its name and version and the
  metadata used to populate an .ABOUT file and document origin and license.
  It contains the downloadable Distribution objects for that version:

  - one Sdist source Distribution
  - a list of Wheel binary Distribution

- A Distribution (either a Wheel or Sdist) is identified by and created from its
  filename as well as its name and version.
  A Distribution is fetched from a Repository.
  Distribution metadata can be loaded from and dumped to ABOUT files.

- A Wheel binary Distribution can have Python/Platform/OS tags it supports and
  was built for and these tags can be matched to an Environment.

- An Environment is a combination of a Python version and operating system
  (e.g., platfiorm and ABI tags.) and is represented by the "tags" it supports.

- A plain LinksRepository which is just a collection of URLs scrape from a web
  page such as HTTP diretory listing. It is used either with pip "--find-links"
  option or to fetch ABOUT and LICENSE files.

- A PypiSimpleRepository is a PyPI "simple" index where a HTML page is listing
  package name links. Each such link points to an HTML page listing URLs to all
  wheels and sdsist of all versions of this package.

PypiSimpleRepository and Packages are related through packages name, version and
filenames.

The Wheel models code is partially derived from the mit-licensed pip and the
Distribution/Wheel/Sdist design has been heavily inspired by the packaging-
dists library https://github.com/uranusjr/packaging-dists by Tzu-ping Chung
"""

"""
Wheel downloader

- parse requirement file
- create a TODO queue of requirements to process
- done: create an empty map of processed binary requirements as {package name: (list of versions/tags}


- while we have package reqs in TODO queue, process one requirement:
    - for each PyPI simple index:
        - fetch through cache the PyPI simple index for this package
        - for each environment:
            - find a wheel matching pinned requirement in this index
            - if file exist locally, continue
            - fetch the wheel for env
                - IF pure, break, no more needed for env
            - collect requirement deps from wheel metadata and add to queue
    - if fetched, break, otherwise display error message


"""

TRACE = False
TRACE_DEEP = False
TRACE_ULTRA_DEEP = False

# Supported environments
PYTHON_VERSIONS = "37", "38", "39", "310"

PYTHON_DOT_VERSIONS_BY_VER = {
    "37": "3.7",
    "38": "3.8",
    "39": "3.9",
    "310": "3.10",
}


def get_python_dot_version(version):
    """
    Return a dot version from a plain, non-dot version.
    """
    return PYTHON_DOT_VERSIONS_BY_VER[version]


ABIS_BY_PYTHON_VERSION = {
    "37": ["cp37", "cp37m", "abi3"],
    "38": ["cp38", "cp38m", "abi3"],
    "39": ["cp39", "cp39m", "abi3"],
    "310": ["cp310", "cp310m", "abi3"],
}

PLATFORMS_BY_OS = {
    "linux": [
        "linux_x86_64",
        "manylinux1_x86_64",
        "manylinux2010_x86_64",
        "manylinux2014_x86_64",
    ],
    "macos": [
        "macosx_10_6_intel",
        "macosx_10_6_x86_64",
        "macosx_10_9_intel",
        "macosx_10_9_x86_64",
        "macosx_10_10_intel",
        "macosx_10_10_x86_64",
        "macosx_10_11_intel",
        "macosx_10_11_x86_64",
        "macosx_10_12_intel",
        "macosx_10_12_x86_64",
        "macosx_10_13_intel",
        "macosx_10_13_x86_64",
        "macosx_10_14_intel",
        "macosx_10_14_x86_64",
        "macosx_10_15_intel",
        "macosx_10_15_x86_64",
        "macosx_11_0_x86_64",
        "macosx_11_intel",
        "macosx_11_0_x86_64",
        "macosx_11_intel",
        "macosx_10_9_universal2",
        "macosx_10_10_universal2",
        "macosx_10_11_universal2",
        "macosx_10_12_universal2",
        "macosx_10_13_universal2",
        "macosx_10_14_universal2",
        "macosx_10_15_universal2",
        "macosx_11_0_universal2",
        # 'macosx_11_0_arm64',
    ],
    "windows": [
        "win_amd64",
    ],
}

THIRDPARTY_DIR = "thirdparty"
CACHE_THIRDPARTY_DIR = ".cache/thirdparty"

################################################################################

ABOUT_BASE_URL = "https://thirdparty.aboutcode.org/pypi"
ABOUT_PYPI_SIMPLE_URL = f"{ABOUT_BASE_URL}/simple"
ABOUT_LINKS_URL = f"{ABOUT_PYPI_SIMPLE_URL}/links.html"
PYPI_SIMPLE_URL = "https://pypi.org/simple"
PYPI_INDEX_URLS = (PYPI_SIMPLE_URL, ABOUT_PYPI_SIMPLE_URL)

################################################################################

EXTENSIONS_APP = (".pyz",)
EXTENSIONS_SDIST = (
    ".tar.gz",
    ".zip",
    ".tar.xz",
)
EXTENSIONS_INSTALLABLE = EXTENSIONS_SDIST + (".whl",)
EXTENSIONS_ABOUT = (
    ".ABOUT",
    ".LICENSE",
    ".NOTICE",
)
EXTENSIONS = EXTENSIONS_INSTALLABLE + EXTENSIONS_ABOUT + EXTENSIONS_APP

LICENSEDB_API_URL = "https://scancode-licensedb.aboutcode.org"

LICENSING = license_expression.Licensing()

collect_urls = re.compile('href="([^"]+)"').findall

################################################################################
# Fetch wheels and sources locally
################################################################################


class DistributionNotFound(Exception):
    pass


def download_wheel(name, version, environment, dest_dir=THIRDPARTY_DIR, repos=tuple()):
    """
    Download the wheels binary distribution(s) of package ``name`` and
    ``version`` matching the ``environment`` Environment constraints into the
    ``dest_dir`` directory. Return a list of fetched_wheel_filenames, possibly
    empty.

    Use the first PyPI simple repository from a list of ``repos`` that contains this wheel.
    """
    if TRACE_DEEP:
        print(f"  download_wheel: {name}=={version} for envt: {environment}")

    if not repos:
        repos = DEFAULT_PYPI_REPOS

    fetched_wheel_filenames = []

    for repo in repos:
        package = repo.get_package_version(name=name, version=version)
        if not package:
            if TRACE_DEEP:
                print(f"    download_wheel: No package in {repo.index_url} for {name}=={version}")
            continue
        supported_wheels = list(package.get_supported_wheels(environment=environment))
        if not supported_wheels:
            if TRACE_DEEP:
                print(
                    f"    download_wheel: No supported wheel for {name}=={version}: {environment} "
                )
            continue

        for wheel in supported_wheels:
            if TRACE_DEEP:
                print(
                    f"    download_wheel: Getting wheel from index (or cache): {wheel.download_url}"
                )
            fetched_wheel_filename = wheel.download(dest_dir=dest_dir)
            fetched_wheel_filenames.append(fetched_wheel_filename)

        if fetched_wheel_filenames:
            # do not futher fetch from other repos if we find in first, typically PyPI
            break

    return fetched_wheel_filenames


def download_sdist(name, version, dest_dir=THIRDPARTY_DIR, repos=tuple()):
    """
    Download the sdist source distribution of package ``name`` and ``version``
    into the ``dest_dir`` directory. Return a fetched filename or None.

    Use the first PyPI simple repository from a list of ``repos`` that contains
    this sdist.
    """
    if TRACE:
        print(f"  download_sdist: {name}=={version}")

    if not repos:
        repos = DEFAULT_PYPI_REPOS

    fetched_sdist_filename = None

    for repo in repos:
        package = repo.get_package_version(name=name, version=version)

        if not package:
            if TRACE_DEEP:
                print(f"    download_sdist: No package in {repo.index_url} for {name}=={version}")
            continue
        sdist = package.sdist
        if not sdist:
            if TRACE_DEEP:
                print(f"    download_sdist: No sdist for {name}=={version}")
            continue

        if TRACE_DEEP:
            print(f"    download_sdist: Getting sdist from index (or cache): {sdist.download_url}")
        fetched_sdist_filename = package.sdist.download(dest_dir=dest_dir)

        if fetched_sdist_filename:
            # do not futher fetch from other repos if we find in first, typically PyPI
            break

    return fetched_sdist_filename


################################################################################
#
# Core models
#
################################################################################


@attr.attributes
class NameVer:
    name = attr.ib(
        type=str,
        metadata=dict(help="Python package name, lowercase and normalized."),
    )

    version = attr.ib(
        type=str,
        metadata=dict(help="Python package version string."),
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

    def sortable_name_version(self):
        """
        Return a tuple of values to sort by name, then version.
        This method is a suitable to use as key for sorting NameVer instances.
        """
        return self.normalized_name, packaging_version.parse(self.version)

    @classmethod
    def sorted(cls, namevers):
        return sorted(namevers or [], key=cls.sortable_name_version)


@attr.attributes
class Distribution(NameVer):

    # field names that can be updated from another Distribution or mapping
    updatable_fields = [
        "license_expression",
        "copyright",
        "description",
        "homepage_url",
        "primary_language",
        "notice_text",
        "extra_data",
    ]

    filename = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="File name."),
    )

    path_or_url = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="Path or URL"),
    )

    sha256 = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="SHA256 checksum."),
    )

    sha1 = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="SHA1 checksum."),
    )

    md5 = attr.ib(
        repr=False,
        type=int,
        default=0,
        metadata=dict(help="MD5 checksum."),
    )

    type = attr.ib(
        repr=False,
        type=str,
        default="pypi",
        metadata=dict(help="Package type"),
    )

    namespace = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="Package URL namespace"),
    )

    qualifiers = attr.ib(
        repr=False,
        type=dict,
        default=attr.Factory(dict),
        metadata=dict(help="Package URL qualifiers"),
    )

    subpath = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="Package URL subpath"),
    )

    size = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="Size in bytes."),
    )

    primary_language = attr.ib(
        repr=False,
        type=str,
        default="Python",
        metadata=dict(help="Primary Programming language."),
    )

    description = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="Description."),
    )

    homepage_url = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="Homepage URL"),
    )

    notes = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="Notes."),
    )

    copyright = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="Copyright."),
    )

    license_expression = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="License expression"),
    )

    licenses = attr.ib(
        repr=False,
        type=list,
        default=attr.Factory(list),
        metadata=dict(help="List of license mappings."),
    )

    notice_text = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="Notice text"),
    )

    extra_data = attr.ib(
        repr=False,
        type=dict,
        default=attr.Factory(dict),
        metadata=dict(help="Extra data"),
    )

    @property
    def package_url(self):
        """
        Return a Package URL string of self.
        """
        return str(
            packageurl.PackageURL(
                type=self.type,
                namespace=self.namespace,
                name=self.name,
                version=self.version,
                subpath=self.subpath,
                qualifiers=self.qualifiers,
            )
        )

    @property
    def download_url(self):
        return self.get_best_download_url()

    def get_best_download_url(self, repos=tuple()):
        """
        Return the best download URL for this distribution where best means this
        is the first URL found for this distribution found in the list of
        ``repos``.

        If none is found, return a synthetic PyPI remote URL.
        """

        if not repos:
            repos = DEFAULT_PYPI_REPOS

        for repo in repos:
            package = repo.get_package_version(name=self.name, version=self.version)
            if not package:
                if TRACE:
                    print(
                        f"     get_best_download_url: {self.name}=={self.version} "
                        f"not found in {repo.index_url}"
                    )
                continue
            pypi_url = package.get_url_for_filename(self.filename)
            if pypi_url:
                return pypi_url
            else:
                if TRACE:
                    print(
                        f"     get_best_download_url: {self.filename} not found in {repo.index_url}"
                    )

    def download(self, dest_dir=THIRDPARTY_DIR):
        """
        Download this distribution into `dest_dir` directory.
        Return the fetched filename.
        """
        assert self.filename
        if TRACE_DEEP:
            print(
                f"Fetching distribution of {self.name}=={self.version}:",
                self.filename,
            )

        # FIXME:
        fetch_and_save(
            path_or_url=self.path_or_url,
            dest_dir=dest_dir,
            filename=self.filename,
            as_text=False,
        )
        return self.filename

    @property
    def about_filename(self):
        return f"{self.filename}.ABOUT"

    @property
    def about_download_url(self):
        return f"{ABOUT_BASE_URL}/{self.about_filename}"

    @property
    def notice_filename(self):
        return f"{self.filename}.NOTICE"

    @property
    def notice_download_url(self):
        return f"{ABOUT_BASE_URL}/{self.notice_filename}"

    @classmethod
    def from_path_or_url(cls, path_or_url):
        """
        Return a distribution built from the data found in the filename of a
        ``path_or_url`` string. Raise an exception if this is not a valid
        filename.
        """
        filename = os.path.basename(path_or_url.strip("/"))
        dist = cls.from_filename(filename)
        dist.path_or_url = path_or_url
        return dist

    @classmethod
    def get_dist_class(cls, filename):
        if filename.endswith(".whl"):
            return Wheel
        elif filename.endswith(
            (
                ".zip",
                ".tar.gz",
            )
        ):
            return Sdist
        raise InvalidDistributionFilename(filename)

    @classmethod
    def from_filename(cls, filename):
        """
        Return a distribution built from the data found in a `filename` string.
        Raise an exception if this is not a valid filename
        """
        filename = os.path.basename(filename.strip("/"))
        clazz = cls.get_dist_class(filename)
        return clazz.from_filename(filename)

    def has_key_metadata(self):
        """
        Return True if this distribution has key metadata required for basic attribution.
        """
        if self.license_expression == "public-domain":
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
            notice_file=self.notice_filename if self.notice_text else "",
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
        return {k: v for k, v in attr.asdict(self).items() if v}

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

            if TRACE:
                print(f"Saving ABOUT (and NOTICE) files for: {self}")
            with open(location, "w") as fo:
                fo.write(content)
            return True

        as_about = self.to_about()

        save_if_modified(
            location=os.path.join(dest_dir, self.about_filename),
            content=saneyaml.dump(as_about),
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
                    if not about_data:
                        return False
            else:
                return False
        else:
            about_data = about_filename_or_data

        md5 = about_data.pop("checksum_md5", None)
        if md5:
            about_data["md5"] = md5
        sha1 = about_data.pop("checksum_sha1", None)
        if sha1:
            about_data["sha1"] = sha1
        sha256 = about_data.pop("checksum_sha256", None)
        if sha256:
            about_data["sha256"] = sha256

        about_data.pop("about_resource", None)
        notice_text = about_data.pop("notice_text", None)
        notice_file = about_data.pop("notice_file", None)
        if notice_text:
            about_data["notice_text"] = notice_text
        elif notice_file:
            notice_loc = os.path.join(dest_dir, notice_file)
            if os.path.exists(notice_loc):
                with open(notice_loc) as fi:
                    about_data["notice_text"] = fi.read()
        return self.update(about_data, keep_extra=True)

    def load_remote_about_data(self):
        """
        Fetch and update self with "remote" data Distribution ABOUT file and
        NOTICE file if any. Return True if the data was updated.
        """
        try:
            about_text = CACHE.get(
                path_or_url=self.about_download_url,
                as_text=True,
            )
        except RemoteNotFetchedException:
            return False

        if not about_text:
            return False

        about_data = saneyaml.load(about_text)
        notice_file = about_data.pop("notice_file", None)
        if notice_file:
            try:
                notice_text = CACHE.get(
                    path_or_url=self.notice_download_url,
                    as_text=True,
                )
                if notice_text:
                    about_data["notice_text"] = notice_text
            except RemoteNotFetchedException:
                print(f"Failed to fetch NOTICE file: {self.notice_download_url}")
        return self.load_about_data(about_data)

    def get_checksums(self, dest_dir=THIRDPARTY_DIR):
        """
        Return a mapping of computed checksums for this dist filename is
        `dest_dir`.
        """
        dist_loc = os.path.join(dest_dir, self.filename)
        if os.path.exists(dist_loc):
            return multi_checksums(dist_loc, checksum_names=("md5", "sha1", "sha256"))
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
        for csk in ("md5", "sha1", "sha256"):
            csv = getattr(self, csk)
            rcv = real_checksums.get(csk)
            if csv and rcv and csv != rcv:
                return False
        return True

    def get_license_keys(self):
        try:
            keys = LICENSING.license_keys(
                self.license_expression,
                unique=True,
                simple=True,
            )
        except license_expression.ExpressionParseError:
            return ["unknown"]
        return keys

    def fetch_license_files(self, dest_dir=THIRDPARTY_DIR, use_cached_index=False):
        """
        Fetch license files if missing in `dest_dir`.
        Return True if license files were fetched.
        """
        urls = LinksRepository.from_url(use_cached_index=use_cached_index).links
        errors = []
        extra_lic_names = [l.get("file") for l in self.extra_data.get("licenses", {})]
        extra_lic_names += [self.extra_data.get("license_file")]
        extra_lic_names = [ln for ln in extra_lic_names if ln]
        lic_names = [f"{key}.LICENSE" for key in self.get_license_keys()]
        for filename in lic_names + extra_lic_names:
            floc = os.path.join(dest_dir, filename)
            if os.path.exists(floc):
                continue

            try:
                # try remotely first
                lic_url = get_license_link_for_filename(filename=filename, urls=urls)

                fetch_and_save(
                    path_or_url=lic_url,
                    dest_dir=dest_dir,
                    filename=filename,
                    as_text=True,
                )
                if TRACE:
                    print(f"Fetched license from remote: {lic_url}")

            except:
                try:
                    # try licensedb second
                    lic_url = f"{LICENSEDB_API_URL}/{filename}"
                    fetch_and_save(
                        path_or_url=lic_url,
                        dest_dir=dest_dir,
                        filename=filename,
                        as_text=True,
                    )
                    if TRACE:
                        print(f"Fetched license from licensedb: {lic_url}")

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

        fn = self.filename
        if fn.endswith(".whl"):
            fmt = "zip"
        elif fn.endswith(".tar.gz"):
            fmt = "gztar"
        else:
            fmt = None

        dist = os.path.join(dest_dir, fn)
        with tempfile.TemporaryDirectory(prefix=f"pypi-tmp-extract-{fn}") as td:
            shutil.unpack_archive(filename=dist, extract_dir=td, format=fmt)
            # NOTE: we only care about the first one found in the dist
            # which may not be 100% right
            for pi in fileutils.resource_iter(location=td, with_dirs=False):
                if pi.endswith(
                    (
                        "PKG-INFO",
                        "METADATA",
                    )
                ):
                    with open(pi) as fi:
                        return fi.read()

    def load_pkginfo_data(self, dest_dir=THIRDPARTY_DIR):
        """
        Update self with data loaded from the PKG-INFO file found in the
        archive of this Distribution in `dest_dir`.
        """
        pkginfo_text = self.extract_pkginfo(dest_dir=dest_dir)
        if not pkginfo_text:
            print(f"!!!!PKG-INFO/METADATA not found in {self.filename}")
            return
        raw_data = email.message_from_string(pkginfo_text)

        classifiers = raw_data.get_all("Classifier") or []

        declared_license = [raw_data["License"]] + [
            c for c in classifiers if c.startswith("License")
        ]
        license_expression = get_license_expression(declared_license)
        other_classifiers = [c for c in classifiers if not c.startswith("License")]

        holder = raw_data["Author"]
        holder_contact = raw_data["Author-email"]
        copyright_statement = f"Copyright (c) {holder} <{holder_contact}>"

        pkginfo_data = dict(
            name=raw_data["Name"],
            declared_license=declared_license,
            version=raw_data["Version"],
            description=raw_data["Summary"],
            homepage_url=raw_data["Home-page"],
            copyright=copyright_statement,
            license_expression=license_expression,
            holder=holder,
            holder_contact=holder_contact,
            keywords=raw_data["Keywords"],
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
        return {k: v for k, v in data.items() if v and k in self.updatable_fields}

    def update(self, data, overwrite=False, keep_extra=True):
        """
        Update self with a mapping of `data`. Keep unknown data as extra_data if
        `keep_extra` is True. If `overwrite` is True, overwrite self with `data`
        Return True if any data was updated, False otherwise. Raise an exception
        if there are key data conflicts.
        """
        package_url = data.get("package_url")
        if package_url:
            purl_from_data = packageurl.PackageURL.from_string(package_url)
            purl_from_self = packageurl.PackageURL.from_string(self.package_url)
            if purl_from_data != purl_from_self:
                print(
                    f"Invalid dist update attempt, no same same purl with dist: "
                    f"{self} using data {data}."
                )
                return

        data.pop("about_resource", None)
        dl = data.pop("download_url", None)
        if dl:
            data["path_or_url"] = dl

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
                        raise Exception(f"{self}, {k}, {v}") from e
                    updated = True

            elif keep_extra:
                # note that we always overwrite extra
                extra[k] = v
                updated = True

        self.extra_data.update(extra)

        return updated


def get_license_link_for_filename(filename, urls):
    """
    Return a link for `filename` found in the `links` list of URLs or paths. Raise an
    exception if no link is found or if there are more than one link for that
    file name.
    """
    path_or_url = [l for l in urls if l.endswith(f"/{filename}")]
    if not path_or_url:
        raise Exception(f"Missing link to file: {filename}")
    if not len(path_or_url) == 1:
        raise Exception(f"Multiple links to file: {filename}: \n" + "\n".join(path_or_url))
    return path_or_url[0]


class InvalidDistributionFilename(Exception):
    pass


def get_sdist_name_ver_ext(filename):
    """
    Return a (name, version, extension) if filename is a valid sdist name. Some legacy
    binary builds have weird names. Return False otherwise.

    In particular they do not use PEP440 compliant versions and/or mix tags, os
    and arch names in tarball names and versions:

    >>> assert get_sdist_name_ver_ext("intbitset-1.3.tar.gz")
    >>> assert not get_sdist_name_ver_ext("intbitset-1.3.linux-x86_64.tar.gz")
    >>> assert get_sdist_name_ver_ext("intbitset-1.4a.tar.gz")
    >>> assert get_sdist_name_ver_ext("intbitset-1.4a.zip")
    >>> assert not get_sdist_name_ver_ext("intbitset-2.0.linux-x86_64.tar.gz")
    >>> assert get_sdist_name_ver_ext("intbitset-2.0.tar.gz")
    >>> assert not get_sdist_name_ver_ext("intbitset-2.1-1.src.rpm")
    >>> assert not get_sdist_name_ver_ext("intbitset-2.1-1.x86_64.rpm")
    >>> assert not get_sdist_name_ver_ext("intbitset-2.1.linux-x86_64.tar.gz")
    >>> assert not get_sdist_name_ver_ext("cffi-1.2.0-1.tar.gz")
    >>> assert not get_sdist_name_ver_ext("html5lib-1.0-reupload.tar.gz")
    >>> assert not get_sdist_name_ver_ext("selenium-2.0-dev-9429.tar.gz")
    >>> assert not get_sdist_name_ver_ext("testfixtures-1.8.0dev-r4464.tar.gz")
    """
    name_ver = None
    extension = None

    for ext in EXTENSIONS_SDIST:
        if filename.endswith(ext):
            name_ver, extension, _ = filename.rpartition(ext)
            break

    if not extension or not name_ver:
        return False

    name, _, version = name_ver.rpartition("-")

    if not name or not version:
        return False

    # weird version
    if any(
        w in version
        for w in (
            "x86_64",
            "i386",
        )
    ):
        return False

    # all char versions
    if version.isalpha():
        return False

    # non-pep 440 version
    if "-" in version:
        return False

    # single version
    if version.isdigit() and len(version) == 1:
        return False

    # r1 version
    if len(version) == 2 and version[0] == "r" and version[1].isdigit():
        return False

    # dotless version (but calver is OK)
    if "." not in version and len(version) < 3:
        return False

    # version with dashes selenium-2.0-dev-9429.tar.gz
    if name.endswith(("dev",)) and "." not in version:
        return False
    # version pre or post, old legacy
    if version.startswith(("beta", "rc", "pre", "post", "final")):
        return False

    return name, version, extension


@attr.attributes
class Sdist(Distribution):

    extension = attr.ib(
        repr=False,
        type=str,
        default="",
        metadata=dict(help="File extension, including leading dot."),
    )

    @classmethod
    def from_filename(cls, filename):
        """
        Return a Sdist object built from a filename.
        Raise an exception if this is not a valid sdist filename
        """
        name_ver_ext = get_sdist_name_ver_ext(filename)
        if not name_ver_ext:
            raise InvalidDistributionFilename(filename)

        name, version, extension = name_ver_ext

        return cls(
            type="pypi",
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
        return f"{self.name}-{self.version}.{self.extension}"


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
        re.VERBOSE,
    ).match

    build = attr.ib(
        type=str,
        default="",
        metadata=dict(help="Python wheel build."),
    )

    python_versions = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help="List of wheel Python version tags."),
    )

    abis = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help="List of wheel ABI tags."),
    )

    platforms = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help="List of wheel platform tags."),
    )

    tags = attr.ib(
        repr=False,
        type=set,
        default=attr.Factory(set),
        metadata=dict(help="Set of all tags for this wheel."),
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

        name = wheel_info.group("name").replace("_", "-")
        # we'll assume "_" means "-" due to wheel naming scheme
        # (https://github.com/pypa/pip/issues/1150)
        version = wheel_info.group("ver").replace("_", "-")
        build = wheel_info.group("build")
        python_versions = wheel_info.group("pyvers").split(".")
        abis = wheel_info.group("abis").split(".")
        platforms = wheel_info.group("plats").split(".")

        # All the tag combinations from this file
        tags = {
            packaging_tags.Tag(x, y, z) for x in python_versions for y in abis for z in platforms
        }

        return cls(
            filename=filename,
            type="pypi",
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
        if TRACE_DEEP:
            print()
            print("is_supported_by_tags: tags:", tags)
            print("self.tags:", self.tags)
        return not self.tags.isdisjoint(tags)

    def to_filename(self):
        """
        Return a wheel filename reconstructed from its fields (that may not be
        the same as the original filename.)
        """
        build = f"-{self.build}" if self.build else ""
        pyvers = ".".join(self.python_versions)
        abis = ".".join(self.abis)
        plats = ".".join(self.platforms)
        return f"{self.name}-{self.version}{build}-{pyvers}-{abis}-{plats}.whl"

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
        return "py3" in self.python_versions and "none" in self.abis and "any" in self.platforms


def is_pure_wheel(filename):
    try:
        return Wheel.from_filename(filename).is_pure()
    except:
        return False


@attr.attributes
class PypiPackage(NameVer):
    """
    A Python package contains one or more wheels and one source distribution
    from a repository.
    """

    sdist = attr.ib(
        repr=False,
        type=Sdist,
        default=None,
        metadata=dict(help="Sdist source distribution for this package."),
    )

    wheels = attr.ib(
        repr=False,
        type=list,
        default=attr.Factory(list),
        metadata=dict(help="List of Wheel for this package"),
    )

    def get_supported_wheels(self, environment, verbose=TRACE_ULTRA_DEEP):
        """
        Yield all the Wheel of this package supported and compatible with the
        Environment `environment`.
        """
        envt_tags = environment.tags()
        if verbose:
            print("get_supported_wheels: envt_tags:", envt_tags)
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
        ...    python_versions=['cp38'], abis=['cp38m'],
        ...    platforms=['linux_x86_64'])
        >>> w2 = Wheel(name='bitarray', version='0.8.1', build='',
        ...    python_versions=['cp38'], abis=['cp38m'],
        ...    platforms=['macosx_10_9_x86_64', 'macosx_10_10_x86_64'])
        >>> sd = Sdist(name='bitarray', version='0.8.1')
        >>> package = PypiPackage.package_from_dists(dists=[w1, w2, sd])
        >>> assert package.name == 'bitarray'
        >>> assert package.version == '0.8.1'
        >>> assert package.sdist == sd
        >>> assert package.wheels == [w1, w2]
        """
        dists = list(dists)
        if TRACE_DEEP:
            print(f"package_from_dists: {dists}")
        if not dists:
            return

        reference_dist = dists[0]
        normalized_name = reference_dist.normalized_name
        version = reference_dist.version

        package = PypiPackage(name=normalized_name, version=version)

        for dist in dists:
            if dist.normalized_name != normalized_name:
                if TRACE:
                    print(
                        f"  Skipping inconsistent dist name: expected {normalized_name} got {dist}"
                    )
                continue
            elif dist.version != version:
                dv = packaging_version.parse(dist.version)
                v = packaging_version.parse(version)
                if dv != v:
                    if TRACE:
                        print(
                            f"  Skipping inconsistent dist version: expected {version} got {dist}"
                        )
                    continue

            if isinstance(dist, Sdist):
                package.sdist = dist

            elif isinstance(dist, Wheel):
                package.wheels.append(dist)

            else:
                raise Exception(f"Unknown distribution type: {dist}")

        if TRACE_DEEP:
            print(f"package_from_dists: {package}")

        return package

    @classmethod
    def packages_from_dir(cls, directory):
        """
        Yield PypiPackages built from files found in at directory path.
        """
        base = os.path.abspath(directory)

        paths = [os.path.join(base, f) for f in os.listdir(base) if f.endswith(EXTENSIONS)]

        if TRACE_ULTRA_DEEP:
            print("packages_from_dir: paths:", paths)
        return PypiPackage.packages_from_many_paths_or_urls(paths)

    @classmethod
    def packages_from_many_paths_or_urls(cls, paths_or_urls):
        """
        Yield PypiPackages built from a list of paths or URLs.
        These are sorted by name and then by version from oldest to newest.
        """
        dists = PypiPackage.dists_from_paths_or_urls(paths_or_urls)
        if TRACE_ULTRA_DEEP:
            print("packages_from_many_paths_or_urls: dists:", dists)

        dists = NameVer.sorted(dists)

        for _projver, dists_of_package in itertools.groupby(
            dists,
            key=NameVer.sortable_name_version,
        ):
            package = PypiPackage.package_from_dists(dists_of_package)
            if TRACE_ULTRA_DEEP:
                print("packages_from_many_paths_or_urls", package)
            yield package

    @classmethod
    def dists_from_paths_or_urls(cls, paths_or_urls):
        """
        Return a list of Distribution given a list of
        ``paths_or_urls`` to wheels or source distributions.

        Each Distribution receives two extra attributes:
            - the path_or_url it was created from
            - its filename

        For example:
        >>> paths_or_urls ='''
        ...     /home/foo/bitarray-0.8.1-cp36-cp36m-linux_x86_64.whl
        ...     bitarray-0.8.1-cp36-cp36m-macosx_10_9_x86_64.macosx_10_10_x86_64.whl
        ...     bitarray-0.8.1-cp36-cp36m-win_amd64.whl
        ...     https://example.com/bar/bitarray-0.8.1.tar.gz
        ...     bitarray-0.8.1.tar.gz.ABOUT
        ...     bit.LICENSE'''.split()
        >>> results = list(PypiPackage.dists_from_paths_or_urls(paths_or_urls))
        >>> for r in results:
        ...    print(r.__class__.__name__, r.name, r.version)
        ...    if isinstance(r, Wheel):
        ...       print(" ", ", ".join(r.python_versions), ", ".join(r.platforms))
        Wheel bitarray 0.8.1
          cp36 linux_x86_64
        Wheel bitarray 0.8.1
          cp36 macosx_10_9_x86_64, macosx_10_10_x86_64
        Wheel bitarray 0.8.1
          cp36 win_amd64
        Sdist bitarray 0.8.1
        """
        dists = []
        if TRACE_ULTRA_DEEP:
            print("     ###paths_or_urls:", paths_or_urls)
        installable = [f for f in paths_or_urls if f.endswith(EXTENSIONS_INSTALLABLE)]
        for path_or_url in installable:
            try:
                dist = Distribution.from_path_or_url(path_or_url)
                dists.append(dist)
                if TRACE_DEEP:
                    print(
                        "     ===> dists_from_paths_or_urls:",
                        dist,
                        "\n     ",
                        "with URL:",
                        dist.download_url,
                        "\n     ",
                        "from URL:",
                        path_or_url,
                    )
            except InvalidDistributionFilename:
                if TRACE_DEEP:
                    print(f"     Skipping invalid distribution from: {path_or_url}")
                continue
        return dists

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
    attributes.

    We can use these to pass as `pip download` options and force fetching only
    the subset of packages that match these Environment constraints as opposed
    to the current running Python interpreter constraints.
    """

    python_version = attr.ib(
        type=str,
        default="",
        metadata=dict(help="Python version supported by this environment."),
    )

    operating_system = attr.ib(
        type=str,
        default="",
        metadata=dict(help="operating system supported by this environment."),
    )

    implementation = attr.ib(
        type=str,
        default="cp",
        metadata=dict(help="Python implementation supported by this environment."),
        repr=False,
    )

    abis = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help="List of ABI tags supported by this environment."),
        repr=False,
    )

    platforms = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help="List of platform tags supported by this environment."),
        repr=False,
    )

    @classmethod
    def from_pyver_and_os(cls, python_version, operating_system):
        if "." in python_version:
            python_version = "".join(python_version.split("."))

        return cls(
            python_version=python_version,
            implementation="cp",
            abis=ABIS_BY_PYTHON_VERSION[python_version],
            platforms=PLATFORMS_BY_OS[operating_system],
            operating_system=operating_system,
        )

    def get_pip_cli_options(self):
        """
        Return a list of pip download command line options for this environment.
        """
        options = [
            "--python-version",
            self.python_version,
            "--implementation",
            self.implementation,
        ]
        for abi in self.abis:
            options.extend(["--abi", abi])

        for platform in self.platforms:
            options.extend(["--platform", platform])

        return options

    def tags(self):
        """
        Return a set of all the PEP425 tags supported by this environment.
        """
        return set(
            utils_pip_compatibility_tags.get_supported(
                version=self.python_version or None,
                impl=self.implementation or None,
                platforms=self.platforms or None,
                abis=self.abis or None,
            )
        )


################################################################################
#
# PyPI repo and link index for package wheels and sources
#
################################################################################


@attr.attributes
class PypiSimpleRepository:
    """
    A PyPI repository of Python packages: wheels, sdist, etc. like the public
    PyPI simple index. It is populated lazily based on requested packages names.
    """

    index_url = attr.ib(
        type=str,
        default=PYPI_SIMPLE_URL,
        metadata=dict(help="Base PyPI simple URL for this index."),
    )

    # we keep a nested mapping of PypiPackage that has this shape:
    # {name: {version: PypiPackage, version: PypiPackage, etc}
    # the inner versions mapping is sorted by version from oldest to newest

    packages = attr.ib(
        type=dict,
        default=attr.Factory(lambda: defaultdict(dict)),
        metadata=dict(
            help="Mapping of {name: {version: PypiPackage, version: PypiPackage, etc} available in this repo"
        ),
    )

    fetched_package_normalized_names = attr.ib(
        type=set,
        default=attr.Factory(set),
        metadata=dict(help="A set of already fetched package normalized names."),
    )

    use_cached_index = attr.ib(
        type=bool,
        default=False,
        metadata=dict(
            help="If True, use any existing on-disk cached PyPI index files. Otherwise, fetch and cache."
        ),
    )

    def _get_package_versions_map(self, name):
        """
        Return a mapping of all available PypiPackage version for this package name.
        The mapping may be empty. It is ordered by version from oldest to newest
        """
        assert name
        normalized_name = NameVer.normalize_name(name)
        versions = self.packages[normalized_name]
        if not versions and normalized_name not in self.fetched_package_normalized_names:
            self.fetched_package_normalized_names.add(normalized_name)
            try:
                links = self.fetch_links(normalized_name=normalized_name)
                # note that thsi is sorted so the mapping is also sorted
                versions = {
                    package.version: package
                    for package in PypiPackage.packages_from_many_paths_or_urls(paths_or_urls=links)
                }
                self.packages[normalized_name] = versions
            except RemoteNotFetchedException as e:
                if TRACE:
                    print(f"failed to fetch package name: {name} from: {self.index_url}:\n{e}")

        if not versions and TRACE:
            print(f"WARNING: package {name} not found in repo: {self.index_url}")

        return versions

    def get_package_versions(self, name):
        """
        Return a mapping of all available PypiPackage version as{version:
        package} for this package name. The mapping may be empty but not None.
        It is sorted by version from oldest to newest.
        """
        return dict(self._get_package_versions_map(name))

    def get_package_version(self, name, version=None):
        """
        Return the PypiPackage with name and version or None.
        Return the latest PypiPackage version if version is None.
        """
        if not version:
            versions = list(self._get_package_versions_map(name).values())
            # return the latest version
            return versions and versions[-1]
        else:
            return self._get_package_versions_map(name).get(version)

    def fetch_links(self, normalized_name):
        """
        Return a list of download link URLs found in a PyPI simple index for package
        name using the `index_url` of this repository.
        """
        package_url = f"{self.index_url}/{normalized_name}"
        text = CACHE.get(
            path_or_url=package_url,
            as_text=True,
            force=not self.use_cached_index,
        )
        links = collect_urls(text)
        # TODO: keep sha256
        links = [l.partition("#sha256=") for l in links]
        links = [url for url, _, _sha256 in links]
        return links


PYPI_PUBLIC_REPO = PypiSimpleRepository(index_url=PYPI_SIMPLE_URL)
PYPI_SELFHOSTED_REPO = PypiSimpleRepository(index_url=ABOUT_PYPI_SIMPLE_URL)
DEFAULT_PYPI_REPOS = PYPI_PUBLIC_REPO, PYPI_SELFHOSTED_REPO
DEFAULT_PYPI_REPOS_BY_URL = {r.index_url: r for r in DEFAULT_PYPI_REPOS}


@attr.attributes
class LinksRepository:
    """
    Represents a simple links repository such an HTTP directory listing or an
    HTML page with links.
    """

    url = attr.ib(
        type=str,
        default="",
        metadata=dict(help="Links directory URL"),
    )

    links = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help="List of links available in this repo"),
    )

    use_cached_index = attr.ib(
        type=bool,
        default=False,
        metadata=dict(
            help="If True, use any existing on-disk cached index files. Otherwise, fetch and cache."
        ),
    )

    def __attrs_post_init__(self):
        if not self.links:
            self.links = self.find_links()

    def find_links(self, _CACHE=[]):
        """
        Return a list of link URLs found in the HTML page at `self.url`
        """
        if _CACHE:
            return _CACHE

        links_url = self.url
        if TRACE_DEEP:
            print(f"Finding links from: {links_url}")
        plinks_url = urllib.parse.urlparse(links_url)
        base_url = urllib.parse.SplitResult(
            plinks_url.scheme, plinks_url.netloc, "", "", ""
        ).geturl()

        if TRACE_DEEP:
            print(f"Base URL {base_url}")

        text = CACHE.get(
            path_or_url=links_url,
            as_text=True,
            force=not self.use_cached_index,
        )

        links = []
        for link in collect_urls(text):
            if not link.endswith(EXTENSIONS):
                continue

            plink = urllib.parse.urlsplit(link)

            if plink.scheme:
                # full URL kept as-is
                url = link

            if plink.path.startswith("/"):
                # absolute link
                url = f"{base_url}{link}"

            else:
                # relative link
                url = f"{links_url}/{link}"

            if TRACE_DEEP:
                print(f"Adding URL: {url}")

            links.append(url)

        if TRACE:
            print(f"Found {len(links)} links at {links_url}")
        _CACHE.extend(links)
        return links

    @classmethod
    def from_url(cls, url=ABOUT_BASE_URL, _LINKS_REPO={}, use_cached_index=False):
        if url not in _LINKS_REPO:
            _LINKS_REPO[url] = cls(url=url, use_cached_index=use_cached_index)
        return _LINKS_REPO[url]


################################################################################
# Globals for remote repos to be lazily created and cached on first use for the
# life of the session together with some convenience functions.
################################################################################


def get_local_packages(directory=THIRDPARTY_DIR):
    """
    Return the list of all PypiPackage objects built from a local directory. Return
    an empty list if the package cannot be found.
    """
    return list(PypiPackage.packages_from_dir(directory=directory))


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

    def get(self, path_or_url, as_text=True, force=False):
        """
        Return the content fetched from a ``path_or_url`` through the cache.
        Raise an Exception on errors. Treats the content as text if as_text is
        True otherwise as treat as binary. `path_or_url` can be a path or a URL
        to a file.
        """
        cache_key = quote_plus(path_or_url.strip("/"))
        cached = os.path.join(self.directory, cache_key)

        if force or not os.path.exists(cached):
            if TRACE_DEEP:
                print(f"        FILE CACHE MISS: {path_or_url}")
            content = get_file_content(path_or_url=path_or_url, as_text=as_text)
            wmode = "w" if as_text else "wb"
            with open(cached, wmode) as fo:
                fo.write(content)
            return content
        else:
            if TRACE_DEEP:
                print(f"        FILE CACHE HIT: {path_or_url}")
            return get_local_file_content(path=cached, as_text=as_text)


CACHE = Cache()


def get_file_content(path_or_url, as_text=True):
    """
    Fetch and return the content at `path_or_url` from either a local path or a
    remote URL. Return the content as bytes is `as_text` is False.
    """
    if path_or_url.startswith("https://"):
        if TRACE_DEEP:
            print(f"Fetching: {path_or_url}")
        _headers, content = get_remote_file_content(url=path_or_url, as_text=as_text)
        return content

    elif path_or_url.startswith("file://") or (
        path_or_url.startswith("/") and os.path.exists(path_or_url)
    ):
        return get_local_file_content(path=path_or_url, as_text=as_text)

    else:
        raise Exception(f"Unsupported URL scheme: {path_or_url}")


def get_local_file_content(path, as_text=True):
    """
    Return the content at `url` as text. Return the content as bytes is
    `as_text` is False.
    """
    if path.startswith("file://"):
        path = path[7:]

    mode = "r" if as_text else "rb"
    with open(path, mode) as fo:
        return fo.read()


class RemoteNotFetchedException(Exception):
    pass


def get_remote_file_content(
    url,
    as_text=True,
    headers_only=False,
    headers=None,
    _delay=0,
):
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
    print(f"    DOWNLOADING: {url}")
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
                raise RemoteNotFetchedException(f"Failed HTTP request from {url} with {status}")

        if headers_only:
            return response.headers, None

        return response.headers, response.text if as_text else response.content


def fetch_and_save(
    path_or_url,
    dest_dir,
    filename,
    as_text=True,
):
    """
    Fetch content at ``path_or_url`` URL or path and save this to
    ``dest_dir/filername``. Return the fetched content. Raise an Exception on
    errors. Treats the content as text if as_text is True otherwise as treat as
    binary.
    """
    content = CACHE.get(
        path_or_url=path_or_url,
        as_text=as_text,
    )
    output = os.path.join(dest_dir, filename)
    wmode = "w" if as_text else "wb"
    with open(output, wmode) as fo:
        fo.write(content)
    return content


################################################################################
#
# Functions to update or fetch ABOUT and license files
#
################################################################################


def clean_about_files(
    dest_dir=THIRDPARTY_DIR,
):
    """
    Given a thirdparty dir, clean ABOUT files
    """
    local_packages = get_local_packages(directory=dest_dir)
    for local_package in local_packages:
        for local_dist in local_package.get_distributions():
            local_dist.load_about_data(dest_dir=dest_dir)
            local_dist.set_checksums(dest_dir=dest_dir)

            if "classifiers" in local_dist.extra_data:
                local_dist.extra_data.pop("classifiers", None)
                local_dist.save_about_and_notice_files(dest_dir)


def fetch_abouts_and_licenses(dest_dir=THIRDPARTY_DIR, use_cached_index=False):
    """
    Given a thirdparty dir, add missing ABOUT. LICENSE and NOTICE files using
    best efforts:

    - use existing ABOUT files
    - try to load existing remote ABOUT files
    - derive from existing distribution with same name and latest version that
      would have such ABOUT file
    - extract ABOUT file data from distributions PKGINFO or METADATA files

    Use available existing on-disk cached index if use_cached_index is True.
    """

    def get_other_dists(_package, _dist):
        """
        Return a list of all the dists from `_package` that are not the `_dist`
        object
        """
        return [d for d in _package.get_distributions() if d != _dist]

    local_packages = get_local_packages(directory=dest_dir)
    packages_by_name = defaultdict(list)
    for local_package in local_packages:
        distributions = list(local_package.get_distributions())
        distribution = distributions[0]
        packages_by_name[distribution.name].append(local_package)

    for local_package in local_packages:
        for local_dist in local_package.get_distributions():
            local_dist.load_about_data(dest_dir=dest_dir)
            local_dist.set_checksums(dest_dir=dest_dir)

            # if has key data we may look to improve later, but we can move on
            if local_dist.has_key_metadata():
                local_dist.save_about_and_notice_files(dest_dir=dest_dir)
                local_dist.fetch_license_files(dest_dir=dest_dir, use_cached_index=use_cached_index)
                continue

            # lets try to get from another dist of the same local package
            for otherd in get_other_dists(local_package, local_dist):
                updated = local_dist.update_from_other_dist(otherd)
                if updated and local_dist.has_key_metadata():
                    break

            # if has key data we may look to improve later, but we can move on
            if local_dist.has_key_metadata():
                local_dist.save_about_and_notice_files(dest_dir=dest_dir)
                local_dist.fetch_license_files(dest_dir=dest_dir, use_cached_index=use_cached_index)
                continue

            # try to get another version of the same package that is not our version
            other_local_packages = [
                p
                for p in packages_by_name[local_package.name]
                if p.version != local_package.version
            ]
            other_local_version = other_local_packages and other_local_packages[-1]
            if other_local_version:
                latest_local_dists = list(other_local_version.get_distributions())
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
                    local_dist.fetch_license_files(
                        dest_dir=dest_dir, use_cached_index=use_cached_index
                    )
                    continue

            # lets try to fetch remotely
            local_dist.load_remote_about_data()

            # if has key data we may look to improve later, but we can move on
            if local_dist.has_key_metadata():
                local_dist.save_about_and_notice_files(dest_dir=dest_dir)
                local_dist.fetch_license_files(dest_dir=dest_dir, use_cached_index=use_cached_index)
                continue

            # try to get a latest version of the same package that is not our version
            # and that is in our self hosted repo
            lpv = local_package.version
            lpn = local_package.name

            other_remote_packages = [
                p for v, p in PYPI_SELFHOSTED_REPO.get_package_versions(lpn).items() if v != lpv
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
                    local_dist.fetch_license_files(
                        dest_dir=dest_dir, use_cached_index=use_cached_index
                    )
                    continue

            # try to get data from pkginfo (no license though)
            local_dist.load_pkginfo_data(dest_dir=dest_dir)

            # FIXME: save as this is the last resort for now in all cases
            # if local_dist.has_key_metadata() or not local_dist.has_key_metadata():
            local_dist.save_about_and_notice_files(dest_dir)

            lic_errs = local_dist.fetch_license_files(dest_dir, use_cached_index=use_cached_index)

            if not local_dist.has_key_metadata():
                print(f"Unable to add essential ABOUT data for: {local_dist}")
            if lic_errs:
                lic_errs = "\n".join(lic_errs)
                print(f"Failed to fetch some licenses:: {lic_errs}")


################################################################################
#
# Functions to build new Python wheels including native on multiple OSes
#
################################################################################


def call(args, verbose=TRACE):
    """
    Call args in a subprocess and display output on the fly if ``trace`` is True.
    Return a tuple of (returncode, stdout, stderr)
    """
    if TRACE_DEEP:
        print("Calling:", " ".join(args))
    with subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8"
    ) as process:

        stdouts = []
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            stdouts.append(line)
            if verbose:
                print(line.rstrip(), flush=True)

        stdout, stderr = process.communicate()
        if not stdout.strip():
            stdout = "\n".join(stdouts)
        return process.returncode, stdout, stderr


def download_wheels_with_pip(
    requirements_specifiers=tuple(),
    requirements_files=tuple(),
    environment=None,
    dest_dir=THIRDPARTY_DIR,
    index_url=PYPI_SIMPLE_URL,
    links_url=ABOUT_LINKS_URL,
):
    """
    Fetch binary wheel(s) using pip for the ``envt`` Environment given a list of
    pip ``requirements_files`` and a list of ``requirements_specifiers`` string
    (such as package names or as name==version).
    Return a tuple of (list of downloaded files, error string).
    Do NOT fail on errors, but return an error message on failure.
    """

    cli_args = [
        "pip",
        "download",
        "--only-binary",
        ":all:",
        "--dest",
        dest_dir,
        "--index-url",
        index_url,
        "--find-links",
        links_url,
        "--no-color",
        "--progress-bar",
        "off",
        "--no-deps",
        "--no-build-isolation",
        "--verbose",
        #         "--verbose",
    ]

    if environment:
        eopts = environment.get_pip_cli_options()
        cli_args.extend(eopts)
    else:
        print("WARNING: no download environment provided.")

    cli_args.extend(requirements_specifiers)
    for req_file in requirements_files:
        cli_args.extend(["--requirement", req_file])

    if TRACE:
        print(f"Downloading wheels using command:", " ".join(cli_args))

    existing = set(os.listdir(dest_dir))
    error = False
    try:
        returncode, _stdout, stderr = call(cli_args, verbose=True)
        if returncode != 0:
            error = stderr
    except Exception as e:
        error = str(e)

    if error:
        print()
        print("###########################################################################")
        print("##################### Failed to fetch all wheels ##########################")
        print("###########################################################################")
        print(error)
        print()
        print("###########################################################################")

    downloaded = existing ^ set(os.listdir(dest_dir))
    return sorted(downloaded), error


################################################################################
#
# Functions to check for problems
#
################################################################################


def check_about(dest_dir=THIRDPARTY_DIR):
    try:
        subprocess.check_output(f"venv/bin/about check {dest_dir}".split())
    except subprocess.CalledProcessError as cpe:
        print()
        print("Invalid ABOUT files:")
        print(cpe.output.decode("utf-8", errors="replace"))


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
            print(f"{package.name}=={package.version}: Missing source distribution.")
        if report_missing_wheels and not package.wheels:
            print(f"{package.name}=={package.version}: Missing wheels.")

        for dist in package.get_distributions():
            dist.load_about_data(dest_dir=dest_dir)
            abpth = os.path.abspath(os.path.join(dest_dir, dist.about_filename))
            if not dist.has_key_metadata():
                print(f"   Missing key ABOUT data in file://{abpth}")
            if "classifiers" in dist.extra_data:
                print(f"   Dangling classifiers data in file://{abpth}")
            if not dist.validate_checksums(dest_dir):
                print(f"   Invalid checksums in file://{abpth}")
            if not dist.sha1 and dist.md5:
                print(f"   Missing checksums in file://{abpth}")

    check_about(dest_dir=dest_dir)


def get_license_expression(declared_licenses):
    """
    Return a normalized license expression or None.
    """
    if not declared_licenses:
        return
    try:
        from packagedcode.licensing import get_only_expression_from_extracted_license

        return get_only_expression_from_extracted_license(declared_licenses)
    except ImportError:
        # Scancode is not installed, clean and join all the licenses
        lics = [python_safe_name(l).lower() for l in declared_licenses]
        return " AND ".join(lics).lower()
