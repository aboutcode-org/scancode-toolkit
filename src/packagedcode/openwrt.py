
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import os

import attr
from debian_inspector import debcon
from debian_inspector.deps import parse_depends
from debian_inspector.deps import VersionedRelationship
from packageurl import PackageURL

from commoncode import archive
from commoncode import filetype
from commoncode import fileutils
from commoncode.fileutils import as_posixpath
from packagedcode import models
from packagedcode.utils import combine_expressions

"""
Handle OpenWRT packages. These are highly similar to the Debian packages and use
control files with the same RFC822-style format.

Each source package Makefile contains pointers to the upstream sources:
https://github.com/openwrt/openwrt/blob/master/package/network/utils/arptables/Makefile
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class OpenwrtPackage(models.Package):
    default_type = 'openwrt'
    default_web_baseurl = 'https://openwrt.org/packages/pkgdata'
    default_download_baseurl = 'https://downloads.openwrt.org/releases'

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        if self.name:
            return f'{baseurl}/{self.name}'

    def repository_download_url(self, baseurl=default_download_baseurl):
        # TODO: This is rather complex as it depends on several arch and
        # release factors
        pass


@attr.s()
class OpenWrtControlFile(OpenwrtPackage, models.PackageManifest):

    file_patterns = ('control',)

    @classmethod
    def is_manifest(cls, location):
        return (
            filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'control'
        )

    @classmethod
    def recognize(cls, location):
        package_data = debcon.get_paragraph_data_from_file(location)
        yield build_package(cls, package_data)


@attr.s()
class OpenWrtIpkArchive(OpenwrtPackage, models.PackageManifest):

    # NOTEs: this is a tar.gz archive, unlike Debian which use ar archives

    file_patterns = ('*.ipk',)
    extensions = ('.ipk',)

    @classmethod
    def is_manifest(cls, location):
        return filetype.is_file(location) and location.endswith('.ipk')

    @classmethod
    def recognize(cls, location):
        ipk_content = get_ipk_control_content(location)
        if ipk_content:
            package_data = debcon.get_paragraph_data(ipk_content)
            package = build_package(cls, package_data)
            if package:
                yield package


@attr.s()
class OpenWrtInstalledDb(OpenwrtPackage, models.PackageManifest):
    """
    An OpenWRT installed package database.
    """
    file_patterns = ('status',)

    @classmethod
    def is_manifest(cls, location):
        return (
            filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'status'
            and as_posixpath(location).endswith('/usr/lib/opkg/status')
        )

    @classmethod
    def recognize(cls, location):
        opkg_dir = fileutils.parent_directory(location)
        rootfs_dir = fileutils.parent_directory(fileutils.parent_directory(opkg_dir))
        openwrt_version = get_openwrt_version(rootfs_dir)

        installed_package = get_installed_packages(
            opkg_dir=opkg_dir,
            openwrt_version=openwrt_version,
            detect_licenses=False,
        )

        for package  in installed_package:
            yield package

    def populate_installed_files(self, usr_lib_opkg_info_dir):
        """
        Populate the installed_file  attribute given a `usr_lib_opkg_info_dir`
        path to an OpenWRT /usr/lib/opkg/info directory.
        """
        self.installed_files = self.get_list_of_installed_files(usr_lib_opkg_info_dir)

    def get_list_of_installed_files(self, usr_lib_opkg_info_dir):
        """
        Return a list of PackageFile given a `usr_lib_opkg_info_dir` path to a
        OpenWRT /usr/lib/opkg/info/ directory where <package>.list and
        <package>.control files can be found for a package name. We use the the
        .list file for this. It does not seem to contain directories.
        """
        # these files are not arch-specific
        list_file = os.path.join(usr_lib_opkg_info_dir, f'{self.name}.list')
        has_list = os.path.exists(list_file)

        if not has_list:
            return []

        installed_files = []
        directories = set()
        with open(list_file) as info_file:
            for path in info_file:
                path = path.strip()
                # we ignore dirs in general, and we ignore these that would
                # be created as a plain dir when we can
                if not path  or path in ignored_root_dirs:
                    continue

                installed_files.append(models.PackageFile(path=path))
                directories.add(os.path.dirname(path))

        # skip directories when possible
        installed_files = [
            f for f in sorted(installed_files)
            if f.path not in directories
        ]

        return installed_files


def get_openwrt_version(rootfs_dir):
    """
    Return an openwrt version string or None given a ``rootfs_dir`` rootfs
    directory.
    """
    # modern
    #     /etc/openwrt_release
    # DISTRIB_ID='OpenWrt'
    # DISTRIB_RELEASE='19.07.5'
    # DISTRIB_REVISION='r11257-5090152ae3'
    # DISTRIB_TARGET='x86/64'
    # DISTRIB_ARCH='x86_64'
    # DISTRIB_DESCRIPTION='OpenWrt 19.07.5 r11257-5090152ae3'
    # DISTRIB_TAINTS=''

    # old
    #     /etc/openwrt_release
    #
    # DISTRIB_RELEASE='Chaos Calmer'
    # DISTRIB_REVISION='3e6f5da37+r49254'
    # DISTRIB_CODENAME='chaos_calmer'
    # DISTRIB_TARGET='ipq/ipq807x_64'
    # DISTRIB_DESCRIPTION='OpenWrt Chaos Calmer 15.05.1'
    # DISTRIB_TAINTS='no-all busybox override'
    return


def get_installed_packages(
    opkg_dir,
    openwrt_version=None,
    detect_licenses=False,
    **kwargs,
):
    """
    Given a directory to a /usr/lib/opkg dir, yield installed OpenwrtPackage (s)
    for the optional `openwrt_version`.
    """

    base_status_file_loc = os.path.join(opkg_dir, 'status')
    if not os.path.exists(base_status_file_loc):
        return

    usr_lib_opkg_info_dir = os.path.join(opkg_dir, 'info')

    installed_packages = parse_status_file(
        location=base_status_file_loc,
        openwrt_version=openwrt_version,
    )
    for package in installed_packages:
        package.populate_installed_files(usr_lib_opkg_info_dir)
        if detect_licenses:
            package.license_expression = package.compute_normalized_license()
        yield package


def parse_status_file(location, openwrt_version=None, installed_only=True):
    """
    Yield OpenwrtPackage objects from an opkg `status` file or None.
    """
    if not os.path.exists(location):
        raise FileNotFoundError(f'[Errno 2] No such file or directory: {location!r}')

    for pkg_data in debcon.get_paragraphs_data_from_file(location):
        if installed_only:
            status = pkg_data.get('status') or ''
            if 'installed' not in status:
                continue

        package = build_package(pkg_data, openwrt_version=openwrt_version)
        if package:
            yield package


def build_package(cls, package_data, openwrt_version=None):
    """
    Return an OpenwrtPackage object of type cls from a ``package_data`` mapping
    (from an opkg status file or manifest) or None.
    """
    package = cls(
        namespace=openwrt_version,
        name=package_data.get('package'),
        version=package_data.get('version'),
        description=package_data.get('description'),
        size=package_data.get('installed-size') or 0,
        dependencies=get_dependencies(package_data.get('depends'))
    )

    arch = package_data.get('architecture')
    if arch:
        package.qualifiers = dict(arch=arch)

    lic = package_data.get('license')
    lic_files = package_data.get('licensefiles')
    if not lic_files:
        # keep the simple case simple
        package.declared_license = lic
    else:
        lic_files = lic_files.split()
        package.declared_license = dict(license=lic, license_files=lic_files)

    maintainer = package_data.get('maintainer')
    if maintainer:
        name, email = parse_email(maintainer)
        party = models.Party(name=name, role='maintainer', email=email)
        package.parties.append(party)

    section = package_data.get('section')
    if section:
        package.keywords = [section]

    source = package_data.get('source')
    if source:
        source_pkg_purl = PackageURL(
            type=package.type,
            namespace=package.namespace,
            name=package.name,
            version=package.version,
            qualifiers=dict(
                type='source',
                vcs_url=f'https://github.com/openwrt/openwrt/blob/master/{source}',
            ),
            subpath='package/utils/util-linux'
        ).to_string()
        package.source_packages = [source_pkg_purl]

    return package


ignored_root_dirs = {
    '/bin',
    '/data',
    '/dev',
    '/etc',
    '/home',
    '/ini',
    '/lib',
    '/lib64',
    '/mnt',
    '/opt',
    '/proc',
    '/rom',
    '/usr',
    '/usr/lib64',
    '/usr/lib',
    '/sbin',
    '/sys',
    '/tmp',
    '/usr',
    '/var',
    '/www',
}


def get_dependencies(depends, openwrt_version=None):
    """
    Return a list of DependentPackage extracted from a `depends` string.
    """
    if not depends:
        return []
    dep_pkgs = []
    root_rel = parse_depends(depends)

    for rel in root_rel.relationships:
        req = None
        purl = PackageURL(
            type='openwrt',
            namespace=openwrt_version,
            name=rel.name,
        )
        is_resolved = False

        if isinstance(rel, VersionedRelationship):
            req = f'{rel.operator} {rel.version}'
            if rel.operator == '=':
                is_resolved = True
                purl = PackageURL(
                    type='openwrt',
                    namespace=openwrt_version,
                    name=rel.name,
                    version=rel.version
                )

        dep = models.DependentPackage(
            purl=purl.to_string(),
            scope='runtime',
            requirement=req,
            is_resolved=is_resolved,
            is_runtime=True,
            is_optional=False,
        )
        dep_pkgs.append(dep)

    return dep_pkgs


def parse_email(text):
    """
    Return a tuple of (name, email) extracted from a `text` string.
    For example:

    >>> parse_email('Debian TeX Maintainers <debian-tex-maint@lists.debian.org>')

    """
    if not text:
        return None, None
    name, _, email = text.partition('<')
    name = name.strip()
    email = email.strip()
    if not email:
        return name, email
    email.strip('>')
    return name, email


# map license codes in OpenWRT to a scancode license expression
license_mappings = {
    'agpl-3.0': 'agpl-3.0',
    'bsd-2c': 'bsd-simplified',
    'bsd-3-clause': 'bsd-new',
    'bsd-4-clause': 'bsd-original',
    'bsd': 'bsd-simplified',
    'closed': 'proprietary-license',
    'gpl-2.0': 'gpl-2.0',
    'gpl-2.0+': 'gpl-2.0-plus',
    'gpl-3.0': 'gpl-3.0',
    'gpl-3.0+': 'gpl-2.0-plus',
    'gpl-3.0-with-gcc-exception': 'gpl-3.0 WITH gcc-exception-3.1',
    'gplv2': 'gpl-2.0',
    'isc': 'isc',
    'lgpl-2.0': 'lgpl-2.0',
    'lgpl-2.1': 'lgpl-2.1',
    'lgpl-2.1+': 'lgpl-2.1-plus',
    'mit': 'mit',
    'openssl': 'openssl-ssleay',
    'psf': 'python',
    'public-domain': 'public-domain',
    'python-2.0': 'python',
    'zlib': 'zlib',
}


def get_license_expression(text):
    """
    Compute a license expression from a text string.
    """
    licenses = []
    for lic in text.split():
        lic = lic.lower()
        mapped = license_mappings.get(lic)
        if mapped:
            licenses.append(mapped)
        else:
            detected = models.compute_normalized_license(lic)
            licenses.append(detected)

    return str(combine_expressions(licenses))


def compute_normalized_license(declared_license):
    """
    Return a normalized license expression string detected from a
    declared_license which is either a string or a mapping
    """
    if not declared_license:
        return

    if isinstance(declared_license, str):
        # we have a single string which should be mostly an SPDX-like license
        # expression
        lic = declared_license
        license_files = []
    else:
        lic = declared_license.get('license')
        license_files = declared_license.get('licensefiles') or []

    primary_expression = get_license_expression(lic)

    for _licfile in license_files:
        # TODO: do something with these files
        pass

    return primary_expression


def get_ipk_control_content(location):
    """
    Return the text content of a control file extracted from the .ipk file at
    ``location`` or None.
    """
    extract_loc = None
    extract_control_loc = None
    try:
        # Extract first level of tar archive
        extract_loc = fileutils.get_temp_dir(prefix='scancode-extract-')
        abs_location = os.path.abspath(os.path.expanduser(location))
        archive.extract_tar(abs_location, extract_loc)

        extract_control = fileutils.get_temp_dir(prefix='scancode-extract-')
        # The tgz control is the second level of archive.
        control_tgz = os.path.join(extract_loc, 'control.tar.gz')

        if not os.path.exists(control_tgz):
            raise Exception('No control file found in OpenWRT .ipk file.')
        archive.extract_tar(control_tgz, extract_control)
        control_loc = os.path.join(extract_control, 'control')
        if not os.path.exists(control_loc):
            raise Exception('No control file found in OpenWRT .ipk file.')

        with open(control_loc) as ci:
            return ci.read()

    finally:
        if extract_loc:
            fileutils.delete(extract_loc)
        if extract_control_loc:
            fileutils.delete(extract_control_loc)
