#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from packagedcode import APPLICATION_PACKAGE_DATAFILE_HANDLERS

def get_dynamic_manifestends():

    """
    This function builds a dynamic list of manifest file extensions that are known
    from all data file handlers in APPLICATION_PACKAGE_DATAFILE_HANDLERS
    """

    manifest_ends = set()
    for handler_class in APPLICATION_PACKAGE_DATAFILE_HANDLERS:
        patterns = getattr(handler_class, 'path_patterns',[])
        for pattern in patterns :
            if pattern.startswith('*'):
                # Extract extension, e.g., '*.json' -> '.json'
                ext = pattern[1:]
                if ext:
                    manifest_ends.add(ext.lower())
            elif pattern.startswith('**/*.'):
                # Handles glob patterns like '**/*.csproj'
                ext = pattern[5:]
                if ext:
                    manifest_ends.add('.' + ext.lower())
    
    return manifest_ends

def get_relative_path(root_path, path):
    """
    Return a path relativefrom the posix 'path' relative to a
    base path of `len_base_path` length where the base is a directory if
    `base_is_dir` True or a file otherwise.
    """
    return path[len(root_path):].lstrip('/')


LEGAL_STARTS_ENDS = (
    'copying',
    'copyright',
    'copyrights',

    'copyleft',
    'notice',
    'license',
    'licenses',
    'licence',
    'licences',
    'licensing',
    'licencing',

    'legal',
    'eula',
    'agreement',
    'copyleft',
    'patent',
    'patents',
)

_MANIFEST_ENDS = get_dynamic_manifestends()

MANIFEST_ENDS = tuple(_MANIFEST_ENDS)

README_STARTS_ENDS = (
    'readme',
)


def check_resource_name_start_and_end(resource, STARTS_ENDS):
    """
    Return True if `resource.name` or `resource.base_name` begins or ends with
    an element of `STARTS_ENDS`
    """
    name = resource.name.lower()
    base_name = resource.base_name.lower()
    return (
        name.startswith(STARTS_ENDS)
        or name.endswith(STARTS_ENDS)
        or base_name.startswith(STARTS_ENDS)
        or base_name.endswith(STARTS_ENDS)
    )


def set_classification_flags(resource,
    _LEGAL=LEGAL_STARTS_ENDS,
    _MANIF=MANIFEST_ENDS,
    _README=README_STARTS_ENDS,
):
    """
    Set classification flags on the `resource` Resource
    """
    path = resource.path.lower()

    resource.is_legal = is_legal = check_resource_name_start_and_end(resource, _LEGAL)
    resource.is_readme = is_readme = check_resource_name_start_and_end(resource, _README)
    # FIXME: this will never be picked up as this is NOT available in a pre-scan plugin
    has_package_data = bool(getattr(resource, 'package_data', False))
    resource.is_manifest = is_manifest = path.endswith(_MANIF) or has_package_data
    resource.is_key_file = (resource.is_top_level and (is_readme or is_legal or is_manifest))
    return resource
