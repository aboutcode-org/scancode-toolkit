#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import logging
from pathlib import Path

from commoncode import fileutils
from debian_inspector.debcon import get_paragraph_data_from_file
from debian_inspector.debcon import get_paragraphs_data_from_file
from debian_inspector.package import DebArchive
from packageurl import PackageURL

from packagedcode import models
from packagedcode.utils import get_ancestor

"""
Handle Debian package archives, control files and installed databases.
"""

SCANCODE_DEBUG_PACKAGE_API = os.environ.get('SCANCODE_DEBUG_PACKAGE_API', False)

TRACE = SCANCODE_DEBUG_PACKAGE_API


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, str) and a or repr(a) for a in args)
        )

# TODO: add dependencies


# TODO: introspect archive
class DebianDebPackageHandler(models.DatafileHandler):
    datasource_id = 'debian_deb'
    default_package_type = 'deb'
    path_patterns = ('*.deb',)
    filetypes = ('debian binary package',)
    description = 'Debian binary package archive'
    documentation_url = 'https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html'

    @classmethod
    def parse(cls, location):
        yield build_package_data_from_package_filename(
            filename=fileutils.file_name(location),
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        # only assign this resource
        return models.DatafileHandler.assign_package_to_resources(package, resource, codebase, package_adder)


# TODO: introspect archive
class DebianSourcePackageMetadataTarballHandler(models.DatafileHandler):
    datasource_id = 'debian_source_metadata_tarball'
    default_package_type = 'deb'
    path_patterns = ('*.debian.tar.xz', '*.debian.tar.gz',)
    filetypes = ('posix tar archive',)
    description = 'Debian source package metadata archive'
    documentation_url = 'https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html'

    @classmethod
    def parse(cls, location):
        # strip extension
        filename, _, _ = location.rpartition('.tar')
        yield build_package_data_from_package_filename(
            filename=filename,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        # only assign this resource
        return models.DatafileHandler.assign_package_to_resources(package, resource, codebase, package_adder)


# TODO: introspect archive
class DebianSourcePackageTarballHandler(models.DatafileHandler):
    datasource_id = 'debian_original_source_tarball'
    default_package_type = 'deb'
    path_patterns = ('*.orig.tar.xz', '*.orig.tar.gz',)
    filetypes = ('posix tar archive',)
    description = 'Debian package original source archive'
    documentation_url = 'https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html'

    @classmethod
    def parse(cls, location):
        # strip extension
        filename, _, _ = location.rpartition('.tar')
        yield build_package_data_from_package_filename(
            filename=filename,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        # only assign this resource
        return models.DatafileHandler.assign_package_to_resources(package, resource, codebase, package_adder)


# TODO: also look into neighboring md5sum and data.tarball copyright files!!!
class DebianControlFileInExtractedDebHandler(models.DatafileHandler):
    datasource_id = 'debian_control_extracted_deb'
    default_package_type = 'deb'
    path_patterns = ('*/control.tar.gz-extract/control',)
    description = 'Debian control file - extracted layout'
    documentation_url = 'https://www.debian.org/doc/debian-policy/ch-controlfields.html'

    @classmethod
    def parse(cls, location):
        # TODO: we cannot know the distro from the name only
        yield build_package_data(
            debian_data=get_paragraph_data_from_file(location=location),
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        # two levels up
        root = resource.parent(codebase).parent(codebase)
        if root:
            return models.DatafileHandler.assign_package_to_resources(package, root, codebase, package_adder)


# TODO: also look into neighboring copyright files!!!
class DebianControlFileInSourceHandler(models.DatafileHandler):
    datasource_id = 'debian_control_in_source'
    default_package_type = 'deb'
    path_patterns = ('*/debian/control',)
    description = 'Debian control file - source layout'
    documentation_url = 'https://www.debian.org/doc/debian-policy/ch-controlfields.html'

    @classmethod
    def parse(cls, location):
        # TODO: we cannot know the distro from the name only
        # NOTE: a control file in a source repo or debina.tar tarball can contain more than one package
        for debian_data in get_paragraphs_data_from_file(location=location):
            yield build_package_data(
                debian_data,
                datasource_id=cls.datasource_id,
                package_type=cls.default_package_type,
            )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        # two levels up
        root = resource.parent(codebase).parent(codebase)
        if root:
            return models.DatafileHandler.assign_package_to_resources(package, root, codebase, package_adder)


class DebianDscFileHandler(models.DatafileHandler):
    # See http://deb.debian.org/debian/pool/main/p/python-docutils/python-docutils_0.16+dfsg-4.dsc
    # or http://ftp.debian.org/debian/pool/main/7/7kaa/7kaa_2.15.4p1+dfsg-1.dsc
    # these are source control files
    datasource_id = 'debian_source_control_dsc'
    default_package_type = 'deb'
    path_patterns = ('*.dsc',)
    description = 'Debian source control file'
    documentation_url = 'https://wiki.debian.org/dsc'

    @classmethod
    def parse(cls, location):
        # this is typically signed
        debian_data = get_paragraph_data_from_file(
            location=location,
            remove_pgp_signature=True,
        )
        yield build_package_data(
            debian_data=debian_data,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        # only assign this resource
        return models.DatafileHandler.assign_package_to_resources(package, resource, codebase, package_adder)


class DebianInstalledStatusDatabaseHandler(models.DatafileHandler):
    datasource_id = 'debian_installed_status_db'
    default_package_type = 'deb'
    path_patterns = ('*var/lib/dpkg/status',)
    description = 'Debian installed packages database'
    documentation_url = 'https://www.debian.org/doc/debian-policy/ch-controlfields.html'

    @classmethod
    def parse(cls, location):
        # note that we do not know yet the distro at this stage
        # we could get it... but we get that later during assemble()
        for debian_data in get_paragraphs_data_from_file(location):
            yield build_package_data(
                debian_data,
                datasource_id=cls.datasource_id,
                package_type=cls.default_package_type,
            )

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        # get the root resource of the rootfs
        levels_up = len('var/lib/dpkg/status'.split('/'))
        root_resource = get_ancestor(
            levels_up=levels_up,
            resource=resource,
            codebase=codebase,
        )

        package_name = package_data.name

        package = models.Package.from_package_data(
            package_data=package_data,
            datafile_path=resource.path,
        )

        package_file_references = []
        package_file_references.extend(package_data.file_references)
        package_uid = package.package_uid

        dependencies = []
        dependent_packages = package_data.dependencies
        if dependent_packages:
            deps = list(
                models.Dependency.from_dependent_packages(
                    dependent_packages=dependent_packages,
                    datafile_path=resource.path,
                    datasource_id=package_data.datasource_id,
                    package_uid=package_uid,
                )
            )
            dependencies.extend(deps)

        # Multi-Arch can be: "foreign", "same", "allowed", "all", "optional" or
        # empty/non-present. See https://wiki.debian.org/Multiarch/HOWTO

        # We only need to adjust the md5sum/list path in the case of `same`
        qualifiers = package_data.qualifiers or {}
        architecture = qualifiers.get('architecture')

        multi_arch = package_data.extra_data.get('multi_arch')

        if TRACE:
            logger_debug(f' debian: assemble: multi_arch: {multi_arch}')
            logger_debug(f' debian: assemble: architecture: {architecture}')

        if multi_arch == 'same':
            arch_path = f':{architecture}'
        else:
            arch_path = ''

        # collect .list, .md5sum, and copyright file for this package
        # and assemble package data
        assemblable_paths = tuple(set([
            # we try both with and without arch in path for multi-arch support
            f'var/lib/dpkg/info/{package_name}.md5sums',
            f'var/lib/dpkg/info/{package_name}{arch_path}.md5sums',

            f'var/lib/dpkg/info/{package_name}.list',
            f'var/lib/dpkg/info/{package_name}{arch_path}.list',

            f'usr/share/doc/{package_name}/copyright',
        ]))
        resources = []
        # TODO: keep track of missing files
        for res in root_resource.walk(codebase):
            if TRACE:
                logger_debug(f'   debian: assemble: root_walk: res: {res}')
            if not res.path.endswith(assemblable_paths):
                continue

            for pkgdt in res.package_data:
                package_data = models.PackageData.from_dict(pkgdt)
                if TRACE:
                    # logger_debug(f'     debian: assemble: root_walk: package_data: {package_data}')
                    logger_debug(f'     debian: assemble: root_walk: package_data: {package_data.license_expression}')

                # Most debian secondary files are only specific to a name. We
                # have a few cases where the arch is included in the lists and
                # md5sums.
                package.update(
                    package_data=package_data,
                    datafile_path=res.path,
                    replace=False,
                    include_version=False,
                    include_qualifiers=False,
                    include_subpath=False,
                )
                package_file_references.extend(package_data.file_references)

            package_adder(package_uid, res, codebase)

            # yield possible dependencies
            dependent_packages = package_data.dependencies
            if dependent_packages:
                deps = list(
                    models.Dependency.from_dependent_packages(
                        dependent_packages=dependent_packages,
                        datafile_path=res.path,
                        datasource_id=package_data.datasource_id,
                        package_uid=package_uid,
                    )
                )
                dependencies.extend(deps)

            resources.append(res)

        root_path = Path(root_resource.path)

        # FIXME: should we consider ONLY the md5sums?
        # merge references for the same path (e.g. .list amd .md5sum)
        file_references_by_path = {}
        for ref in package_file_references:
            # a file ref extends from the root of the filesystem
            ref_path = str(root_path / ref.path)
            existing = file_references_by_path.get(ref_path)
            if existing:
                existing.update(ref)
            else:
                file_references_by_path[ref_path] = ref

        for res in root_resource.walk(codebase):
            ref = file_references_by_path.get(res.path)
            if not ref:
                continue

            # path is found and processed: remove it, so we can check if we found all of them
            del file_references_by_path[res.path]
            package_adder(package_uid, res, codebase)

            resources.append(res)

        # if we have left over file references, add these to extra data
        if file_references_by_path:
            missing = sorted(file_references_by_path.values(), key=lambda r:r.path)
            package.extra_data['missing_file_references'] = missing

        yield package
        yield from resources
        yield from dependencies


class DebianDistrolessInstalledDatabaseHandler(models.DatafileHandler):
    datasource_id = 'debian_distroless_installed_db'
    default_package_type = 'deb'
    path_patterns = ('*var/lib/dpkg/status.d/*',)
    description = 'Debian distroless installed database'
    documentation_url = 'https://www.debian.org/doc/debian-policy/ch-controlfields.html'

    @classmethod
    def parse(cls, location):
        """
        Yield installed PackageData objects given a ``location``
        var/lib/dpkg/status.d/<status> file as found in a distroless container
        rootfs installation. distroless is derived from Debian but each package
        has its own status file.
        """
        for debian_data in get_paragraphs_data_from_file(location):
            yield build_package_data(
                debian_data,
                datasource_id=cls.datasource_id,
                package_type=cls.default_package_type,
                distro='distroless',
            )

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        # get the root resource of the rootfs
        levels_up = len('var/lib/dpkg/status.d/name'.split('/'))
        root_resource = get_ancestor(
            levels_up=levels_up,
            resource=resource,
            codebase=codebase,
        )

        package_name = package_data.name

        package = models.Package.from_package_data(
            package_data=package_data,
            datafile_path=resource.path,
        )
        package_uid = package.package_uid

        # collect copyright file for this package
        # and merge in package data
        assemblable_paths = (
            f'usr/share/doc/{package_name}/copyright',
        )
        resources = []
        if package_uid:
            for res in root_resource.walk(codebase):
                if not res.path.endswith(assemblable_paths):
                    continue

                for pkgdt in res.package_data:
                    package.update(
                        package_data=pkgdt,
                        datafile_path=res.path,
                    )

                package_adder(package_uid, res, codebase)

                resources.append(res)

        yield package

        dependent_packages = package_data.dependencies
        if dependent_packages:
            yield from models.Dependency.from_dependent_packages(
                dependent_packages=dependent_packages,
                datafile_path=resource.path,
                datasource_id=package_data.datasource_id,
                package_uid=package_uid,
            )

        yield from resources


class DebianInstalledFilelistHandler(models.DatafileHandler):
    # seen in installed rootfs in:
    #  - /var/lib/dpkg/info/<package name>.list
    datasource_id = 'debian_installed_files_list'
    default_package_type = 'deb'
    path_patterns = (
        '*var/lib/dpkg/info/*.list',
    )
    description = 'Debian installed file paths list'

    @classmethod
    def parse(cls, location):
        return parse_debian_files_list(
            location=location,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        # this is assembled only from a database entry
        return


class DebianInstalledMd5sumFilelistHandler(models.DatafileHandler):
    # seen in installed rootfs in:
    #  - /var/lib/dpkg/info/<package name>.md5sums
    #  - /var/lib/dpkg/info/<package name:arch>.md5sums
    datasource_id = 'debian_installed_md5sums'
    default_package_type = 'deb'
    path_patterns = (
        '*var/lib/dpkg/info/*.md5sums',
    )
    description = 'Debian installed file MD5 and paths list'
    documentation_url = 'https://www.debian.org/doc/manuals/debian-handbook/sect.package-meta-information.en.html#sect.configuration-scripts'

    @classmethod
    def parse(cls, location):
        return parse_debian_files_list(
            location=location,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        # this is assembled only from a database entry
        return []


class DebianMd5sumFilelistInPackageHandler(models.DatafileHandler):
    datasource_id = 'debian_md5sums_in_extracted_deb'
    default_package_type = 'deb'
    path_patterns = (
        # in .deb control tarball
        '*/control.tar.gz-extract/md5sums',
        '*/control.tar.xz-extract/md5sums',
    )
    description = 'Debian file MD5 and paths list in .deb archive'
    documentation_url = 'https://www.debian.org/doc/manuals/debian-handbook/sect.package-meta-information.en.html#sect.configuration-scripts'

    @classmethod
    def parse(cls, location):
        return parse_debian_files_list(
            location=location,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        # two levels up
        root = resource.parent(codebase).parent(codebase)
        if root:
            return models.DatafileHandler.assign_package_to_resources(package, root, codebase, package_adder)


def build_package_data_from_package_filename(filename, datasource_id, package_type,):
    """
    Return a PackageData built from the filename of a Debian package archive.
    """

    # TODO: we cannot know the distro from the name only
    deb = DebArchive.from_filename(filename=filename)

    if deb.architecture:
        qualifiers = dict(architecture=deb.architecture)
    else:
        qualifiers = {}

    return models.PackageData(
        datasource_id=datasource_id,
        type=package_type,
        name=deb.name,
        version=deb.version,
        qualifiers=qualifiers,
    )


def parse_debian_files_list(location, datasource_id, package_type):
    """
    Yield PackageData from a list of file paths at locations such as an from a
    Debian installed .list or .md5sums file.
    """
    qualifiers = {}
    filename = fileutils.file_base_name(location)
    if ':' in filename:
        name, _, arch = filename.partition(':')
        qualifiers['arch'] = arch
    else:
        name = filename

    file_references = []
    with open(location) as info_file:
        for line in info_file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # for a plain file lits, the md5sum will be empty
            md5sum, _, path = line.partition(' ')
            path = path.strip()
            md5sum = md5sum and md5sum.strip() or None

            # we ignore dirs in general, and we ignore these that would
            # be created a plain dir when we can
            if path in ignored_root_dirs:
                continue

            ref = models.FileReference(path=path, md5=md5sum)
            file_references.append(ref)

    if not file_references:
        return

    yield models.PackageData(
        datasource_id=datasource_id,
        type=package_type,
        name=name,
        qualifiers=qualifiers,
        file_references=file_references,
    )


def build_package_data(debian_data, datasource_id, package_type='deb', distro=None):
    """
    Return a PackageData object from a package_data mapping (from a dpkg status
    or similar file) or None.
    """
    name = debian_data.get('package')
    version = debian_data.get('version')

    qualifiers = {}
    architecture = debian_data.get('architecture')
    if architecture:
        qualifiers['architecture'] = architecture

    extra_data = {}
    # Multi-Arch can be: "foreign", "same", "allowed", "all", "optional" or
    # empty/non-present. See https://wiki.debian.org/Multiarch/HOWTO
    multi_arch = debian_data.get('multi-arch')
    if multi_arch:
        extra_data['multi_arch'] = multi_arch

    description = debian_data.get('description')
    homepage_url = debian_data.get('homepage')
    size = debian_data.get('installed')

    parties = []

    maintainer = debian_data.get('maintainer')
    if maintainer:
        party = models.Party(role='maintainer', name=maintainer)
        parties.append(party)

    orig_maintainer = debian_data.get('original_maintainer')
    if orig_maintainer:
        party = models.Party(role='original_maintainer', name=orig_maintainer)
        parties.append(party)

    keywords = []
    keyword = debian_data.get('section')
    if keyword:
        keywords.append(keyword)

    source_packages = []
    source = debian_data.get('source')
    if source:
        source_pkg_purl = PackageURL(
            type=package_type,
            name=source,
            namespace=distro
        ).to_string()

        source_packages.append(source_pkg_purl)

    return models.PackageData(
        datasource_id=datasource_id,
        type=package_type,
        namespace=distro,
        name=name,
        version=version,
        qualifiers=qualifiers,
        description=description,
        homepage_url=homepage_url,
        size=size,
        source_packages=source_packages,
        keywords=keywords,
        parties=parties,
        extra_data=extra_data,
    )


ignored_root_dirs = {
    '/.',
    '/bin',
    '/boot',
    '/cdrom',
    '/dev',
    '/etc',
    '/etc/skel',
    '/home',
    '/lib',
    '/lib32',
    '/lib64',
    '/lost+found',
    '/mnt',
    '/media',
    '/opt',
    '/proc',
    '/root',
    '/run',
    '/usr',
    '/sbin',
    '/snap',
    '/sys',
    '/tmp',
    '/usr',
    '/usr/games',
    '/usr/include',
    '/usr/sbin',
    '/usr/share/info',
    '/usr/share/man',
    '/usr/share/misc',
    '/usr/src',

    '/var',
    '/var/backups',
    '/var/cache',
    '/var/lib/dpkg',
    '/var/lib/misc',
    '/var/local',
    '/var/lock',
    '/var/log',
    '/var/opt',
    '/var/run',
    '/var/spool',
    '/var/tmp',
    '/var/lib',
}
