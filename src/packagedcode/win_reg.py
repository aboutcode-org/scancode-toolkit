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
from pathlib import Path
from pathlib import PureWindowsPath

import attr

try:
    from regipy.exceptions import NoRegistrySubkeysException
    from regipy.exceptions import RegistryKeyNotFoundException
    from regipy.registry import RegistryHive
except ImportError:
    pass

from packagedcode import models

# TODO: Find "boilerplate" files, what are the things that we do not care about, e.g. thumbs.db
# TODO: check for chocolatey
# TODO: Windows appstore

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


def get_registry_name_key_entry(registry_hive, registry_path):
    """
    Return the "name" key entry for ```registry_path`` from the ```registry_hive``
    RegistryHive. Return None if the ``registry_path`` is not found.
    """
    try:
        return registry_hive.get_key(registry_path)
    except (RegistryKeyNotFoundException, NoRegistrySubkeysException):
        return


def get_registry_tree(registry_location, registry_path):
    """
    Return a list of dictionaries of Window registry entries from the hive at
    ``registry_location`` found under a given ``registry_path``.
    """
    registry_hive = RegistryHive(registry_location)
    name_key_entry = get_registry_name_key_entry(
        registry_hive=registry_hive, registry_path=registry_path
    )
    if not name_key_entry:
        return []
    return [
        attr.asdict(entry) for entry in registry_hive.recurse_subkeys(name_key_entry, as_json=True)
    ]


def get_installed_dotnet_versions_from_hive(
    location,
    datasource_id,
    package_type,
    registry_path='\\Microsoft\\NET Framework Setup\\NDP',
):
    """
    Yield PackageData for the installed versions of .NET framework from the
    registry hive at ``location``.

    The logic to retrieve installed .NET version has been outlined here:
    https://docs.microsoft.com/en-us/dotnet/framework/migration-guide/how-to-determine-which-versions-are-installed
    """
    registry_tree = get_registry_tree(registry_location=location, registry_path=registry_path)
    yield from get_installed_dotnet_versions_from_regtree(
        registry_tree=registry_tree,
        datasource_id=datasource_id,
        package_type=package_type,
    )


def get_installed_dotnet_versions_from_regtree(
    registry_tree,
    datasource_id,
    package_type,
):
    """
    Yield PackageData for the installed versions of .NET framework from a
    Windows ``registry_tree``.
    """
    if not registry_tree:
        return

    for entry in registry_tree:
        # The .NET version can be found in the path whose last segment ends with
        # `Full`
        if not entry.get('path', '').endswith('\\Full'):
            continue

        file_references = []
        version = None
        for values in entry.get('values', []):
            key = values.get('name')
            value = values.get('value')

            if key == 'Version':
                version = value
            if key == 'InstallPath':
                file_references.append(models.FileReference(path=value))

        yield models.PackageData(
            datasource_id=datasource_id,
            type=package_type,
            name='microsoft-dot-net-framework',
            version=version,
            file_references=file_references,
        )


def get_installed_windows_programs_from_hive(
    location,
    datasource_id,
    package_type,
    registry_path='\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
):
    """
    Yield installed Windows PackageData from a Windows registry file at
    ``location``.

    This is done by looking at the entries of the uninstallable programs list.

    If ``registry_path`` is provided, then we will load Registry entries
    starting from ``registry_path``
    """
    registry_tree = get_registry_tree(registry_location=location, registry_path=registry_path)
    yield from get_installed_windows_programs_from_regtree(
        registry_tree=registry_tree,
        datasource_id=datasource_id,
        package_type=package_type,
    )


def get_installed_windows_programs_from_regtree(
    registry_tree,
    datasource_id,
    package_type,
):
    """
    Yield installed Windows PackageData from a Windows ``registry_tree``.
    """
    if not registry_tree:
        return

    field_by_regkey = {
        'DisplayName': 'name',
        'DisplayVersion': 'version',
        'URLInfoAbout': 'homepage_url',
        'Publisher': 'publisher',
        'DisplayIcon': 'display_icon',
        'UninstallString': 'uninstall_string',
        'InstallLocation': 'install_location',
    }

    for entry in registry_tree:
        package_info = {}
        for entry_value in entry.get('values', []):
            key = entry_value.get('name')
            value = entry_value.get('value')
            pkg_field = field_by_regkey.get(key)
            if pkg_field:
                package_info[pkg_field] = value

        name = package_info.get('name')
        version = package_info.get('version')

        homepage_url = package_info.get('homepage_url')
        publisher = package_info.get('publisher')

        parties = []
        if publisher:
            parties.append(
                models.Party(
                    type=models.party_org,
                    role='publisher',
                    name=publisher,
                )
            )

        file_references = []
        install_location = package_info.get('install_location')
        if install_location:
            file_references.append(models.FileReference(path=install_location))

        display_icon = package_info.get('display_icon')
        if display_icon:
            file_references.append(models.FileReference(path=display_icon))

        uninstall_string = package_info.get('uninstall_string')
        if uninstall_string:
            file_references.append(models.FileReference(path=uninstall_string))

        yield models.PackageData(
            datasource_id=datasource_id,
            type=package_type,
            name=name,
            version=version,
            parties=parties,
            homepage_url=homepage_url,
            file_references=file_references,
        )


def get_packages_from_registry_from_hive(
    location,
    datasource_id,
    package_type,
):
    """
    Yield PackageData for Installed Windows Programs from the Windows registry
    hive at ``location``
    """
    yield from get_installed_windows_programs_from_hive(
        location=location,
        datasource_id=datasource_id,
        package_type=package_type,
        registry_path='\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
    )

    yield from get_installed_windows_programs_from_hive(
        location=location,
        datasource_id=datasource_id,
        package_type=package_type,
        registry_path='\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
    )

    yield from get_installed_dotnet_versions_from_hive(
        location=location,
        datasource_id=datasource_id,
        package_type=package_type,
        registry_path='\\Microsoft\\NET Framework Setup\\NDP',
    )


def get_installed_packages(root_dir, is_container=True):
    """
    Yield PackageData for Installed Windows Programs for every detected
    installed program from Windows registry hive files found in well known
    locations under a ``root_dir`` root filesystem directory.
    """
    # These paths are relative to a Windows docker image layer root directory
    if is_container:
        hives_software_delta_loc = os.path.join(root_dir, 'Hives/Software_Delta')
        files_software_loc = os.path.join(root_dir, 'Files/Windows/System32/config/SOFTWARE')
        utilityvm_software_loc = os.path.join(
            root_dir, 'UtilityVM/Files/Windows/System32/config/SOFTWARE'
        )
        root_prefixes_by_software_reg_locations = {
            hives_software_delta_loc: 'Files',
            files_software_loc: 'Files',
            utilityvm_software_loc: 'UtilityVM/Files',
        }
    else:
        # TODO: Add support for virtual machines
        raise Exception('Unsuported file system type')

    for software_reg_loc, root_prefix in root_prefixes_by_software_reg_locations.items():
        if not os.path.exists(software_reg_loc):
            continue
        for package in get_packages_from_registry_from_hive(software_reg_loc):
            package.populate_installed_files(root_dir, root_prefix=root_prefix)
            yield package


def remove_drive_letter(path):
    """
    Given a Windows path string, remove the leading drive letter and return the
    path string as a POSIX-styled path.
    """
    # Remove leading drive letter ("C:\\")
    path = PureWindowsPath(path)
    path_no_drive_letter = path.relative_to(*path.parts[:1])
    # POSIX-ize the path
    posixed_path = path_no_drive_letter.as_posix()
    return posixed_path


def create_absolute_installed_file_path(root_dir, file_path):
    """
    Return an absolute path to `file_path` given the root directory path at
    `root_dir`
    """
    file_path = remove_drive_letter(file_path)
    # Append the install location to the path string `root_dir`
    return str(Path(root_dir).joinpath(file_path))


def create_relative_file_path(file_path, root_dir, root_prefix=''):
    """
    Return a subpath of `file_path` that is relative to `root_dir`

    >>> file_path = '/home/test/example/foo.txt'
    >>> root_dir = '/home/test/'
    >>> create_relative_file_path(file_path, root_dir)
    'example/foo.txt'

    If there is a `root_prefix`, then it is prepended to the resulting
    relative file path.

    >>> file_path = '/home/test/example/foo.txt'
    >>> root_dir = '/home/test/'
    >>> create_relative_file_path(file_path, root_dir, 'prefix')
    'prefix/example/foo.txt'
    """
    relative_file_path = str(Path(file_path).relative_to(root_dir))
    if root_prefix:
        return os.path.join(root_prefix, relative_file_path)
    return relative_file_path


class BaseRegInstalledProgramHandler(models.DatafileHandler):
    default_package_type = 'windows-program'
    documentation_url = 'https://en.wikipedia.org/wiki/Windows_Registry'

    # The rootfs location (of a Docker image layer) can be in a
    # subdirectory of the layer tree. This is a path to the root of the windows filesystem relative to the
    # datafile (e.g. the registry hive file)

    root_path_relative_to_datafile_path = None

    @classmethod
    def parse(cls, location):
        yield from get_packages_from_registry_from_hive(
            location=location,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )

    @classmethod
    def get_root_resource(cls, resource, codebase):
        """
        Return the root Resource given  a datafile ``resource`` in ``codebase``.
        """
        segments = cls.root_path_relative_to_datafile_path.split('/')

        has_root = True
        for segment in segments:
            if segment == '..':
                resource = resource.parent(codebase)
                if not resource:
                    has_root = False
                    break
            else:
                ress = [r for r in resource.children(codebase) if r.name == segment]
                if not len(ress) == 1:
                    has_root = False
                    break
                resource = ress[0]

            if not resource:
                has_root = False
                break

        if has_root:
            return resource

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        package_uid = package.package_uid
        if package_uid:
            package_adder(package_uid, resource, codebase)

        refs = package.file_references
        if not refs:
            return

        root = cls.get_root_resource(resource, codebase)
        if not root:
            # FIXME: this should not happen
            return

        root_path = Path(root.path)

        refs_by_path = {}
        for ref in refs:
            # a file ref may be a Windows path with a drive
            ref_path = remove_drive_letter(ref.path)
            # a file ref extends from the root of the Windows filesystem
            refs_by_path[str(root_path / ref_path)] = ref

        for res in root.walk(codebase):
            ref = refs_by_path.get(res.path)
            if not ref:
                continue

            if package_uid:
                # path is found and processed: remove it, so we can check if we
                # found all of them
                del refs_by_path[res.path]
                package_adder(package_uid, res, codebase)

        # if we have left over file references, add these to extra data
        if refs_by_path:
            missing = sorted(refs_by_path.values(), key=lambda r: r.path)
            package.extra_data['missing_file_references'] = missing


class InstalledProgramFromDockerSoftwareDeltaHandler(BaseRegInstalledProgramHandler):
    datasource_id = 'win_reg_installed_programs_docker_software_delta'
    path_patterns = ('*/Hives/Software_Delta',)
    description = 'Windows Registry Installed Program - Docker Software Delta'
    root_path_relative_to_datafile_path = '../../Files'


class InstalledProgramFromDockerFilesSoftwareHandler(BaseRegInstalledProgramHandler):
    datasource_id = 'win_reg_installed_programs_docker_file_software'
    path_patterns = ('*/Files/Windows/System32/config/SOFTWARE',)
    description = 'Windows Registry Installed Program - Docker SOFTWARE'
    root_path_relative_to_datafile_path = '../../../..'


class InstalledProgramFromDockerUtilityvmSoftwareHandler(BaseRegInstalledProgramHandler):
    datasource_id = 'win_reg_installed_programs_docker_utility_software'
    path_patterns = ('*/UtilityVM/Files/Windows/System32/config/SOFTWARE',)
    description = 'Windows Registry Installed Program - Docker UtilityVM SOFTWARE'
    root_path_relative_to_datafile_path = '../../../..'
