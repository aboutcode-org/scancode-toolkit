#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
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


# Tracing flags
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import sys
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str)
                                     and a or repr(a) for a in args))


# TODO: Find "boilerplate" files, what are the things that we do not care about, e.g. thumbs.db
# TODO: check for chocolatey
# TODO: Windows appstore

def get_registry_name_key_entry(registry_hive, registry_path):
    """
    Given a RegistryHive `registry_hive`, return the name key entry for
    `registry_path` from `registry_hive`

    Return if the registry path cannot be found.
    """
    try:
        name_key_entry = registry_hive.get_key(registry_path)
    except (RegistryKeyNotFoundException, NoRegistrySubkeysException) as ex:
        if TRACE:
            logger_debug('Did not find the key: {}'.format(ex))
        return
    return name_key_entry


def get_registry_tree(registry_location, registry_path):
    """
    Return a list of dictionaries of Window registry entries found under a given
    registry path
    """
    registry_hive = RegistryHive(registry_location)
    name_key_entry = get_registry_name_key_entry(
        registry_hive=registry_hive,
        registry_path=registry_path
    )
    if not name_key_entry:
        return []
    return [attr.asdict(entry) for entry in registry_hive.recurse_subkeys(name_key_entry, as_json=True)]


def report_installed_dotnet_versions(location, registry_path='\\Microsoft\\NET Framework Setup\\NDP'):
    """
    Yield the installed versions of .NET framework from `location`. The logic to
    retrieve installed .NET version has been outlined here:
    https://docs.microsoft.com/en-us/dotnet/framework/migration-guide/how-to-determine-which-versions-are-installed
    """
    registry_tree = get_registry_tree(location, registry_path)
    return _report_installed_dotnet_versions(registry_tree)


def _report_installed_dotnet_versions(registry_tree):
    if not registry_tree:
        return

    for entry in registry_tree:
        # The .NET version can be found in the path whose last segment ends with
        # `Full`
        if not entry.get('path', '').endswith('\\Full'):
            continue

        dotnet_info = {}
        for dotnet_info_value in entry.get('values', []):
            dotnet_info_value_name = dotnet_info_value.get('name')
            dotnet_info_value_value = dotnet_info_value.get('value')
            if dotnet_info_value_name == 'Version':
                dotnet_info['version'] = dotnet_info_value_value
            if dotnet_info_value_name == 'InstallPath':
                dotnet_info['InstallPath'] = dotnet_info_value_value

        version = dotnet_info.get('version')
        if not version:
            continue

        install_path = dotnet_info.get('InstallPath')
        extra_data = {}
        if install_path:
            extra_data['install_location'] = install_path

        # Yield package
        yield InstalledWindowsProgram(
            name='Microsoft .NET Framework',
            version=version,
            extra_data=extra_data,
        )


def report_installed_programs(location, registry_path='\\Microsoft\\Windows\\CurrentVersion\\Uninstall'):
    """
    Yield installed Windows packages from a Windows registry file at `location`.
    This is done by looking at the entries of the uninstallable programs list.

    If `registry_path` is provided, then we will load Registry entries starting
    from `registry_path`
    """
    registry_tree = get_registry_tree(location, registry_path)
    return _report_installed_programs(registry_tree)


def _report_installed_programs(registry_tree):
    if not registry_tree:
        return

    # Collect Package information and create Package if we have a valid Package name
    for entry in registry_tree:
        package_info = {}
        for entry_value in entry.get('values', []):
            name = entry_value.get('name')
            value = entry_value.get('value')

            if name == 'DisplayName':
                package_info['name'] = value
            if name == 'DisplayVersion':
                package_info['version'] = value
            if name == 'InstallLocation':
                package_info['install_location'] = value
            if name == 'Publisher':
                package_info['publisher'] = value
            if name == 'URLInfoAbout':
                package_info['homepage_url'] = value
            if name == 'DisplayIcon':
                package_info['DisplayIcon'] = value
            if name == 'UninstallString':
                package_info['UninstallString'] = value

        name = package_info.get('name')
        if not name:
            continue

        version = package_info.get('version')
        homepage_url = package_info.get('homepage_url')
        install_location = package_info.get('install_location')
        publisher = package_info.get('publisher')
        display_icon = package_info.get('DisplayIcon')
        uninstall_string = package_info.get('UninstallString')

        parties = []
        if publisher:
            parties.append(
                models.Party(
                    type=models.party_org,
                    role='publisher',
                    name=publisher
                )
            )

        known_program_files = []
        if display_icon:
            known_program_files.append(display_icon)
        if uninstall_string:
            known_program_files.append(uninstall_string)

        extra_data = {}
        if install_location:
            extra_data['install_location'] = install_location
        if known_program_files:
            extra_data['known_program_files'] = known_program_files

        yield InstalledWindowsProgram(
            name=name,
            version=version,
            parties=parties,
            homepage_url=homepage_url,
            extra_data=extra_data
        )


def reg_parse(location):
    """
    Yield InstalledWindowsPrograms from `location` using
    `report_installed_programs` and `report_installed_dotnet_versions`
    """
    for installed_program in report_installed_programs(location):
        yield installed_program
    for installed_program in report_installed_programs(
        location,
        registry_path='\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
    ):
        yield installed_program
    for installed_dotnet in report_installed_dotnet_versions(location):
        yield installed_dotnet


def get_installed_packages(root_dir, is_container=True):
    """
    Yield InstalledWindowsProgram objects for every detected installed program
    from Windows registry files in known locations
    """
    # These paths are relative to a Windows docker image layer root directory
    if is_container:
        hives_software_delta_loc = os.path.join(root_dir, 'Hives', 'Software_Delta')
        files_software_loc = os.path.join(
            root_dir,
            'Files',
            'Windows',
            'System32',
            'config',
            'SOFTWARE'
        )
        utilityvm_software_loc = os.path.join(
            root_dir,
            'UtilityVM',
            'Files',
            'Windows',
            'System32',
            'config',
            'SOFTWARE'
        )
        root_prefixes_by_software_registry_locations = {
            hives_software_delta_loc: 'Files',
            files_software_loc: 'Files',
            utilityvm_software_loc: os.path.join('UtilityVM', 'Files')
        }
    else:
        # TODO: Add support for virtual machines
        raise Exception('Unsuported file system type')

    for software_registry_loc, root_prefix in root_prefixes_by_software_registry_locations.items():
        if not os.path.exists(software_registry_loc):
            continue
        for package in reg_parse(software_registry_loc):
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


@attr.s()
class InstalledWindowsProgram(models.Package):
    default_type = 'windows-program'

    @classmethod
    def recognize(cls, location):
        for installed in reg_parse(location):
            yield installed

    def populate_installed_files(self, root_dir, root_prefix=''):
        install_location = self.extra_data.get('install_location')
        if not install_location:
            return

        if root_prefix:
            # The rootfs location of a Docker image layer can be in a
            # subdirectory of the layer directory (where `root_dir` is the path
            # to the layer directory), so we append `root_prefix` (where prefix
            # is relative to the file paths within the Docker image layer's
            # rootfs files) to `root_dir`
            root_dir = os.path.join(root_dir, root_prefix)

        absolute_install_location = create_absolute_installed_file_path(
            root_dir=root_dir,
            file_path=install_location
        )
        if not os.path.exists(absolute_install_location):
            return

        installed_files = []
        for root, _, files in os.walk(absolute_install_location):
            for file in files:
                installed_file_location = os.path.join(root, file)
                relative_installed_file_path = create_relative_file_path(
                    file_path=installed_file_location,
                    root_dir=root_dir,
                    root_prefix=root_prefix
                )
                installed_files.append(relative_installed_file_path)

        known_program_files = self.extra_data.get('known_program_files', [])
        for known_program_file_path in known_program_files:
            known_program_file_location = create_absolute_installed_file_path(
                root_dir=root_dir,
                file_path=known_program_file_path,
            )
            relative_known_file_path = create_relative_file_path(
                file_path=known_program_file_location,
                root_dir=root_dir,
                root_prefix=root_prefix
            )
            if (not os.path.exists(known_program_file_location)
                    or relative_known_file_path in installed_files):
                continue
            installed_files.append(relative_known_file_path)

        self.installed_files = [models.PackageFile(path=path) for path in sorted(installed_files)]
