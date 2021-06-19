from regipy.exceptions import RegistryKeyNotFoundException
from regipy.registry import RegistryHive
import logbook

import attr

from commoncode.command import execute
from packagedcode import models


logger = logbook.Logger(__name__)


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


def parse(location):
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

    return WindowsMSI(
        name=name,
        description=description,
        parties=parties,
        keywords=keywords,
        extra_data=info
    )


@attr.s()
class WindowsMSI(models.Package):
    metafiles = ()
    extensions = ('.msi',)
    mimetypes = ('application/x-msi',)

    default_type = 'msi'

    default_web_baseurl = None
    default_download_baseurl = None
    default_api_baseurl = None

    @classmethod
    def recognize(cls, location):
        yield parse(location)

# TODO: Find "boilerplate" files, what are the things that we do not care about, e.g. thumbs.db
# TODO: check for chocolatey
# TODO: Windows appstore

def load_registry(location, registry_path='SOFTWARE\\Microsoft\\NET Framework Setup\\NDP'):
    """
    Return the installed versions of .NET framework

    If `registry_path` is provided, then we will load Registry entries starting
    from `registry_path`
    """
    registry_hive = RegistryHive(location)
    if registry_path:
        try:
            name_key_entry = registry_hive.get_key(registry_path)
        except RegistryKeyNotFoundException as ex:
            logger.debug('Did not find the key: {}'.format(ex))
            return
    else:
        name_key_entry = registry_hive.root

    # Check to see if
    start = 'SOFTWARE\\Microsoft\\NET Framework Setup\\NDP'
    for entry in registry_hive.recurse_subkeys(name_key_entry):
        full_subdir = start + '\\Full'
        try:
            dotnet_info_values = registry_hive.get_key(full_subdir).get_values()
        except RegistryKeyNotFoundException:
            # Pass if we cannot find the path with the name and version info
            continue

        dotnet_info = {}
        for dotnet_info_value in dotnet_info_values:
            if dotnet_info_value.name == 'Version':
                dotnet_info['version'] = dotnet_info_value.value

        if not dotnet_info:
            continue

        # Create package
        yield Package
