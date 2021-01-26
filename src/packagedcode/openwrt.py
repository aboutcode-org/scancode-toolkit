#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import os

import attr
from debut import debcon
from debut.deps import parse_depends
from debut.deps import VersionedRelationship
from packageurl import PackageURL

from commoncode import filetype
from commoncode import fileutils
from commoncode.datautils import List
from packagedcode import models
from packagedcode.utils import combine_expressions
from commoncode import archive
from commoncode.fileutils import as_posixpath

"""
Handle OpenWRT packages. These are highly similar to the Debian packages and use
control files.


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
    # metafiles = ('*.control',)
    # this is a tar.gz archive, unlike Debian which use ar archives
    extensions = ('.ipk',)
    filetypes = ('gzip compressed data',)
    mimetypes = ('application/gzip',)
    installed_dbs = ('/usr/lib/opkg/status',)
    default_type = 'openwrt'

    installed_files = List(
        item_type=models.PackageFile,
        label='installed files',
        help='List of files installed by this package.')

    default_web_baseurl = 'https://openwrt.org/packages/pkgdata'
    default_download_baseurl = 'https://downloads.openwrt.org/releases'

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return f'{self.default_web_baseurl}/{self.name}'

    @classmethod
    def recognize(cls, location):
        for package in parse(location):
            yield package

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)

    def to_dict(self, _detailed=True, **kwargs):
        data = models.Package.to_dict(self, **kwargs)
        if _detailed:
            #################################################
            # remove temporary fields
            data['installed_files'] = [istf.to_dict() for istf in (self.installed_files or [])]
            #################################################
        else:
            #################################################
            # remove temporary fields
            data.pop('installed_files', None)
            #################################################

        return data

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
        installed_files = [f for f in sorted(installed_files) if f.path not in directories]

        return installed_files


def is_control_file(location):
    return (
        filetype.is_file(location)
        and fileutils.file_extension(location).lower() == '.control'
    )


def is_ipk(location):
    return (
        filetype.is_file(location)
        and fileutils.file_extension(location).lower() == '.ipk'
    )


def is_status_file(location, include_path=False):
    has_name = (
        filetype.is_file(location)
        and fileutils.file_name(location).lower() == 'status'
    )
    if include_path:
        posix_location = as_posixpath(location)
        return has_name and posix_location.endswith('/usr/lib/opkg/status')
    else:
        return has_name


def parse(location):
    """
    Return a Package object from an ipk or control file or None.
    """
    if is_control_file(location):
        package_data = debcon.get_paragraph_data_from_file(location)
        yield build_package(package_data)

    elif is_ipk(location):
        ipk_content = get_ipk_control_content(location)
        if ipk_content:
            package_data = debcon.get_paragraph_data(ipk_content)
            package = build_package(package_data)
            if package:
                yield package

    elif is_status_file(location, include_path=True):
        opkg_dir = fileutils.parent_directory(location)
        rootfs_dir = fileutils.parent_directory(fileutils.parent_directory(opkg_dir))
        openwrt_version = get_openwrt_version(rootfs_dir)
        for package  in get_installed_packages(opkg_dir=opkg_dir, openwrt_version=openwrt_version, detect_licenses=False):
            yield package


def get_openwrt_version(rootfs_dir):
    """
    Return an openwrt version string  or None
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


def get_installed_packages(opkg_dir, openwrt_version=None, detect_licenses=False, **kwargs):
    """
    Given a directory to a /usr/lib/opkg dir, yield installed OpenwrtPackage (s) for the
    optional `openwrt_version`.
    """

    base_status_file_loc = os.path.join(opkg_dir, 'status')
    if not os.path.exists(base_status_file_loc):
        return

    usr_lib_opkg_info_dir = os.path.join(opkg_dir, 'info')

    for package in parse_status_file(base_status_file_loc, openwrt_version=openwrt_version):
        package.populate_installed_files(usr_lib_opkg_info_dir)
        if detect_licenses:
            package.license_expression = package.compute_normalized_license()
        yield package


def parse_status_file(location, openwrt_version=None, installed_only=True):
    """
    Yield OpenwrtPackage objects from an opkg `status` file or None.
    """
    if not os.path.exists(location):
        raise FileNotFoundError('[Errno 2] No such file or directory: {}'.format(repr(location)))
    if not is_status_file(location):
        return

    for pkg_data in debcon.get_paragraphs_data_from_file(location):
        if installed_only:
            status = pkg_data.get('status') or ''
            if 'installed' not in status:
                continue

        package = build_package(pkg_data, openwrt_version=openwrt_version)
        if package:
            yield package


def build_package(package_data, openwrt_version=None):
    """
    Return an OpenwrtPackage object from a package_data mapping (from an opkg
    status file) or None.
    """
    package = OpenwrtPackage(
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
            qualifiers=dict(type='source', vcs_url=f'https://github.com/openwrt/openwrt/blob/master/{source}'),
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
        # we have a single string which should be mostly an SPDX-like license expression
        lic = declared_license
        license_files = []
    else:
        lic = declared_license.get('license')
        license_files = declared_license.get('licensefiles') or []

    primary_expression = get_license_expression(lic)

    for _licfile in license_files:
        # TODO: do somthing with these files
        pass

    return primary_expression


def get_ipk_control_content(location):
    """
    Return the text content of an extracted control file from the .ipk file at
    location or None.
    """
    if not is_ipk(location):
        return

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

