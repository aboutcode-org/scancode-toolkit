#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import os
import sys
from collections import namedtuple
from pathlib import Path

from license_expression import Licensing

from packagedcode import models
from packagedcode import nevra
from packagedcode.pyrpm import RPM
from packagedcode.rpm_installed import collect_installed_rpmdb_xmlish_from_rpmdb_loc
from packagedcode.rpm_installed import parse_rpm_xmlish
from packagedcode.utils import build_description
from packagedcode.utils import get_ancestor

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

"""
Support for RPMs, installed databases and spec files.
"""
# TODO: retrieve dependencies

# TODO: parse spec files see:
#  http://www.faqs.org/docs/artu/ch05s02.html#id2906931%29.)
#  http://code.activestate.com/recipes/436229-record-jar-parser/

# TODO:  license and docs are typically at usr/share/doc/packages/<package name>/* and should be used
# packages_doc_dir = os.path.join(root_dir, 'usr/share/doc/packages')
# note that we also have file flags that can tell us which file is a license and doc.

RPM_TAGS = (
    'name',
    'epoch',
    'version',
    'release',
    'arch',
    'os',
    'summary',
    # the full description is often a long text
    'description',
    'distribution',
    'vendor',
    'license',
    'packager',
    'group',
    'url',
    'source_rpm',
    'dist_url',
    'is_binary',
)

RPMtags = namedtuple('RPMtags', list(RPM_TAGS))


def get_rpm_tags(location, include_desc=False):
    """
    Return an RPMtags object for the file at location or None.
    Include the long RPM description value if `include_desc` is True.
    """
    with open(location, 'rb') as rpmf:
        rpm = RPM(rpmf)
        tags = {k: v for k, v in rpm.to_dict().items() if k in RPM_TAGS}
        if not include_desc:
            tags['description'] = None
        return RPMtags(**tags)


class EVR(namedtuple('EVR', 'epoch version release')):
    """
    The RPM Epoch, Version, Release tuple.
    """

    def __new__(self, version, release=None, epoch=None):
        """
        note: the sort order of the named tuple is the sort order.
        But for creation we put the rarely used epoch last with a default to None.
        """
        if epoch and epoch.strip() and not epoch.isdigit():
            raise ValueError('Invalid epoch: must be a number or empty.')
        if not version:
            raise ValueError('Version is required: {}'.format(repr(version)))

        return super().__new__(EVR, epoch, version, release)

    def __str__(self, *args, **kwargs):
        return self.to_string()

    def to_string(self):
        if self.release:
            vr = f'{self.version}-{self.release}'
        else:
            vr = self.version

        if self.epoch:
            vr = ':'.join([self.epoch, vr])
        return vr


# TODO: add dependencies!!!
class BaseRpmInstalledDatabaseHandler(models.DatafileHandler):

    @classmethod
    def parse(cls, location):
        # we receive the location of the Package database file and we need to
        # scan the parent which is the directory that contains the rpmdb
        loc_path = Path(location)
        rpmdb_loc = str(loc_path.parent)

        # dump and parse the rpmdb to XMLish
        xmlish_loc = collect_installed_rpmdb_xmlish_from_rpmdb_loc(rpmdb_loc=rpmdb_loc)
        package_data = parse_rpm_xmlish(
            location=xmlish_loc,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )
        # TODO: package_data.namespace = cls.default_package_namespace
        return package_data

    @classmethod
    def compute_normalized_license(cls, package):
        _declared, detected = detect_declared_license(package.declared_license)
        return detected

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        # get the root resource of the rootfs
        # take the 1st pattern as a reference
        # for instance: '*usr/lib/sysimage/rpm/Packages.db'
        base_path_patterns = cls.path_patterns[0]

        # how many levels up are there to the root of the rootfs?
        levels_up = len(base_path_patterns.split('/'))

        root_resource = get_ancestor(
            levels_up=levels_up,
            resource=resource,
            codebase=codebase,
        )

        package = models.Package.from_package_data(
            package_data=package_data,
            datafile_path=resource.path,
        )
        package_uid = package.package_uid

        root_path = root_resource.path
        # get etc/os-release for namespace
        namespace = None
        os_release_rootfs_paths = ('etc/os-release', 'usr/lib/os-release',)
        for os_release_rootfs_path in os_release_rootfs_paths:
            os_release_path = '/'.join([root_path, os_release_rootfs_path])
            os_release_res = codebase.get_resource(os_release_path)
            if not os_release_res:
                continue
            # there can be only one distro
            distro = os_release_res.package_data and os_release_res.package_data[0]
            if distro:
                namespace = distro.namespace
                break

        package.namespace = namespace

        # detect license
        _declared, detected = detect_declared_license(package.declared_license)
        package.license_expression = detected

        # tag files from refs
        resources = []
        missing_file_references = []
        # a file ref extends from the root of the filesystem
        for ref in package.file_references:
            ref_path = '/'.join([root_path, ref.path])
            res = codebase.get_resource(ref_path)
            if not res:
                missing_file_references.append(ref)
            else:
                if package_uid:
                    # path is found and processed: remove it, so we can check if we
                    # found all of them
                    resources.append(res)

        # if we have left over file references, add these to extra data
        if missing_file_references:
            missing = sorted(missing_file_references, key=lambda r: r.path)
            package.extra_data['missing_file_references'] = missing

        yield package

        # yield deps
        dependent_packages = package_data.dependencies
        if dependent_packages:
            for dep in models.Dependency.from_dependent_packages(
                dependent_packages=dependent_packages,
                datafile_path=resource.path,
                datasource_id=package_data.datasource_id,
                package_uid=package_uid,
            ):
                if not dep.namespace:
                    dep.namespace = namespace
                yield dep

        for resource in resources:
            package_adder(package_uid, resource, codebase)
            yield resource


# TODO: add dependencies!!!
class RpmInstalledNdbDatabaseHandler(BaseRpmInstalledDatabaseHandler):
    # used by recent Suse
    datasource_id = 'rpm_installed_database_ndb'
    path_patterns = ('*usr/lib/sysimage/rpm/Packages.db',)
    default_package_type = 'rpm'
    default_package_namespace = 'TBD'
    description = 'RPM installed package NDB database'
    documentation_url = 'https://fedoraproject.org/wiki/Changes/NewRpmDBFormat'


# TODO: add dependencies!!!
class RpmInstalledSqliteDatabaseHandler(BaseRpmInstalledDatabaseHandler):
    # used by newer RHEL/CentOS/Fedora
    datasource_id = 'rpm_installed_database_sqlite'
    path_patterns = ('*var/lib/rpm/rpmdb.sqlite',)
    filetypes = ('berkeley',)
    default_package_type = 'rpm'
    default_package_namespace = 'TBD'
    description = 'RPM installed package SQLite database'
    documentation_url = 'https://fedoraproject.org/wiki/Changes/Sqlite_Rpmdb'


# TODO: add dependencies!!!
class RpmInstalledBdbDatabaseHandler(BaseRpmInstalledDatabaseHandler):
    # used by legacy RHEL/CentOS/Fedora/Suse
    datasource_id = 'rpm_installed_database_bdb'
    path_patterns = ('*var/lib/rpm/Packages',)
    filetypes = ('berkeley',)
    default_package_type = 'rpm'
    default_package_namespace = 'TBD'
    description = 'RPM installed package BDB database'
    documentation_url = 'https://man7.org/linux/man-pages/man8/rpmdb.8.html'


# TODO: implement me!!@
class RpmSpecfileHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'rpm_spefile'
    path_patterns = ('*.spec',)
    default_package_type = 'rpm'
    default_package_namespace = 'TBD'
    description = 'RPM specfile'
    documentation_url = 'https://en.wikipedia.org/wiki/RPM_Package_Manager'


# TODO: add dependencies!!!
class RpmArchiveHandler(models.DatafileHandler):
    datasource_id = 'rpm_archive'
    path_patterns = ('*.rpm', '*.src.rpm', '*.srpm', '*.mvl', '*.vip',)
    filetypes = ('rpm',)
    default_package_type = 'rpm'
    default_package_namespace = 'TBD'
    description = 'RPM package archive'
    documentation_url = 'https://en.wikipedia.org/wiki/RPM_Package_Manager'

    @classmethod
    def compute_normalized_license(cls, package):
        _declared, detected = detect_declared_license(package.declared_license)
        return detected

    @classmethod
    def parse(cls, location):
        rpm_tags = get_rpm_tags(location, include_desc=True)

        if TRACE: logger_debug('recognize: rpm_tags', rpm_tags)
        if not rpm_tags:
            return

        name = rpm_tags.name

        try:
            epoch = rpm_tags.epoch and int(rpm_tags.epoch) or None
        except ValueError:
            epoch = None

        evr = EVR(
            version=rpm_tags.version or None,
            release=rpm_tags.release or None,
            epoch=epoch).to_string()

        qualifiers = {}
        os = rpm_tags.os
        if os and os.lower() != 'linux':
            qualifiers['os'] = os

        arch = rpm_tags.arch
        if arch:
            qualifiers['arch'] = arch

        source_packages = []
        if rpm_tags.source_rpm:
            sepoch, sname, sversion, srel, sarch = nevra.from_name(rpm_tags.source_rpm)
            src_evr = EVR(sversion, srel, sepoch).to_string()
            src_qualifiers = {}
            if sarch:
                src_qualifiers['arch'] = sarch

            src_purl = models.PackageURL(
                type=cls.default_package_type,
                # TODO: namespace=cls.default_package_namespace,
                name=sname,
                version=src_evr,
                qualifiers=src_qualifiers
            ).to_string()

            if TRACE: logger_debug('recognize: source_rpm', src_purl)
            source_packages = [src_purl]

        parties = []

        # TODO: also use me to craft a namespace!!!
        # TODO: assign a namespace to Package URL based on distro names.
        # CentOS
        # Fedora Project
        # OpenMandriva Lx
        # openSUSE Tumbleweed
        # Red Hat

        if rpm_tags.distribution:
            parties.append(models.Party(name=rpm_tags.distribution, role='distributor'))

        if rpm_tags.vendor:
            parties.append(models.Party(name=rpm_tags.vendor, role='vendor'))

        description = build_description(summary=rpm_tags.summary, description=rpm_tags.description)

        if TRACE:
            data = dict(
                name=name,
                version=evr,
                description=description or None,
                homepage_url=rpm_tags.url or None,
                parties=parties,
                declared_license=rpm_tags.license or None,
                source_packages=source_packages,
            )
            logger_debug('recognize: data to create a package:\n', data)

        package = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            # TODO: namespace=cls.default_package_namespace,
            name=name,
            version=evr,
            description=description or None,
            homepage_url=rpm_tags.url or None,
            parties=parties,
            declared_license=rpm_tags.license or None,
            source_packages=source_packages,
        )

        if TRACE:
            logger_debug('recognize: created package:\n', package)

        yield package

############################################################################
# FIXME: this license detection code is mostly copied from debian_copyright.py and alpine.py
# See https://github.com/rpminspect/rpminspect-data-fedora/blob/master/licenses/fedora.json for some mapping
############################################################################


def detect_declared_license(declared):
    """
    Return a tuple of (declared license, detected license expression) from a
    declared license. Both can be None.
    """
    declared = normalize_and_cleanup_declared_license(declared)
    if not declared:
        return None, None

    # apply multiple license detection in sequence
    detected = detect_using_name_mapping(declared)
    if detected:
        return declared, detected

    # cases of using a comma are for an AND
    normalized_declared = declared.replace(',', ' and ')
    detected = models.compute_normalized_license(normalized_declared)
    return declared, detected


def normalize_and_cleanup_declared_license(declared):
    """
    Return a cleaned and normalized declared license.
    """
    if declared:
        # normalize spaces
        declared = ' '.join(declared.split())
        return declared


def detect_using_name_mapping(declared, licensing=Licensing()):
    """
    Return a license expression detected from a `declared` license string.
    """
    # TODO: use RPM symbology
    declared = declared.lower()
    detected = get_declared_to_detected().get(declared)
    if detected:
        return str(licensing.parse(detected, simple=True))


_DECLARED_TO_DETECTED = None


def get_declared_to_detected(data_file=None):
    """
    Return a mapping of declared to detected license expression cached and
    loaded from a tab-separated text file, all lowercase, normalized for spaces.

    This data file is from license keys used in RPMs files and should be
    derived from a large collection of RPMs files.
    """
    global _DECLARED_TO_DETECTED
    if _DECLARED_TO_DETECTED is not None:
        return _DECLARED_TO_DETECTED

    _DECLARED_TO_DETECTED = {}
    if not data_file:
        data_file = os.path.join(os.path.dirname(__file__), 'rpm_licenses.txt')
    with open(data_file) as df:
        for line in df:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            decl, _, detect = line.partition('\t')
            if detect and detect.strip():
                decl = decl.strip()
                _DECLARED_TO_DETECTED[decl] = detect
    return _DECLARED_TO_DETECTED


ALGO_BY_ID = {
    None: 'md5',
    0: 'md5',
    2: 'sha1',
    8: 'sha256',
    9: 'sha384',
    10: 'sha512',
}


def get_digest_algo(rpm_tags):
    """
    Return a string representing a digest algorightm given an ``rpm_tags``
    RPMtags object
    """
    fda = rpm_tags.files_digest_algo
    return ALGO_BY_ID.get(fda, 'md5',)
