import os
from pathlib import PureWindowsPath

import attr
import logbook
from regipy.exceptions import RegistryKeyNotFoundException
from regipy.registry import RegistryHive

from commoncode.command import execute
from packagedcode import models


logger = logbook.Logger(__name__)
TRACE = False


MSIINFO_BIN_LOCATION = 'packagedcode_msitools.msiinfo'


def get_msiinfo_bin_location():
    """
    Return the binary location for msiinfo
    """
    from plugincode.location_provider import get_location
    msiinfo_bin_loc = get_location(MSIINFO_BIN_LOCATION)
    if not msiinfo_bin_loc:
        raise Exception(
            'CRITICAL: msiinfo not provided. '
            'Unable to continue: you need to install the plugin packagedcode-msitools'
        )
    return msiinfo_bin_loc


class MsiinfoException(Exception):
    pass


def parse_msiinfo_suminfo_output(output_string):
    """
    Return a dictionary containing information from the output of `msiinfo suminfo`
    """
    # Split lines by newline and place lines into a list
    output_list = output_string.split('\n')
    results = {}
    # Partition lines by the leftmost ":", use the string to the left of ":" as
    # the key and use the string to the right of ":" as the value
    for output in output_list:
        key, _, value = output.partition(':')
        if key:
            results[key] = value.strip()
    return results


def get_msi_info(location):
    """
    Run the command `msiinfo suminfo` on the file at `location` and return the
    results in a dictionary

    This function requires the `packagedcode-msiinfo` plugin to be installed on the system
    """
    rc, stdout, stderr = execute(
        cmd_loc=get_msiinfo_bin_location(),
        args=[
            'suminfo',
            location,
        ],
    )
    if stderr:
        error_message = f'Error encountered when reading MSI information from {location}: '
        error_message = error_message + stderr
        raise MsiinfoException(error_message)
    return parse_msiinfo_suminfo_output(stdout)


def msi_parse(location):
    """
    TODO: get proper package name and version from MSI

    Currently, we use the contents `Subject` field from the msiinfo suminfo
    results as the package name because it contains the package name most of
    the time. Getting the version out of the `Subject` string is not
    straightforward because the format of the string is usually different
    between different MSIs
    """
    info = get_msi_info(location)

    author_name = info.get('Author', '')
    parties = []
    if author_name:
        parties.append(
            models.Party(
                type=None,
                role='author',
                name=author_name
            )
        )

    name = info.get('Subject', '')
    description = info.get('Comments', '')
    keywords = info.get('Keywords', '')

    return MsiInstallerPackage(
        name=name,
        description=description,
        parties=parties,
        keywords=keywords,
        extra_data=info
    )


@attr.s()
class MsiInstallerPackage(models.Package):
    filetypes = ('msi installer',)
    mimetypes = ('application/x-msi',)
    extensions = ('.msi',)
    default_type = 'msi'

    @classmethod
    def recognize(cls, location):
        yield msi_parse(location)

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
    except RegistryKeyNotFoundException as ex:
        if TRACE:
            logger.debug('Did not find the key: {}'.format(ex))
        return
    return name_key_entry


def report_installed_dotnet_versions(location, registry_path='\\Microsoft\\NET Framework Setup\\NDP'):
    """
    Return the installed versions of .NET framework. The logic to retrieve
    installed .NET version has been outlined here:
    https://docs.microsoft.com/en-us/dotnet/framework/migration-guide/how-to-determine-which-versions-are-installed

    If `registry_path` is provided, then we will load Registry entries starting
    from `registry_path`
    """
    registry_hive = RegistryHive(location)
    name_key_entry = get_registry_name_key_entry(
        registry_hive=registry_hive,
        registry_path=registry_path
    )
    if not name_key_entry:
        return

    for entry in registry_hive.recurse_subkeys(name_key_entry):
        # The .NET version can be found in the path whose last segment ends with
        # `Full`
        if not entry.path.endswith('\\Full'):
            continue

        dotnet_info = {}
        for dotnet_info_value in entry.values:
            if dotnet_info_value.name == 'Version':
                dotnet_info['version'] = dotnet_info_value.value
            if dotnet_info_value.name == 'InstallPath':
                dotnet_info['InstallPath'] = dotnet_info_value.value

        version = dotnet_info.get('version')
        if not version:
            continue

        install_path = dotnet_info.get('InstallPath')
        extra_data = {}
        if install_path:
            extra_data['install_location'] = install_path

        # Create package
        yield InstalledWindowsProgram(
            name='.NET Framework',
            version=version,
            extra_data=extra_data,
        )


def report_installed_programs(location, registry_path='\\Microsoft\\Windows\\CurrentVersion\\Uninstall'):
    """
    Return the installed programs from a Windows registry file. This is done by
    looking at the entries of the uninstallable programs list.

    If `registry_path` is provided, then we will load Registry entries starting
    from `registry_path`
    """
    registry_hive = RegistryHive(location)
    name_key_entry = get_registry_name_key_entry(
        registry_hive=registry_hive,
        registry_path=registry_path
    )
    if not name_key_entry:
        return

    # Collect Package information and create Package if we have a valid Package name
    for entry in registry_hive.recurse_subkeys(name_key_entry):
        package_info = {}
        for entry_value in entry.values:
            if entry_value.name == 'DisplayName':
                package_info['DisplayName'] = entry_value.value
            if entry_value.name == 'DisplayVersion':
                package_info['DisplayVersion'] = entry_value.value
            if entry_value.name == 'InstallLocation':
                package_info['InstallLocation'] = entry_value.value
            if entry_value.name == 'Publisher':
                package_info['Publisher'] = entry_value.value
            if entry_value.name == 'URLInfoAbout':
                package_info['URLInfoAbout'] = entry_value.value

        name = package_info.get('DisplayName')
        if not name:
            continue

        version = package_info.get('DisplayVersion')
        install_location = package_info.get('InstallLocation')
        publisher = package_info.get('Publisher')

        parties = []
        if publisher:
            parties.append(
                models.Party(
                    type=None,
                    role='publisher',
                    name=publisher
                )
            )

        extra_data = {}
        if install_location:
            extra_data['install_location'] = install_location

        yield InstalledWindowsProgram(
            name=name,
            version=version,
            parties=parties,
            extra_data=extra_data
        )


def reg_parse(location):
    for installed_program in report_installed_programs(location):
        yield installed_program
    for installed_dotnet in report_installed_dotnet_versions(location):
        yield installed_dotnet


def get_installed_programs(root_dir):
    """
    Yield InstalledWindowsProgram objects for every detected installed program
    from Windows registry files in known locations
    """

    # These paths are relative to a Windows docker image layer root directory
    software_delta_loc = os.path.join(root_dir, 'Hives', 'Software_Delta')
    SOFTWARE_reg_file_loc = os.path.join(root_dir, 'Files/Windows/System32/config/SOFTWARE')
    software_registry_locations = [
        software_delta_loc,
        SOFTWARE_reg_file_loc
    ]
    for software_registry_loc in software_registry_locations:
        if not os.path.exists(software_registry_loc):
            continue
        for installed_program in reg_parse(software_registry_loc):
            installed_program.populate_installed_files(root_dir)
            yield installed_program


@attr.s()
class InstalledWindowsProgram(models.Package):
    filetypes = ('SOFTWARE',)
    mimetypes = ('application/octet-stream',)
    default_type = 'windows-program'

    @classmethod
    def recognize(cls, location):
        for installed in reg_parse(location):
            yield installed

    def populate_installed_files(self, root_dir):
        install_location = self.extra_data.get('install_location')
        if not install_location:
            return

        # Manipulate install_location to fit extracted Docker image structure
        install_location = PureWindowsPath(install_location)
        # Remove leading drive letter ("C:\\") and replace all spaces with underscore
        install_location_no_root = install_location.relative_to(*install_location.parts[:1])
        install_location_no_root = str(install_location_no_root)
        install_location_no_root = install_location_no_root.replace(' ', '_')
        install_location_in_image = PureWindowsPath(root_dir).joinpath('Files', PureWindowsPath(install_location_no_root))

        installed_files = []
        for root, _, files in os.walk(install_location_in_image):
            for file in files:
                installed_file_path = os.path.join(root, file)
                installed_files.append(
                    models.PackageFile(path=installed_file_path)
                )

        self.installed_files = installed_files
